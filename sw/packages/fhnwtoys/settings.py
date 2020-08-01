#!/usr/bin/env python3

'''aionfpga ~ fhnwtoys.settings
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import cv2

from enum import IntEnum
from pathlib import Path

# Database -------------------------------------------------------------------

# Connection
host = '<host>'
port = 3306
user = '<user>'
passwd = '<password>'
database = 'aionfpga' # default to this database

# Tables
tab_frames = 'frames'
tab_settings = 'settings'

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
# objects_san = ['nerf-dart', 'american-football', 'table-tennis-ball',
#     'shuttlecock', 'sporf', 'arrow', 'hand-featherball', 'floorball',
#     'spiky-ball', 'tesafilm', 'sponge', 'lego-duplo-brick-red',
#     'lego-duplo-brick-green', 'lego-duplo-figure', 'foam-dice',
#     'infant-shoe', 'stuffed-bunny', 'goalkeeper-glove', 'hemp-cord',
#     'paper-ball', 'beer-cap', 'water-bottle'
# ]

num_objects = len(objects)

# Directories ----------------------------------------------------------------

dir_sw = Path('/home/xilinx/AIonFPGA/sw')

dir_app = dir_sw / 'inference' / 'aionfpga'
dir_dpu = dir_app / 'build'

dir_cam = dir_sw / 'inference' / 'camera' / 'build'

# todo: legacy, remove
# dir_frames = Path(r'B:\aionfpga\frames')
# dir_temp = Path(r'B:\aionfpga\temporary')

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
inf_height = int(inf_width // ar)
inf_frmt = {'width': inf_width, 'height': inf_height, 'num_channels': 3}
# Inference shape tuple: (height, width, num_channels)
inf_shape = (inf_frmt['height'], inf_frmt['width'], inf_frmt['num_channels'])
inf_dsize = (inf_frmt['width'], inf_frmt['height'])

# Camera settings
frame_rate = 200.0 # fps
buff_size = 200 # 200 ≙ 1 s @ 200 fps
exposure_time = 250 # us
camera_gain = 4

avg_diffs = 8 # 8 diffs ≙ 40 ms @ 200 fps
threshold_mult = 1.1

# Max. amount of frames to take into consideration
frames_to_consider = 22

# Max. amount of frames to acquire
frames_to_acquire = 2 * frames_to_consider

# DPU ------------------------------------------------------------------------
dpu_name = 'dpu'

dpu_bit_file = f'{dpu_name}.bit'
dpu_hwh_file = f'{dpu_name}.hwh'
dpu_xclbin_file = f'{dpu_name}.xclbin'

kernel_name = 'fhnw_toys_0' # model name / net name

kernel_conv_input = 'sequential_conv2d_Conv2D'
kernel_fc_output = 'sequential_dense_1_MatMul'

dpu_assembly_file = f'dpu_{kernel_name}.elf'

# Enums ----------------------------------------------------------------------

class Interpolation(IntEnum):
    NEAREST = cv2.INTER_NEAREST
    LINEAR = cv2.INTER_LINEAR
    CUBIC = cv2.INTER_CUBIC
    AREA = cv2.INTER_AREA
    LANCZOS4 = cv2.INTER_LANCZOS4
    LINEAR_EXACT = cv2.INTER_LINEAR_EXACT
    # MAX = cv2.INTER_MAX # interpolation not working
    # FILL_OUTLIERS = cv2.WARP_FILL_OUTLIERS # interpolation not working
    # INVERSE_MAP = cv2.WARP_INVERSE_MAP # interpolation not working

class ReturnCodes(IntEnum):
    SUCCESS = 0

    ERROR = 1 # Generic error

    NO_SYSTEMS = 2 # Producers
    NO_INTERFACES = 3
    NO_DEVICES = 4
    NO_DATASTREAMS = 5

    NOT_INITIALIZED = 6
    NOT_IMPLEMENTED = 7
    RESOURCE_IN_USE = 8
    ACCESS_DENIED = 9
    INVALID_HANDLE = 10
    OBJECT_INVALIDID = 11
    NO_DATA = 12
    INVALID_PARAMETER = 13
    LOW_LEVEL = 14
    ABORT = 15
    INVALID_BUFFER = 16
    NOT_AVAILABLE = 17

# todo: maybe rename to NeuralNetworkArchitectures
class NeuralNetworks(IntEnum):
    pass
