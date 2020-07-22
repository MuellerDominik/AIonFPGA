#!/bin/bash

git clone https://github.com/opencv/opencv.git
cd opencv
git checkout tags/3.4.3

mkdir build && cd build && cmake -DCMAKE_TOOLCHAIN_FILE=../platforms/linux/aarch64-gnu.toolchain.cmake ..

make all install
