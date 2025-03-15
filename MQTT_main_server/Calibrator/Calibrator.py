from main_computer import MainComputer
import json
from Utils.MQTTCmdMessage import MQTTCmdMessage

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
                config["SMC"]["Knives"].append({"Axis": axis, "Pos": response["data"]["position"]})

        # Опрос фотодиода
        if self.diod_axis != -1:
            response = self.main.handlers["smc"].get_axis_pos(self.diod_axis)
            if response is not None:
                config["SMC"]["Photodiod"].append({"Axis": self.diod_axis, "Pos": response["data"]["position"]})

        # Запись в файл
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

        print(f"Конфигурация сохранена в {file_path}")

    def load_configuration(self, file_path):
        """Загружает конфигурацию из файла и устанавливает позиции моторов и фотодиода."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                config = json.load(file)

            knives = config.get("SMC", {}).get("Knives", [])
            photodiode = config.get("SMC", {}).get("Photodiod", [])

            if not isinstance(knives, list):
                raise ValueError("'Knives' должно быть списком, а не множеством или другим типом.")

            if not isinstance(photodiode, list):
                raise ValueError("'Photodiod' должно быть списком, а не множеством или другим типом.")

            # Восстановление позиций моторов
            for motor in knives:
                if not isinstance(motor, dict):
                    raise ValueError(f"Ожидался словарь, получено: {type(motor)}")
                msg = MQTTCmdMessage("smc/commands", "smc", "add", [motor["Axis"]])
                self.main.handlers["smc"].send_command(msg)
                msg = MQTTCmdMessage("smc/commands", "smc", "move", [motor["Axis"], motor["Pos"]])
                self.main.handlers["smc"].send_command(msg)

            # Восстановление позиции фотодиода
            for motor in photodiode:
                if not isinstance(motor, dict):
                    raise ValueError(f"Ожидался словарь, получено: {type(motor)}")
                msg = MQTTCmdMessage("smc/commands", "smc", "add", [motor["Axis"]])
                self.main.handlers["smc"].send_command(msg)
                msg = MQTTCmdMessage("smc/commands", "smc", "move", [motor["Axis"], motor["Pos"]])
                self.main.handlers["smc"].send_command(msg)

            print(f"Конфигурация загружена из {file_path}")
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")

    def calibrate_from_configuration(self, file_path):
        """
        Выполняет калибровку установки на основе загруженной конфигурации.

        :param file_path: Путь к файлу с конфигурацией
        """
        pass

