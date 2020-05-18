#!/bin/bash

BUILD_DIR=mpsoc/comp_model/build
HWH_FILE=mpsoc/os/build/Vitis-AI/DPU-TRD-ULTRA96V2/prj/Vitis/binary_container_1/sd_card/ULTRA96V2.hwh
DC_FILE=mpsoc/comp_model/build//ULTRA96V2.dcf
ARCH_CONF=mpsoc/comp_model/scripts/conf/arch.json

QUANT_MODEL=mpsoc/quant_model/build/deploy_model.pb
MODEL_NAME=model

source /opt/vitis_ai/conda/etc/profile.d/conda.sh
conda activate vitis-ai-tensorflow

# Create DPU Configuration File
dlet -f $HWH_FILE
mv dpu*.dcf $DC_FILE

# Compile Model with DNNDK-Tool 
vai_c_tensorflow \
--arch $ARCH_CONF \
--frozen_pb $QUANT_MODEL \
--output_dir $BUILD_DIR \
--net_name $MODEL_NAME \
--options "{'mode': 'normal'}"

# Change owner permission from root to User
sudo chown $USER $BUILD_DIR/*
