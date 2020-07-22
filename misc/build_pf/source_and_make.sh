#!/bin/bash

# Installation paths to source needed tools
source /opt/xilinx/Vivado/2019.2/settings64.sh
source /opt/xilinx/Vitis/2019.2/settings64.sh
source /opt/xilinx/petalinux/2019.2/settings.sh
# source /opt/xilinx/xrt/setup.sh

cd Vitis-AI/Avnet/vitis

# mkdir -p ../hdl/Projects/ultra96v2_oob/ULTRA96V2_2019_2
# cp ../../../ULTRA96V2.xsa ../hdl/Projects/ultra96v2_oob/ULTRA96V2_2019_2/.
# cp ../../../make_ultra96v2_oob_bsp.sh ../petalinux/scripts/.

make ultra96v2_oob