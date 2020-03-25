#!/bin/bash

# aionfpga ~ flash
# Copyright (C) 2020 Dominik Müller and Nico Canzani

# This script must be run with superuser privileges.

WD=./ # trailing slash necessary

DISK=/dev/sdb
PART= # e.g.: p

BOOT=/mnt/boot
ROOTFS=/mnt/rootfs

# make sure the device is not mounted
umount ${DISK}?*

sleep 10

# format disk
# dd if=/dev/zero of=$DISK bs=512 status=progress # slow
dd if=/dev/zero of=$DISK bs=4096 status=progress # fast

sleep 10

parted $DISK -s mklabel msdos
parted $DISK -s mkpart primary fat32 1MiB 1025MiB
parted $DISK -s mkpart primary ext4 1026MiB 100%

parted $DISK -s set 1 boot on

sleep 10

mkfs -t vfat -F 32 -n boot $DISK${PART}1
mkfs -t ext4 -L rootfs $DISK${PART}2

# debug
# parted $DISK -s print

mkdir $BOOT $ROOTFS
mount $DISK${PART}1 $BOOT
mount $DISK${PART}2 $ROOTFS

cp ${WD}BOOT.BIN $BOOT
cp ${WD}image.ub $BOOT

tar -xf ${WD}rootfs.tar.gz -C $ROOTFS

sync
sleep 10

umount ${DISK}?*
rm -r $BOOT $ROOTFS
