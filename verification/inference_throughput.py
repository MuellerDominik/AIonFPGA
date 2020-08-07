#!/usr/bin/env python3

'''aionfpga ~ inference throughput
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import sys
import math
import base64
import ctypes

from threading import Thread
from datetime import datetime

import cv2
import numpy as np

from dnndk import n2cube
from pynq_dpu import DpuOverlay

import fhnwtoys.inference as fh

def sine_window(N, num_frames):
    window = np.zeros((fh.frames_to_consider,), dtype=np.float32)
    for n in range(num_frames):
        window[n] = math.sin((n + 1) / (N + 1) * math.pi)
    return window

def get_dict():
    return {'start': [], 'end': []}

def main():

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
    libcamera.set_frames_to_acquire.restype = None

    libcamera.initialize.restype = ctypes.c_int
    libcamera.start_acquisition.restype = ctypes.c_int
    libcamera.terminate.restype = ctypes.c_int

    # Set up of variables
    frames = np.empty((fh.frames_to_consider,) + fh.bgr_shape, dtype=np.uint8)

    # Initialize Camera
    initialize = libcamera.initialize()

    if initialize != fh.ReturnCodes.SUCCESS:
        try:
            return_code = fh.ReturnCodes(initialize).name
        except ValueError:
            return_code = initialize
        print(f'Initialization failed: {return_code}')
        sys.exit()
    else:
        print('================================= READY =================================')

    # Reset predictions
    predictions = np.zeros((fh.frames_to_consider, fh.num_objects), dtype=np.float32)

    # Start acquisition (Threaded)
    t = Thread(target=libcamera.start_acquisition)
    t.start()

    # Wait until the throw has ended
    while not libcamera.get_throw_end():
        pass

    stages = ['Get raw bayer', 'Transform color', 'Resize', 'Normalize', 'Run inference', 'Softmax', 'Weighting']
    meas_time = {s: get_dict() for s in stages}

    throw_bgn_idx = libcamera.get_throw_bgn_idx()
    throw_end_idx = libcamera.get_throw_end_idx()

    num_frames = throw_end_idx - throw_bgn_idx - 1 # Ignore the last two captured frames

    for idx, frame_id in enumerate(range(throw_bgn_idx, throw_end_idx - 1)):

        meas_time['Get raw bayer']['start'].append(datetime.now())
        frame_ptr = libcamera.get_frame_ptr(frame_id)
        raw_frame = np.ctypeslib.as_array(frame_ptr, shape=fh.raw_shape)
        meas_time['Get raw bayer']['end'].append(datetime.now())

        # Transform Baumer BayerRG8 to BGR8 (Baumer BayerRG ≙ OpenCV BayerBG)
        meas_time['Transform color']['start'].append(datetime.now())
        frames[idx] = cv2.cvtColor(raw_frame, cv2.COLOR_BayerBG2BGR)
        meas_time['Transform color']['end'].append(datetime.now())

        meas_time['Resize']['start'].append(datetime.now())
        frame_resized = cv2.resize(frames[idx], fh.inf_dsize, interpolation=fh.Interpolation.NEAREST)
        meas_time['Resize']['end'].append(datetime.now())

        meas_time['Normalize']['start'].append(datetime.now())
        frame_inference = frame_resized.astype(np.float32) / 255.0
        meas_time['Normalize']['end'].append(datetime.now())

        meas_time['Run inference']['start'].append(datetime.now())
        n2cube.dpuSetInputTensorInHWCFP32(task, kernel_conv_input, frame_inference, input_tensor_size)
        n2cube.dpuRunTask(task)
        meas_time['Run inference']['end'].append(datetime.now())

        # n2cube.dpuRunSoftmax(.) sometimes returns all zeros except one NaN
        # This section replaces the first occurrence of NaN in the prediction array with 1.0 and sets everything else to 0.0
        meas_time['Softmax']['start'].append(datetime.now())
        prediction = n2cube.dpuRunSoftmax(output_tensor_address, output_tensor_channel, output_tensor_size//output_tensor_channel, output_tensor_scale)
        nan = np.isnan(prediction)
        if nan.any():
            nan_idx = nan.argmax() # return the index of the first occurrence of NaN
            prediction = np.zeros((fh.num_objects,), dtype=np.float32)
            prediction[nan_idx] = 1.0
        predictions[idx] = prediction
        meas_time['Softmax']['end'].append(datetime.now())

        if idx == fh.frames_to_consider - 1:
            break

    meas_time['Weighting']['start'].append(datetime.now())
    num_frames_considered = min(fh.frames_to_consider, num_frames)
    window = sine_window(num_frames, num_frames_considered) # weighting
    weighted_prediction = np.matmul(window, predictions) / np.sum(window)
    meas_time['Weighting']['end'].append(datetime.now())

    for k in meas_time:
        meas_time[k] = [(e - s).total_seconds() * 1000 for s, e in zip(meas_time[k]['start'], meas_time[k]['end'])]
        meas_time[k] = sum(meas_time[k]) / len(meas_time[k])

    # create output file
    mmax = 0
    for s in stages:
        if len(s) > mmax:
            mmax = len(s)
    output = f'Number of captured frames: {num_frames_considered}\n\n'
    for idx, s in enumerate(stages):
        output += f'{s}:{" "*(mmax - len(stages[idx]))} {meas_time[s]:.3f} ms\n'

    output += f'\nSum:{" "*(mmax - len("Sum"))} {sum(meas_time.values()):.3f} ms\n'

    output += f'Frame rate:{" "*(mmax - len("Frame rate"))} {1000 / sum(meas_time.values()):.3f} fps\n'

    print(output)

    with open(fh.dir_verification / 'throughput.log', 'w') as f:
        f.write(output)

    # Wait until the camera thread (process due to ctypes) is terminated
    t.join()

    # Terminate Camera
    terminate = libcamera.terminate()

    # Clean up the DPU IP
    n2cube.dpuDestroyKernel(kernel)
    n2cube.dpuDestroyTask(task)

if __name__ == '__main__':
    main()
