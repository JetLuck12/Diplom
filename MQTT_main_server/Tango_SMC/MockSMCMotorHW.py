import time

class MockSMCMotorHW:
    """Моделируемый контроллер SMC100 с интерфейсом, совпадающим с SMCBaseMotorController."""

    def __init__(self, port="COM3", num_devices=16):
        self.port = port
        self.motors = {}

        for axis in range(1, num_devices+1):
            try:
                self.motors[axis] = {
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
                print(f"[INIT] Motor {axis} initialized on {port}")
            except Exception as e:
                print(f"[WARN] Failed to initialize motor {axis}: {e}")


    def ReadOne(self, axis : int):
        """Возвращает текущую позицию оси."""
        if axis in self.motors:
            position = self.motors[axis]["position"]
            print(f"Read position for axis {axis}: {position}")
            return position
        else:
            raise ValueError(f"Axis {axis} not found.")

    def StateOne(self, axis : int):
        """Возвращает состояние оси."""
        if axis in self.motors:
            state = self.motors[axis]["state"]
            if state == "On":
                return 1, "Motor in target position"
            elif state == "Moving":
                return 2, "Motor is moving"
            elif state == "Fault":
                return 3, "Fault state"
            return 0, "Unknown state"
        else:
            raise ValueError(f"Axis {axis} not found.")

    def StartOne(self, axis : int, position : float):
        """Начинает движение оси к заданной позиции."""
        print(f"axis type: {type(axis)}")
        print(f"motor keys: {[type(k) for k in self.motors.keys()]}")
        if axis in self.motors:
            device = self.motors[axis]
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

    def StopOne(self, axis : int):
        """Останавливает движение оси."""
        if axis in self.motors:
            device = self.motors[axis]
            if device["state"] == "Moving":
                device["state"] = "On"
                print(f"Axis {axis} stopped.")
            else:
                print(f"Axis {axis} is not moving.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def Home(self, axis : int):
        """Отправляет в начало."""
        if axis in self.motors:
            device = self.motors[axis]
            print(f"Axis {axis} moving to рщьу")
            device["state"] = "Moving"
            time.sleep(0.5)  # Имитация движения
            device["position"] = device["lower_limit"]
            device["state"] = "On"
            print(f"Axis {axis} reached position {device['lower_limit']}.")
        else:
            raise ValueError(f"Axis {axis} not found.")

    def _get_motor(self, axis : int):
        if axis not in self.motors:
            raise ValueError(f"Motor with axis ID {axis} not found")
        return self.motors[axis]
