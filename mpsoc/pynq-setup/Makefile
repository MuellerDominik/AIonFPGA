
IP = 10.223.65.36
USER_BOARD = xilinx
ROOT_BOARD = root
HOME_BOARD = /home/$(USER_BOARD)

APP_DIR = $(HOME_BOARD)/AIonFPGA/sw/inference/aionfpga
APPLICATION = $(APP_DIR)/aionfpga.py

DEB_PKGS_BOARD = $(HOME_BOARD)/packages

DPU_XCLBIN = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.xclbin
DPU_HWH = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.hwh
DPU_BIT = ../dpu/build/DPU-PYNQ/boards/Ultra96/dpu.bit

DPU_MODEL = ../cnn-model/build/dpu_*.elf

SERVICE_DIR = $(HOME_BOARD)/AIonFPGA/mpsoc/pynq-setup
SERVICE_FILE = aionfpga.service
SERVICE_SH_FILE = start_app.sh

AI_REPO = https://github.com/MuellerDominik/AIonFPGA.git

DPU_INSTALL_DIR = $(APP_DIR)/build

SSH_DIR = /home/$$USER/.ssh
PUBKEY := $(shell find $(SSH_DIR) -name "*.pub")

.PHONY: all
all: exchange-key rm-background-tasks install-dnndk install-tools install-aionfpga

.PHONY: exchange-key
exchange-key:
ifeq (, $(PUBKEY))
	@echo you do not have a public key at $(SSH_DIR), you can create one with ssh-keygen
else
	@echo sending your public key to the board
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
	cd $(HOME_BOARD) && git clone --recursive --shallow-submodules https://github.com/Xilinx/DPU-PYNQ.git
	cd $(HOME_BOARD)/DPU-PYNQ/upgrade && make
	pip3 install pynq-dpu
	EOF

# 	pip3 install --upgrade setuptools
# setuptools for testing purposes, causes problem 

.PHONY: install-tools
.ONESHELL:
install-tools:
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	apt-get update
	apt-get install $(DEB_PKGS_BOARD)/libpq5_10.4-0ubuntu0.18.04_arm64.deb
	apt-get install $(DEB_PKGS_BOARD)/libmysqlclient20_5.7.23-0ubuntu0.18.04.1_arm64.deb
	apt-get install $(DEB_PKGS_BOARD)/baumer-gapi-sdk-linux-v2.9.2.22969-Ubuntu-18.04-rock64.deb -y
	apt-get install python3-tk -y
	apt-get upgrade -y
	apt-get autoremove
	pip3 install PySimpleGUI
	EOF

.PHONY: install-aionfpga
.ONESHELL:
install-aionfpga:
	@ssh $(USER_BOARD)@$(IP) /bin/bash << EOF
	git clone $(AI_REPO) $(HOME_BOARD)/AIonFPGA
	mkdir $(DPU_INSTALL_DIR)
	EOF
	@ssh $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	mv $(SERVICE_DIR)/$(SERVICE_FILE) /etc/systemd/system/
	cd $(HOME_BOARD)/AIonFPGA/sw/inference/camera && ./install.sh
	cd $(HOME_BOARD)/AIonFPGA/sw/packages && pip3 install -e .
	chmod +x $(APPLICATION)
	systemctl enable $(SERVICE_FILE)
	EOF
	@scp $(DPU_MODEL) $(DPU_BIT) $(DPU_HWH) $(DPU_XCLBIN) $(USER_BOARD)@$(IP):$(DPU_INSTALL_DIR)

.PHONY: help
help:
	@echo
	@echo 'exchange-key:		Send your public key to the ULTRA96V2 board, to avoid password requests'
	@echo 'rm-background-tasks:	Remove Chromium and deactivate jupyter notebook to reduce background processing'
	@echo 'install-dnndk:		Download the DPU-PYNQ Repo and install: pynq xrt ubuntu_pkg opencv protobuf json_c dpu_clk glog'
	@echo 'install-tools:		Install the .deb files on the board for baumer and some other packages'
	@echo 'install-aionfpga:	Get AIonFPGA repo from Github, enable aionfpga.service to run AI Application at boot and copy dpu.bit, dpu.hwh, dpu.xclbin and dpu_fhnw_toys_0.elf to the target'
	@echo 
