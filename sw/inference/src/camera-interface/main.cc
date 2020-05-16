/**
 * aionfpga ~ camera interface
 * Copyright (C) 2020 Dominik Müller and Nico Canzani
 */

#include <string>

#include "opencv2/opencv.hpp" // OpenCV
#include "bgapi2_genicam/bgapi2_genicam.hpp" // Baumer GAPI

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

int main(int argc, char **argv) {

    // Configuration
    const int width = 1280;
    const int height = 1024;
    const double frame_rate = 200; // fps
    const unsigned buff_size = 200; // 200 ≙ 1 s @ 200 fps
    const unsigned exposure_time = 250; // us
    const unsigned camera_gain = 4;
    const unsigned avg_diffs = 8; // 8 diffs ≙ 40 ms @ 200 fps
    const double threshold_mult = 1.1;
    const std::string output_path = "/home/xilinx/imgs/";

    // Parameters
    double mean_diff;
    double threshold;
    double sum_thresh = 0;

    unsigned frame_id = 0;
    unsigned throw_bgn_idx, throw_end_idx;
    bool throw_bgn = false; // Begin of the throw
    bool throw_end = false; // End of the throw

    int returncode = SUCCESS;

    // OpenCV
    cv::Mat cv_buffer[buff_size];
    cv::Mat cv_abs, cv_transformed;

    // Baumer
    BGAPI2::SystemList *systemList = NULL;
    BGAPI2::System *pSystem = NULL;
    BGAPI2::String sSystemID;

    BGAPI2::InterfaceList *interfaceList = NULL;
    BGAPI2::Interface *pInterface = NULL;
    BGAPI2::String sInterfaceID;

    BGAPI2::DeviceList *deviceList = NULL;
    BGAPI2::Device *pDevice = NULL;
    BGAPI2::String sDeviceID;

    BGAPI2::DataStreamList *datastreamList = NULL;
    BGAPI2::DataStream *pDataStream = NULL;
    BGAPI2::String sDataStreamID;

    BGAPI2::BufferList *bufferList = NULL;
    BGAPI2::Buffer *pBuffer = NULL;

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
        for (int i = 0; i < buff_size; ++i) {
            pBuffer = new BGAPI2::Buffer();
            bufferList->Add(pBuffer);
        }
    } catch (BGAPI2::Exceptions::IException &ex) {
        returncode = SUCCESS == returncode ? ERROR : returncode;
    }

    try {
        // Allocate all of the Buffers to the input queue of the DataStream
        for (BGAPI2::BufferList::iterator bufIterator = bufferList->begin(); bufIterator != bufferList->end(); bufIterator++) {
            bufIterator->second->QueueBuffer();
        }
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
                cv_buffer[frame_id % buff_size] = cv::Mat(height, width, CV_8UC1, (void *)pBufferFilled->GetMemPtr());

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
                            if (!throw_bgn) {
                                throw_bgn_idx = frame_id;
                                throw_bgn = true;
                            }
                        } else {
                            if (throw_bgn) {
                                throw_end_idx = frame_id;

                                // Remove glitches (a single frame change is considered a glitch)
                                // NOTE: Each removed glitch decrements the Buffer size.
                                //       This is due to the fact, that the reference to the filled Buffer object is already lost, once a glitch is detected.
                                //       So there is no way to queue the respective Buffer object again.
                                //       This could be solved by keeping track of at least one of the filled Buffer objects.
                                if ((throw_end_idx - throw_bgn_idx) == 1) {
                                    throw_bgn = false;
                                } else {
                                    throw_end = true;
                                }
                            }
                        }

                    }

                }

                ++frame_id;

                // If no throw is detected, release the Buffer
                if (!throw_bgn) {
                    pBufferFilled->QueueBuffer();
                }

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

    // Save the frames from the captured throw (before discarding all the Buffers)
    for (int i = throw_bgn_idx; i < (throw_end_idx - 1); ++i) { // Don't save the last two captured frames
        // Transform Baumer BayerRG8 to BGR8 (Baumer BayerRG ≙ OpenCV BayerBG)
        cv::cvtColor(cv_buffer[i % buff_size], cv_transformed, cv::COLOR_BayerBG2BGR);
        cv::imwrite(output_path + std::to_string(i - throw_bgn_idx) + ".png", cv_transformed);
    }

    try {
        // Stop the DataStream acquisition
        pDataStream->StopAcquisition();
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
