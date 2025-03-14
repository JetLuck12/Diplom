from main_computer import MainComputer
import json

class Calibrator:
    def __init__(self, main_computer : MainComputer, diod_axis : int = -1):
        """
        Инициализация калибровщика.

        :param main_computer: Ссылка на центральный клиент
        :param diod_axis: Ось фотодиода
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
        if self.diod_axis != -1:
            response = self.main.handlers["smc"].get_axis_pos(self.diod_axis)
            if response is not None:
                config["SMC"]["Photodiod"].append({"Axis": self.diod_axis, "Pos": response})

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

