import time

class MockSMCMotorHW:
    """Моделируемый контроллер SMC100 с интерфейсом, совпадающим с SMCBaseMotorController."""

    def __init__(self, port="/dev/mock"):
        """Инициализация фиктивного контроллера."""
        self.port = port
        self.devices = {}
        print(f"MockSMCMotorHW initialized on port {self.port}")

    def AddDevice(self, axis):
        """Добавляет устройство (ось)."""
        self.devices[axis] = {
            "position": 0.0,
            "state": "On",
            "lower_limit": 2.0,
            "upper_limit": 20.0,
            "step_per_unit": 1.0,
            "acceleration": 1.0,
            "velocity": 1.0,
            "offset": 0.0,
            "revision": f"MockRevision-{axis}"
        }
        print(f"Device {axis} added.")

    def DeleteDevice(self, axis):
        """Удаляет устройство (ось)."""
        if axis in self.devices:
            del self.devices[axis]
            print(f"Device {axis} deleted.")
        else:
            print(f"Device {axis} does not exist.")

    def ReadOne(self, axis):
        """Возвращает текущую позицию оси."""
        if axis in self.devices:
            position = self.devices[axis]["position"]
            print(f"Read position for axis {axis}: {position}")
            return position
        else:
            raise ValueError(f"Axis {axis} not found.")

    def StateOne(self, axis):
        """Возвращает состояние оси."""
        if axis in self.devices:
            state = self.devices[axis]["state"]
            if state == "On":
                return 1, "Motor in target position"
            elif state == "Moving":
                return 2, "Motor is moving"
            elif state == "Fault":
                return 3, "Fault state"
            return 0, "Unknown state"
        else:
            raise ValueError(f"Axis {axis} not found.")

    def StartOne(self, axis, position):
        """Начинает движение оси к заданной позиции."""
        if axis in self.devices:
            device = self.devices[axis]
            if position < device["lower_limit"] or position > device["upper_limit"]:
                raise ValueError(f"Position {position} is out of limits for axis {axis}.")
            print(f"Axis {axis} moving to position {position}...")
            device["state"] = "Moving"
            time.sleep(0.5)  # Имитация движения
            device["position"] = position
            device["state"] = "On"
            print(f"Axis {axis} reached position {position}.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def StopOne(self, axis):
        """Останавливает движение оси."""
        if axis in self.devices:
            device = self.devices[axis]
            if device["state"] == "Moving":
                device["state"] = "On"
                print(f"Axis {axis} stopped.")
            else:
                print(f"Axis {axis} is not moving.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def SendToCtrl(self, cmd):
        """
        Выполняет отправку команды контроллеру (имитация).
        Возвращает фиктивный ответ.
        """
        print(f"Command sent to controller: {cmd}")
        if cmd.lower().startswith("revision"):
            return "MockRevision-Response"
        return "MockResponse"

    def SetAxisPar(self, axis, name, value):
        """Устанавливает параметр для указанной оси."""
        if axis in self.devices:
            if name in self.devices[axis]:
                self.devices[axis][name] = value
                print(f"Set {name} to {value} for axis {axis}.")
            else:
                raise ValueError(f"Parameter {name} not found for axis {axis}.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def GetAxisPar(self, axis, name):
        """Возвращает значение параметра для указанной оси."""
        if axis in self.devices:
            if name in self.devices[axis]:
                value = self.devices[axis][name]
                print(f"Get {name} for axis {axis}: {value}")
                return value
            else:
                raise ValueError(f"Parameter {name} not found for axis {axis}.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def GetAxisExtraPar(self, axis, name):
        """Возвращает значение дополнительного параметра для оси."""
        return self.GetAxisPar(axis, name)

    def SetAxisExtraPar(self, axis, name, value):
        """Устанавливает значение дополнительного параметра для оси."""
        self.SetAxisPar(axis, name, value)
