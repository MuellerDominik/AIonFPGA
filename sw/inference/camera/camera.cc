/**
 * aionfpga ~ camera (libcamera.so)
 * Copyright (C) 2020 Dominik Müller and Nico Canzani
 */

#include "opencv2/opencv.hpp" // OpenCV
#include "bgapi2_genicam/bgapi2_genicam.hpp" // Baumer GAPI

// Return Codes
enum returncodes {
    SUCCESS = 0,

    ERROR = 1, // Generic error

    NO_SYSTEMS = 2, // Producers
    NO_INTERFACES = 3,
    NO_DEVICES = 4,
    NO_DATASTREAMS = 5,

    NOT_INITIALIZED = 6,
    NOT_IMPLEMENTED = 7,
    RESOURCE_IN_USE = 8,
    ACCESS_DENIED = 9,
    INVALID_HANDLE = 10,
    OBJECT_INVALIDID = 11,
    NO_DATA = 12,
    INVALID_PARAMETER = 13,
    LOW_LEVEL = 14,
    ABORT = 15,
    INVALID_BUFFER = 16,
    NOT_AVAILABLE = 17
};

// Configuration
const int width = 1280;
const int height = 1024;

const unsigned payloadsize = (unsigned)(width * height);

volatile double frame_rate = 200.0; // fps
volatile unsigned buff_size = 200; // 200 ≙ 1 s @ 200 fps
volatile unsigned exposure_time = 250; // us
volatile unsigned camera_gain = 4;

volatile unsigned avg_diffs = 8; // 8 diffs ≙ 40 ms @ 200 fps
volatile double threshold_mult = 1.1;

volatile unsigned frames_to_acquire = 44; // max. amount of frames to acquire

// Parameters
double mean_diff, threshold, sum_thresh;

unsigned frame_id;
// Index (frame_id) of the beginning/end of the throw
volatile unsigned throw_bgn_idx;
volatile unsigned throw_end_idx;
// Begin/end of the throw
volatile bool throw_bgn;
volatile bool throw_end;

int returncode = SUCCESS;

// OpenCV
cv::Mat* cv_buffer;
cv::Mat cv_abs;

// Baumer
BGAPI2::SystemList* systemList = NULL;
BGAPI2::System* pSystem = NULL;
BGAPI2::String sSystemID;

BGAPI2::InterfaceList* interfaceList = NULL;
BGAPI2::Interface* pInterface = NULL;
BGAPI2::String sInterfaceID;

BGAPI2::DeviceList* deviceList = NULL;
BGAPI2::Device* pDevice = NULL;
BGAPI2::String sDeviceID;

BGAPI2::DataStreamList* datastreamList = NULL;
BGAPI2::DataStream* pDataStream = NULL;
BGAPI2::String sDataStreamID;

BGAPI2::BufferList* bufferList = NULL;
BGAPI2::Buffer* pBuffer = NULL;

// Buffer
char** pMemoryBlock;

// Getter
extern "C" void* get_frame_ptr(unsigned idx) {
    return (void*)cv_buffer[idx % buff_size].data;
}

extern "C" unsigned get_throw_bgn_idx() {
    return throw_bgn_idx;
}

extern "C" unsigned get_throw_end_idx() {
    return throw_end_idx;
}

extern "C" bool get_throw_bgn() {
    return throw_bgn;
}

extern "C" bool get_throw_end() {
    return throw_end;
}

// Setter
extern "C" void set_frame_rate(double frame_rate) {
    ::frame_rate = frame_rate;
}

extern "C" void set_buff_size(unsigned buff_size) {
    ::buff_size = buff_size;
}

extern "C" void set_exposure_time(unsigned exposure_time) {
    ::exposure_time = exposure_time;
}

extern "C" void set_camera_gain(unsigned camera_gain) {
    ::camera_gain = camera_gain;
}

extern "C" void set_avg_diffs(unsigned avg_diffs) {
    ::avg_diffs = avg_diffs;
}

extern "C" void set_threshold_mult(double threshold_mult) {
    ::threshold_mult = threshold_mult;
}

extern "C" void set_frames_to_acquire(unsigned frames_to_acquire) {
    ::frames_to_acquire = frames_to_acquire;
}

