##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This is the demo macro module"""



__all__ = ["smc_init"]

import PyTango

from sardana.macroserver.macro import macro, Type
from sardana.macroserver.msexception import UnknownEnv

_ENV = "_SMC_INIT"


def get_free_names(db, prefix, nb, start_at=1):
    ret = []
    i = start_at
    failed = 96
    while len(ret) < nb and failed > 0:
        name = "%s%02d" % (prefix, i)
        try:
            db.get_device_alias(name)
            failed -= 1
        except:
            ret.append(name)
        i += 1
    if len(ret) < nb or failed == 0:
        raise Exception("Too many sardana demos registered on this system.\n"
                        "Please try using a different tango system")
    return ret



@macro()
def smc_init(self):
    """Sets up a SMC environment."""

    try:
        SMC_INIT = self.getEnv(_ENV)
        self.unsetEnv(_ENV)#FIX ME!
        self.error("A demo has already been prepared on this sardana")
        return
    except:
        pass

    db = PyTango.Database()

    mot_ctrl_name = get_free_names(db, "smc_motctrl", 1)[0]

    motor_names = get_free_names(db, "smc_mot", 11)

#    gap, offset = get_free_names(db, "gap", 1) + \
#        get_free_names(db, "offset", 1)
        
    pools = self.getPools()
    if not len(pools):
        self.error('This is not a valid sardana demonstration system.\n'
                   'Sardana demonstration systems must be connect to at least '
                   'one Pool')
        return
    pool = pools[0]

    self.print("Creating motor controller", mot_ctrl_name, "...")
 #   self.defctrl("DummyMotorController", mot_ctrl_name)
    self.defctrl("SMCBaseMotorController", mot_ctrl_name)
    
    for axis, motor_name in enumerate(motor_names, 1):
        self.print("Creating motor", motor_name, "...")
        self.defelem(motor_name, mot_ctrl_name, axis)

    self.print("Creating instruments: /slit, /mirror and /monitor ...")
    pool.createInstrument('/slit', 'NXcollimator')
    pool.createInstrument('/mirror', 'NXmirror')


    self.print("Assigning elements to instruments...")
    self.getMotor(motor_names[0]).setInstrumentName('/slit')
    self.getMotor(motor_names[1]).setInstrumentName('/slit')
    self.getMotor(motor_names[2]).setInstrumentName('/mirror')
    self.getMotor(motor_names[3]).setInstrumentName('/mirror')
    self.getMotor(motor_names[4]).setInstrumentName('/slit')
    self.getMotor(motor_names[5]).setInstrumentName('/slit')
    self.getMotor(motor_names[6]).setInstrumentName('/mirror')
    self.getMotor(motor_names[7]).setInstrumentName('/mirror')
    self.getMotor(motor_names[8]).setInstrumentName('/mirror')
    self.getMotor(motor_names[9]).setInstrumentName('/mirror')
    self.getMotor(motor_names[10]).setInstrumentName('/mirror')


    controllers = mot_ctrl_name
    elements = motor_names
    instruments = ["/slit", "/mirror"]
    d = dict(controllers=controllers, elements=elements, instruments=instruments)

    self.setEnv(_ENV, d)

    self.print("DONE!")
    
    
    
@macro()
def clear_smc_init(self):
    """Undoes changes done with sar_demo"""
    try:
        SMC_INIT = self.getEnv(_ENV)
    except:
        self.error("No demo has been prepared yet on this sardana!")
        return

    self.print("Removing elements...")
    elements = SMC_INIT.get("elements", ())
    if len(elements) > 0:
        self.udefelem(elements)

    self.print("Removing controllers...")
    for ctrl in SMC_INIT.get("controllers", ()):
        self.udefctrl(ctrl)

    self.print("Removing instruments...")
    pool = self.getPools()[0]
    for instrument in SMC_INIT.get("instruments", ()):
        pool.DeleteElement(instrument)

    self.unsetEnv(_ENV)

    self.print("DONE!")

    

