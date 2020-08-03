#!/usr/bin/env python3

'''aionfpga ~ dump input function (for the calibration)
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import numpy as np

from pathlib import Path

path = Path('../../sw/training/build')

calib_images_path = path / 'fhnw_toys_calibration_images.npy'
calib_batch_size = 1

calib_images = np.load(calib_images_path)

def calib_input(iter):
    start = iter * calib_batch_size
    end = start + calib_batch_size
    images = np.asarray(calib_images[start:end], dtype=np.float32) / 255.0

    return {'x': images}
