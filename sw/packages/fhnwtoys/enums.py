#!/usr/bin/env python3

'''aionfpga ~ fhnwtoys.enums
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import cv2

from enum import IntEnum

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

class DatasetConfig(IntEnum):
    ALL = 0
    PARTIALLY_VISIBLE_ONLY = 1 # do not use
    FULLY_VISIBLE_ONLY = 2

class Verification(IntEnum):
    TRAINING = 0
    INFERENCE = 1

class NeuralNetworkArchitectures(IntEnum):
    pass
