
cmake_minimum_required(VERSION 3.21)
project(StickyPiTakePicture)

SET(COMPILE_DEFINITIONS -Werror)


set(VCOS_PTHREADS_BUILD_SHARED TRUE)
set(CMAKE_BUILD_TYPE Release)

SET(COMPILE_DEFINITIONS -Werror)

include_directories(/opt/vc/include/interface/vcos/pthreds)
include_directories(/opt/vc/include/interface/vcos/pthreads)
include_directories(/opt/vc/include/interface/vmcs_host/linux)
include_directories(/opt/vc/include/interface/vmcs_host)
include_directories(/opt/vc/include)



find_package (Threads)
FIND_LIBRARY(MMAL_CORE_LIBRARY mmal_core /opt/vc/lib)
FIND_LIBRARY(MMAL_UTIL_LIBRARY mmal_util /opt/vc/lib)
FIND_LIBRARY(MMAL_VC_CLIENT_LIBRARY mmal_vc_client /opt/vc/lib)
FIND_LIBRARY(VCOS_LIBRARY vcos /opt/vc/lib)
FIND_LIBRARY(BCM_HOST_LIBRARY bcm_host /opt/vc/lib)
FIND_LIBRARY(WIRINGPI_LIBRARIES NAMES wiringPi)



set (COMMON_SOURCES
   RaspiCamControl.c
   RaspiPreview.c
   RaspiHelpers.c)


add_executable(take_picture  ${COMMON_SOURCES} take_picture.c DHT22.c)


target_link_libraries(take_picture
     ${MMAL_CORE}
     ${MMAL_CORE_LIBRARY}
     ${MMAL_UTIL_LIBRARY}
     ${MMAL_VC_CLIENT_LIBRARY}
     ${VCOS_LIBRARY}
     ${BCM_HOST_LIBRARY}
     ${CMAKE_THREAD_LIBS_INIT}
     ${WIRINGPI_LIBRARIES}
     m #libm
     )

INCLUDE(cmake_env_vars.txt)

install(TARGETS take_picture DESTINATION /usr/local/bin)


