cmake_minimum_required(VERSION 3.5)
set(CMAKE_CXX_STANDARD 20)
project(Redis_LCard LANGUAGES CXX)

set(CMAKE_PREFIX_PATH "C:/Qt/5.15.2/msvc2019/lib/cmake")
set(LCARD_DIR "${CMAKE_SOURCE_DIR}/Lcard_packs")
set(MOSQUITTO_DIR "C:/Program Files/mosquitto/devel")
set(INCLUDE_DIRS
    "MockLcardLib"
    "DeviceInterface"
    "RealLcardLib"
    "MQTTHandler"
    "DeviceManager"
    "Utils"
    "Utils/CmdMessage"
    "Utils/RespMessage"
    "Utils/Response"
    "${LCARD_DIR}/include"
    "${MOSQUITTO_DIR}/include"
)


add_executable(Redis_LCard main.cpp
    MockLcardLib/MockDevice.cpp         MockLcardLib/MockDevice.h
    DeviceInterface/DeviceInterface.h
    RealLcardLib/LcardDevice.cpp        RealLcardLib/LcardDevice.h
    MQTTHandler/mqtthandler.h           MQTTHandler/mqtthandler.cpp
    DeviceManager/devicemanager.h       DeviceManager/devicemanager.cpp
    Utils/json.hpp
    Utils/MQTTMessage.h                 Utils/MQTTMessage.cpp
    Utils/Response/IResponse.h
    Utils/Response/dataresponse.h
    Utils/Response/statusresponse.h
    Utils/RespMessage/mqttrespmessage.cpp Utils/RespMessage/mqttrespmessage.h
    Utils/CmdMessage/mqttcmdmessage.cpp Utils/CmdMessage/mqttcmdmessage.h

)

target_include_directories(Redis_LCard PRIVATE ${INCLUDE_DIRS})

# Укажите путь к заголовочным файлам
include_directories(${LCARD_DIR}/include)
include_directories(${MOSQUITTO_DIR})

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
