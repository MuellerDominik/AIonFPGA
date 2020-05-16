.PHONY: all
all:
	build-os
	quant-model
	comp-model
	comp-app
	prep-cont
	flash-sd


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