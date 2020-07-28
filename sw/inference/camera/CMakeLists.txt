# aionfpga ~ camera
# Copyright (C) 2020 Dominik Müller and Nico Canzani

cmake_minimum_required(VERSION 2.8)
project(camera)

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    # default path is '/usr/local'
    get_filename_component(BGAPI2_SDK_PATH /usr/local ABSOLUTE)
    include_directories(${BGAPI2_SDK_PATH}/src/baumer/inc)

    if(CMAKE_BUILD_TYPE MATCHES debug)
        message(STATUS "DEBUG ============================================")
        set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -D_DEBUG -O0")
    elseif(CMAKE_BUILD_TYPE MATCHES release)
        message(STATUS "RELEASE ==========================================")
        set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -O3")
    endif()

    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GNULINUX")

    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -finline-limit=10000")
        execute_process(COMMAND ${CMAKE_C_COMPILER} -dumpversion OUTPUT_VARIABLE GCC_VERSION)
        if(GCC_VERSION VERSION_GREATER 4.7 OR GCC_VERSION VERSION_EQUAL 4.7)
            message(STATUS "GCC version >= 4.7")
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11")
        else()
            message(FATAL_ERROR "GCC version must be >= 4.7")
        endif()
    else()
        message(FATAL_ERROR "Currently, only GCC is supported.")
    endif()

    if(PLATFORM_ARM AND NOT CROSS_COMPILE)
        set(CMAKE_CXX_FLAGS
            "${CMAKE_CXX_FLAGS} -Wall -Wno-long-long -fexpensive-optimizations -fomit-frame-pointer -funroll-loops -pipe -fexceptions -Wpointer-arith -Wcast-align -Wsign-compare -pedantic")
        set(LIB_PROJECT ${LIB_PROJECT} bgapi2_genicam pthread dl)
    else()
        set(CMAKE_CXX_FLAGS
            "${CMAKE_CXX_FLAGS} -Wall -Wno-long-long -fexpensive-optimizations -fomit-frame-pointer -funroll-loops -pipe -fexceptions -Wpointer-arith -Wcast-align -Wsign-compare -pedantic -mmmx -msse")
        set(LIB_PROJECT ${LIB_PROJECT} bgapi2_genicam pthread)
    endif()

    set(LIB_SYSTEM ${LIB_SYSTEM} ${BGAPI2_SDK_PATH}/lib/baumer)

    foreach(LIB ${LIB_PROJECT})
        set(SHARELIB ${SHARELIB}-NOTFOUND)
        find_library(SHARELIB NAMES ${LIB} PATHS ${PROJECT_BINARY_DIR}/lib ${LIB_SYSTEM})
        if(SHARELIB)
            set(LIBS_ALL ${LIBS_ALL} ${SHARELIB})
            set(SHARELIB ${SHARELIB}-NOTFOUND)
        endif()
    endforeach()

    set(BGAPI2_EXT_SC_LIB ${SHARELIB}-NOTFOUND)
    find_library(BGAPI2_EXT_SC_LIB NAMES bgapi2_ext_sc PATHS ${PROJECT_BINARY_DIR}/lib ${LIB_SYSTEM})

    # OpenCV
    message(STATUS "OpenCV ===========================================")
    option(ENABLE_OPENCV "Enable OpenCV support" ON)

    if(ENABLE_OPENCV)
        find_package(OpenCV QUIET COMPONENTS core highgui imgproc)
        if(OpenCV_FOUND)
            message(STATUS "OpenCV version: '${OpenCV_VERSION}'")
            if(NOT "${OpenCV_LIB_PATH}" STREQUAL "")
                get_filename_component(OpenCV_BIN_PATH "${OpenCV_LIB_PATH}/../bin" ABSOLUTE)
            else()
                set(OpenCV_BIN_PATH "${_OpenCV_LIB_PATH}")
            endif()

            if(OpenCV_VERSION_MAJOR GREATER "2")
                add_definitions(-DUSE_OCL_COMPONENT=3)
                find_package(OpenCV COMPONENTS videoio imgcodecs)
                if(NOT OpenCV_FOUND)
                    message(FATAL_ERROR "OpenCV has no video support.")
                endif()
            else()
                message(FATAL_ERROR "OpenCV version must be > 2.x.x")
            endif()
        else()
            message(FATAL_ERROR "OpenCV not found.")
        endif()

        add_definitions(-DUSE_OPENCV=1)
        list(APPEND INCLUDE_DIR ${OpenCV_INCLUDE_DIRS})
        message(STATUS "OpenCV Libs:    '${OpenCV_LIBS}'")
    endif()

    if(INCLUDE_DIR)
        include_directories("${INCLUDE_DIR}")
    endif()
else()
    message(FATAL_ERROR "Currently, only Linux is supported.")
endif()

set(SOURCE_FILES camera.cc)

# add_executable(${PROJECT_NAME} ${SOURCE_FILES})
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} ${LIBS_ALL} ${OpenCV_LIBS})
