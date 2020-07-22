
cmake_minimum_required(VERSION 2.8)
project(AIonFPGA)

get_filename_component(WORKSPACE_PATH /workspace ABSOLUTE)

# Enable / disable debug mode
if(CMAKE_BUILD_TYPE MATCHES debug)
    message(STATUS "DEBUG ============================================")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -D_DEBUG -O0")
elseif(CMAKE_BUILD_TYPE MATCHES release)
    message(STATUS "RELEASE ==========================================")
    set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -O3")
endif()

# Set cross compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GNULINUX")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -finline-limit=10000")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-long-long -fexpensive-optimizations -fomit-frame-pointer -funroll-loops -pipe -fexceptions -Wpointer-arith -Wcast-align -Wsign-compare -pedantic")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-long-long -fexpensive-optimizations -fomit-frame-pointer -funroll-loops -pipe -fexceptions -Wpointer-arith -Wcast-align -Wsign-compare -pedantic -mmmx -msse")

# Set Path to hpp-files
include_directories(/workspace/baumer/include)
# include_directories(/workspace/opencv/build/install/include)
# include_directories(/opt/vitis_ai/petalinux_sdk/sysroots/aarch64-xilinx-linux/usr/include) # Try tomorrow
include_directories(/opt/vitis_ai/petalinux_sdk/sysroots/aarch64-xilinx-linux/usr/include)

# Choose which packages to include from Baumer and where to find them
set(LIB_BAUMER ${LIB_BAUMER} bgapi2_genicam pthread) # pthread
# set(LIB_BAUMER ${LIB_BAUMER} bgapi2_genicam pthread dl)
set(LIB_BAUMER_PATH ${LIB_BAUMER_PATH} ${WORKSPACE_PATH}/baumer/lib)

#find_library(LIBS_BAUMER NAMES ${LIB_BAUMER} PATHS ${LIB_BAUMER_PATH})
#set(LIBS_ALL ${LIBS_ALL} ${LIBS_BAUMER})

foreach(LIB ${LIB_BAUMER})
    set(SHARELIB ${SHARELIB}-NOTFOUND)
    find_library(SHARELIB NAMES ${LIB} PATHS ${LIB_BAUMER_PATH})
    if(SHARELIB)
        set(LIBS_ALL ${LIBS_ALL} ${SHARELIB})
        set(SHARELIB ${SHARELIB}-NOTFOUND)
    endif()
endforeach()

# Choose which packages to include from opencv and where to find them
set(LIB_OPENCV ${LIB_OPENCV} opencv_core opencv_highgui opencv_imgproc opencv_imgcodecs)
# set(LIB_OPENCV_PATH ${LIB_OPENCV_PATH} ${WORKSPACE_PATH}/opencv/build/install/lib)
set(LIB_OPENCV_PATH ${LIB_OPENCV_PATH} /opt/vitis_ai/petalinux_sdk/sysroots/aarch64-xilinx-linux/usr/lib/)

#find_library(LIBS_OPENCV NAMES ${LIB_OPENCV} PATHS ${LIB_OPENCV_PATH})
#set(LIBS_ALL ${LIBS_ALL} ${LIBS_OPENCV})

foreach(LIB ${LIB_OPENCV})
    set(SHARELIB ${SHARELIB}-NOTFOUND)
    find_library(SHARELIB NAMES ${LIB} PATHS ${LIB_OPENCV_PATH})
    if(SHARELIB)
        set(LIBS_ALL ${LIBS_ALL} ${SHARELIB})
        set(SHARELIB ${SHARELIB}-NOTFOUND)
    endif()
endforeach()

# Choose which packages to include from dnndk and where to find them
set(LIB_DNNDK ${LIB_DNNDK} n2cube) # dpuaol
set(LIB_DNNDK_PATH ${LIB_DNNDK_PATH} /opt/vitis_ai/petalinux_sdk/sysroots/aarch64-xilinx-linux/usr/lib/)

foreach(LIB ${LIB_DNNDK})
    set(SHARELIB ${SHARELIB}-NOTFOUND)
    find_library(SHARELIB NAMES ${LIB} PATHS ${LIB_DNNDK_PATH})
    if(SHARELIB)
        set(LIBS_ALL ${LIBS_ALL} ${SHARELIB})
        set(SHARELIB ${SHARELIB}-NOTFOUND)
    endif()
endforeach()


set(CMAKE_CXX_COMPILER /usr/bin/aarch64-linux-gnu-g++)

set(SOURCE_FILES ../src/main.cc)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
# message(STATUS "=========================== All Libs:== '${LIBS_ALL}'")
target_link_libraries(${PROJECT_NAME} ${LIBS_ALL} /workspace/model/dpu_model_0.elf) # ${LIB_OPENCV}
