######################################################################
#
#  Project:        Daisy Client Library
#
#  Filename:       example500.py
#
#  Purpose:        Python example for using daisybase lib with ASC500
#
#  Author:         NHands GmbH & Co KG
#
######################################################################
# $Id: example500.c,v 1.10 2018/03/22 16:08:42 trurl Exp $


from ctypes import *
import time
import asc500const

# ASC500 Wrapper class --------------------------------------------------------------
class Asc500:
    def __init__(self):
        # Load Daisybase DLL ...
        self.daisybase = CDLL('daisybase.dll')
        # ... and define the parameter types of its functions ...
        # ... from daisybase.h
        self.daisybase.DYB_init.argtypes              = [c_char_p,c_char_p,c_char_p,c_int32]
        self.daisybase.DYB_init.restype               = c_int32
        self.daisybase.DYB_run.argtypes               = None
        self.daisybase.DYB_run.restype                = None
        self.daisybase.DYB_stop.argtypes              = None
        self.daisybase.DYB_stop.restype               = c_int32
        self.daisybase.DYB_setParameterAsync.argtypes = [c_int32,c_int32,c_int32]
        self.daisybase.DYB_setParameterAsync.restype  = c_int32
        self.daisybase.DYB_getParameterSync.argtypes  = [c_int32,c_int32,POINTER(c_int32)]
        self.daisybase.DYB_getParameterSync.restype   = c_int32
        self.daisybase.DYB_sendProfile.argtypes       = [c_char_p]
        self.daisybase.DYB_sendProfile.restype        = c_int32
        # ... from daisydata.h
        self.daisybase.DYB_configureChannel.argtypes  = [c_int32,c_int32,c_int32,c_int32,c_double]
        self.daisybase.DYB_configureChannel.restype   = c_int32
        self.daisybase.DYB_configureDataBuffering.argtypes = [c_int32,c_int32]
        self.daisybase.DYB_configureDataBuffering.restype  = c_int32
        self.daisybase.DYB_getFrameSize.argtypes      = [c_int32]
        self.daisybase.DYB_getFrameSize.restype       = c_int32
        self.daisybase.DYB_getDataBuffer.argtypes     = [c_int32,c_int32,POINTER(c_int32),
                                                         POINTER(c_int32),POINTER(c_int32),
                                                         POINTER(c_int32),POINTER(c_int32)]
        self.daisybase.DYB_getDataBuffer.restype      = c_int32
        self.daisybase.DYB_writeBuffer.argtypes       = [c_char_p,c_char_p,c_int32,c_int32,c_int32,
                                                         POINTER(c_int32),POINTER(c_int32)]
        self.daisybase.DYB_writeBuffer.restype        = c_int32
        self.daisybase.DYB_waitForEvent.argtypes      = [c_int32,c_int32,c_int32]
        self.daisybase.DYB_waitForEvent.restype       = c_int32

