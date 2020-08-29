#!/usr/bin/env python3

'''aionfpga ~ aionfpga
Copyright (C) 2020 Dominik Mueller and Nico Canzani
'''

import math
import ctypes

from threading import Thread

import cv2
import numpy as np

from ui import UI
import fhnwtoys.inference as fh

# returns the rectangular window function
def rect_window():
  window = np.ones((fh.frames_to_consider,), dtype=np.float32)
  return window

# integer num_frames and num_frames_considered
# returns the stretched and phase-shifted sine window function
def sine_window(num_frames, num_frames_considered):
  window = np.zeros((fh.frames_to_consider,), dtype=np.float32)
  for n in range(num_frames_considered):
    window[n] = math.sin((n + 1) / (num_frames + 1) * math.pi)
  return window

# integer num_frames and num_frames_considered
# returns the stretched and phase-shifted sine-squared window function
def sine_squared_window(num_frames, num_frames_considered):(*\label{lst:ln:sine_squared_window}*)
  window = np.zeros((fh.frames_to_consider,), dtype=np.float32)
  for n in range(num_frames_considered):
    window[n] = math.sin((n + 1) / (num_frames + 1) * math.pi)**2
  return window

# numpy array series (dtype=np.float32)
# returns a list of the to one decimal place rounded percentages using the largest remainder method (lrm)
def lrm_round(series):(*\label{lst:ln:lrm_round}*)
  floored_series = np.floor(series * 10.0)
  decimal_series = series * 10.0 - floored_series
  decimal_series_argsorted = np.argsort(decimal_series)[::-1]
  difference = 1000 - np.sum(floored_series, dtype=np.uint16)
  for idx in decimal_series_argsorted[0:difference]:
    floored_series[idx] += 1
  return_series = floored_series.astype(np.float64) / 10.0
  return return_series.tolist()

