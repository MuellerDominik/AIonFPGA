#!/bin/bash

BUILD_DIR=../bin
RFS_DIR=$BUILD_DIR/rootfs
ARCHIV_NAME=rootfs.tar.gz

ROOT_TARGET=$RFS_DIR/home/root

GEN_SD_CONT_DIR=../mpsoc/os/build/Vitis-AI/DPU-TRD-ULTRA96V2/prj/Vitis/binary_container_1/sd_card/

DATASET=../mpsoc/os/build/Vitis-AI/DPU-TRD-ULTRA96V2/app/Vitis/samples/resnet50/img
WORDS=../mpsoc/os/build/Vitis-AI/mpsoc/dnndk_samples_zcu104/dataset/image500_640_480/words.txt

BOOT_BIN=$GEN_SD_CONT_DIR/BOOT.BIN
DPU_XCLBIN=$GEN_SD_CONT_DIR/dpu.xclbin
IMAGE_UB=$GEN_SD_CONT_DIR/image.ub
ULTRA96V2_HWH=$GEN_SD_CONT_DIR/ULTRA96V2.hwh

RFS=$GEN_SD_CONT_DIR/rootfs.tar.gz

APPLICATION=../sw/inference/build/ai_application

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR
mkdir -p $RFS_DIR

####################### Docker Session to copy VAI Board Package #######################

IMAGE_NAME=xilinx/vitis-ai:runtime-1.0.0-cpu
CONTAINERNAME=docker-vitis-ai-runtime-compile
DOCKER_SH_SCRIPT=util/dockerscripts/get_package.sh
CWD=$(pwd)
ROOT=$CWD/..

user=`whoami`
uid=`id -u`
gid=`id -g`

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

#####################################################################################3

cp $BOOT_BIN $BUILD_DIR
cp $DPU_XCLBIN $BUILD_DIR
cp $IMAGE_UB $BUILD_DIR
cp $ULTRA96V2_HWH $BUILD_DIR

sudo tar -xf $RFS -C $RFS_DIR

sudo cp $APPLICATION $ROOT_TARGET
sudo cp -r $DATASET $ROOT_TARGET
sudo cp $WORDS $ROOT_TARGET/dataset/image500_640_480
sudo cp $DPU_XCLBIN $RFS_DIR/usr/lib

# Workaround, because normal user has no read permission
# sudo chmod u+r $RFS_DIR/usr/bin/sudo

sudo tar -czf $BUILD_DIR/$ARCHIV_NAME -C $RFS_DIR .
# rm -rf $RFS_DIR

echo
echo Content ready!