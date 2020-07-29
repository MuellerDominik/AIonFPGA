#!/usr/bin/env python3

'''aionfpga ~ aionfpga
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import sys
import math
import ctypes

from datetime import datetime

import cv2
import numpy as np

import fhnwtoys.inference as fh

def rect_window(N):
    window = np.ones((fh.max_num_frames,), dtype=np.float32)
    return window

def sine_window(N):
    window = np.zeros((fh.max_num_frames,), dtype=np.float32)
    for n in range(N):
        window[n] = math.sin((n + 1) / (N + 1) * math.pi)
    return window

def sine_squared_window(N):
    window = np.zeros((fh.max_num_frames,), dtype=np.float32)
    for n in range(N):
        window[n] = math.sin((n + 1) / (N + 1) * math.pi)**2
    return window

def main():

    # Bootscreen (Initialize DPU)

    from dnndk import n2cube
    from pynq_dpu import DpuOverlay

    # Set up the DPU IP
    overlay = DpuOverlay(str(fh.dir_dpu / fh.dpu_bit_file))
    overlay.load_model(str(fh.dir_dpu / fh.dpu_assembly_file))

    # Set up the Neural Network Runtime (N2Cube)
    kernel_name = fh.kernel_name

    kernel_conv_input = fh.kernel_conv_input
    kernel_fc_output = fh.kernel_fc_output

    n2cube.dpuOpen()
    kernel = n2cube.dpuLoadKernel(kernel_name)
    task = n2cube.dpuCreateTask(kernel, 0)

    input_tensor_size = n2cube.dpuGetInputTensorSize(task, kernel_conv_input)

    output_tensor_size = n2cube.dpuGetOutputTensorSize(task, kernel_fc_output)
    output_tensor_channel = n2cube.dpuGetOutputTensorChannel(task, kernel_fc_output)
    output_tensor_address = n2cube.dpuGetOutputTensorAddress(task, kernel_fc_output)
    output_tensor_scale = n2cube.dpuGetOutputTensorScale(task, kernel_fc_output)


    # Bootscreen (Initialize Camera)

    # libcamera
    libcamera = ctypes.CDLL(fh.dir_cam / fh.libcamera_file)

    libcamera.get_frame_ptr.restype = ctypes.POINTER(ctypes.c_ubyte)
    libcamera.get_throw_bgn_idx.restype = ctypes.c_uint
    libcamera.get_throw_end_idx.restype = ctypes.c_uint
    libcamera.get_throw_bgn.restype = ctypes.c_bool
    libcamera.get_throw_end.restype = ctypes.c_bool

    libcamera.set_frame_rate.restype = None
    libcamera.set_buff_size.restype = None
    libcamera.set_exposure_time.restype = None
    libcamera.set_camera_gain.restype = None
    libcamera.set_avg_diffs.restype = None
    libcamera.set_threshold_mult.restype = None

    libcamera.initialize.restype = ctypes.c_int
    libcamera.start_acquisition.restype = ctypes.c_int
    libcamera.terminate.restype = ctypes.c_int

    # todo: set global variables according to fhnwtoys.settings

    # Set up of variables
    frames = np.empty((fh.max_num_frames,) + fh.bgr_shape, dtype=np.uint8)


    # Initialize Camera
    initialize = libcamera.initialize()

    # todo: try until successful ('Camera Error, try to replug the camera.')
    # maybe call terminate() after
    if initialize != fh.ReturnCodes.SUCCESS:
        try:
            return_code = fh.ReturnCodes(initialize).name
        except ValueError:
            return_code = initialize
        print(f'Initialization failed: {return_code}')
        sys.exit()
    else:
        print('================================= READY =================================')

    # while True:
    for i in range(5):
        # Reset predictions
        predictions = np.zeros((fh.max_num_frames, fh.num_objects), dtype=np.float32)

        # Start acquisition
        # todo: error handling ('Unexpected Error, system reboot required.')
        start_acquisition = libcamera.start_acquisition()

        start = [] # debug
        end = [] # debug
        start.append(datetime.now()) # debug

        throw_bgn_idx = libcamera.get_throw_bgn_idx()
        throw_end_idx = libcamera.get_throw_end_idx()

        num_frames = throw_end_idx - throw_bgn_idx - 1 # Ignore the last two captured frames

        for idx, frame_id in enumerate(range(throw_bgn_idx, throw_end_idx - 1)):
            frame_ptr = libcamera.get_frame_ptr(frame_id)
            raw_frame = np.ctypeslib.as_array(frame_ptr, shape=fh.raw_shape)
            # Transform Baumer BayerRG8 to BGR8 (Baumer BayerRG ≙ OpenCV BayerBG)
            frames[idx] = cv2.cvtColor(raw_frame, cv2.COLOR_BayerBG2BGR)
            frame_resized = cv2.resize(frames[idx], fh.inf_dsize, interpolation=fh.Interpolation.NEAREST)
            frame_inference = np.asarray(frame_resized / 255.0, dtype=np.float32)

            # start.append(datetime.now()) # debug
            n2cube.dpuSetInputTensorInHWCFP32(task, kernel_conv_input, frame_inference, input_tensor_size)
            n2cube.dpuRunTask(task)

            # Either n2cube.dpuRunTask(.) or n2cube.dpuRunSoftmax(.) sometimes returns all zeros except one NaN
            # This section replaces the first occurrence of NaN in the prediction array with 1.0 and sets everything else to 0.0
            prediction = n2cube.dpuRunSoftmax(output_tensor_address, output_tensor_channel, output_tensor_size//output_tensor_channel, output_tensor_scale)
            nan = np.isnan(prediction)
            if nan.any():
                nan_idx = nan.argmax() # return the index of the first occurrence of NaN
                prediction = np.zeros((fh.num_objects,), dtype=np.float32)
                prediction[nan_idx] = 1.0
            predictions[idx] = prediction
            # end.append(datetime.now()) # debug

        # start.append(datetime.now()) # debug

        window = sine_window(num_frames)
        weighted_predictions = np.matmul(window, predictions) / np.sum(window)

        prediction_idx = weighted_predictions.argmax()

        end.append(datetime.now()) # debug

        durations = [(e - s).total_seconds() for s, e in zip(start, end)] # debug
        duration = sum(durations)/len(durations) # debug

        print(f'-' * 73) # debug
        print(f'{num_frames} images processed in {duration} => Throughput = {num_frames / duration} fps') # debug
        print(f'Prediction = {fh.objects[prediction_idx]} (Confidence = {weighted_predictions[prediction_idx] * 100:.4f}%)') # debug
        # print(f'weighted_predictions = {weighted_predictions}') # debug

        # debug: show images
        # for i in range(num_frames):
        #     cv2.imshow('debug', frames[i])
        #     cv2.waitKey(0)
        # cv2.destroyAllWindows()

    # Terminate Camera
    # todo: error handling (not really required, will never be reached)
    terminate = libcamera.terminate()

if __name__ == '__main__':
    main()
