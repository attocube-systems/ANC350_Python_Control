# -*- coding: utf8 -*-
#  PylibANC350 is a control scheme suitable for the Python coding style
#    for the attocube ANC350 closed-loop positioner system.

import ANC350lib as ANC
import ctypes, time

class Positioner(object):

    def __init__(self):
        print('starting __init__')
        self.discover()
        self.device = self.connect()

        print('__init__ done')

    # Safest to use python's "with notation":
    # with Positioner as atto:
    #     execute code
    def __enter__(self):
        print('__enter__ done')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print ('starting __exit__')
        self.disconnect()
        #anc350.disconnect()
        print ('__exit__ done')




    def connect(self, devNo=0):
        '''
        Initializes and connects the selected device. This has to be done before any access to control variables or measured data.

        Parameters
            devNo	Sequence number of the device. Must be smaller than the devCount from the last ANC_discover call. Default: 0
        Returns
            device	Handle to the opened device, NULL on error
        '''
        device = ctypes.c_void_p()
        ANC.connect(devNo, ctypes.byref(device))
        print('ANC350 connected at', device.value)
        return device


    def disconnect(self):
        '''
        Closes the connection to the device. The device handle becomes invalid.

        Parameters
            None
        Returns
            None
        '''
        print('Disconnectting ANC350 at,',self.device.value)
        ANC.disconnect(self.device)



    def discover(self, ifaces=3):
        '''
        The function searches for connected ANC350RES devices on USB and LAN and initializes internal data structures per device. Devices that are in use by another application or PC are not found. The function must be called before connecting to a device and must not be called as long as any devices are connected.

        The number of devices found is returned. In subsequent functions, devices are identified by a sequence number that must be less than the number returned.

        Parameters
            ifaces	Interfaces where devices are to be searched. {None: 0, USB: 1, ethernet: 2, all:3} Default: 3
        Returns
            devCount	number of devices found
        '''
        devCount = ctypes.c_int()
        ANC.discover(ifaces, ctypes.byref(devCount))
        print("%d ANC350 devices found."%devCount.value)
        return devCount.value



    def getAmplitude(self, axisNo):
        '''
        Reads back the amplitude parameter of an axis.

        Parameters
            axisNo	Axis number (0 ... 2)
        Returns
            amplitude	Amplitude V
        '''
        amplitude = ctypes.c_double()
        ANC.getAmplitude(self.device, axisNo, ctypes.byref(amplitude))
        return amplitude.value


    def getPosition(self, axisNo):
        '''
        Retrieves the current actuator position. For linear type actuators the position unit is m; for goniometers and rotators it is degree.

        Parameters
            axisNo	Axis number (0 ... 2)
        Returns
            position	Output: Current position [m] or [°]
        '''
        position = ctypes.c_double()
        ANC.getPosition(self.device, axisNo, ctypes.byref(position))
        return position.value




    def setAxisOutput(self, axisNo, enable, autoDisable):
        '''
        Enables or disables the voltage output of an axis.

        Parameters
            axisNo	Axis number (0 ... 2)
            enable	Enables (1) or disables (0) the voltage output.
            autoDisable	If the voltage output is to be deactivated automatically when end of travel is detected. Enable voltage deactivation(1), Disable voltage deactivation(0)
        Returns
            None
        '''
        ANC.setAxisOutput(self.device, axisNo, enable, autoDisable)



    def setFrequency(self, axisNo, frequency):
        '''
        Sets the frequency parameter for an axis

        Parameters
            axisNo	Axis number (0 ... 2)
            frequency	Frequency in Hz, internal resolution is 1 Hz
        Returns
            None
        '''
        ANC.setFrequency(self.device, axisNo, ctypes.c_double(frequency))


    def setAmplitude(self, axisNo, amplitude):
        '''
        Sets the amplidude/voltage parameter for an axis

        Parameters
            axisNo	Axis number (0 ... 2)
            amplidude	Voltage in V, internal resolution is 1 mV
        Returns
            None
        '''
        ANC.setAmplitude(self.device, axisNo, ctypes.c_double(amplitude))



    def startContinuousMove(self, axisNo, start, backward):
        '''
        Starts or stops continous motion in forward direction. Other kinds of motions are stopped.

        Parameters
            axisNo	Axis number (0 ... 2)
            start	Starts (1) or stops (0) the motion
            backward	If the move direction is forward (0) or backward (1)
        Returns
            None
        '''
        ANC.startContinousMove(self.device, axisNo, start, backward)

    def convertPositionToMicrons(self, axisNo):

        pos=self.getPosition(0)
        #float_pos=float(pos)
        #posum=float_pos*1000000
        posum1=pos*1000000
        return posum1

#pos = []
#t = []

with Positioner() as anc350:

    if __name__=='__main__':

        pos = []
        t = []

        print('starting main code')
        #anc350=Positioner()

        axis = 2


        anc350.setAmplitude(axis, 45)
        anc350.setFrequency(axis, 50)
        anc350.setAxisOutput(axis, 0, 1)



        posum = anc350.convertPositionToMicrons(axis)
        print ('Start was at: %.2f um' %posum)
        anc350.startContinuousMove(axis, 1, 0)
        starttime=time.time()

#        while posum < 700:
#
#            posum=anc350.convertPositionToMicrons(0)
#            pos.append(posum)
#            t.append(time.time()-starttime)
        time.sleep(0.1)

        print ('Turning around at about: %d um' %posum)
        anc350.startContinuousMove(axis, 0, 0)

#        while posum > 600:
#            posum=anc350.convertPositionToMicrons(0)
#            pos.append(posum)
#            t.append(time.time()-starttime)
#            time.sleep(0.001)



        anc350.startContinuousMove(axis, 0, 1)
        print ("Stopped at: %.2f um"  %posum)

#        anc350.disconnect()
