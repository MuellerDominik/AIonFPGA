#!/bin/bash

cd mpsoc/cnn-model

# Build the Arch-Config file
echo '{"target": "dpuv2", "dcf": "'$DCF_FILE'", "cpu_arch": "arm64"}' > $ARCH_CONF

source /opt/vitis_ai/conda/etc/profile.d/conda.sh
conda activate vitis-ai-tensorflow

# Create DPU Configuration File
dlet -f $HWH_FILE
mv dpu*.dcf $DCF_FILE

# Compile Model with DNNDK-Tool 
vai_c_tensorflow \
--arch $ARCH_CONF \
--frozen_pb $QUANT_MODEL \
--output_dir $BUILD_DIR \
--net_name $MODEL_NAME \
--options "{'mode': 'normal'}"

# Change owner permission from root to User for build and pycache folders
sudo chown $USER $BUILD_DIR/*
sudo chgrp $GID $BUILD_DIR/*
sudo chown $USER $BUILD_DIR
sudo chgrp $GID $BUILD_DIR

sudo chown $USER $PYCACHE/*
sudo chgrp $GID $PYCACHE/*
sudo chown $USER $PYCACHE
sudo chgrp $GID $PYCACHE