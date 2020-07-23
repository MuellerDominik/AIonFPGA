
BUILD_DIR = build
PYNQ_REPO_DIR = $(BUILD_DIR)/DPU-PYNQ
PYNQ_BOARD_DIR = $(PYNQ_REPO_DIR)/boards

DISK = /dev/sdb
ROOTFS = /mnt/rootfs
PART =

WPA_CONFIG_FILE = wifi/wpa_supplicant.conf
INTERFACES_CONFIG_FILE = wifi/interfaces
WIFI_SCRIPT = wifi/wifi.sh

ROOTFS_SCRIPTS = $(ROOTFS)/home/xilinx/scripts
ROOTFS_SCRIPTS_CONF = $(ROOTFS_SCRIPTS)/conf

PYNQ_IMG_NAME = ultra96v2_v2.5.img
PYNQ_IMG_URL_NAME = 2MMrXcS
PYNQ_IMG_URL = http://bit.ly/$(PYNQ_IMG_URL_NAME)

.PHONY: all
all: get-img flash-img install-wifi

.PHONY: get-img
get-img:
ifneq (,$(wildcard $(BUILD_DIR)/$(PYNQ_IMG_NAME)))
	@echo Image already exists, clean if you want to download and extract again
else
	@mkdir -p $(BUILD_DIR)
	@wget $(PYNQ_IMG_URL)
	@unzip $(PNYQ_IMG_URL_NAME) -d $(BUILD_DIR)
	@mv $(PYNQ_IMG_URL_NAME) $(BUILD_DIR)
endif

.PHONY: flash-img
flash-img:
	@umount $(DISK) || :
	@umount $(DISK)$(PART)1 || :
	@umount $(DISK)$(PART)2 || :
	@sudo dd bs=4M if=$(BUILD_DIR)/$(PYNQ_IMG_NAME) of=$(DISK) status=progress # conv=fsync

.PHONY: install-wifi
install-wifi:
	@sudo mkdir $(ROOTFS)
	@sudo mount $(DISK)$(PART)2 $(ROOTFS)
	@sudo cp $(WPA_CONFIG_FILE) $(ROOTFS)/etc
	@sudo cp $(INTERFACES_CONFIG_FILE) $(ROOTFS)/etc/network
	@sudo mkdir -p $(ROOTFS_SCRIPTS_CONF)
	@sudo cp $(WIFI_SCRIPT) $(ROOTFS_SCRIPTS)
	@sudo cp $(WPA_CONFIG_FILE) $(ROOTFS_SCRIPTS_CONF)
	@sudo umount $(DISK)$(PART)2
	@sudo rmdir $(ROOTFS)

.PHONY: clean
clean:
	@rm -rf $(BUILD_DIR)

.PHONY: help
help:
	@echo
	@echo 'all:		run get-img, flash-img and install-wifi'
	@echo
	@echo 'get-img: 	Pull PYNQ image from Avnet if it does not exist yet'
	@echo 'flash-img: 	Flash PYNQ image on SD card ps: edit mounting point of your SD card, get mnt-pnt with lsblk'
	@echo 'install-wifi:	Copy wifi config files and wifi-script to the rootfs on the SD card'
	@echo 'clean:		Remove all builded files'
	@echo
