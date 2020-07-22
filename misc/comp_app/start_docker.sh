#!/bin/bash

CWD=$(pwd)
ROOT=$CWD
CONTAINERNAME=docker-compile

IMAGE_NAME=xilinx/vitis-ai:runtime-1.0.0-cpu

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

# -v: Mount volume
# -e: Set Environment Variables
# -w: Working directory inside the container
# -i: Keep STDIN open even if not attached 
# -t: Allocate a pseudo-TTY
# --rm: Automatically remove the container when it exits
# --name: Assign a name to the container
# --network: Connect a container to a network

docker run \
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

# docker exec $CONTAINERNAME ./$DOCKER_SH_SCRIPT

# docker stop $CONTAINERNAME
