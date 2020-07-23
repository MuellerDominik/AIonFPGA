
BUILD_DIR = build
PYNQ_REPO_DIR = $(BUILD_DIR)/DPU-PYNQ
PYNQ_BOARD_DIR = $(PYNQ_REPO_DIR)/boards

BOARD = Ultra96
DPU_CONFIG_FILES = config/*

IP = 10.223.65.36
USER_BOARD = xilinx
ROOT_BOARD = root
HOME_BOARD = /home/$(USER_BOARD)

BAUMER_DEB_PKGS = baumer
BAUMER_DEB_PKGS_BOARD = $(HOME_BOARD)/baumer_deb

SOURCE_VITIS = /opt/xilinx/Vitis/2019.2/settings64.sh
SOURCE_XRT = /opt/xilinx/xrt/setup.sh

DPU_PYNQ_REPO_URL = https://github.com/Xilinx/DPU-PYNQ.git

DPU_XCLBIN = $(PYNQ_BOARD_DIR)/Ultra96/dpu.xclbin
DPU_HWH = $(PYNQ_BOARD_DIR)/Ultra96/dpu.hwh
DPU_BIT = $(PYNQ_BOARD_DIR)/Ultra96/dpu.bit

DPU_INSTALL_DIR = /usr/local/lib/python3.6/dist-packages/pynq_dpu/overlays

SSH_DIR = /home/$$USER/.ssh
PUBKEY := $(shell find $(SSH_DIR) -name "*.pub")

.PHONY: all
all: 

.PHONY: get-dpu-repo
.ONESHELL:
get-dpu-repo:
ifneq (,$(wildcard $(PYNQ_REPO_DIR)))
	@echo Repo already exists, remove before cloning again 
else
	@mkdir -p $(PYNQ_REPO_DIR)
	@sleep 1
	@git clone --recursive --shallow-submodules $(DPU_PYNQ_REPO_URL) $(PYNQ_REPO_DIR)
endif

.PHONY: dpu
.ONESHELL:
dpu:
	@. $(SOURCE_VITIS)
	@. $(SOURCE_XRT)
	@cp $(DPU_CONFIG_FILES) $(PYNQ_BOARD_DIR)/$(BOARD)
	@make BOARD=$(BOARD) -C $(PYNQ_BOARD_DIR)

.PHONY: exchange-key
exchange-key:
ifeq (, $(PUBKEY))
	@echo you do not have a public key at $(SSH_DIR), you can create one with ssh-keygen
else
	@echo sending your public key to the board
	@ssh-copy-id $(USER_BOARD)@$(IP)
	@ssh-copy-id $(ROOT_BOARD)@$(IP)
	@ssh -t $(USER_BOARD)@$(IP) "echo "PermitRootLogin yes" | sudo tee -a /etc/ssh/sshd_config"
endif

# # -t needed to run command with sudo

.PHONY: install-baumer
install-baumer:
	@scp -r $(BAUMER_DEB_PKGS) $(USER_BOARD)@$(IP):$(BAUMER_DEB_PKGS_BOARD)
	@ssh -t $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	apt install $(BAUMER_DEB_PKGS_BOARD)/libpq5_10.4-0ubuntu0.18.04_arm64.deb
	apt install $(BAUMER_DEB_PKGS_BOARD)/libmysqlclient20_5.7.23-0ubuntu0.18.04.1_arm64.deb
	apt install $(BAUMER_DEB_PKGS_BOARD)/baumer-gapi-sdk-linux-v2.9.2.22969-Ubuntu-18.04-rock64.deb -y
	EOF

.PHONY: install-dnndk
install-dnndk:
	@ssh -t $(ROOT_BOARD)@$(IP) /bin/bash << EOF
	cd $(HOME_BOARD) && git clone --recursive --shallow-submodules https://github.com/Xilinx/DPU-PYNQ.git
	cd $(HOME_BOARD)/DPU-PYNQ/upgrade && make
	pip3 install pynq-dpu
	EOF

.PHONY: install-dpu
install-dpu:
	scp $(DPU_BIT) $(DPU_HWH) $(DPU_XCLBIN) $(ROOT_BOARD)@$(IP):$(DPU_INSTALL_DIR)

.PHONY: clean-dpu
clean-dpu:
	@make -C $(PYNQ_BOARD_DIR) clean

.PHONY: clean-all
clean-all:
	@rm -rf $(BUILD_DIR)

.PHONY: help
help:
	@echo
	@echo 'get-dpu-repo:		Pull DPU-PYNQ Repo from Github/Xilinx'
	@echo 'dpu: 			Build DPU.bit, DPU.xclbin and dpu.hwh file, config dpu with build/DPU-PYNQ/boards/Ultra96/dpu_conf.vh'
	@echo 'exchange-key:		Send your public key to the ULTRA96V2 board, to avoid password request'
	@echo 'install-baumer:		Copy the .deb files to the board and install remotely'
	@echo 'install-dnndk:		Download the DPU-PYNQ Repo and install: pynq xrt ubuntu_pkg opencv protobuf json_c dpu_clk glog'
	@echo 'install-dpu:		Copy files containing the DPU to the target'
	@echo 
