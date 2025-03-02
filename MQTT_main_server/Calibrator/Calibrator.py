from main_computer import MainComputer

class Calibrator:
    def __init__(self, main_computer : MainComputer, diod_axis : int):
        """
        Инициализация калибровщика.

        :param tango_handler: Экземпляр TangoHandler для управления моторами
        :param motor_axes: Список осей моторов (list[int])
        :param photodiode_axis: Ось фотодиода (int)
        :param lcard_handler: Экземпляр LcardHandler для работы с фотодиодом
        """
        self.main = main_computer
        self.diod_axis = diod_axis

    def calibrate(self):
        """
        Запускает процесс калибровки.
        """
        pass

    def save_configuration(self, file_path):
        """
        Сохраняет текущие позиции моторов и фотодиода в конфигурационный файл.

        :param file_path: Путь к файлу для сохранения конфигурации.
        """
        config = {"SMC": {"Knives": [], "Photodiod": []}}

        motor_axes = self.main.handlers["smc"].axes

        # Опрос моторов (Knives)
        for axis in motor_axes:
            response = self.main.handlers["smc"].get_axis_pos(axis)
            if response is not None:
                config["SMC"]["Knives"].append({"Axis": axis, "Pos": response})

        # Опрос фотодиода
        response = self.send_command("pos", self.photodiode_axis, {})
        if response is not None:
            config["SMC"]["Photodiod"].append({"Axis": self.photodiode_axis, "Pos": response})

        # Запись в файл
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

        print(f"Конфигурация сохранена в {file_path}")

    def load_configuration(self, file_path):
        """
        Загружает конфигурацию установки из файла.

        :param file_path: Путь к файлу с конфигурацией
        """
        pass

    def calibrate_from_configuration(self, file_path):
        """
        Выполняет калибровку установки на основе загруженной конфигурации.

        :param file_path: Путь к файлу с конфигурацией
        """
        pass

