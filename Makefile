.PHONY: all
all:
	@cd mpsoc/quant_model && ./quantize_model.sh
	@cd mpsoc/comp_model && ./build_model.sh
	@cd sw/inference && ./build_app.sh
	@cd util && ./sd_content.sh
	@cd util && ./flash.sh

get-repos:
	@cd mpsoc/os && ./get_repos.sh

build-os:
	@cd mpsoc/os && ./build_os.sh

quant-model:
	@cd mpsoc/quant_model && ./quantize_model.sh

comp-model:
	@cd mpsoc/comp_model && ./build_model.sh

comp-app:
	@cd sw/inference && ./build_app.sh

prep-cont:
	@cd util && ./sd_content.sh

flash-sd:
	@cd util && ./flash.sh