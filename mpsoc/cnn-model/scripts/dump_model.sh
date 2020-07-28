#!/bin/bash

# source and start conda environment
source /opt/vitis_ai/conda/etc/profile.d/conda.sh
conda activate vitis-ai-tensorflow

# change to directory to where the input function is located
cd mpsoc/cnn-model

vai_q_tensorflow dump \
    --input_frozen_graph ${FROZEN_GRAPH_DUMP} \
    --input_fn $DUMP_INPUT_FUNCTION \
    --max_dump_batches $N_DUMP_BATCHES \
    --dump_float $DUMP_FLOAT \
    --output_dir $BUILD_DIR \
    --method $DUMP_METHOD
