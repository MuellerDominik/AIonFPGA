//Setting the arch of DPU, for more details, please read the PG338 


// Define architecture, B2304 has best performance on ZU3EG
`define B2304

// No URAM on Ultrascale+ ZU3EG
`define URAM_DISABLE 

// Config URAM
`ifdef URAM_ENABLE
    `define def_UBANK_IMG_N          5
    `define def_UBANK_WGT_N          17
    `define def_UBANK_BIAS           1
`elsif URAM_DISABLE
    `define def_UBANK_IMG_N          0
    `define def_UBANK_WGT_N          0
    `define def_UBANK_BIAS           0
`endif

// Using more Block RAM for higher performance
`define RAM_USAGE_HIGH

// Use, when the number of input channels is much lower than the available channel parallelism (case in most cnn's).
`define CHANNEL_AUGMENTATION_ENABLE

// In depthwise separable convolution, the operation is performed in two steps: depthwise convolution and pointwise convolution. Enabled: performance is better but more resources are needed.
`define DWCV_ENABLE

// Run average pooling operation on the DPU, faster
`define POOL_AVG_ENABLE

// LeakyReLU becomes available as an activation function
`define RELU_LEAKYRELU_RELU6

// Not enough DSPs available to set high with B2304 architecture on ZU3EG chip
`define DSP48_USAGE_LOW
