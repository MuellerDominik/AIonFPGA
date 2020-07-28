
DOCKERSTART_SCRIPT = scripts/start_docker.sh
QUANT_SCRIPT = mpsoc/cnn-model/scripts/quant_model.sh
DUMP_SCRIPT = mpsoc/cnn-model/scripts/dump_model.sh
COMP_SCRIPT = mpsoc/cnn-model/scripts/comp_model.sh
ENV_SCRIPT = mpsoc/cnn-model/scripts/set_env.sh

BUILD_DIR = build
PYCACHE = __pycache__

CONTAINERNAME = build-model
IMAGE_NAME="xilinx/vitis-ai:1.1.56"


.PHONY: all
.ONESHELL:
all: start-docker quantize-exec dump-exec compile-exec end-docker

.PHONY: start-docker
start-docker:
	@./$(DOCKERSTART_SCRIPT) $(CONTAINERNAME) $(IMAGE_NAME)

.PHONY: quantize quant
quantize quant: start-docker quantize-exec end-docker

.PHONY: dump
dump: start-docker dump-exec end-docker

.PHONY: compile comp
compile comp: start-docker compile-exec end-docker

.PHONY: quantize-exec quant-exec
quantize-exec quant-exec:
	@docker exec $(CONTAINERNAME) sh -c ". ./$(ENV_SCRIPT) && ./$(QUANT_SCRIPT)"

.PHONY: dump-exec
dump-exec:
	@docker exec $(CONTAINERNAME) sh -c ". ./$(ENV_SCRIPT) && ./$(DUMP_SCRIPT)"

.PHONY: compile-exec comp-exec
compile-exec comp-exec:
	@docker exec $(CONTAINERNAME) sh -c ". ./$(ENV_SCRIPT) && ./$(COMP_SCRIPT)"

.PHONY: end-docker
end-docker:
	@docker stop $(CONTAINERNAME)

.PHONY: clean
clean:
	@rm -rf $(BUILD_DIR)
	@rm -rf $(PYCACHE)
