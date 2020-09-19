# AIonFPGA

> AI High-Performance Solution on FPGA

<img src="https://github.com/MuellerDominik/AIonFPGA/blob/master/doc/.imgs/arch.svg" alt="Architecture of the Convolutional Neural Network">

## Abstract

In a world of self-driving cars and automated quality control in manufacturing, real-time image classification is becoming increasingly important.
Artificial intelligence, and deep learning in particular, are achieving excellent classification accuracies, but there are some challenges.

For one thing, high-resolution image acquisition systems require a lot of processing power.
For another, a large labeled dataset of training data is required to train deep convolutional neural networks.

A solution for the former is to use field-programmable gate arrays (FPGAs) as hardware accelerators.
Therefore, an embedded system featuring a multiprocessor system-on-chip with an integrated FPGA is deployed.
The second problem is approached with data augmentation to artificially increase the size of the labeled dataset.

This allowed the deployed convolutional neural network to achieve a Top-1 accuracy of 97.2&nbsp;% and a Top-5 accuracy of 99.5&nbsp;%.
In addition, the throughput of the image classification chain reached 41.1&nbsp;fps for color images of 1280×1024&nbsp;px.

Using data augmentation significantly improved the real-world classification performance by reducing the impact of ambient light.
Furthermore, it completely eliminated the need to collect additional data samples.

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
| Presentation        | [.pdf][Presentation]    | `2e3b39469f03a21843b4881c65a7d82646388275b02431f400497ac3d9e51925` |
| Fact Sheet          | [.pdf][Fact Sheet]      | `b85f36d1627cad99a8532ecc9528f8b2400884795de159473b460e02a38514ba` |
| Poster              | [.pdf][Poster]          | `8605bac39041a88e24b22f1d9ff3b48a6822ba567db58a8b4c57e0f313d0df62` |

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

## Previous Project

This bachelor thesis is the continuation of the following previous project: [P5-AIonFPGA](https://git.io/p5-aionfpga)

## License

Copyright &copy; 2020 Dominik Müller and Nico Canzani

This project is licensed under the terms of the Apache License 2.0 - see the [LICENSE](LICENSE "LICENSE") file for details

[Project Plan]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v0.0.2/project-plan_aionfpga_canzani_mueller_v002.pdf
[Bachelor Thesis]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/p6_aionfpga_thesis_canzani_mueller.pdf
[Presentation]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/p6_aionfpga_presentation_canzani_mueller.pdf
[Fact Sheet]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/p6_aionfpga_fact-sheet_canzani_mueller.pdf
[Poster]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/p6_aionfpga_poster_canzani_mueller.pdf

[Camera Library]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/libcamera.so
[Saved Model]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/SavedModel.zip
[Frozen Graph]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/frozen_graph.pb
[Quantized Model]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu_fhnw_toys_0.elf
[DPU bit]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.bit
[DPU hwh]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.hwh
[DPU xclbin]: https://github.com/MuellerDominik/AIonFPGA/releases/download/v1.0.0/dpu.xclbin
