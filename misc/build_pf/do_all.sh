#!/bin/bash

# Vitis AI is not needed to build the platform

# Installation paths to source needed tools
source /opt/xilinx/Vivado/2019.2/settings64.sh
source /opt/xilinx/Vitis/2019.2/settings64.sh
source /opt/xilinx/petalinux/2019.2/settings.sh
source /opt/xilinx/xrt/setup.sh

git clone https://github.com/Xilinx/Vitis-AI

cd Vitis-AI
git checkout v1.1-ultra96v2
export VITIS_AI_HOME="$PWD"

mkdir Avnet
cd Avnet
git clone https://github.com/Avnet/bdf
git clone -b 2019.2 https://github.com/Avnet/hdl
git clone -b 2019.2 https://github.com/Avnet/petalinux
git clone https://github.com/Avnet/vitis
cd vitis

# mkdir -p ../hdl/Projects/ultra96v2_oob/ULTRA96V2_2019_2
# cp ../../../ULTRA96V2.xsa ../hdl/Projects/ultra96v2_oob/ULTRA96V2_2019_2/.

# Replace source paths in make_ultra96v2_oob_bsp.sh

cp ../../../make_ultra96v2_oob_bsp.sh ../petalinux/scripts/.

make ultra96v2_oob
