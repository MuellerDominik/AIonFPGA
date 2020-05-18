#!/bin/bash

CWD=$(pwd)
ROOT=$CWD/../..
CONTAINERNAME=docker-vitis-ai-tools-quantize
DOCKER_SH_SCRIPT=mpsoc/quant_model/scripts/quant_model.sh
BUILD_DIR=build

IMAGE_NAME=xilinx/vitis-ai:tools-1.0.0-cpu

user=`whoami`
uid=`id -u`
gid=`id -g`

#rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

xclmgmt_driver="$(find /dev -name xclmgmt\*)"
docker_devices=""
for i in ${xclmgmt_driver} ;
do
  docker_devices+="--device=$i "
done

render_driver="$(find /dev/dri -name renderD\*)"
for i in ${render_driver} ;
do
  docker_devices+="--device=$i "
done

docker run \
    -d \
    $docker_devices \
    -v /opt/xilinx/dsa:/opt/xilinx/dsa \
    -v /opt/xilinx/overlaybins:/opt/xilinx/overlaybins \
    -e USER=$user -e UID=$uid -e GID=$gid \
    -v $ROOT:/workspace \
    -w /workspace \
    -it \
    --rm \
    --name $CONTAINERNAME \
    --network=host \
    $IMAGE_NAME \
    bash

docker exec $CONTAINERNAME ./$DOCKER_SH_SCRIPT

docker stop $CONTAINERNAME
