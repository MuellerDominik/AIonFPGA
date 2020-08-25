#!/usr/bin/env python3

'''aionfpga ~ fhnwtoys.settings
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

from pathlib import Path

from .enums import *

# Database -------------------------------------------------------------------

# Connection
host = '<host>'
port = 3306
user = '<user>'
passwd = '<password>'
database = 'aionfpga' # defaults to this database

# Tables
tab_frames = 'frames'

# Objects --------------------------------------------------------------------

# special chars: only spaces and round brackets (i.e. `(` and `)`)
objects = [
    'Nerf Dart', 'American Football', 'Table Tennis Ball',
    'Shuttlecock', 'Sporf', 'Arrow', 'Hand Featherball', 'Floorball',
    'Spiky Ball', 'Tesafilm', 'Sponge', 'Lego Duplo Brick (Red)',
    'Lego Duplo Brick (Green)', 'Lego Duplo Figure', 'Foam Dice',
    'Infant Shoe', 'Stuffed Bunny', 'Goalkeeper Glove', 'Hemp Cord',
    'Paper Ball', 'Beer Cap', 'Water Bottle'
]

# list `objects_san` is dynamically created in `__init__.py`
# objects_san = [
#     'nerf-dart', 'american-football', 'table-tennis-ball',
#     'shuttlecock', 'sporf', 'arrow', 'hand-featherball', 'floorball',
#     'spiky-ball', 'tesafilm', 'sponge', 'lego-duplo-brick-red',
#     'lego-duplo-brick-green', 'lego-duplo-figure', 'foam-dice',
#     'infant-shoe', 'stuffed-bunny', 'goalkeeper-glove', 'hemp-cord',
#     'paper-ball', 'beer-cap', 'water-bottle'
# ]

objects_ui = [
    'Nerf Dart', 'American Football', 'Table Tennis Ball',
    'Shuttlecock', 'Sporf', 'Arrow', 'Hand Featherball', 'Floorball',
    'Spiky Ball', 'Tesafilm', 'Sponge', 'Red Duplo Brick',
    'Green Duplo Brick', 'Duplo Figure', 'Foam Die', # formerly 'Foam Dice'
    'Infant Shoe', 'Stuffed Bunny', 'Goalkeeper Glove', 'Hemp Cord',
    'Paper Ball', 'Beer Cap', 'Water Bottle'
]

num_objects = len(objects)

# Directories ----------------------------------------------------------------

# Inference
dir_repo = Path('/home/xilinx/AIonFPGA') # location of the cloned repository

dir_sw = dir_repo / 'sw'

dir_app = dir_sw / 'inference' / 'aionfpga'
dir_graphics = dir_app / 'graphics' # for the UI

dir_dpu = dir_app / 'build'

dir_cam = dir_sw / 'inference' / 'camera' / 'build'

# Training
dir_training = dir_sw / 'training'
dir_training_build = dir_training / 'build'

# - Dataset
dir_dataset = dir_training_build / 'dataset'

dir_frames = dir_dataset / 'frames'
dir_frames_augmented = dir_dataset / 'frames_augmented'

dir_training_dataset = dir_dataset / 'training'
dir_validation_dataset = dir_dataset / 'validation'
dir_test_dataset = dir_dataset / 'test'
dir_calibration_dataset = dir_dataset / 'calibration'

# - CNN
dir_cnn = dir_training_build / 'cnn'

dir_model = dir_cnn / 'model'
dir_frozen_model = dir_cnn / 'frozen_model'

dir_checkpoint = dir_cnn / 'checkpoint'
dir_model_without_opt = dir_cnn / 'model_without_opt'
dir_hdf5 = dir_cnn / 'hdf5'
dir_weights = dir_cnn / 'weights'

# Verification
dir_verification = dir_sw / 'verification'

# Camera ---------------------------------------------------------------------

camera_name = 'camera'

libcamera_file = f'lib{camera_name}.so'

# Original (Baumer BayerRG8)
raw_frmt = {'width': 1280, 'height': 1024, 'num_channels': 1} # RAW format
ar = raw_frmt['width'] / raw_frmt['height'] # 5:4 aspect ratio
# RAW shape tuple: (height, width, num_channels)
raw_shape = (raw_frmt['height'], raw_frmt['width'], raw_frmt['num_channels'])

# Original (BGR)
bgr_frmt = {'width': 1280, 'height': 1024, 'num_channels': 3} # BGR format
# BGR shape tuple: (height, width, num_channels)
bgr_shape = (bgr_frmt['height'], bgr_frmt['width'], bgr_frmt['num_channels'])

# Inference
inf_width = 320 # px
inf_height = int(inf_width / ar)
inf_frmt = {'width': inf_width, 'height': inf_height, 'num_channels': 3}
# Inference shape tuple: (height, width, num_channels)
inf_shape = (inf_frmt['height'], inf_frmt['width'], inf_frmt['num_channels'])
inf_dsize = (inf_frmt['width'], inf_frmt['height'])

# UI
ui_width = 1024 # px
ui_height = int(ui_width / ar)
ui_frmt = {'width': ui_width, 'height': ui_height, 'num_channels': 3}
# UI shape tuple: (height, width, num_channels)
ui_shape = (ui_frmt['height'], ui_frmt['width'], ui_frmt['num_channels'])
ui_dsize = (ui_frmt['width'], ui_frmt['height'])

# Camera settings
frame_rate = 200.0 # fps
buff_size = 200 # 200 ≙ 1 s @ 200 fps
exposure_time = 250.0 # us
camera_gain = 4.0

avg_diffs = 8 # 8 diffs ≙ 40 ms @ 200 fps
threshold_mult = 1.1

# Max. amount of frames to take into consideration
frames_to_consider = 22

# Max. amount of frames to acquire
frames_to_acquire = 2 * frames_to_consider

# Inference ------------------------------------------------------------------

dpu_name = 'dpu'

dpu_bit_file = f'{dpu_name}.bit'
dpu_hwh_file = f'{dpu_name}.hwh'
dpu_xclbin_file = f'{dpu_name}.xclbin'

# 0 has to be there (Xilinx will remove any trailing s'es)
kernel_name = 'fhnw_toys_0' # model name / net name

kernel_conv_input = 'sequential_conv2d_Conv2D'
kernel_fc_output = 'sequential_dense_1_MatMul'

dpu_assembly_file = f'dpu_{kernel_name}.elf'

# Dataset / Verification -----------------------------------------------------

dataset_config = DatasetConfig.ALL # Include all frames
verification = Verification.TRAINING # Verify the training

seed = 0x41496F6E46504741 # AIonFPGA

batch_size = 32
batch_size_calibration = 22

training_frames_name = 'fhnw_toys_training_frames'
training_labels_name = 'fhnw_toys_training_labels'

validation_frames_name = 'fhnw_toys_validation_frames'
validation_labels_name = 'fhnw_toys_validation_labels'

test_frames_name = 'fhnw_toys_test_frames'
test_labels_name = 'fhnw_toys_test_labels'

calibration_frames_name = 'fhnw_toys_calibration_frames'
calibration_labels_name = 'fhnw_toys_calibration_labels'

training_predictions_name = 'fhnw_toys_training_predictions'
# fully visible only (fvo) predictions
training_fvo_predictions_name = 'fhnw_toys_training_fvo_predictions'

inference_predictions_name = 'fhnw_toys_inference_predictions'
# fully visible only (fvo) predictions
inference_fvo_predictions_name = 'fhnw_toys_inference_fvo_predictions'
