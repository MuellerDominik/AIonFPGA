
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
ROOTFS_SCRIPTS_CONF = $(ROOTFS_SCRIPTS)/config

PYNQ_IMG_NAME = ultra96v2_v2.5.img
PYNQ_IMG_URL_NAME = 2MMrXcS
PYNQ_IMG_URL = http://bit.ly/$(PYNQ_IMG_URL_NAME)

USER_BOARD = xilinx
ROOT_BOARD = root
HOME_BOARD = /home/$(USER_BOARD)

BAUMER_DEB_PKGS = packages
BAUMER_DEB_PKGS_BOARD = $(HOME_BOARD)/packages

.PHONY: all
all: get-img flash-img copy-files

.PHONY: get-img
get-img:
ifneq (,$(wildcard $(BUILD_DIR)/$(PYNQ_IMG_NAME)))
	@echo Image already exists, clean if you want to download and extract again
else
	@mkdir -p $(BUILD_DIR)
	@wget $(PYNQ_IMG_URL)
	@unzip $(PYNQ_IMG_URL_NAME) -d $(BUILD_DIR)
	@mv $(PYNQ_IMG_URL_NAME) $(BUILD_DIR)
	@echo
	@echo Stored image in build folder
	@echo
endif

.PHONY: flash-img
flash-img:
	@sudo umount -f $(wildcard $(DISK)?*) || : # Will result in 'bad usage' if no partition present 
	@sleep 10
	@echo
	@echo Erasing SD card
	@echo
	@sudo dd if=/dev/zero of=$(DISK) bs=1M status=progress  || :
	@sleep 10
	@echo
	@echo Flashing image to SD card
	@echo
	@sudo dd bs=1M if=$(BUILD_DIR)/$(PYNQ_IMG_NAME) of=$(DISK) status=progress # conv=fsync
	@echo
	@echo Image written to SD card
	@echo

.PHONY: copy-files
copy-files:
	@sudo mkdir -p $(ROOTFS)
	@sleep 10
	@sudo mount $(DISK)$(PART)2 $(ROOTFS)
	@sudo cp $(WPA_CONFIG_FILE) $(ROOTFS)/etc
	@sudo cp $(INTERFACES_CONFIG_FILE) $(ROOTFS)/etc/network
	@sudo mkdir -p $(ROOTFS_SCRIPTS_CONF)
	@sudo cp $(WIFI_SCRIPT) $(ROOTFS_SCRIPTS)
	@sudo cp $(WPA_CONFIG_FILE) $(ROOTFS_SCRIPTS_CONF)
	@sudo cp -r $(BAUMER_DEB_PKGS) $(ROOTFS)/$(BAUMER_DEB_PKGS_BOARD)
	@echo "PermitRootLogin yes" | sudo tee -a $(ROOTFS)/etc/ssh/sshd_config
	@sudo umount $(DISK)$(PART)2 || :
	@sudo rmdir $(ROOTFS)
	@echo
	@echo All files copied
	@echo

.PHONY: clean
clean:
	@rm -rf $(BUILD_DIR)

.PHONY: help
help:
	@echo
	@echo 'all:		run get-img, flash-img and install-wifi'
	@echo 'get-img: 	Pull PYNQ image from Avnet if it does not exist locally yet'
	@echo 'flash-img: 	Flash PYNQ image on SD card, ps: edit mounting point of your SD card, get mnt-pnt with lsblk'
	@echo 'copy files:	Copy wifi config files, wifi-script and baumer deb files to the rootfs on the SD card'
	@echo 'clean:		Remove all builded files'
	@echo
