#!/bin/bash

# source and start conda environment
. /opt/vitis_ai/conda/etc/profile.d/conda.sh
conda activate vitis-ai-tensorflow

# change to directory, where the input function is located
cd mpsoc/cnn-model

vai_q_tensorflow quantize \
    --input_frozen_graph ${FROZEN_GRAPH} \
    --input_nodes ${INPUT_NODE} \
    --input_shapes ${INPUT_SHAPE} \
    --output_nodes ${OUTPUT_NODE} \
    --input_fn $INPUT_FUNCTION \
    --calib_iter $N_CALIB_ITER_COMP \
    --output_dir $BUILD_DIR \
    --method $QUANT_METHOD
