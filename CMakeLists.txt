cmake_minimum_required(VERSION 3.21)

project(llama_cpp)

option(LLAMA_BUILD "Build llama.cpp shared library and install alongside python package" ON)
option(LLAMA_BUILD_EXTRAS "Copy convert scripts from llama.cpp and build llama_cpp.extra module" ON)

if (LLAMA_BUILD)
    set(BUILD_SHARED_LIBS "On")
    set(LLAMA_VENDOR_DIR ${CMAKE_CURRENT_SOURCE_DIR}/vendor/llama.cpp)
    set(LLAMA_LIB_INSTALL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/llama_cpp/lib)
    file(COPY ${LLAMA_VENDOR_DIR}/LICENSE 
        DESTINATION ${LLAMA_LIB_INSTALL_DIR}
    )

    # Building llama
    if (APPLE AND NOT CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        # Need to disable these llama.cpp flags on Apple x86_64,
        # otherwise users may encounter invalid instruction errors
        set(LLAMA_AVX "Off" CACHE BOOL "llama: enable AVX" FORCE)
        set(LLAMA_AVX2 "Off" CACHE BOOL "llama: enable AVX2" FORCE)
        set(LLAMA_FMA "Off" CACHE BOOL "llama: enable FMA" FORCE)
        set(LLAMA_F16C "Off" CACHE BOOL "llama: enable F16C" FORCE)
    endif()
    add_subdirectory(${LLAMA_VENDOR_DIR})
    install(
        TARGETS llama 
        LIBRARY DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        RUNTIME DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        ARCHIVE DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        FRAMEWORK DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        RESOURCE DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
    )
    # Temporary fix for https://github.com/scikit-build/scikit-build-core/issues/374
    install(
        TARGETS llama 
        LIBRARY DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        RUNTIME DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        ARCHIVE DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        FRAMEWORK DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        RESOURCE DESTINATION ${LLAMA_LIB_INSTALL_DIR}
    )
    # Workaround for Windows + CUDA https://github.com/abetlen/llama-cpp-python/issues/563
    install(
        FILES $<TARGET_RUNTIME_DLLS:llama>
        DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
    )
    install(
        FILES $<TARGET_RUNTIME_DLLS:llama>
        DESTINATION ${LLAMA_LIB_INSTALL_DIR}
    )

    # Building llava
    add_subdirectory(${LLAMA_VENDOR_DIR}/examples/llava)
    set_target_properties(llava_shared PROPERTIES OUTPUT_NAME "llava")
    # Set CUDA_ARCHITECTURES to OFF on windows
    if (WIN32)
        set_target_properties(llava_shared PROPERTIES CUDA_ARCHITECTURES OFF)
    endif()
    install(
        TARGETS llava_shared
        LIBRARY DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        RUNTIME DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        ARCHIVE DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        FRAMEWORK DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
        RESOURCE DESTINATION ${SKBUILD_PLATLIB_DIR}/llama_cpp
    )
    # Temporary fix for https://github.com/scikit-build/scikit-build-core/issues/374
    install(
        TARGETS llava_shared
        LIBRARY DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        RUNTIME DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        ARCHIVE DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        FRAMEWORK DESTINATION ${LLAMA_LIB_INSTALL_DIR}
        RESOURCE DESTINATION ${LLAMA_LIB_INSTALL_DIR}
    )

    if(LLAMA_BUILD_EXTRAS)
        find_package(Python COMPONENTS Interpreter REQUIRED)
        if(DEFINED ENV{VIRTUAL_ENV} OR DEFINED ENV{CONDA_PREFIX})
            set(_pip_args "-q")
        else()
            set(_pip_args "--user" "-q")
        endif()
        execute_process(COMMAND ${Python_EXECUTABLE} -m pip install ${_pip_args} -r ${${LLAMA_VENDOR_DIR}}/requirements.txt)
        set(EXTRAS_INSTALL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/llama_cpp/extra)
        file(
            COPY ${LLAMA_VENDOR_DIR}/LICENSE 
            DESTINATION ${EXTRAS_INSTALL_DIR}
        )
        file(WRITE ${EXTRAS_INSTALL_DIR}/__init__.py "")
        file(COPY
            ${LLAMA_VENDOR_DIR}/convert.py
            ${LLAMA_VENDOR_DIR}/convert-hf-to-gguf.py
            ${LLAMA_VENDOR_DIR}/convert-llama-ggml-to-gguf.py
            DESTINATION ${EXTRAS_INSTALL_DIR}
        )
    endif()
endif()
