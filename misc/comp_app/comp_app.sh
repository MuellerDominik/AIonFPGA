#!/bin/bash

CWD=$(pwd)
SRC=$CWD/scripts

B_DIR=$CWD/build

B_TYPE=debug

CMAKE_OPTIONS=""
CMAKE_OPTIONS="$CMAKE_OPTIONS -DPLATFORM_ARM=ON"
CMAKE_OPTIONS="$CMAKE_OPTIONS -DCROSS_COMPILE=ON"
CMAKE_OPTIONS="$CMAKE_OPTIONS -DCMAKE_BUILD_TYPE=$B_TYPE"
CMAKE_OPTIONS="$CMAKE_OPTIONS -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"

# Build directory
rm -rf $B_DIR && mkdir $B_DIR && cd $B_DIR

# Generate the project files
cmake -G "Unix Makefiles" $CMAKE_OPTIONS $SRC

# Build the project
make
