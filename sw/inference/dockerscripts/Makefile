
PROJECT   =  ai_application    

override CROSS_COMPILE := /opt/vitis_ai/petalinux_sdk/sysroots/x86_64-petalinux-linux/usr/bin/aarch64-xilinx-linux/aarch64-xilinx-linux-
override SYSROOT := /opt/vitis_ai/petalinux_sdk/sysroots/aarch64-xilinx-linux

CXX       :=   $(CROSS_COMPILE)g++

CFLAGS    :=   --sysroot=$(SYSROOT) -O2 -Wall -Wpointer-arith -std=c++11 -ffast-math
CFLAGS    +=   -I$(SYSROOT)/usr/include -I$(SYSROOT)/usr/local/include -I./include
CFLAGS +=  -mcpu=cortex-a53

LDFLAGS   :=  --sysroot=$(SYSROOT) -L$(SYSROOT)/usr/local/lib/ -L${SYSROOT}/lib -L${SYSROOT}/usr/lib 
LDFLAGS   +=  -ln2cube -lopencv_videoio  -lopencv_imgcodecs -lopencv_highgui -lopencv_imgproc -lopencv_core -lpthread 

CUR_DIR =   $(shell pwd)

BUILD   =   $(CUR_DIR)/../build
VPATH   =   $(SRC)

CC_DIR :=   $(CUR_DIR)/../src/main.cc
OBJ    +=   $(patsubst %.cc, %.o, $(notdir $(CC_DIR)))

ARCH	=   $(shell uname -m | sed -e s/arm.*/armv71/ \
				  -e s/aarch64.*/aarch64/ )

MODEL = $(CUR_DIR)/../../../mpsoc/comp_model/build/dpu_model_0.elf
SRC     =   $(CUR_DIR)/../src

.PHONY: all clean 

all: $(BUILD) $(PROJECT) 
 
$(PROJECT) : $(OBJ) 
	$(CXX) $(CFLAGS) $(addprefix $(BUILD)/, $^) $(MODEL) -o $(BUILD)/$@ $(LDFLAGS)

%.o : %.cc
	$(CXX) -c $(CFLAGS) $< -o $(BUILD)/$@

clean:
	$(RM) -rf $(BUILD)
	$(RM) $(PROJECT) 

$(BUILD) : 
	-mkdir -p $@ 
