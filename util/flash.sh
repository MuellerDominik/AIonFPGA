#!/bin/bash

DISK=/dev/mmcblk0
PART=p

BOOT=/mnt/boot
ROOTFS=/mnt/rootfs

# ROOTFS_CONT=../mpsoc/os/build/Vitis-AI/DPU-TRD-ULTRA96V2/prj/Vitis/binary_container_1/sd_card/rootfs.tar.gz
ROOTFS_CONT=../bin/rootfs.tar.gz
BOOT_BIN=../bin/BOOT.BIN
IMAGE_UB=../bin/image.ub

# make sure the device is not mounted
# (todo: unmount all partitions properly and not just the first two)
sudo umount $DISK
sudo umount $DISK${PART}1
sudo umount $DISK${PART}2

sleep 10

# format disk
sudo dd if=/dev/zero of=$DISK bs=4096 status=progress # fast

#sleep 10

sudo parted $DISK -s mklabel msdos
sudo parted $DISK -s mkpart primary fat32 1MiB 1025MiB
sudo parted $DISK -s mkpart primary ext4 1026MiB 100%

sudo parted $DISK -s set 1 boot on

sleep 10

sudo mkfs -t vfat -F 32 -n boot $DISK${PART}1
sudo mkfs -t ext4 -L rootfs $DISK${PART}2

# debug
#parted $DISK -s print

sudo mkdir $BOOT
sudo mkdir $ROOTFS

sudo mount $DISK${PART}1 $BOOT
sudo mount $DISK${PART}2 $ROOTFS

sudo cp $BOOT_BIN $BOOT
sudo cp $IMAGE_UB $BOOT

sudo tar -xf $ROOTFS_CONT -C $ROOTFS

sync
sleep 10

sudo umount $DISK${PART}1
sudo umount $DISK${PART}2

sudo rmdir $BOOT
sudo rmdir $ROOTFS
