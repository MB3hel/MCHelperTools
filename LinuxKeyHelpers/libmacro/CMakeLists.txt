cmake_minimum_required(VERSION 3.16)
project(MCHelperScriptsLinux)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/")

find_package(Libinput REQUIRED)
find_package(UDev REQUIRED)

add_library(macro SHARED src/libmacro.c)
target_link_libraries(macro Libinput::Libinput UDev::UDev)
target_include_directories(macro PUBLIC "${PROJECT_SOURCE_DIR}/include/")