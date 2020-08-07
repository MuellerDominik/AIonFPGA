#!/usr/bin/env python3

'''aionfpga ~ inference predictions
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import numpy as np
import math
import os

from datetime import datetime

from pathlib import Path

from pynq_dpu import DpuOverlay
from dnndk import n2cube

import fhnwtoys.inference as fh

batch_size = fh.batch_size
num_objects = fh.num_objects

# batch start is included, E.g.: you have batch_3...50 -> batch_start = 3
batch_start = 0
# batch end is not included, E.g.: you have batch_3...50 -> batch_end = 51
batch_end = 525

def main(config=fh.DatasetConfig.ALL):

    if config == fh.DatasetConfig.ALL:
        out_file_name = f'{fh.inference_predictions_name}.npy'
    elif config == fh.DatasetConfig.FULLY_VISIBLE_ONLY:
        out_file_name = f'{fh.inference_fvo_predictions_name}.npy'
    else: # fh.DatasetConfig.PARTIALLY_VISIBLE_ONLY
        raise ValueError('This configuration has no use case!')

    build_dir = fh.dir_verification

    num_labels = len(np.load(fh.dir_test_dataset / f'{fh.test_labels_name}.npy'))
    num_batches = math.ceil(num_labels / batch_size)

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

    #######################################################
    # Initialize Array (depends on starting at first batch or somewhere in between)
    if batch_start == 0:
        prediction_array = np.empty((num_labels, num_objects), dtype=np.float32)
    else:
        if os.path.isfile(build_dir / out_file_name):
            prediction_array = np.load(build_dir / out_file_name)
        else:
            raise FileNotFoundError(f"File {out_file_name} does not exist, start first with batch 0")

    #######################################################
    # Iterate over defined batches
    start = datetime.now()
    for i in range(batch_start, batch_end):
        print(f'starting with batch {i}')
        batch = np.load(fh.dir_test_dataset / f'{fh.test_frames_name}_batch_{i}_of_{num_batches}.npy')
        batch = batch.astype(dtype=np.float32) / 255.0

        for j, _ in enumerate(batch):
            n2cube.dpuSetInputTensorInHWCFP32(task, kernel_conv_input, batch[j], input_tensor_size)
            n2cube.dpuRunTask(task)

            prediction = n2cube.dpuRunSoftmax(output_tensor_address, output_tensor_channel, output_tensor_size//output_tensor_channel, output_tensor_scale)

            # Catch nan from softmax (occurs when one prediction is very high)
            nan = np.isnan(prediction)
            if nan.any():
                nan_idx = nan.argmax()
                prediction = np.zeros((fh.num_objects,), dtype=np.float32)
                prediction[nan_idx] = 1.0

            prediction_array[i * batch_size + j] = prediction

    end = datetime.now()
    print(f'Total time for all batches needed: {end - start}')

    np.save(build_dir / out_file_name, prediction_array)

if __name__ == '__main__':
    config = fh.config
    main(config)
