# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:42:49 2019

@author: schaecl
"""

import ctypes
import os
import types

# List of error types, manually imported from the header file anc350.h
ANC_Ok = 0            # No error
ANC_Error = -1        # Unknown / other error
ANC_Timeout = 1       # Timeout during data retrieval
ANC_NotConnected = 2  # No contact with the positioner via USB
ANC_DriverError = 3   # Error in the driver response
ANC_DeviceLocked = 7  # A connection attempt failed because the device is already in use
ANC_Unknown = 8       # Unknown error
ANC_NoDevice = 9      # Invalid device number used in call
ANC_NoAxis = 10       # Invalid axis number in function call
ANC_OutOfRange = 11   # Parameter in call is out of range
ANC_NotAvailable = 12 # Function not available for device type
ANC_FileError = 13    # Error opening or interpreting a file

def checkError(code, func, args):
    """
    Translates the errors returned from the dll.

    Parameters
    ----------
    code : int
        Return value
    func : function
        Function that is called
    args : list
        Paramaters passed to the function
    """
    assert str(type(func)) == "<class 'ctypes.CDLL.__init__.<locals>._FuncPtr'>"
    if code == ANC_Ok:
        pass
    elif code == ANC_Error:
        raise RuntimeError("Error: unspecific in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_Timeout:
        raise RuntimeError("Error: timeout in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_NotConnected:
        raise RuntimeError("Error: not connected in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_DriverError:
        raise RuntimeError("Error: driver error in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_DeviceLocked:
        raise RuntimeError("Error: device locked in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_NoDevice:
        raise RuntimeError("Error: invalid device number in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_NoAxis:
        raise RuntimeError("Error: invalid axis number in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_OutOfRange:
        raise RuntimeError("Error: parameter out of range in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_NotAvailable:
        raise RuntimeError("Error: function not available in " + str(func.__name__) + " with parameters: " + str(args))
    elif code == ANC_FileError:
        raise RuntimeError("Error: file not available in " + str(func.__name__) + " with parameters: " + str(args))
    else:
        raise RuntimeError("Error: unknown in " + str(func.__name__) + " with parameters: " + str(args))
    return code

# Import dll. Pay attention to have libusb0 available too.
root_path = os.path.dirname(os.path.realpath(__file__))

if os.name == 'nt': # Windows
    lib_path = os.path.join(root_path, 'win64')
    lib = os.path.join(lib_path, 'anc350v4.dll')
    if not os.path.isfile(lib):
        raise FileNotFoundError('Error: can not find win64\anc350v4.dll')
    anc350v4 = ctypes.cdll.LoadLibrary(lib)
else: # Assume Linux-like
    lib_path = os.path.join(root_path, 'linux64')
    lib = os.path.join(lib_path, 'libanc350v4.so')
    if not os.path.isfile(lib):
        raise FileNotFoundError('Error: can not find linux\anc350v4.so')
    anc350v4 = ctypes.cdll.LoadLibrary(lib)

# Aliases for the functions from the dll
discover = getattr(anc350v4, "ANC_discover")
getDeviceInfo = getattr(anc350v4, "ANC_getDeviceInfo")
connect = getattr(anc350v4, "ANC_connect")
disconnect = getattr(anc350v4, "ANC_disconnect")
getDeviceConfig = getattr(anc350v4, "ANC_getDeviceConfig")
getAxisStatus = getattr(anc350v4, "ANC_getAxisStatus")
setAxisOutput = getattr(anc350v4, "ANC_setAxisOutput")
setAmplitude = getattr(anc350v4, "ANC_setAmplitude")
setFrequency = getattr(anc350v4, "ANC_setFrequency")
setDcVoltage = getattr(anc350v4, "ANC_setDcVoltage")
getAmplitude = getattr(anc350v4, "ANC_getAmplitude")
getFrequency = getattr(anc350v4, "ANC_getFrequency")
startSingleStep = getattr(anc350v4, "ANC_startSingleStep")
startContinousMove = getattr(anc350v4, "ANC_startContinousMove")
startAutoMove = getattr(anc350v4, "ANC_startAutoMove")
setTargetPosition = getattr(anc350v4, "ANC_setTargetPosition")
setTargetRange = getattr(anc350v4, "ANC_setTargetRange")
getPosition = getattr(anc350v4, "ANC_getPosition")
getFirmwareVersion = getattr(anc350v4, "ANC_getFirmwareVersion")
configureExtTrigger = getattr(anc350v4, "ANC_configureExtTrigger")
configureAQuadBIn = getattr(anc350v4, "ANC_configureAQuadBIn")
configureAQuadBOut = getattr(anc350v4, "ANC_configureAQuadBOut")
configureRngTriggerPol = getattr(anc350v4, "ANC_configureRngTriggerPol")
configureRngTrigger = getattr(anc350v4, "ANC_configureRngTrigger")
configureRngTriggerEps = getattr(anc350v4, "ANC_configureRngTriggerEps")
configureNslTrigger = getattr(anc350v4, "ANC_configureNslTrigger")
configureNslTriggerAxis = getattr(anc350v4, "ANC_configureNslTriggerAxis")
selectActuator = getattr(anc350v4, "ANC_selectActuator")
getActuatorName = getattr(anc350v4, "ANC_getActuatorName")
getActuatorType = getattr(anc350v4, "ANC_getActuatorType")
measureCapacitance = getattr(anc350v4, "ANC_measureCapacitance")
saveParams = getattr(anc350v4, "ANC_saveParams")

# Set error checking & handling
discover.errcheck = checkError
connect.errcheck = checkError
disconnect.errcheck = checkError
getDeviceConfig.errcheck = checkError
getAxisStatus.errcheck = checkError
setAxisOutput.errcheck = checkError
setAmplitude.errcheck = checkError
setFrequency.errcheck = checkError
setDcVoltage.errcheck = checkError
getAmplitude.errcheck = checkError
getFrequency.errcheck = checkError
startSingleStep.errcheck = checkError
startContinousMove.errcheck = checkError
startAutoMove.errcheck = checkError
setTargetPosition.errcheck = checkError
setTargetRange.errcheck = checkError
getPosition.errcheck = checkError
getFirmwareVersion.errcheck = checkError
configureExtTrigger.errcheck = checkError
configureAQuadBIn.errcheck = checkError
configureAQuadBOut.errcheck = checkError
configureRngTriggerPol.errcheck = checkError
configureRngTrigger.errcheck = checkError
configureRngTriggerEps.errcheck = checkError
configureNslTrigger.errcheck = checkError
configureNslTriggerAxis.errcheck = checkError
selectActuator.errcheck = checkError
getActuatorName.errcheck = checkError
getActuatorType.errcheck = checkError
measureCapacitance.errcheck = checkError
saveParams.errcheck = checkError
