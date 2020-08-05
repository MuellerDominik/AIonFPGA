#!/usr/bin/env python3

'''aionfpga ~ dump input function (for the calibration)
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

from pathlib import Path

import numpy as np

path = Path('../../sw/training/build/dataset/calibration')

calib_batch_size = 22
calib_batches = 1000 // calib_batch_size

def calib_input(iter):
    images = np.load(path / f'fhnw_toys_calibration_frames_batch_{iter}_of_{calib_batches}.npy')
    images = images[np.newaxis, 0]

    return {'x': images.astype(np.float32) / 255.0}
