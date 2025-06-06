#import PyTango


#import smc100_new as smc100lib
from smc100 import SMC100
import serial

class SMCBaseMotorController():
    def __init__(self, port="COM3", num_devices=16):
        self.port = port
        self.motors = {}

        self._port = serial.Serial(
            port = port,
            baudrate = 57600,
            bytesize = 8,
            stopbits = 1,
            parity = 'N',
            xonxoff = True,
            timeout = 0.050)

        for axis in range(1, num_devices+1):
            try:
                motor = SMC100(smcID=axis, _port=self._port)
                motor.reset_and_configure()

                self.motors[str(axis)] = motor

                print(f"[INIT] Motor {axis} initialized on {port}")
            except Exception as e:
                print(f"[WARN] Failed to initialize motor {axis}: {e}")

    def StartOne(self, axis, position):
        self._get_motor(axis).move_absolute_um(position)

    def Home(self, axis):
        self._get_motor(axis).home()

    def StopOne(self, axis):
        self._get_motor(axis).stop()

    def StateOne(self, axis):
        motor = self._get_motor(axis)
        return (motor.get_position_um(), motor.get_status())

    def ReadOne(self, axis):
        return self._get_motor(axis).get_position_um()

    def _get_motor(self, axis):
        if axis not in self.motors:
            raise ValueError(f"Motor with axis ID {axis} not found")
        return self.motors[axis]
