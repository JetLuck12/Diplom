from main_computer import MainComputer
import json
from Utils.MQTTCmdMessage import MQTTCmdMessage
import time

class Calibrator:
    def __init__(self, main_computer : MainComputer, diod_axis : int = -1):
        """
        Инициализация калибровщика.

        :param main_computer: Ссылка на центральный клиент
        :param diod_axis: Ось фотодиода
        """
        self.main = main_computer
        self.diod_axis = diod_axis

    def calibrate(self, len):
        """
        Запускает процесс калибровки.
        """

        """Get max limit"""
        msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_params", [self.diod_axis, "upper_limit"])
        response = self.main.handlers["smc"].send_inner_command(msg)
        max_pos = response["data"]["param"]

        """Get min limit"""
        msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_params", [self.diod_axis, "lower_limit"])
        response = self.main.handlers["smc"].send_inner_command(msg)
        min_pos = response["data"]["param"]

        """Go to min"""
        to_zero = MQTTCmdMessage("smc/commands", "smc", "move", [self.diod_axis, min_pos])
        self.main.handlers["smc"].send_command(to_zero)

        """Check pos while not min"""
        msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_position", [self.diod_axis])
        position = self.main.handlers["smc"].send_inner_command(msg)
        while (self.main.handlers["smc"].send_inner_command(msg)["data"]["position"] > min_pos + 0.5):
            time.sleep(0.5)

        """Go to max and check intensity"""
        to_max = MQTTCmdMessage("smc/commands", "smc", "move", [self.diod_axis, max_pos])
        self.main.handlers["smc"].send_command(to_max)
        max_intensity = 0
        max_int_pos = -1
        temp_int = self.main.handlers["lcard"].get_data()
        while (position["data"]["position"] < max_pos - 0.5):
            position = self.main.handlers["smc"].get_axis_pos(self.diod_axis)
            temp_int = self.main.handlers["lcard"].get_data()
            if temp_int > max_intensity:
                max_intensity = temp_int
                max_int_pos = position
        msg = MQTTCmdMessage("smc/inner_commands", "smc", "move", [self.diod_axis, max_int_pos])
        self.main.handlers["smc"].send_command(msg)


        def calibrate_axis(axis, len):
            """Get max limit"""
            msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_params", [axis, "upper_limit"])
            response = self.main.handlers["smc"].send_inner_command(msg)
            max_pos = response["data"]["param"]

            """Get min limit"""
            msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_params", [axis, "lower_limit"])
            response = self.main.handlers["smc"].send_inner_command(msg)
            min_pos = response["data"]["param"]

            """Go to min"""
            to_zero = MQTTCmdMessage("smc/commands", "smc", "move", [axis, min_pos])
            self.main.handlers["smc"].send_command(to_zero)

            """Check pos while not min"""
            msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_position", [axis])
            position = self.main.handlers["smc"].send_inner_command(msg)
            while (self.main.handlers["smc"].send_inner_command(msg)["data"]["position"] > min_pos + 0.5):
                time.sleep(0.5)

            """Go to max and check intensity"""
            to_max = MQTTCmdMessage("smc/commands", "smc", "move", [axis, max_pos])
            self.main.handlers["smc"].send_command(to_max)
            temp_int = self.main.handlers["lcard"].get_data()
            half_int = max_intensity / 2
            while (position["data"]["position"] < max_pos - 0.5):
                position = self.main.handlers["smc"].get_axis_pos(axis)
                temp_int = self.main.handlers["lcard"].get_data()
                if temp_int < half_int:
                    break
            msg = MQTTCmdMessage("smc/commands", "smc", "move", [axis, min_pos])
            self.main.handlers["smc"].send_command(msg)
            return position

        """calibrate axes and write positions"""

        positions = {}
        for axis in self.main.handlers["smc"].axes:
            if axis != self.diod_axis:
                positions[axis] = calibrate_axis(axis, len/2)

        """move axes on positions"""

        for (axis, pos) in positions.items():
            msg = MQTTCmdMessage("smc/commands", "smc", "move", [axis, pos])
            self.main.handlers["smc"].send_command(msg)

    def save_configuration(self, file_path):
        """
        Сохраняет текущие позиции моторов и фотодиода в конфигурационный файл.

        :param file_path: Путь к файлу для сохранения конфигурации.
        """
        config = {"SMC": {"Knives": [], "Photodiod": []}}

        motor_axes = self.main.handlers["smc"].axes
        # Опрос моторов (Knives)
        for axis in motor_axes:
            if axis == self.diod_axis:
                continue
            msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_position", [axis])
            response = self.main.handlers["smc"].send_inner_command(msg)
            if response is not None:
                config["SMC"]["Knives"].append({"Axis": axis, "Pos": response["data"]["position"]})

        # Опрос фотодиода
        if self.diod_axis != -1:
            msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_position", [axis])
            response = self.main.handlers["smc"].send_inner_command(msg)
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
