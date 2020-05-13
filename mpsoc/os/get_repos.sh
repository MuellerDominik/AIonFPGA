#!/bin/bash
REPOPATH=build

rm -rf $REPOPATH

mkdir -p $REPOPATH

git clone https://github.com/Xilinx/Vitis-AI
cd Vitis-AI
git checkout v1.0
cd ..
mv Vitis-AI/ $REPOPATH/Vitis-AI


wget http://downloads.element14.com/downloads/zedboard/ultra96-v2/ULTRA96V2_2019_2.tar.xz?ICID=ultra96v2-datasheet-widget
mv ULTRA96V2_2019_2.tar.xz?ICID=ultra96v2-datasheet-widget ULTRA96V2_2019_2.tar.xz
tar -xf ULTRA96V2_2019_2.tar.xz -C $REPOPATH
rm ULTRA96V2_2019_2.tar.xz