// Camera
extern "C" int initialize() {

    pMemoryBlock = new char*[buff_size];

    cv_buffer = new cv::Mat[buff_size];

    try {
        // Instantiate and update SystemList
        systemList = BGAPI2::SystemList::GetInstance();
        systemList->Refresh();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Iterate over the SystemList
        for (BGAPI2::SystemList::iterator sysIterator = systemList->begin(); sysIterator != systemList->end(); sysIterator++) {

            try {
                // Open System
                sysIterator->second->Open();
                sSystemID = sysIterator->first;

                try {
                    // Get and update the InterfaceList
                    interfaceList = sysIterator->second->GetInterfaces();
                    interfaceList->Refresh(100); // Timeout of 100 ms
                } catch (BGAPI2::Exceptions::IException &ex) {
                    returncode = SUCCESS == returncode ? ERROR : returncode;
                }

                try {
                    // Iterate over the InterfaceList
                    for (BGAPI2::InterfaceList::iterator ifIterator = interfaceList->begin(); ifIterator != interfaceList->end(); ifIterator++) {
                        try {
                            // Search for Devices connected to the Interface
                            ifIterator->second->Open();
                            deviceList = ifIterator->second->GetDevices();
                            deviceList->Refresh(100); // Timeout of 100 ms
                            if (deviceList->size() == 0) {
                                ifIterator->second->Close();
                            } else {
                                // If a Device is connected to the Interface, leave the Interface loop
                                sInterfaceID = ifIterator->first;
                                break;
                            }
                        } catch (BGAPI2::Exceptions::ResourceInUseException &ex) {
                            // If in use, skip the Interface
                            returncode = SUCCESS == returncode ? RESOURCE_IN_USE : returncode;
                        }
                    }
                } catch (BGAPI2::Exceptions::IException &ex) {
                    returncode = SUCCESS == returncode ? ERROR : returncode;
                }

                // If a Device is connected to the Interface, leave the System loop
                if (sInterfaceID != "") {
                    break;
                }
            } catch (BGAPI2::Exceptions::ResourceInUseException &ex) {
                // If in use, skip the System
                returncode = SUCCESS == returncode ? RESOURCE_IN_USE : returncode;
            }
        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    if (sSystemID == "") {
        BGAPI2::SystemList::ReleaseInstance();
        return NO_SYSTEMS;
    } else {
        pSystem = (*systemList)[sSystemID];
    }

    if (sInterfaceID == "") {
        pSystem->Close();
        BGAPI2::SystemList::ReleaseInstance();
        // Either there are no Interfaces present or no Devices in any of the present Interfaces (more likely)
        return NO_DEVICES; // NO_INTERFACES
    } else {
        pInterface = (*interfaceList)[sInterfaceID];
    }

    try {
        // Get and update DeviceList
        deviceList = pInterface->GetDevices();
        deviceList->Refresh(100); // Timeout of 100 ms
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Iterate over the DeviceList
        for (BGAPI2::DeviceList::iterator devIterator = deviceList->begin(); devIterator != deviceList->end(); devIterator++) {
            try {
                // Open Device
                devIterator->second->Open();
                sDeviceID = devIterator->first;
                break;
            } catch (BGAPI2::Exceptions::ResourceInUseException &ex) {
                // If in use, skip the Device
                returncode = SUCCESS == returncode ? RESOURCE_IN_USE : returncode;
            }
        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    // Device unplugged since the initial check or in use
    if (sDeviceID == "") {
        pInterface->Close();
        pSystem->Close();
        BGAPI2::SystemList::ReleaseInstance();
        return NO_DEVICES;
    } else {
        pDevice = (*deviceList)[sDeviceID];
    }

    try {
        // Device configuration

        // Stop acquisition
        pDevice->GetRemoteNode("AcquisitionStop")->Execute();

        // White balance (once at the beginning)
        pDevice->GetRemoteNode("BalanceWhiteAuto")->SetValue("Once");

        // Set gain to `camera_gain` and exposure time to `exposure_time`
        pDevice->GetRemoteNode("Gain")->SetDouble(camera_gain);
        pDevice->GetRemoteNode("ExposureTime")->SetDouble(exposure_time);

        // Set frame rate to `frame_rate`
        pDevice->GetRemoteNode("AcquisitionFrameRateEnable")->SetBool(true);
        pDevice->GetRemoteNode("AcquisitionFrameRate")->SetDouble(frame_rate);

        // Set trigger mode to `Off` (free run)
        pDevice->GetRemoteNode("TriggerMode")->SetString("Off");

        // Set pixel format to `BayerRG8` (necessary to achieve the max. frame rate)
        pDevice->GetRemoteNode("PixelFormat")->SetString("BayerRG8");

    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Get and update DataStreamList
        datastreamList = pDevice->GetDataStreams();
        datastreamList->Refresh();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Iterate over the DataStreamList
        for (BGAPI2::DataStreamList::iterator dstIterator = datastreamList->begin(); dstIterator != datastreamList->end(); dstIterator++) {
            // Open DataStream
            dstIterator->second->Open();
            sDataStreamID = dstIterator->first;
            break;
        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    if (sDataStreamID == "") {
        pDevice->Close();
        pInterface->Close();
        pSystem->Close();
        BGAPI2::SystemList::ReleaseInstance();
        return NO_DATASTREAMS;
    } else {
        pDataStream = (*datastreamList)[sDataStreamID];
    }

    try {
        // Get BufferList
        bufferList = pDataStream->GetBufferList();

        // Create `buff_size` Buffers (encapsulates a single memory buffer) and add them to the BufferList
        for (unsigned i = 0; i < buff_size; ++i) {
            pMemoryBlock[i] = (char*)new char[payloadsize];
            pBuffer = new BGAPI2::Buffer(pMemoryBlock[i], (bo_uint64)payloadsize, NULL);
            bufferList->Add(pBuffer);
        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    return returncode;
}

extern "C" int start_acquisition() {

    // Reset global variables
    mean_diff = 0.0;
    threshold = 0.0;
    sum_thresh = 0.0;

    frame_id = 0;
    throw_bgn_idx = 0;
    throw_end_idx = 0;
    throw_bgn = false;
    throw_end = false;

    returncode = SUCCESS;

    // Declare local variables
    // Is set to true one frame before `throw_bgn` and used to detect glitches
    // (using a separate variable prevents applications reading the global variables form getting a false positive)
    bool throw_bgn_tmp = false;

    try {
        // Allocate all of the Buffers to the input queue of the DataStream
        bufferList->FlushAllToInputQueue();

    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Start DataStream acquisition
        pDataStream->StartAcquisitionContinuous();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Start the Device
        pDevice->GetRemoteNode("AcquisitionStart")->Execute();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    // Process the aquired frames in real-time (detect throw)
    BGAPI2::Buffer *pBufferFilled = NULL;
    BGAPI2::Buffer *prev_pBufferFilled = NULL; // Previous Buffer object
    try {
        while (!throw_end) {

            pBufferFilled = pDataStream->GetFilledBuffer(15); // Timeout of 15 ms

            if (pBufferFilled == NULL) {
                // Buffer timeout after 15 ms corresponds to a loss of 3 frames @ 200 fps
            } else if (pBufferFilled->GetIsIncomplete() == true) {
                // Image incomplete, queue buffer again
                pBufferFilled->QueueBuffer();
            } else {

                // OpenCV matrix with Baumer BayerRG8 (OpenCV BayerBG) pixel format
                cv_buffer[frame_id % buff_size] = cv::Mat(height, width, CV_8UC1, (void*)pBufferFilled->GetMemPtr());

                if (frame_id != 0) { // Skip the first frame (no difference computation possible)

                    // Compute the mean pixel difference
                    cv::absdiff(cv_buffer[frame_id % buff_size], cv_buffer[(frame_id - 1) % buff_size], cv_abs);
                    mean_diff = cv::sum(cv_abs)[0] / (width * height);

                    // Average diffs over (`avg_diffs` + 1) frames
                    if (frame_id < avg_diffs) {
                        sum_thresh += mean_diff;
                    } else if (frame_id == avg_diffs) {
                        sum_thresh += mean_diff;
                        threshold = sum_thresh / avg_diffs * threshold_mult;
                    } else {

                        // Detect throw
                        if (mean_diff >= threshold) {
                            if (!throw_bgn_tmp) {
                                throw_bgn_idx = frame_id;
                                // Make sure a glitch is not misinterpreted as the beginning of a throw
                                throw_bgn_tmp = true;
                            } else if (!throw_bgn) { // throw_bgn_tmp has been set, but not throw_bgn
                                throw_bgn = true;
                            } else if ((frame_id - throw_bgn_idx - 1) == frames_to_acquire) {
                                throw_end_idx = frame_id;
                                throw_end = true;
                                break; // not necessary (shows that the while loop execution is terminated here)
                            }
                        } else {
                            if (throw_bgn) {
                                throw_end_idx = frame_id;
                                throw_end = true;
                                break; // not necessary (shows that the while loop execution is terminated here)
                            // Remove glitches (a single frame change is considered a glitch)
                            } else if (throw_bgn_tmp) { // throw_bgn_tmp has been set, but not throw_bgn
                                prev_pBufferFilled->QueueBuffer();
                                throw_bgn_tmp = false;
                            }
                        }

                    }

                }

                // If no throw is detected, release the Buffer
                if (!throw_bgn_tmp) { // !throw_bgn && !throw_bgn_tmp
                    pBufferFilled->QueueBuffer();
                } else {
                    prev_pBufferFilled = pBufferFilled;
                }

                ++frame_id;

            }

        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Stop the Device
        pDevice->GetRemoteNode("AcquisitionAbort")->Execute();
        pDevice->GetRemoteNode("AcquisitionStop")->Execute();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Stop the DataStream acquisition
        pDataStream->StopAcquisition();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    return returncode;
}

extern "C" int terminate() {

    delete[] cv_buffer;

    try {
        // Stop the DataStream acquisition
        bufferList->DiscardAllBuffers();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Release the Buffers
        while (bufferList->size() > 0) {
            pBuffer = bufferList->begin()->second;
            bufferList->RevokeBuffer(pBuffer);
            delete pBuffer;
        }

        for (unsigned i = 0; i < buff_size; ++i) {
            if (pMemoryBlock[i]) {
                delete[] pMemoryBlock[i];
            }
        }

        delete[] pMemoryBlock;

        pDataStream->Close();
        pDevice->Close();
        pInterface->Close();
        pSystem->Close();
        BGAPI2::SystemList::ReleaseInstance();
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    return returncode;
}
