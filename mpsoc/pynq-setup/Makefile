
IP = 10.223.65.36
USER_BOARD = xilinx
ROOT_BOARD = root

HOME_BOARD = /home/$(USER_BOARD)

AI_REPO = $(HOME_BOARD)/AIonFPGA
SW = $(AI_REPO)/sw
PACKAGES = $(SW)/packages
INFERENCE = $(SW)/inference
CAMERA = $(INFERENCE)/camera
CAMERA_BUILD = $(CAMERA)/build
CAMERA_SO = $(CAMERA_BUILD)/camera
AI_APP_DIR = $(INFERENCE)/aionfpga
AI_APP = $(AI_APP_DIR)/aionfpga.py

MPSOC = $(AI_REPO)/mpsoc
PYNQ_SETUP = $(MPSOC)/pynq-setup
BACKGROUND = $(PYNQ_SETUP)/background.png
BACKGROUND_DEST = /usr/local/share/x11/pynq-background.png

DPU_INSTALL_DIR = $(AI_APP_DIR)/build

DEB_PKGS_BOARD = $(HOME_BOARD)/packages
DEB_PQ5 = $(DEB_PKGS_BOARD)/libpq5_10.4-0ubuntu0.18.04_arm64.deb
DEB_MYSQLCLIENT = $(DEB_PKGS_BOARD)/libmysqlclient20_5.7.23-0ubuntu0.18.04.1_arm64.deb
DEB_BAUMER = $(DEB_PKGS_BOARD)/baumer-gapi-sdk-linux-v2.9.2.22969-Ubuntu-18.04-rock64.deb

DPU_XCLBIN = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.xclbin
DPU_HWH = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.hwh
DPU_BIT = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.bit
DPU_MODEL = ../cnn-model/build/dpu_*.elf

SERVICE_DIR = $(PYNQ_SETUP)
SERVICE_FILE_DEST = /etc/systemd/system/
SERVICE_FILE = aionfpga.service
SERVICE_SH_FILE = start_app.sh

DPU_PYNQ_REPO = $(HOME_BOARD)/DPU-PYNQ
PYNQ_UPGRADE = $(DPU_PYNQ_REPO)/upgrade

AI_REPO_URL = https://github.com/MuellerDominik/AIonFPGA.git
DPU_PYNQ_REPO_URL = https://github.com/Xilinx/DPU-PYNQ.git

FONT_NAME = "Agency FB.ttf"
FONT_DIR = "/usr/share/fonts/truetype"
FONT_LINK = "https://img.download-free-fonts.com/dl.php?id=70765&hash=d4507f921f3975b8e76d416ba8e5d189"

LOCAL_SSH_DIR = /home/$$USER/.ssh
LOCAL_PUBKEY := $(shell find $(LOCAL_SSH_DIR) -name "*.pub")

.PHONY: all
all: exchange-key rm-background-tasks install-dnndk install-tools install-aionfpga

.PHONY: exchange-key
exchange-key:
ifeq (, $(LOCAL_PUBKEY))
	@echo "you do not have a public key at $(LOCAL_SSH_DIR), you can create one with ssh-keygen"
else
	@echo "sending your public key to the board"
	@ssh-copy-id $(USER_BOARD)@$(IP)
	@ssh-copy-id $(ROOT_BOARD)@$(IP)
endif

.PHONY: rm-background-tasks
.ONESHELL:
rm-background-tasks:
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	apt-get remove chromium-browser -y
	sudo systemctl disable jupyter.service
	sudo systemctl stop jupyter.service
	EOF

.PHONY: install-dnndk
.ONESHELL:
install-dnndk:
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	git clone --recursive --shallow-submodules $(DPU_PYNQ_REPO_URL) $(DPU_PYNQ_REPO)
	make -C $(PYNQ_UPGRADE)
	pip3 install pynq-dpu
	EOF

# 	pip3 install --upgrade setuptools
# setuptools for testing purposes, causes problem 

.PHONY: install-tools
.ONESHELL:
install-tools:
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	apt-get update
	apt-get install $(DEB_PQ5) -y
	apt-get install $(DEB_MYSQLCLIENT) -y
	apt-get install $(DEB_BAUMER) -y
	apt-get remove python3-matplotlib -y
	apt-get remove python3-numpy -y
	apt-get remove cython3 -y
	apt-get install python3-tk -y
	apt-get upgrade -y
	apt-get autoremove
	pip3 install PySimpleGUI
	pip3 install cython
	pip3 install matplotlib==3.1.1
	curl -o $(FONT_DIR)/$(FONT_NAME) $(FONT_LINK)
	python3 -c "import matplotlib.font_manager as font_manager; font_manager._rebuild()"
	EOF

.PHONY: install-aionfpga
.ONESHELL:
install-aionfpga:
	@ssh $(USER_BOARD)@$(IP) /bin/bash << EOF
	git clone $(AI_REPO_URL) $(HOME_BOARD)/AIonFPGA
	mkdir $(DPU_INSTALL_DIR)
	EOF
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	cp $(BACKGROUND) $(BACKGROUND_DEST)
	cp $(SERVICE_DIR)/$(SERVICE_FILE) $(SERVICE_FILE_DEST)
	cd $(CAMERA) && ./install.sh
	cd $(PACKAGES) && pip3 install -e .
	chmod +x $(AI_APP)
	systemctl enable $(SERVICE_FILE)
	EOF
	@scp $(DPU_MODEL) $(DPU_BIT) $(DPU_HWH) $(DPU_XCLBIN) $(USER_BOARD)@$(IP):$(DPU_INSTALL_DIR)

.PHONY: help
help:
	@echo
	@echo "exchange-key:		Send your public key to the ULTRA96V2 board, to avoid password requests"
	@echo "rm-background-tasks:	Remove Chromium and deactivate jupyter notebook to reduce background processing"
	@echo "install-dnndk:		Download the DPU-PYNQ Repo and install: pynq xrt ubuntu_pkg opencv protobuf json_c dpu_clk glog"
	@echo "install-tools:		Install the .deb files on the board for baumer and some other packages"
	@echo "install-aionfpga:	Get AIonFPGA repo from Github, enable aionfpga.service to run AI Application at boot and copy dpu.bit, dpu.hwh, dpu.xclbin and dpu_fhnw_toys_0.elf to the target"
	@echo 
