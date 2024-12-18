#include "LcardDevice.h"
#include <iostream>
#include "Lcard_packs/include/ltrapi.h"
#include "Lcard_packs/include/ltr114api.h"


#define SIZE 1

PTLTR114 init_photodiod() {
    printf("start initialization");
    fflush(stdout);
    TLTR ltr;
    int error = LTR_Init(&ltr);
    if (error) {
        printf("Init Error with code: %d", error);
        return NULL;
    }
    error = LTR_OpenSvcControl(&ltr, LTRD_ADDR_DEFAULT, LTRD_PORT_DEFAULT);
    if (error) {
        printf("OpenSvcControl Error with code: %d", error);
        return NULL;
    }

    BYTE crates[LTR_CRATES_MAX][LTR_CRATE_SERIAL_SIZE];

    error = LTR_GetCrates(&ltr, *crates);
    if (error) {
        printf("LTR_GetCrates Error with code: %d", error);
        LTR_Close(&ltr);
        return NULL;
    }

    TLTR crate;

    error = LTR_Init(&crate);
    if (error) {
        printf("Init Error with code: %d", error);
        LTR_Close(&ltr);
        return NULL;
    }

    error = LTR_OpenCrate(&crate, LTRD_ADDR_DEFAULT, LTRD_PORT_DEFAULT, LTR_CRATE_IFACE_USB, (const char*)crates[0]);
    if (error) {
        printf("LTR_OpenCrate Error with code: %d", error);
        LTR_Close(&ltr);
        return NULL;
    }
    WORD mid[LTR_MODULES_PER_CRATE_MAX];
    error = LTR_GetCrateModules(&crate, mid);
    if (error) {
        printf("GetCrateModules Error with code: %d", error);
        LTR_Close(&ltr);
        return NULL;
    }
    LTR_Close(&ltr);
    TLTR114* LTR114_array[LTR_MODULES_PER_CRATE_MAX];
    for (int i = 0; i < LTR_MODULES_PER_CRATE_MAX; i++) {
        if (mid[i] == LTR_MID_EMPTY) {
            continue;
        }
        TLTR114 ltr1;
        error = LTR114_Init(&ltr1);
        if (error) {
            printf("LTR114_Init Error with code: %d", error);
            return NULL;
        }
        error = LTR114_Open(&ltr1, SADDR_DEFAULT, SPORT_DEFAULT, (const char*)crates[0], CC_MODULE1);
        if (error) {
            printf("LTR114_Open Error with code: %d", error);
            return NULL;
        }
        LTR114_array[i] = &ltr1;
        error = LTR114_GetConfig(&ltr1);
        if (error) {
            printf("LTR114_GetConfig Error with code: %d", error);
            LTR114_Close(&ltr1);
            return NULL;
        }

    }
    error = LTR114_SetADC(LTR114_array[0]);
    if (error) {
        printf("LTR114_SetADC Error with code: %d", error);
        LTR114_Close(LTR114_array[0]);
        return NULL;
    }

    LTR114_array[0]->FreqDivider = 4;

    error = LTR114_Calibrate(LTR114_array[0]);
    if (error) {
        printf("LTR114_Calibrate Error with code: %d", error);
        LTR114_Close(LTR114_array[0]);
        return NULL;
    }

    error = LTR114_Start(LTR114_array[0]);
    if (error) {
        printf("LTR114_Start Error with code: %d", error);
        LTR114_Close(LTR114_array[0]);
        return NULL;
    }
    return LTR114_array[0];
}

float get_ltr_data(TLTR114* ltr)
{
    int array_size = 1;

    DWORD data[SIZE];
    double dest[1];

    int error = LTR114_Recv(ltr, data, NULL, ltr->FrameLength, 100);
    if (error < 0) {
        printf("LTR114_Recv Error with code: %d", error);
        LTR114_Close(ltr);
        LTR114_Stop(ltr);

        return 1;
    }
    if (error > 0) {
        error = LTR114_ProcessData(ltr, data, dest, &array_size, LTR114_CORRECTION_MODE_INIT, LTR114_PROCF_VALUE);
        if (error < 0) {
            printf("LTR114_ProcessData Error with code: %d", error);
            LTR114_Close(ltr);
            LTR114_Stop(ltr);

            return 1;
        }
    }
    else if (error < 0) {
        printf("LTR114_ProcessData Error with code: %d", error);
        LTR114_Close(ltr);
        LTR114_Stop(ltr);

        return 1;
    }
    else{
        printf("No data in LTR114_Recv : %d", error);
    }
    return dest[0];
}

LcardDevice::LcardDevice() : ltr(nullptr) {}

// Инициализация устройства
bool LcardDevice::init() {
    ltr = init_photodiod();
    if (ltr == nullptr) {
        std::cerr << "Failed to initialize the real device.\n";
        return false;
    }
    return true;
}

// Запуск устройства
void LcardDevice::start() {
    if (LTR114_Start(ltr) != 0) {
        std::cerr << "Failed to start the device.\n";
    }
}

// Получение данных с устройства
float LcardDevice::get_data() {
    return get_ltr_data(ltr);
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
