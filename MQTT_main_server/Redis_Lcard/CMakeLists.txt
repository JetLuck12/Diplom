cmake_minimum_required(VERSION 3.5)
set(CMAKE_CXX_STANDARD 17)
project(Redis_LCard LANGUAGES CXX)

set(CMAKE_PREFIX_PATH "C:/Qt/5.15.2/msvc2019/lib/cmake")
set(LCARD_DIR "C:/Qt/Labs/Diplom/MQTT_main_server/Redis_LCard/Lcard_packs")
set(MOSQUITTO_DIR "C:/Program Files/mosquitto/devel")

add_executable(Redis_LCard main.cpp
    MockDevice.cpp MockDevice.h
    DeviceInterface.h
    LcardDevice.cpp LcardDevice.h
    mqtthandler.h mqtthandler.cpp
    devicemanager.h devicemanager.cpp
    json.hpp)

# Укажите путь к заголовочным файлам
include_directories(${LCARD_DIR}/include)
include_directories(${MOSQUITTO_DIR})


# Укажите путь к файлам библиотеки
link_directories(${LCARD_DIR}/lib/msvc)
link_directories(${MOSQUITTO_DIR})

target_link_libraries(Redis_LCard
    "${LCARD_DIR}/lib/msvc64/ltrapi.lib"
    "${LCARD_DIR}/lib/msvc64/ltr114api.lib"
    "${MOSQUITTO_DIR}/mosquitto.lib"
)


include(GNUInstallDirs)
install(TARGETS Redis_LCard
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
