#import PyTango


#import smc100_new as smc100lib
from smc100_new import SMCMotorHW

from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, DefaultValue, Description

class SMCBaseMotorController(MotorController):
    organization = "IAIE"
    gender = "Motor"
    model = "SMC100"
    state = ""
    status = ""


    # The properties used to connect to the SMC100 motor controller
    ctrl_properties = {
                 'Port' : { Type : str,
                            Description : 'port name',
                            DefaultValue: '/dev/ttyUSB0' }
             }

    axis_attributes = \
             {
                 'lower_limit' : { Type : float,
                            Description : 'motor lower limit, mm',
                            DefaultValue: 2 },
                 'upper_limit' : { Type : float,
                            Description : 'motor upper limit, mm',
                            DefaultValue: 20 },
                 'revision' : { Type : str,
                            Description : 'name of motor controller',
                            DefaultValue: 'None' }
             }




    MaxDevice = 128

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        super(SMCBaseMotorController, self).__init__(
            inst, props, *args, **kwargs)
        self._log.info('SMC100 Motor Controller Initialization ...')
        self.smc100 = SMCMotorHW(self.Port)
        print('Init: SUCCESS')
#        print(self.lower_limit,self.upper_limit)

        # do some initialization
        self.attributes = {}
        self._motors = {}
        self._isMoving = None
        self._moveStartTime = None
#        self._threshold = 0.05
#        self._target = None
        self._timeout = 10


    def AddDevice(self, axis):
        self.attributes[axis] = {}
#        self.attributes[position_value] = None
        self.attributes[axis]['step_per_unit'] = 0
        self.attributes[axis]['step_per_unit_set'] = False
        self.attributes[axis]['lower_limit'] = 2
        self.attributes[axis]['upper_limit'] = 20
        self.attributes[axis]['offset'] = 0
        self.attributes[axis]['revision'] = self.smc100.getRevision(axis)
#        print(self.attributes[axis]['revision'])
#        print(self.smc100.getRevision(axis))
        self._motors[axis] = True

    def DeleteDevice(self, axis):
        self.attributes.pop(axis)
        del self._motors[axis]

    StateMap = {
        1: State.On,
        2: State.Moving,
        3: State.Fault,
    }


    def ReadOne(self, axis):
        """Get the specified motor position"""
        return self.smc100.getPosition(axis)

    def StateOne(self, axis):
        """Get the specified motor state"""
        state = self.smc100.getState(axis)
        if state == 1:
            return State.On, "Motor in target position"
        elif state == 2:
            return State.Moving, "Motor is moving"
        elif state == 3:
            return State.Unknown, "Unknown state"

    def StartOne(self, axis, position):
        """Move the specified motor to the specified position"""
        low = self.attributes[axis]['lower_limit']
        upp = self.attributes[axis]['upper_limit']
#        offset = self.attributes[axis]['offset']

#        new_position = position
#        if(offset>=0):
#            new_position = position + offset
#        print(position)
#        print(new_position)
#        print(offset)
        if(position < low or position > upp):
            raise ValueError('Invalid position: exceed lower or upper limit')
        self.smc100.move(axis, position, waitStop=False) #we dont want to wait until reach position...

    def StopOne(self, axis):
        """Stop the specified motor"""
        self.smc100.stop(axis)

    def SendToCtrl(self, cmd):
        """
        Send custom native commands. The cmd is a space separated string
        containing the command information. Parsing this string one gets
        the command name and the following are the arguments for the given
        command i.e.command_name, [arg1, arg2...]
        :param cmd: string
        :return: string (MANDATORY to avoid OMNI ORB exception)
        """
        response = '' #SendToCtrl must return String, not documented well
        # Get the process to send
        mode = cmd.split(' ')[0].lower()
        args = cmd.strip().split(' ')[1:]

        if mode == 'homing':
            try:
                if len(args) == 2:
                    axis, direction = args
                    axis = int(axis)
                    direction = int(direction)
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)
#            self._log.info('Starting homing for axis {:d} in direction id {:d}'.format(axis, direction))
            self._log.info('Starting homing for axis {:d}'.format(axis))
            try:
                self.smc100.home(axis)
#                if direction == 0:
#                    self.axis_extra_pars[axis]['Proxy'].command_inout("homing_minus")
#                else:
#                    self.axis_extra_pars[axis]['Proxy'].command_inout("homing_plus")
            except Exception as e:
                self._log.error(e)
        elif mode == 'revision':
            try:
                if len(args) == 1:
                    axis, = args
                    axis = int(axis)
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)
            response = self.smc100.getRevision(axis)

        return response

    def SetAxisPar(self, axis, name, value):
        """ Set the standard pool motor parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        par_name = name.lower()
        spu = float(value)

        if par_name == 'step_per_unit':
            self.attributes[axis]['step_per_unit_set'] = True
            self.attributes[axis]['step_per_unit'] = spu
        elif name == 'acceleration':
            self.smc100.setAcceleration(axis, spu)
        elif name == 'velocity':
            self.smc100.setVelocity(axis, spu)
        elif name == 'offset':
            self.attributes[axis]['offset'] = spu

#        elif name == 'lower_limit':
#            self.attributes[axis]['lower_limit'] = float(value)
#        elif name == 'upper_limit':
#            self.attributes[axis]['upper_limit'] = float(value)


    def GetAxisPar(self, axis, name):
        """ Get the standard pool motor parameters.
        @param axis to get the parameter
        @param name of the parameter to get the value
        @return the value of the parameter
        """
        par_name = name.lower()
        if par_name == 'step_per_unit':
            value = self.attributes[axis]['step_per_unit']
        elif name == 'acceleration':
            value = self.smc100.getAcceleration(axis)
        elif name == 'velocity':
            value = self.smc100.getVelocity(axis)
        elif name == 'offset':
            value = self.attributes[axis]['offset']
        return value

    def GetAxisExtraPar(self, axis, name):
        par_name = name.lower()
        if par_name == 'lower_limit':
            value = self.attributes[axis]['lower_limit']
        elif par_name == 'upper_limit':
            value = self.attributes[axis]['upper_limit']
        elif par_name == 'revision':
            value = self.attributes[axis]['revision']
#            value = self.smc100.getRevision(axis)
        return value



    def SetAxisExtraPar(self, axis, name, value):
        par_name = name.lower()
        if par_name == 'lower_limit':
            self.attributes[axis]['lower_limit'] = float(value)
        elif par_name == 'upper_limit':
            self.attributes[axis]['upper_limit'] = float(value)
        elif par_name == 'revision':
            pass
#            self.attributes[axis]['revision'] = str(value)





# Tests #####################################################################
#def test_sardana():
#  inst = PyTango.DeviceProxy("sardana/motor1/1")
#  inst = SardanaDevice("sardana/motor1/1")

#  print(inst.ping())
#  print(inst.state())
#  smc100 = SMCBaseMotorController(inst,{})

  
#  print(smc100.StateOne(axis=1))
  
  #smc100.StartOne(axis=1, position=1, waitStop=False)
#  print("pos=", smc100.getPosition(axis=1))
#  print(smc100.getState(axis=1))
#  smc100.stop(axis=1)
#  print("pos=", smc100.getPosition(axis=1))


