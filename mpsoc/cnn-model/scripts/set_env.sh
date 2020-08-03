#!/bin/bash

# All paths relative to workspace of docker session (correspondents to repo main folder)

HERE=$(pwd)

export MODEL_NAME=fhnw_toys_0

export BUILD_DIR=$HERE/mpsoc/cnn-model/build
export PYCACHE=$HERE/mpsoc/cnn-model/__pycache__

export FROZEN_GRAPH=$HERE/sw/training/build/frozen_graph.pb
export FROZEN_GRAPH_DUMP=$BUILD_DIR/quantize_eval_model.pb
export QUANT_MODEL=$BUILD_DIR/deploy_model.pb

export DPU_FILES=$HERE/mpsoc/dpu/build/DPU-PYNQ/boards/Ultra96
export HWH_FILE=$DPU_FILES/dpu.hwh
export DCF_FILE=$BUILD_DIR/ULTRA96V2.dcf
export ARCH_CONF=$BUILD_DIR/arch.json

export INPUT_NODE=x
export OUTPUT_NODE=Identity

export INPUT_HEIGHT=256
export INPUT_WIDTH=320
export INPUT_CHAN=3
export INPUT_SHAPE=?,${INPUT_HEIGHT},${INPUT_WIDTH},${INPUT_CHAN}

export N_CALIB_ITER_COMP=45
export INPUT_FUNCTION=input_fn.calib_input
export QUANT_METHOD=0
export QUANT_METHOD=1

export DUMP_INPUT_FUNCTION=dump_input_fn.calib_input
export N_DUMP_BATCHES=1
export DUMP_FLOAT=0
export DUMP_METHOD=1

# METHOD
# The method for quantization.
# 0: Non-overflow method. Makes sure that no values are saturated during quantization. Sensitive to outliers.
# 1: Min-diffs method. Allows saturation for quantization to get a lower quantization difference. Higher tolerance to outliers. Usually ends with narrower ranges than the non-overflow method.
# Choices: [0, 1]
# Default: 1
