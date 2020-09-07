# AIonFPGA

> AI High-Performance Solution on FPGA

<img src="https://github.com/MuellerDominik/AIonFPGA/blob/master/doc/.imgs/arch.svg" alt="Architecture of the Convolutional Neural Network">

## Repository Structure

This repository is structured as follows:

```
.
├── doc                 # Documentation
│   ├── fact-sheet
│   ├── poster
│   ├── presentation
│   ├── project-plan
│   └── thesis          # Bachelor Thesis
│
├── mpsoc               # OS / DPU / Model
│   ├── build-pynq
│   ├── cnn-model       # Quantization
│   ├── dpu
│   └── pynq-setup
│
└── sw                  # Software
    ├── inference
    │   ├── aionfpga    # Inference Application
    │   └── camera      # Camera Library
    ├── packages
    │   └── fhnwtoys    # Package fhnwtoys
    ├── training        # Model
    └── verification
```

## Downloads

### Documents

The compiled `.pdf` files can be downloaded from here directly:

| Name                | Download                | SHA-256 checksum                                                   |
|:------------------  |:----------------------  |:------------------------------------------------------------------ |
| Project Plan        | [.pdf][Project Plan]    | `ca5c77def20f017892c571859c7772a77c04b8ebc5d4bef795865e88b3c6474f` |
| **Bachelor Thesis** | [.pdf][Bachelor Thesis] | `818df883f765bed2fa2e500bd5064ae3236327c9e5a2626e270d5e65cc38c8f0` |
| Presentation        | [.pptx][Presentation]   | `...` |
| Fact Sheet          | [.pdf][Fact Sheet]      | `...` |
| Poster              | [.pdf][Poster]          | `...` |

#### Compilation

The `.pdf` files can be built by running `make` in the respective directory:

```bash
$ make build clean
```

### Software

| Name            | Download                                                        | SHA-256 checksum                                                   |
|:--------------- |:--------------------------------------------------------------- |:------------------------------------------------------------------ |
| Camera Library  | [.so][Camera Library]                                           | `f3182088466f0b83008e450eb1ce2bf8fa49996659b8dc2617379498735bf5b2` |
| Saved Model     | [.zip][Saved Model]                                             | `d54530104d07541d01fefe949ed7b5767533bcafba8ac65b19a765e1547bea49` |
| Frozen Graph    | [.pb][Frozen Graph]                                             | `2ca336ebf425bb668925599aedb67197557b3082694dfa79aeac130b576a4523` |
| Quantized Model | [.elf][Quantized Model]                                         | `9ff451d90434959103951976859c2be538e2d89b06f886ac267ea05bff0ac436` |
| DPU             | [.bit][DPU bit] <br> [.hwh][DPU hwh] <br> [.xclbin][DPU xclbin] | `478f05f4b1a9a35121b8cf3824cc096ba514157be8aa402950668746027e3d0c` <br> `0c64dc4a6f8912893d6fa3967ed937d2ec10abd4e1d81800386e6540eed877ab` <br> `29e5adb0218e1ead172f36f8c88f805d3f3d039bb1ccb6041286e0e21ba86dcf` |

## License

Copyright &copy; 2020 Dominik Müller and Nico Canzani

This project is licensed under the terms of the Apache License 2.0 - see the [LICENSE](LICENSE "LICENSE") file for details

[Project Plan]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v0.0.2/project-plan_aionfpga_canzani_mueller_v002.pdf
[Bachelor Thesis]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/p6_aionfpga_thesis_canzani_mueller.pdf
[Presentation]: #
[Fact Sheet]: #
[Poster]: #

[Camera Library]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/libcamera.so
[Saved Model]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/SavedModel.zip
[Frozen Graph]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/frozen_graph.pb
[Quantized Model]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu_fhnw_toys_0.elf
[DPU bit]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.bit
[DPU hwh]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.hwh
[DPU xclbin]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.xclbin
