
BUILD_DIR = build
PYNQ_REPO_DIR = $(BUILD_DIR)/DPU-PYNQ
PYNQ_BOARD_DIR = $(PYNQ_REPO_DIR)/boards

BOARD = Ultra96
DPU_CONFIG_FILES = config/*

SOURCE_VITIS = /opt/xilinx/Vitis/2019.2/settings64.sh
SOURCE_XRT = /opt/xilinx/xrt/setup.sh

DPU_PYNQ_REPO_URL = https://github.com/Xilinx/DPU-PYNQ.git

.PHONY: all
all: get-dpu-repo dpu

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

.PHONY: clean-dpu
clean-dpu:
	@make -C $(PYNQ_BOARD_DIR) clean

.PHONY: clean
clean-all:
	@rm -rf $(BUILD_DIR)

.PHONY: help
help:
	@echo
	@echo 'all:			Execute get-dpu-repo and dpu'
	@echo 'get-dpu-repo:		Pull DPU-PYNQ Repo from Github/Xilinx'
	@echo 'dpu: 			Build DPU.bit, DPU.xclbin and dpu.hwh file, config dpu with build/DPU-PYNQ/boards/Ultra96/dpu_conf.vh'
	@echo 
