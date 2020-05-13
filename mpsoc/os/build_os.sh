#!/bin/bash

CWD=$(pwd)
DPU_CONF_FILE=config/dpu_conf.vh
DPU_CONNECTION_FILE=config/prj_config

# Absolute paths needed
export VITIS_AI_HOME=$CWD/build/Vitis-AI
export TRD_HOME=$VITIS_AI_HOME/DPU-TRD-ULTRA96V2
export SDX_PLATFORM=$CWD/build/ULTRA96V2/ULTRA96V2.xpfm

# Installation paths to source needed tools
source /opt/xilinx/Vivado/2019.2/settings64.sh
source /opt/xilinx/Vitis/2019.2/settings64.sh
source /opt/xilinx/xrt/setup.sh
source /opt/xilinx/petalinux/2019.2/settings.sh

cp -r $VITIS_AI_HOME/DPU-TRD $VITIS_AI_HOME/DPU-TRD-ULTRA96V2

cp $DPU_CONNECTION_FILE $TRD_HOME/prj/Vitis/config_file/prj_config
cp $DPU_CONF_FILE $TRD_HOME/prj/Vitis/dpu_conf.vh

make -C $TRD_HOME/prj/Vitis KERNEL=DPU DEVICE=ULTRA96V2