# Wrapper functions --------------------------------------------------------------

    def perror(self,environ,returnCode):                        # Error Check
        if (returnCode!=0):
            msgs = { 0:"No error",
                     1:"Unknown / other error",
                     2:"Communication timeout",
                     4:"No contact to controller via USB",
                     5:"Error when calling USB driver",
                     6:"Controller boot image not found",
                     7:"Server executable not found",
                     8:"No contact to the server",
                     9:"Invalid parameter in fct call",
                     10:"Call in invalid thread context",
                     11:"Invalid format of profile file",
                     12:"Can't open specified file" }
            raise Exception("Daisybase: call to {} returned: {}".format(environ,msgs[returnCode]))

    def init(self,dummy,ipath,shost,port):
        cdummy = create_string_buffer(dummy.encode('utf-8'))    # Convert Python strings to C
        cipath = create_string_buffer(ipath.encode('utf-8'))
        cshost = create_string_buffer(shost.encode('utf-8'))
        rc = self.daisybase.DYB_init(cdummy,cipath,cshost,port) # initialize DLL
        self.perror( "DYB_init",rc);
        if (rc==0):
            self.daisybase.DYB_run()                            # Start server

    def stop(self):
        rc = self.daisybase.DYB_stop                            # Stop server

    def setParameter(self,address,index,value):
        rc = self.daisybase.DYB_setParameterAsync(address,index,value)
        message = "DYB_setParameterAsync({})".format(address);
        self.perror(message,rc);

    def getParameter(self,address,index):
        val = c_int32(0)
        rc = self.daisybase.DYB_getParameterSync(address,index,byref(val))
        message = "DYB_getParameterSync({})".format(address);
        self.perror(message,rc);
        return val.value

    def sendProfile(self,pfile):
        cfn = create_string_buffer(pfile.encode('utf-8'))       # Convert Python strings to C
        rc = self.daisybase.DYB_sendProfile(cfn)                # Send parameter set to device
        self.perror("DYB_sendProfile",rc);

    def configureChannel(self,channel,trigger,source,average,smpTime):
        rc = self.daisybase.DYB_configureChannel(channel,trigger,source,average,smpTime)
        self.perror( "DYB_configureChannel", rc );

    def configureDataBuffering(self,channel,size):
        rc = self.daisybase.DYB_configureDataBuffering(channel,size)
        self.perror( "DYB_configureDataBuffering", rc );

    def getDataBuffer(self,channel,fullOnly,frameNo,index,dataSize,data,meta):
        rc = self.daisybase.DYB_getDataBuffer(channel,fullOnly,frameNo,index,dataSize,data,meta)
        self.perror( "DYB_getDataBuffer", rc );
        return rc

    def writeBuffer(self,fileName,comment,bin,forward,index,size,data,meta):
        cfn = create_string_buffer(fileName.encode('utf-8'))    # Convert Python strings to C
        ccm = create_string_buffer(comment.encode('utf-8'))
        rc = self.daisybase.DYB_writeBuffer(cfn,ccm,bin,forward,index,size,data,meta)
        self.perror( "DYB_writeBuffer", rc );

    def getFrameSize(self,channel):
        return self.daisybase.DYB_getFrameSize(channel)

    def waitForEvent(self,timeout,mask,customId):
        return self.daisybase.DYB_waitForEvent(timeout,mask,customId)


# Some Constants ----------------------------------------------------------------

CHANNELNO       = 0                                             # use channel 0
COLUMNS         = 100                                           # Scanrange number of columns
LINES           = 150                                           # Scanrange number of lines
PIXELSIZE       = 1000                                          # Width of a column/line [10pm]
SAMPLETIME      = 100                                           # Scanner sample time [2.5us]
FRAMESIZE       = COLUMNS*LINES*2                               # Amount of data in a frame
DYB_EVT_DATA_00 = 1                                             # from daisydata.h
DYB_EVT_CUSTOM  = 0x8000                                        # from daisydata.h

# Translate Constants from asc500const ------------------------------------------

def cc(symbol):
    return int(asc500const.cc[symbol],0)                        # necessary to convert '0x10' to 16

# Scanner Command ----------------------------------------------------------------
# Starting the scanner is a little bit more complicated as it requires two commands
# with handshake. The function encapsulates the processing of all scanner commands.

def sendScannerCommand(command):
    if (command == cc('SCANRUN_ON') ):
        # Scan start requires two commands; the first one to move to the start position,
        # (which can take a long time), the second one to actually run the scan.
        # A rather simple approach: send command cyclically until the scanner is running
        state = 0
        while ( (state & cc('SCANSTATE_SCAN')) == 0 ):
            asc500.setParameter( cc('ID_SCAN_COMMAND'), 0, command )
            time.sleep( .1 )
            state = asc500.getParameter( cc('ID_SCAN_STATUS'), 0 )
            print( "Scanner State: ", end='' );
            if ( state & cc('SCANSTATE_PAUSE')  ): print( "Pause ", end='' )
            if ( state & cc('SCANSTATE_MOVING') ): print( "Move ",  end='' )
            if ( state & cc('SCANSTATE_SCAN')   ): print( "Scan ",  end='' )
            if ( state & cc('SCANSTATE_IDLE')   ): print( "Idle ",  end='' )
            if ( state & cc('SCANSTATE_LOOP')   ): print( "Loop ",  end='' )
            print( "" )
    else:
        # Stop and pause only require one command
        asc500.setParameter( cc('ID_SCAN_COMMAND'), 0, command );

# Read scanner position -----------------------------------------------------------
# Get scanner position in abs. coordinates and in um

def getScannerXYPos():
  xOrigin   = asc500.getParameter( cc('ID_SCAN_COORD_ZERO_X'), 0 );
  yOrigin   = asc500.getParameter( cc('ID_SCAN_COORD_ZERO_Y'), 0 );
  xRelative = asc500.getParameter( cc('ID_SCAN_CURR_X'),       0 );
  yRelative = asc500.getParameter( cc('ID_SCAN_CURR_Y'),       0 );
  x = (xOrigin + xRelative) / 1.e5;  # 10pm -> um
  y = (yOrigin + yRelative) / 1.e5;
  return [x,y]


