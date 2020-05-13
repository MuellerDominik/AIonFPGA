#!/bin/bash

DISK=/dev/mmcblk0
PART=p

BOOT=/mnt/boot
ROOTFS=/mnt/rootfs

# ROOTFS_CONT=../mpsoc/os/build/Vitis-AI/DPU-TRD-ULTRA96V2/prj/Vitis/binary_container_1/sd_card/rootfs.tar.gz
ROOTFS_CONT=../bin/rootfs.tar.gz
BOOT_BIN=../bin/BOOT.BIN
IMAGE_UB=../bin/image.ub
dpu_XCLBIN=../bin/dpuxclbin
VAI_PACKAGE=../bin/xilinx_vai_board_package

# make sure the device is not mounted
# (todo: unmount all partitions properly and not just the first two)
umount $DISK
umount $DISK${PART}1
umount $DISK${PART}2

sleep 10

# format disk
dd if=/dev/zero of=$DISK bs=4096 status=progress # fast

#sleep 10

parted $DISK -s mklabel msdos
parted $DISK -s mkpart primary fat32 1MiB 1025MiB
parted $DISK -s mkpart primary ext4 1026MiB 100%

parted $DISK -s set 1 boot on

sleep 10

mkfs -t vfat -F 32 -n boot $DISK${PART}1
mkfs -t ext4 -L rootfs $DISK${PART}2

# debug
#parted $DISK -s print

mkdir $BOOT
mkdir $ROOTFS

mount $DISK${PART}1 $BOOT
mount $DISK${PART}2 $ROOTFS

cp $BOOT_BIN $BOOT
cp $IMAGE_UB $BOOT

cp -r $VAI_PACKAGE $BOOT

tar -xf $ROOTFS_CONT -C $ROOTFS

# Correct changes from sd_conten.sh workaround
# sudo chmod u-r $ROOTFS/usr/bin/sudo

sync
sleep 10

umount $DISK${PART}1
umount $DISK${PART}2

rmdir $BOOT
rmdir $ROOTFS
