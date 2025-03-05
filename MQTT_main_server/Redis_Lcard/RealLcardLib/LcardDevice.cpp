#include "LcardDevice.h"
#include <iostream>
#include "ltrapi.h"
#include "ltr114api.h"


#define SIZE 1

void init_photodiod(TLTR114* ltr1) {
    printf("start initialization");
    fflush(stdout);
    TLTR ltr;
    int error = LTR_Init(&ltr);
    if (error) {
        printf("Init Error with code: %d", error);
        return ;
    }
    error = LTR_OpenSvcControl(&ltr, LTRD_ADDR_DEFAULT, LTRD_PORT_DEFAULT);
    if (error) {
        printf("OpenSvcControl Error with code: %d", error);
        return ;
    }

    BYTE crates[LTR_CRATES_MAX][LTR_CRATE_SERIAL_SIZE];

    error = LTR_GetCrates(&ltr, *crates);
    if (error) {
        printf("LTR_GetCrates Error with code: %d", error);
        LTR_Close(&ltr);
        return ;
    }

    TLTR crate;

    error = LTR_Init(&crate);
    if (error) {
        printf("Init Error with code: %d", error);
        LTR_Close(&ltr);
        return ;
    }

    error = LTR_OpenCrate(&crate, LTRD_ADDR_DEFAULT, LTRD_PORT_DEFAULT, LTR_CRATE_IFACE_USB, (const char*)crates[0]);
    if (error) {
        printf("LTR_OpenCrate Error with code: %d", error);
        LTR_Close(&ltr);
        return ;
    }
    WORD mid[LTR_MODULES_PER_CRATE_MAX];
    error = LTR_GetCrateModules(&crate, mid);
    if (error) {
        printf("GetCrateModules Error with code: %d", error);
        LTR_Close(&ltr);
        return ;
    }
    LTR_Close(&ltr);
    //ltr1 = new TLTR114;
    error = LTR114_Init(ltr1);
    if (error) {
        printf("LTR114_Init Error with code: %d", error);
        return ;
    }
    error = LTR114_Open(ltr1, SADDR_DEFAULT, SPORT_DEFAULT, (const char*)crates[0], CC_MODULE1);
    if (error) {
        printf("LTR114_Open Error with code: %d", error);
        return ;
    }
    error = LTR114_GetConfig(ltr1);
    if (error) {
        printf("LTR114_GetConfig Error with code: %d", error);
        LTR114_Close(ltr1);
        return ;
    }
    error = LTR114_SetADC(ltr1);
    if (error) {
        printf("LTR114_SetADC Error with code: %d", error);
        LTR114_Close(ltr1);
        return ;
    }

    ltr1->FreqDivider = 4;

    error = LTR114_Calibrate(ltr1);
    if (error) {
        printf("LTR114_Calibrate Error with code: %d", error);
        LTR114_Close(ltr1);
        return ;
    }
}

float get_ltr_data(TLTR114* ltr)
{
    int array_size = 1;
    DWORD* data = new DWORD[sizeof(DWORD)*SIZE*ltr->FrameLength];
    double dest[100];

    int error  = LTR114_GetFrame(ltr, data);
    if (error < 0) {
        printf("LTR114_GetFrame Error with code: %d", error);
        LTR114_Close(ltr);
        LTR114_Stop(ltr);

        return 1;
    }
    else if (error > 0) {
        error = LTR114_ProcessData(ltr, data, dest, &array_size, LTR114_CORRECTION_MODE_INIT, LTR114_PROCF_VALUE);
        if (error < 0) {
            printf("LTR114_ProcessData Error with code: %d", error);
            LTR114_Close(ltr);
            LTR114_Stop(ltr);

            return 1;
        }
    }
    else{
        printf("No data in LTR114_Recv : %d", error);
    }
    delete[] data;
    return dest[0];
}

LcardDevice::LcardDevice() : ltr(nullptr) {}

// Инициализация устройства
bool LcardDevice::init() {
    ltr = new TLTR114;
    init_photodiod(ltr);
    if (ltr == nullptr) {
        std::cerr << "Failed to initialize the real device.\n";
        return false;
    }
    return true;
}

// Запуск устройства
void LcardDevice::start() {
    return;
}

// Получение данных с устройства
float LcardDevice::get_data() {
    float res = 0.5;
    try {
        res = get_ltr_data(ltr);
    }
    catch (std::exception& e){
        std::cerr << e.what() << std::endl;
    }
    return res;
}

// Остановка устройства
void LcardDevice::stop() {
    if (LTR114_Stop(ltr) != 0) {
        std::cerr << "Failed to stop the device.\n";
    }
    if (LTR114_Close(ltr) != 0) {
        std::cerr << "Failed to close the device.\n";
    }
}

std::unique_ptr<DeviceInterface> create_real_device() {
    return std::make_unique<LcardDevice>();
}