# Poll Data ----------------------------------------------------------------------
# Wait for the first full buffer and write it to a file

def pollDataFull():
    event   = 0                                                 # Returncode of waitForEvent
    frameNo = c_int32( 0 )                                      # Return param of getDataBuffer
    index   = c_int32( 0 )                                      # Return param of getDataBuffer
    dSize   = c_int32( FRAMESIZE )                              # In- and output of getDataBuffer
    frame   = (c_int32 * FRAMESIZE)()                           # Array to receive data
    meta    = (c_int32 * 13)()                                  # Metadata, should be a struct...

    # Wait for full buffer on channel 0 and show progress
    while ( event == 0 ):
        event = asc500.waitForEvent( 500, DYB_EVT_DATA_00, 0 );
        pos = getScannerXYPos()
        print( "Scanner at ", pos[0], " , ", pos[1], " um" )

    # Read and print data frame, forward and backward scan in separate files
    print( "Reading frame; bufSize=", dSize.value, ", frameSize=",
           asc500.getFrameSize( CHANNELNO ) );
    asc500.getDataBuffer( CHANNELNO, 1, byref(frameNo), byref(index), byref(dSize), frame, meta );
    if ( dSize.value > 0 ):
        asc500.writeBuffer( 'scan_fwd', 'ADC2', 0, 1, index, dSize, frame, meta )
        asc500.writeBuffer( 'scan_bwd', 'ADC2', 0, 0, index, dSize, frame, meta )
    else:
        raise( "No data have been received!" )


# Main function -----------------------------------------------------------------

try:
    asc500 = Asc500()

    dummy   = 'FindSim'                                         # Hack: enable device simulation
    asc500.init( dummy, '..\\..', '', cc('ASC500_PORT_NUMBER') )# Initalize DLL & start
    asc500.sendProfile( '..\\..\\afm.ngp' )                     # Send parameter set to device
    asc500.configureChannel( CHANNELNO, cc('CHANCONN_SCANNER'), # Connect Ch. 0 with Scanner / ADC2
                             cc('CHANADC_ADC_MIN') + 1, 0, 0 )
    asc500.configureDataBuffering( 0, 1024 )                    # Size not relevant here but >0
    asc500.setParameter( cc('ID_SCAN_X_EQ_Y'),   0, 0 );        # Switch off annoying automatics ..
    asc500.setParameter( cc('ID_SCAN_GEOMODE'),  0, 0 );        # that are useful only for GUI users
    asc500.setParameter( cc('ID_SCAN_PIXEL'),    0, PIXELSIZE ) # Adjust scanner parameters 
    asc500.setParameter( cc('ID_SCAN_COLUMNS'),  0, COLUMNS )
    asc500.setParameter( cc('ID_SCAN_LINES'),    0, LINES )
    asc500.setParameter( cc('ID_SCAN_OFFSET_X'), 0, 150 * PIXELSIZE )
    asc500.setParameter( cc('ID_SCAN_OFFSET_Y'), 0, 150 * PIXELSIZE )
    asc500.setParameter( cc('ID_SCAN_MSPPX'),    0, SAMPLETIME )

    # Enable Outputs and wait for success (enable outputs takes some time)
    outActive = 0
    asc500.setParameter( cc('ID_OUTPUT_ACTIVATE'), 0, 1  )
    while ( outActive == 0 ):
        outActive = asc500.getParameter( cc('ID_OUTPUT_STATUS'), 0 )
        print( "Output Status: ", outActive )
        time.sleep( .05 )

    sendScannerCommand( cc('SCANRUN_ON') )                      # Start scanner
    pollDataFull()                                              # Wait for data
    sendScannerCommand( cc('SCANRUN_OFF') )                     # Stop scanner

    # Disable Outputs and wait until finished.
    # We use wait for event instead of polling for demonstration.
    asc500.setParameter( cc('ID_OUTPUT_ACTIVATE'), 0, 0  )
    asc500.waitForEvent( 5000, DYB_EVT_CUSTOM, cc('ID_OUTPUT_STATUS') )
    outActive = asc500.getParameter( cc('ID_OUTPUT_STATUS'), 0 );
    if ( outActive != 0 ):
        print( "Outputs are not deactivated!" );

finally:
    asc500.stop()

