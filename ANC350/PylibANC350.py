# -*- coding: utf-8 -*-
'''
Created on Fri Jul  5 16:11:11 2019

@author: Clemens Schaefermeier, attocube systems AG
'''

import ctypes
import os
import warnings
import platform

def ANC_errcheck(code, func, args):
    '''
    Translates the errors returned from the dll functions.

    Parameters
    ----------
    code : int
        Return value from the function
    func : function
        Function that is called
    args : list
        Parameters passed to the function

    Returns
    -------
    code : int
    '''
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

    assert str(type(func)) == "<class 'ctypes.CDLL.__init__.<locals>._FuncPtr'>"

    if code == ANC_Ok:
        pass
    elif code == ANC_Error:
        raise RuntimeError('Error: unspecific error in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_Timeout:
        raise RuntimeError('Error: timeout error in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_NotConnected:
        raise RuntimeError('Error: not connected error in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_DriverError:
        raise RuntimeError('Error: driver error in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_DeviceLocked:
        raise RuntimeError('Error: device locked in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_Unknown:
        raise RuntimeError('Error: unknown error in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_NoDevice:
        raise RuntimeError('Error: invalid device number in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_NoAxis:
        raise RuntimeError('Error: invalid axis number in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_OutOfRange:
        raise RuntimeError('Error: parameter out of range in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_NotAvailable:
        raise RuntimeError('Error: function not available in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    elif code == ANC_FileError:
        raise RuntimeError('Error: file not available in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    else:
        raise RuntimeError('Error: this should not happen in ' +
                           str(func.__name__) +
                           ' with parameters: ' + str(args))
    return code

def load_ANC350dll():
    '''
    Import .dll/.so to communicate with ANC350. Pay attention to have libusb0
    available too for Windows systems.

    Returns
    -------
    anc : ctypes
        Instance of the LoadLibrary method
    '''
    root_path = os.path.dirname(os.path.realpath(__file__))
    lib_name = 'anc350v4'
    bitness = platform.architecture()[0]
    os_name = platform.system()

    if os_name not in ('Windows', 'Linux'):
        RuntimeError('Running only on Windows or Linux OS')
    if bitness not in ('64bit', '32bit'):
        RuntimeError('Can not determine OS bit-ness')

    if os_name == 'Windows':
        # Note: MSVCP100.dll is required to work with the dll
        lib_name_usb = 'libusb0.dll'
        if bitness == '64bit':
            lib_path = os.path.join(root_path, 'win64')
        else:
            lib_path = os.path.join(root_path, 'win32')
        libusb = os.path.join(lib_path, lib_name_usb)
        if not os.path.isfile(libusb):
            raise FileNotFoundError('Error: can not find '
                                    + lib_path + lib_name_usb)
        lib = os.path.join(lib_path, lib_name + '.dll')
        if not os.path.isfile(lib):
            raise FileNotFoundError('Error: can not find '
                                    + lib_path + lib_name + '.dll')
        anc = ctypes.cdll.LoadLibrary(lib)
    else:
        if bitness == '64bit':
            lib_path = os.path.join(root_path, 'linux64')
        else:
            lib_path = os.path.join(root_path, 'linux32')
        lib = os.path.join(lib_path, lib_name + '.so')
        if not os.path.isfile(lib):
            raise FileNotFoundError('Error: can not find '
                                    + lib_path + lib_name + '.so')
        anc = ctypes.cdll.LoadLibrary(lib)

    return anc

def discover_ANC350(ifaces=3):
    '''
    The function searches for connected ANC350RES devices on USB and LAN
    and initialises internal data structures per device. Devices that are
    in use by another application or PC are not found. The function must
    be called *before* connecting to a device and must not be called as
    long as any devices are connected.

    The number of devices found is returned. In subsequent functions,
    devices are identified by a sequence number that must be less than the
    number returned.

    Parameters
    ----------
    ifaces : int
        Interfaces where devices are to be searched.
        {None: 0, USB: 1, ethernet: 2, all: 3} Default: 3

    Returns
    -------
    devCount : int
        Number of devices found
    '''
    anc = load_ANC350dll()

    discover_dll = anc.ANC_discover
    discover_dll.errcheck = ANC_errcheck

    devCount = ctypes.c_int()
    discover_dll(ctypes.c_int(ifaces),
                 ctypes.byref(devCount))
    print('{:} ANC350 devices found.'.format(devCount.value))
    return devCount.value

def registerExternalIp(hostname):
    '''
    discover is able to find devices connected via TCP/IP
    in the same network segment, but it can't "look through" routers.
    To connect devices in external networks, reachable by routing,
    the IP addresses of those devices have to be registered prior to
    calling discover. The function registers one device and can
    be called several times.

    The function will return ANC_Ok if the name resolution succeeds
    (ANC_NoDevice otherwise); it *doesn't test* if the device is reachable.
    Registered and reachable devices will be found by discover.

    Parameters
    ----------
    hostname : str
        hostname or IP Address in dotted decimal notation of the device to
        register.
    '''
    anc = load_ANC350dll()

    registerExternalIp_dll = anc.ANC_registerExternalIp
    registerExternalIp_dll.errcheck = ANC_errcheck

    registerExternalIp_dll(ctypes.c_char_p(hostname)) # @todo To check

class Positioner_ANC350:
    '''
    Class of a positioner connected to the ANC350.
    '''
    def __init__(self, devNo=0):
        '''
        Initialises the device.

        Parameters
        ----------
        devNo : int
            Device number to be initialised. Default: 0
        '''
        anc = load_ANC350dll()
        # Aliases for the functions from the dll. For handling return
        # values: '.errcheck' is an attribute from ctypes.
        # Taken from anc350res.h,v 1.12 2017/08/04 13:59:18
        self._configureAQuadBIn_dll = anc.ANC_configureAQuadBIn
        self._configureAQuadBIn_dll.errcheck = ANC_errcheck
        self._configureAQuadBOut_dll = anc.ANC_configureAQuadBOut
        self._configureAQuadBOut_dll.errcheck = ANC_errcheck
        self._configureExtTrigger_dll = anc.ANC_configureExtTrigger
        self._configureExtTrigger_dll.errcheck = ANC_errcheck
        self._configureNslTrigger_dll = anc.ANC_configureNslTrigger
        self._configureNslTrigger_dll.errcheck = ANC_errcheck
        self._configureNslTriggerAxis_dll = anc.ANC_configureNslTriggerAxis
        self._configureNslTriggerAxis_dll.errcheck = ANC_errcheck
        self._configureRngTrigger_dll = anc.ANC_configureRngTrigger
        self._configureRngTrigger_dll.errcheck = ANC_errcheck
        self._configureRngTriggerEps_dll = anc.ANC_configureRngTriggerEps
        self._configureRngTriggerEps_dll.errcheck = ANC_errcheck
        self._configureRngTriggerPol_dll = anc.ANC_configureRngTriggerPol
        self._configureRngTriggerPol_dll.errcheck = ANC_errcheck
        self._connect_dll = anc.ANC_connect
        self._connect_dll.errcheck = ANC_errcheck
        self._disconnect_dll = anc.ANC_disconnect
        self._disconnect_dll.errcheck = ANC_errcheck
        self._getActuatorName_dll = anc.ANC_getActuatorName
        self._getActuatorName_dll.errcheck = ANC_errcheck
        self._getActuatorType_dll = anc.ANC_getActuatorType
        self._getActuatorType_dll.errcheck = ANC_errcheck
        self._getAmplitude_dll = anc.ANC_getAmplitude
        self._getAmplitude_dll.errcheck = ANC_errcheck
        self._getAxisStatus_dll = anc.ANC_getAxisStatus
        self._getAxisStatus_dll.errcheck = ANC_errcheck
        self._getDcVoltage_dll = anc.ANC_getDcVoltage
        self._getDcVoltage_dll.errcheck = ANC_errcheck
        self._getDeviceConfig_dll = anc.ANC_getDeviceConfig
        self._getDeviceConfig_dll.errcheck = ANC_errcheck
        self._getDeviceInfo_dll = anc.ANC_getDeviceInfo
        self._getDeviceInfo_dll.errcheck = ANC_errcheck
        self._getFirmwareVersion_dll = anc.ANC_getFirmwareVersion
        self._getFirmwareVersion_dll.errcheck = ANC_errcheck
        self._getFrequency_dll = anc.ANC_getFrequency
        self._getFrequency_dll.errcheck = ANC_errcheck
        self._getPosition_dll = anc.ANC_getPosition
        self._getPosition_dll.errcheck = ANC_errcheck
        self._loadLutFile_dll = anc.ANC_loadLutFile
        self._loadLutFile_dll.errcheck = ANC_errcheck
        self._measureCapacitance_dll = anc.ANC_measureCapacitance
        self._measureCapacitance_dll.errcheck = ANC_errcheck
        self._saveParams_dll = anc.ANC_saveParams
        self._saveParams_dll.errcheck = ANC_errcheck
        self._selectActuator_dll = anc.ANC_selectActuator
        self._selectActuator_dll.errcheck = ANC_errcheck
        self._setAmplitude_dll = anc.ANC_setAmplitude
        self._setAmplitude_dll.errcheck = ANC_errcheck
        self._setAxisOutput_dll = anc.ANC_setAxisOutput
        self._setAxisOutput_dll.errcheck = ANC_errcheck
        self._setDcVoltage_dll = anc.ANC_setDcVoltage
        self._setDcVoltage_dll.errcheck = ANC_errcheck
        self._setFrequency_dll = anc.ANC_setFrequency
        self._setFrequency_dll.errcheck = ANC_errcheck
        try:
            self._getLutName_dll = anc.ANC_getLutName
            self._getLutName_dll.errcheck = ANC_errcheck
        except:
            warnings.warn('ANC_getLutName not available')
        self._setTargetGround_dll = anc.ANC_setTargetGround
        self._setTargetGround_dll.errcheck = ANC_errcheck
        self._setTargetPosition_dll = anc.ANC_setTargetPosition
        self._setTargetPosition_dll.errcheck = ANC_errcheck
        self._setTargetRange_dll = anc.ANC_setTargetRange
        self._setTargetRange_dll.errcheck = ANC_errcheck
        self._startAutoMove_dll = anc.ANC_startAutoMove
        self._startAutoMove_dll.errcheck = ANC_errcheck
        self._startContinousMove_dll = anc.ANC_startContinousMove
        self._startContinousMove_dll.errcheck = ANC_errcheck
        self._startSingleStep_dll = anc.ANC_startSingleStep
        self._startSingleStep_dll.errcheck = ANC_errcheck
        # Method count: 35 without ANC_discover and ANC_registerExternalIp

        # Not implemented -- start (found in non-res products):
        self._configureDutyCycle_dll = anc.ANC_configureDutyCycle
        self._configureDutyCycle_dll.errcheck = ANC_errcheck
        self._enableRefAutoReset_dll = anc.ANC_enableRefAutoReset
        self._enableRefAutoReset_dll.errcheck = ANC_errcheck
        self._enableRefAutoUpdate_dll = anc.ANC_enableRefAutoUpdate
        self._enableRefAutoUpdate_dll.errcheck = ANC_errcheck
        self._enableSensor_dll = anc.ANC_enableSensor
        self._enableSensor_dll.errcheck = ANC_errcheck
        self._enableTrace_dll = anc.ANC_enableTrace
        self._enableTrace_dll.errcheck = ANC_errcheck
        self._getRefPosition_dll = anc.ANC_getRefPosition
        self._getRefPosition_dll.errcheck = ANC_errcheck
        self._moveReference_dll = anc.ANC_moveReference
        self._moveReference_dll.errcheck = ANC_errcheck
        self._resetPosition_dll = anc.ANC_resetPosition
        self._resetPosition_dll.errcheck = ANC_errcheck
        # Not implemented -- stop.

        self.devNo = devNo
        self.device = self.connect(self.devNo)

    def __enter__(self):
        print('Enter __enter__')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('Enter __exit__')
        self.disconnect()

    def configureAQuadBIn(self, axisNo, enable, resolution):
        '''
        Enables and configures the A-Quad-B (quadrature) input for the target
        position.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2).
        enable : int
            Enable (1) or disable (0) A-Quad-B input.
        resolution : float
            A-Quad-B step width in m. Internal resolution is 1 nm.
        '''
        self._configureAQuadBIn_dll(self.device,
                                    ctypes.c_uint(axisNo),
                                    ctypes.c_int(enable),
                                    ctypes.c_double(resolution))

    def configureAQuadBOut(self, axisNo, enable, resolution, clock):
        '''
        Enables and configures the A-Quad-B output of the current position.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        enable : int
            Enable (1) or disable (0) A-Quad-B output
        resolution : float
            A-Quad-B step width in m; internal resolution is 1 nm
        clock : float
            Clock of the A-Quad-B output [s]. Allowed range is 40 ns ... 1.3 ms.
            Internal resolution is 20 ns.
        '''
        self._configureAQuadBOut_dll(self.device,
                                     ctypes.c_uint(axisNo),
                                     ctypes.c_int(enable),
                                     ctypes.c_double(resolution),
                                     ctypes.c_double(clock))

    def configureExtTrigger(self, axisNo, mode):
        '''
        Enables the input trigger for steps.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        mode : int
            Disable (0), Quadratur (1), Trigger(2) for external triggering
        '''
        self._configureExtTrigger_dll(self.device,
                                      ctypes.c_uint(axisNo),
                                      ctypes.c_uint(mode))

    def configureNslTrigger(self, enable):
        '''
        Enables NSL input as Trigger Source.

        Parameters
        ----------
        enable : int
            disable(0), enable(1)
        '''
        self._configureNslTrigger_dll(self.device,
                                      ctypes.c_int(enable))

    def configureNslTriggerAxis(self, axisNo):
        '''
        Selects Axis for NSL Trigger.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        '''
        self._configureNslTriggerAxis_dll(self.device,
                                          ctypes.c_uint(axisNo))

    def configureRngTrigger(self, axisNo, lower, upper):
        '''
        Configure lower position for range Trigger.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        lower : int
            Lower position for range trigger (nm)
        upper : int
            Upper position for range trigger (nm)
        '''
        self._configureRngTrigger_dll(self.device,
                                      ctypes.c_uint(axisNo),
                                      ctypes.c_uint(lower),
                                      ctypes.c_uint(upper))

    def configureRngTriggerEps(self, axisNo, epsilon):
        '''
        Configure hysteresis for range Trigger.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        epsilon : int
            Hysteresis in nm / mdeg
        '''
        self._configureRngTriggerEps_dll(self.device,
                                         ctypes.c_uint(axisNo),
                                         ctypes.c_uint(epsilon))

    def configureRngTriggerPol(self, axisNo, polarity):
        '''
        Configure lower position for range Trigger.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        polarity : int
            Polarity of trigger signal when position is between lower and upper
            Low (0) and High (1)
        '''
        self._configureRngTriggerPol_dll(self.device,
                                         ctypes.c_uint(axisNo),
                                         ctypes.c_uint(polarity))

    def connect(self, devNo=0):
        '''
        Initialises and connects the selected device. This has to be done
        before any access to control variables or measured data.

        Parameters
        ----------
        devNo : int
            Sequence number of the device. Must be smaller than the devCount
            from the last ANC_discover call. Default: 0

        Returns
        -------
        device : ctypes.c_void_p
            Handle to the opened device, NULL pointer on error.
        '''
        device = ctypes.c_void_p()
        self._connect_dll(devNo,
                          ctypes.byref(device))
        print('ANC350 found at', device.value)
        return device

    def disconnect(self):
        '''
        Closes the connection to the device. The device handle becomes invalid.
        '''
        print('Disconnecting ANC350 from', self.device.value)
        self._disconnect_dll(self.device)

    def getActuatorName(self, axisNo):
        '''
        Get the name of the currently selected actuator.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        name : str
            Name of the actuator
        '''
        name = ctypes.create_string_buffer(32)
        self._getActuatorName_dll(self.device,
                                  ctypes.c_uint(axisNo),
                                  ctypes.byref(name))
        return name.value.decode('utf-8')

    def getActuatorType(self, axisNo):
        '''
        Get the type of the currently selected actuator.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        type_ : int
            Type of the actuator {0: linear, 1: goniometer, 2: rotator}
        '''
        type_ = ctypes.c_int()
        self._getActuatorType_dll(self.device,
                                  ctypes.c_uint(axisNo),
                                  ctypes.byref(type_))
        return type_.value

    def getAmplitude(self, axisNo):
        '''
        Returns the amplitude in V of an axis.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        Returns
        -------
        amplitude : float
            Amplitude in V
        '''
        amplitude = ctypes.c_double()
        self._getAmplitude_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.byref(amplitude))
        return amplitude.value

    def getAxisStatus(self, axisNo):
        '''
        Reads status information about an axis of the device.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        connected : int
            If the axis is connected to a sensor
        enabled : int
            If the axis voltage output is enabled
        moving : int
            If the axis is moving
        target : int
            If the target is reached in automatic positioning
        eotFwd : int
            If end of travel detected in forward direction
        eotBwd : int
            If end of travel detected in backward direction
        error : int
            If the axis' sensor is in error state
        '''
        connected = ctypes.c_int()
        enabled = ctypes.c_int()
        moving = ctypes.c_int()
        target = ctypes.c_int()
        eotFwd = ctypes.c_int()
        eotBwd = ctypes.c_int()
        error = ctypes.c_int()

        self._getAxisStatus_dll(self.device,
                                ctypes.c_uint(axisNo),
                                ctypes.byref(connected),
                                ctypes.byref(enabled),
                                ctypes.byref(moving),
                                ctypes.byref(target),
                                ctypes.byref(eotFwd),
                                ctypes.byref(eotBwd),
                                ctypes.byref(error))

        print('Status of device # {:}, axis {:}\n'
              '----------------------------\n'
              'Connected          {:}\n'
              'Enabled            {:}\n'
              'Moving             {:}\n'
              'Target             {:}\n'
              'End of travel (fw) {:}\n'
              'End of travel (bw) {:}\n'
              'Error state        {:}'.format(self.devNo,
                                              axisNo,
                                              connected.value,
                                              enabled.value,
                                              moving.value,
                                              target.value,
                                              eotFwd.value,
                                              eotBwd.value,
                                              error.value))

        return connected.value, enabled.value, moving.value, \
               target.value, eotFwd.value, eotBwd.value, error.value

    def getDcVoltage(self, axisNo):
        '''
        Reads back the current DC level. It may be the level that has been set
        by setDcVoltage or the value currently adjusted by the feedback
        controller.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        dcvolt : float
            DC voltage in V
        '''
        dcvolt = ctypes.c_double()
        self._getDcVoltage_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.byref(dcvolt))
        return dcvolt.value

    def getDeviceConfig(self):
        '''
        Reads static device configuration data.

        Returns
        -------
        featureSync : int
            'Sync': Ethernet enabled (1) or disabled (0)
        featureLockin : int
            'Lockin': Low power loss measurement enabled (1) or disabled (0)
        featureDuty : int
            'Duty': Duty cycle enabled (1) or disabled (0)
        featureApp : int
            'App': Control by IOS app enabled (1) or disabled (0)
        '''
        features = ctypes.c_uint()
        self._getDeviceConfig_dll(self.device,
                                  ctypes.byref(features))

        featureSync = 0x01 & features.value
        featureLockin = int((0x02 & features.value) / 2)
        featureDuty = int((0x04 & features.value) / 4)
        featureApp = int((0x08 & features.value) / 8)

        print('Configuration of device # {}\n'
              '---------------------------\n'
              'Sync   {:}\n'
              'Lockin {:}\n'
              'Duty   {:}\n'
              'App    {:}\n'.format(self.devNo,
                                    featureSync,
                                    featureLockin,
                                    featureDuty,
                                    featureApp))

        return featureSync, featureLockin, featureDuty, featureApp

    def getDeviceInfo(self):
        '''
        Returns available information about a device. The function can not be
        called before ANC_discover but the devices don't have to be connected.
        All pointers to output parameters may be zero to ignore the respective
        value.

        Returns
        -------
        devType : int
            Type of the ANC350 device:
            {0: Anc350Res, 1: Anc350Num, 2: Anc350Fps, 3: Anc350None}
        id : int
            Hardware ID of the device
        serialNo : str
            The device's serial number.
        address : str
            The device's interface address if applicable. Returns the
            IP address in dotted-decimal notation or the string "USB",
            respectively.
        connected : int
            If the device is already connected
        '''
        devType = ctypes.c_int()
        id_ = ctypes.c_int()
        serialNo = ctypes.create_string_buffer(32)
        address = ctypes.create_string_buffer(32)
        connected = ctypes.c_int()

        self._getDeviceInfo_dll(ctypes.c_uint(self.devNo),
                                ctypes.byref(devType),
                                ctypes.byref(id_),
                                ctypes.byref(serialNo),
                                ctypes.byref(address),
                                ctypes.byref(connected))

        print('Info of device # {:}\n'
              '------------------\n'
              'Type        {:}\n'
              'Hardware ID {:}\n'
              'Serial No   {:}\n'
              'Address     {:}\n'
              'Connected   {:}'.format(self.devNo,
                                       devType.value,
                                       id_.value,
                                       serialNo.value.decode('utf-8'),
                                       address.value.decode('utf-8'),
                                       connected.value))

        return devType.value, \
               id_.value, \
               serialNo.value.decode('utf-8'), \
               address.value.decode('utf-8'), \
               connected.value

    def getFirmwareVersion(self):
        '''
        Retrieves the version of currently loaded firmware.

        Returns
        -------
        version : int
            Version number
        '''
        version = ctypes.c_int()
        self._getFirmwareVersion_dll(self.device,
                                     ctypes.byref(version))
        return version.value

    def getFrequency(self, axisNo):
        '''
        Reads back the frequency parameter of an axis.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        frequency : float
            Frequency in Hz
        '''
        frequency = ctypes.c_double()
        self._getFrequency_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.byref(frequency))
        return frequency.value

    def getLutName(self, axisNo):
        '''
        Get the name of the currently selected sensor lookup table.
        The function is only available in RES devices.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        name : str
            Name of the LUT
        '''
        name = ctypes.create_string_buffer(32)
        self._getLutName_dll(self.device,
                             ctypes.c_uint(axisNo),
                             ctypes.byref(name))
        return name.value.decode('utf-8')

    def getPosition(self, axisNo):
        '''
        Retrieves the current actuator position. For linear type actuators the
        position unit is m; for goniometers and rotators it is degree.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        position : float
            Current position m or deg
        '''
        position = ctypes.c_double()
        self._getPosition_dll(self.device,
                              ctypes.c_uint(axisNo),
                              ctypes.byref(position))
        return position.value

    def loadLutFile(self, axisNo, fileName):
        '''
        Loads a sensor lookup table from a file into the device.
        The function is only available for ANC350Res devices.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        fileName : str
            Name of the LUT file to import, optionally with path
        '''
        self._loadLutFile_dll(self.device,
                              ctypes.c_uint(axisNo),
                              ctypes.c_char_p(fileName.encode('utf-8')))

    def measureCapacitance(self, axisNo):
        '''
        Performs a measurement of the capacitance of the piezo motor and
        returns the result. If no motor is connected, the result will be 0.
        The function doesn't return before the measurement is complete; this
        will take a few seconds of time.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)

        Returns
        -------
        cap : float
            Output: Capacitance in F
        '''
        cap = ctypes.c_double()
        self._measureCapacitance_dll(self.device,
                                     ctypes.c_uint(axisNo),
                                     ctypes.byref(cap))
        return cap.value

    def saveParams(self):
        '''
        Saves parameters to persistent flash memory in the device. They will be
        present as defaults after the next power-on. The following parameters
        are affected: Amplitude, frequency, actuator selections as well as
        trigger and quadrature settings.
        '''
        self._saveParams_dll(self.device)

    def selectActuator(self, axisNo, actuator):
        '''
        Selects the actuator to be used for the axis from actuator presets.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        actuator : int
            Actuator selection (0 ... 255)
            0: ANPx51
            1: ANPz51
            2: ANPz51ext
            3: ANPx101
            4: ANPz101
            5: ANPz102
            6: ANPz101ext
            7: ANPz111(ext)
            8: ANPx111(ext)
            9: ANPx121
            10: ANPx311
            11: ANPx321
            12: ANPx341
            13: ANGt101
            14: ANGp101
            15: ANR(v)101
            16: ANR(v)5*
            17: ANR(v)200/240
            18: ANR(v)220
        '''
        self._selectActuator_dll(self.device,
                                 ctypes.c_uint(axisNo),
                                 ctypes.c_uint(actuator))

    def setAmplitude(self, axisNo, amplitude):
        '''
        Sets the amplitude parameter in V for an axis.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        amplitude : float
            Amplitude in V, internal resolution is 1 mV
        '''
        self._setAmplitude_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.c_double(amplitude))

    def setAxisOutput(self, axisNo, enable, autoDisable):
        '''
        Enables or disables the voltage output of an axis.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        enable : int
            Enables (1) or disables (0) the voltage output.
        autoDisable : int
            If the voltage output is to be deactivated automatically when end
            of travel is detected. Enable voltage deactivation (1), disable
            voltage deactivation (0).
        '''
        self._setAxisOutput_dll(self.device,
                                ctypes.c_uint(axisNo),
                                ctypes.c_int(enable),
                                ctypes.c_int(autoDisable))

    def setDcVoltage(self, axisNo, voltage):
        '''
        Sets the DC level on the voltage output when no sawtooth based motion
        is active.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        voltage : float
            DC output voltage V, internal resolution is 1 mV
        '''
        self._setDcVoltage_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.c_double(voltage))

    def setFrequency(self, axisNo, frequency):
        '''
        Sets the frequency parameter for an axis.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        frequency : float
            Frequency in Hz, internal resolution is 1 Hz
        '''
        self._setFrequency_dll(self.device,
                               ctypes.c_uint(axisNo),
                               ctypes.c_double(frequency))

    def setTargetGround(self, axisNo, targetGnd):
        '''
        Sets or clears the Target GND Flag. It determines the action performed
        in automatic positioning mode when the target position is reached.
        If set, the DC output is set to 0 V and the position control feedback
        loop is stopped.

        Paramters
        ---------
        axisNo : int
            Axis number (0 ... 2)
        targetGnd : int
            Clears (0) or sets (1) target GND flag
        '''
        self._setTargetGround_dll(self.device,
                                  ctypes.c_uint(axisNo),
                                  ctypes.c_int(targetGnd))

    def setTargetPosition(self, axisNo, target):
        '''
        Sets the target position for automatic motion, see startAutoMove.
        For linear type actuators the position unit is m, for goniometers and
        rotators it is degree.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        target : float
            Target position m or deg. Internal resulution is 1 nm or 1 µdeg.
        '''
        self._setTargetPosition_dll(self.device,
                                    ctypes.c_uint(axisNo),
                                    ctypes.c_double(target))

    def setTargetRange(self, axisNo, targetRg):
        '''
        Defines the range around the target position where the target is
        considered to be reached.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        targetRg : float
            Target range m or deg. Internal resulution is 1 nm or 1 µdeg.
        '''
        self._setTargetRange_dll(self.device,
                                 ctypes.c_uint(axisNo),
                                 ctypes.c_double(targetRg))

    def startAutoMove(self, axisNo, enable, relative):
        '''
        Switches automatic moving (i.e. following the target position) on or off

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        enable : int
            Enables (1) or disables (0) automatic motion
        relative : int
            If the target position is to be interpreted absolute (0) or
            relative to the current position (1)
        '''
        self._startAutoMove_dll(self.device,
                                ctypes.c_uint(axisNo),
                                ctypes.c_int(enable),
                                ctypes.c_int(relative))

    def startContinuousMove(self, axisNo, start, backward):
        '''
        Starts or stops continuous motion in forward direction. Other kinds of
        motions are stopped.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        start : int
            Starts (1) or stops (0) the motion
        backward : int
            If the move direction is forward (0) or backward (1)
        '''
        self._startContinousMove_dll(self.device,
                                     ctypes.c_uint(axisNo),
                                     ctypes.c_int(start),
                                     ctypes.c_int(backward))

    def startSingleStep(self, axisNo, backward):
        '''
        Triggers a single step in desired direction.

        Parameters
        ----------
        axisNo : int
            Axis number (0 ... 2)
        backward : int
            If the step direction is forward (0) or backward (1)
        '''
        self._startSingleStep_dll(self.device,
                                  ctypes.c_uint(axisNo),
                                  ctypes.c_int(backward))

if __name__ == '__main__':

    ANC350_devcount = discover_ANC350()
    assert ANC350_devcount == 1

    posi1 = Positioner_ANC350(0)
    #posi2 = Positioner_ANC350(1)

    posi1.getAxisStatus(0)
    posi1.getDeviceInfo()
    posi1.getDeviceConfig()

    posi1.measureCapacitance(0)

    fname = 'ANPx101_01_123.LUT'
    assert os.path.isfile(fname)

    for i in range(100):
        posi1.loadLutFile(0, fname)

    posi1.setAxisOutput(0, 1, 0)

    # posi1.selectActuator(2, 1)

    print(posi1.getPosition(0))
    # posi1.startSingleStep(2, 0)

    # posi1.startContinuousMove(2, 1, 1)
    # import time
    # time.sleep(1)
    # posi1.startContinuousMove(2, 0, 0)

    posi1.disconnect()