def main():

  # UI: DPU
  ui = UI()
  ui.update_boot_window('Initializing DPU...')

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

  # UI: Camera
  ui.update_boot_window('Initializing Camera...')

  # libcamera
  libcamera = ctypes.CDLL(fh.dir_cam / fh.libcamera_file)

  # Getter
  libcamera.get_frame_ptr.restype = ctypes.POINTER(ctypes.c_ubyte)
  libcamera.get_frame_ptr.argtypes = [ctypes.c_uint]
  libcamera.get_throw_bgn_idx.restype = ctypes.c_uint
  libcamera.get_throw_bgn_idx.argtypes = None
  libcamera.get_throw_end_idx.restype = ctypes.c_uint
  libcamera.get_throw_end_idx.argtypes = None
  libcamera.get_throw_bgn.restype = ctypes.c_bool
  libcamera.get_throw_bgn.argtypes = None
  libcamera.get_throw_end.restype = ctypes.c_bool
  libcamera.get_throw_end.argtypes = None

  # Setter
  libcamera.set_frame_rate.restype = None
  libcamera.set_frame_rate.argtypes = [ctypes.c_double]
  libcamera.set_buff_size.restype = None
  libcamera.set_buff_size.argtypes = [ctypes.c_uint]
  libcamera.set_exposure_time.restype = None
  libcamera.set_exposure_time.argtypes = [ctypes.c_double]
  libcamera.set_camera_gain.restype = None
  libcamera.set_camera_gain.argtypes = [ctypes.c_double]
  libcamera.set_avg_diffs.restype = None
  libcamera.set_avg_diffs.argtypes = [ctypes.c_uint]
  libcamera.set_threshold_mult.restype = None
  libcamera.set_threshold_mult.argtypes = [ctypes.c_double]
  libcamera.set_frames_to_acquire.restype = None
  libcamera.set_frames_to_acquire.argtypes = [ctypes.c_uint]

  # Camera
  libcamera.initialize.restype = ctypes.c_int
  libcamera.initialize.argtypes = None
  libcamera.reset_global_variables.restype = None
  libcamera.reset_global_variables.argtypes = None
  libcamera.start_acquisition.restype = ctypes.c_int
  libcamera.start_acquisition.argtypes = None
  libcamera.terminate.restype = ctypes.c_int
  libcamera.terminate.argtypes = None

  # Set the global variables according to the module `fhnwtoys.settings`
  libcamera.set_frame_rate(fh.frame_rate)
  libcamera.set_buff_size(fh.buff_size)
  libcamera.set_exposure_time(fh.exposure_time)
  libcamera.set_camera_gain(fh.camera_gain)
  libcamera.set_avg_diffs(fh.avg_diffs)
  libcamera.set_threshold_mult(fh.threshold_mult)
  libcamera.set_frames_to_acquire(fh.frames_to_acquire)

  # Initialize Camera
  initialize = fh.ReturnCodes.NOT_INITIALIZED
  initialization_tries = 0

  while initialize != fh.ReturnCodes.SUCCESS:
    if initialization_tries > 0:
      try:
        return_code = fh.ReturnCodes(initialize).name
      except ValueError:
        return_code = initialize
      ui.update_boot_window(f'Camera Error ({return_code}), try to replug the camera.')
    initialize = libcamera.initialize()
    initialization_tries += 1

  # UI: Ready
  ui.update_boot_window('READY')

  # Set up the `frames` array
  frames = np.empty((fh.frames_to_consider,) + fh.bgr_shape, dtype=np.uint8)

  while True:
    # Reset the predictions
    predictions = np.zeros((fh.frames_to_consider, fh.num_objects), dtype=np.float32)

    # Start acquisition (threaded)
    # todo: error handling ('Unexpected Error, system reboot required.')
    # start_acquisition = libcamera.start_acquisition() # non threaded approach
    t = Thread(target=libcamera.start_acquisition) # threaded approach (process due to ctypes)
    t.start()

    # Wait until the throw has ended (the Ultra96-V2 is not powerful enough to process the data during the acquisition)
    while not libcamera.get_throw_end():
      pass

    throw_bgn_idx = libcamera.get_throw_bgn_idx()
    throw_end_idx = libcamera.get_throw_end_idx()

    num_frames = throw_end_idx - throw_bgn_idx - 1 # Ignore the last two captured frames

    # Image processing (including inference)
    for idx, frame_id in enumerate(range(throw_bgn_idx, throw_end_idx - 1)):
      frame_ptr = libcamera.get_frame_ptr(frame_id)
      raw_frame = np.ctypeslib.as_array(frame_ptr, shape=fh.raw_shape) # Raw Baumer BayerRG8 frame
      # Transform Baumer BayerRG8 to BGR8 (Baumer BayerRG = OpenCV BayerBG)
      frames[idx] = cv2.cvtColor(raw_frame, cv2.COLOR_BayerBG2BGR) # Color space conversion
      # Image scaling using nearest-neighbor interpolation
      frame_resized = cv2.resize(frames[idx], fh.inf_dsize, interpolation=fh.Interpolation.NEAREST)
      frame_inference = frame_resized.astype(np.float32) / 255.0 # Normalization (float32 precision)

      # Inference
      n2cube.dpuSetInputTensorInHWCFP32(task, kernel_conv_input, frame_inference, input_tensor_size)
      n2cube.dpuRunTask(task)

      # Softmax function (normalized exponential function)
      # Confident predictions lead to all zeros and a NaN, when run through `n2cube.dpuRunSoftmax(.)`
      # This section replaces the first occurrence of NaN in the `prediction` array with 1.0 and sets everything else to 0.0
      prediction = n2cube.dpuRunSoftmax(output_tensor_address, output_tensor_channel, output_tensor_size//output_tensor_channel, output_tensor_scale)
      nan = np.isnan(prediction)
      if nan.any():
        nan_idx = nan.argmax() # returns the index of the first occurrence of NaN
        prediction = np.zeros((fh.num_objects,), dtype=np.float32)
        prediction[nan_idx] = 1.0
      predictions[idx] = prediction

      # Only consider `fh.frames_to_consider` frames
      if idx == fh.frames_to_consider - 1: # (-1: idx starts with 0)
        break

    num_frames_considered = min(fh.frames_to_consider, num_frames)

    window = sine_squared_window(num_frames, num_frames_considered) # weighting function
    weighted_prediction = np.matmul(window, predictions) / np.sum(window)(*\label{lst:ln:matrix_multiplication}*) # computation of the weighted prediction

    # UI: Prepare data for the UI
    weighted_prediction_percent = weighted_prediction * 100
    weighted_prediction_sorted = np.sort(weighted_prediction_percent)[::-1]
    weighted_prediction_argsorted = np.argsort(weighted_prediction_percent)[::-1]

    # this is the index of the best guess (computed by weighting the `fh.frames_to_consider` frames)
    guess_idx = weighted_prediction_argsorted[0]

    relevant_pct_ui = np.asarray(weighted_prediction_percent >= 1.0).nonzero()[0] # value of prediction must be at least 1.0%
    relevant_pct_ui_len = len(relevant_pct_ui)
    predictions_ui_len = min(4, relevant_pct_ui_len) # show at most Top 4

    predictions_ui = [] # the object names
    percentages_ui = np.empty((predictions_ui_len + 1,), dtype=np.float32) # the percentages (+1: 'Others')
    for i, w in enumerate(weighted_prediction_argsorted[0:predictions_ui_len]):
      predictions_ui.append(fh.objects_ui[w])
      percentages_ui[i] = weighted_prediction_percent[w]

    # the object names
    predictions_ui.append('Others')

    # the percentages
    percentages_ui[-1] = np.sum(weighted_prediction_sorted[predictions_ui_len:])
    percentages_ui = lrm_round(percentages_ui)

    # the frame
    wighted_guesses = np.multiply(window, predictions[:, guess_idx])(*\label{lst:ln:frame_selection1}*)
    frame_ui_idx = wighted_guesses.argmax()

    frame_ui_resized = cv2.resize(frames[frame_ui_idx], fh.ui_dsize, interpolation=fh.Interpolation.NEAREST)
    _, frame_ui_png = cv2.imencode('.png', frame_ui_resized)
    frame_ui = frame_ui_png.tobytes()(*\label{lst:ln:frame_selection2}*) # the frame

    # UI: Show results
    if percentages_ui[-1] == 0.0:
      predictions_ui = predictions_ui[:-1]
      percentages_ui = percentages_ui[:-1]

    # UI: Inference
    ui.update_inference_window(predictions_ui, percentages_ui, frame_ui)

    # Wait until the camera thread (process due to ctypes) is terminated
    t.join()

    # Reset the global variables (has to be done manually to avoid race conditions)
    libcamera.reset_global_variables()

  # Under regular circumstances, this section should never be reached

  # Terminate Camera
  terminate = libcamera.terminate()

  # Clean up the DPU IP
  n2cube.dpuDestroyKernel(kernel)
  n2cube.dpuDestroyTask(task)

if __name__ == '__main__':
  main()
