cmake_minimum_required(VERSION 2.8)
project (minecraft_interface)

option(BUILD_TEST_TARGET "Build executable to test run" OFF)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O3")

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

add_library(minecraft_dqn_interface SHARED minecraft_dqn_interface.cpp)

if (BUILD_TEST_TARGET)
  add_executable(test_interface minecraft_dqn_interface.cpp)

  target_link_libraries(test_interface ${PYTHON_LIBRARIES})

  find_package(OpenCV REQUIRED)
  include_directories(${OpenCV_INCLUDE_DIRS})
  target_link_libraries(test_interface ${OpenCV_LIBS})
endif()
