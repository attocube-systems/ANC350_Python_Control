/*****************************************************************************
 *
 *  Project:        ANC350 Custom Programming Library
 *
 *  Filename:       anc350res.h
 *
 *  Author:         NHands GmbH & Co KG
 */
/*****************************************************************************/
/** @mainpage Custom Programming Library for ANC350
 *
 *  @ref anc350res.h "ANC350 Custom Programming Library" is a library
 *  that allows to create custom software that controls the ANC350
 *  positioner controller. All sensor type variants ANC350RES, ANC350NUM,
 *  and ANC350FPS are supported. It can manage multiple devices that are
 *  connected to the PC via USB or ethernet.
 *
 *  Documentation for the functions that apply to all three variants
 *  can be found \ref anc350res.h "here".
 *
 *  In addition, specific functions are provided for the variants
 *  \ref anc350num.h "ANC350NUM" and \ref anc350fps.h "ANC350FPS".
 */
/*****************************************************************************/
/** @file anc350res.h
 *
 *  @brief Control and acquisition functions for ANC350
 *
 *  Defines functions for connecting and controlling the ANC350 (RES, NUM, and FPS).
 *  The functions are not thread safe!
 *
 *  Use \ref ANC_discover to discover devices on USB or ethernet.
 *  Inspect them with \ref ANC_getDeviceInfo and connect to selected devices
 *  using \ref ANC_connect. The handle received from the that function allows
 *  to call all all the other functions for configuration, motion, and position
 *  readback. When finished, close the connection with \ref ANC_disconnect.
 */
/*****************************************************************************/
/* $Id: anc350res.h,v 1.16 2019/02/12 13:56:21 trurl Exp $ */

#ifndef __ANC350RES_H__
#define __ANC350RES_H__

#include "ancdecl.h"


/** @name Return values of the functions
 *
 *  All functions of this lib - as far as they can fail - return
 *  one of these constants for success control.
 *  @{
 */
#define ANC_Ok                0          /**< Success                                */
#define ANC_Error           (-1)         /**< Unspecified error                      */
#define ANC_Timeout           1          /**< Receive timed out                      */
#define ANC_NotConnected      2          /**< No connection was established          */
#define ANC_DriverError       3          /**< Error accessing the USB driver         */
#define ANC_DeviceLocked      7          /**< Can't connect, device already in use   */
#define ANC_Unknown           8          /**< Unknown error                          */
#define ANC_NoDevice          9          /**< Invalid device number used in call     */
#define ANC_NoAxis           10          /**< Invalid axis number in function call   */
#define ANC_OutOfRange       11          /**< Parameter in call is out of range      */
#define ANC_NotAvailable     12          /**< Function not available for device type */
#define ANC_FileError        13          /**< Error opening or interpreting a file   */
/* @} */


/** @name ANC350RES Feature Flags
 *  @anchor FFlags
 *
 *  The flags describe optional features of the device.
 *  They are used by @ref ANC_getDeviceConfig .
 *  @{
 */
#define ANC_FeatureSync    0x01          /**< "Sync":   Ethernet enabled             */
#define ANC_FeatureLockin  0x02          /**< "Lockin": Low power loss measurement   */
#define ANC_FeatureDuty    0x04          /**< "Duty":   Duty cycle enabled           */
#define ANC_FeatureApp     0x08          /**< "App":    Control by IOS app enabled   */
/* @} */
 
/** @brief ANC350 Device Types
 */
typedef enum { Anc350Res,                /**< ANC350RES for RES sensors              */
               Anc350Num,                /**< ANC350NUM for NUM sensors              */
               Anc350Fps,                /**< ANC350FPS for FPS sensors              */
               Anc350None                /**< No device / invalid                    */
} ANC_DeviceType;

/** @brief Actuator Types
 */
typedef enum {
  ActLinear,                             /**< Actuator is of linear type             */
  ActGonio,                              /**< Actuator is of goniometer type         */
  ActRot                                 /**< Actuator is of rotator type            */
} ANC_ActuatorType;


/** @brief Interface Types
 */
typedef enum { IfNone = 0x00,            /**< Device invalid / not connected         */
               IfUsb  = 0x01,            /**< Device connected via USB               */
               IfTcp  = 0x02,            /**< Device connected via ethernet (TCP/IP) */
               IfAll  = 0x03             /**< All physical interfaces                */
} ANC_InterfaceType;


/** @brief Moving Status
 */
typedef enum { MoveIdle,                 /**< No motion                              */
               MoveMove,                 /**< Motion in progress                     */
               MovePending               /**< Motion scheduled but blocked by EOT etc*/
} ANC_MovingStatus;


typedef void * ANC_Handle;               /**< Handle to access an opened ANC350RES   */


/** @brief Discover Devices
 *
 *  The function searches for connected ANC350RES devices on USB and LAN and
 *  initializes internal data structures per device. Devices that are in use
 *  by another application or PC are not found.
 *  The function must be called before connecting to a device and must not be
 *  called as long as any devices are connected.
 *
 *  The number of devices found is returned. In subsequent functions, devices
 *  are identified by a sequence number that must be less than the number returned.
 *  @param  ifaces    Interfaces where devices are to be searched
 *  @param  devCount  Output: number of devices found
 *  @return           Error code
 */
ANC_API Int32 WINCC ANC_discover( ANC_InterfaceType ifaces,
                                  Uit32           * devCount );


/** @brief Device Information
 *
 *  Returns available information about a device. The function can not be
 *  called before @ref ANC_discover but the devices don't have to be
 *  @ref ANC_connect "connected" . All Pointers to output parameters may
 *  be zero to ignore the respective value.
 *  @param  devNo     Sequence number of the device. Must be smaller than
 *                    the devCount from the last @ref ANC_discover call.
 *  @param  devType   Output: Type of the ANC350 device
 *  @param  id        Output: programmed hardware ID of the device
 *  @param  serialNo  Output: The device's serial number. The string buffer
 *                    should be NULL or at least 16 bytes long.
 *  @param  address   Output: The device's interface address if applicable.
 *                    Returns the IP address in dotted-decimal notation or the
 *                    string "USB", respectively. The string buffer should be
 *                    NULL or at least 16 bytes long.
 *  @param  connected Output: If the device is already connected
 *  @return           Error code
 */
ANC_API Int32 WINCC ANC_getDeviceInfo( Uit32            devNo,
                                       ANC_DeviceType * devType,
                                       Int32          * id,
                                       Int8           * serialNo,
                                       Int8           * address,
                                       Bln32          * connected );


/** @brief Register IP Device in external Network
 *
 *  @ref ANC_discover is able to find devices connected via TCP/IP
 *  in the same network segment, but it can't "look through" routers.
 *  To connect devices in external networks, reachable by routing,
 *  the IP addresses of those devices have to be registered prior to
 *  calling @ref ANC_discover. The function registers one device and can
 *  be called several times.
 *
 *  The function will return ANC_Ok if the name resolution succeeds
 *  (ANC_NoDevice otherwise); it doesn't test if the device is reachable.
 *  Registered and reachable devices will be found by @ref ANC_discover.
 *  @param    hostname  Hostname or IP Address in dotted decimal notation
 *                      of the device to register.
 *  @return             Error code. ANC_NoDevice means here that the
 *                      hostname could not be resolved. A return code of 0
 *                      doesn't guarantee that the device is reachable.
 */
ANC_API Int32 WINCC ANC_registerExternalIp( const char * hostname );


/** @brief Connect Device
 *
 *  Initializes and connects the selected device.
 *  This has to be done before any access to control variables or measured data.
 *  @param  devNo      Sequence number of the device. Must be smaller than
 *                     the devCount from the last @ref ANC_discover call.
 *  @param  device     Output: Handle to the opened device, NULL on error
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_connect( Uit32        devNo,
                                 ANC_Handle * device );


/** @brief Disconnect Device
 *
 *  Closes the connection to the device. The device handle becomes invalid.
 *  @param  device     Handle of the device to close
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_disconnect( ANC_Handle device );


/** @brief Read Device Configuration
 *
 *  Reads static device configuration data
 *  @param  device     Handle of the device to access
 *  @param  features   Output: Bitfield of enabled features,
 *                     see @ref FFlags "Feature Flags"
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getDeviceConfig( ANC_Handle device,
                                         Uit32    * features );


/** @brief Read Axis Status
 *
 *  Reads status information about an axis of the device.
 *  All pointers to output values may be NULL to ignore the information.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  connected  Output: If the axis is connected to a sensor.
 *  @param  enabled    Output: If the axis voltage output is enabled.
 *  @param  moving     Output: If the axis is moving.
 *  @param  target     Output: If the target is reached in automatic positioning
 *  @param  eotFwd     Output: If end of travel detected in forward direction.
 *  @param  eotBwd     Output: If end of travel detected in backward direction.
 *  @param  error      Output: If the axis' sensor is in error state.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getAxisStatus( ANC_Handle device,
                                       Uit32      axisNo,
                                       Bln32    * connected,
                                       Bln32    * enabled,
                                       Bln32    * moving,
                                       Bln32    * target,
                                       Bln32    * eotFwd,
                                       Bln32    * eotBwd,
                                       Bln32    * error  );


/** @brief Enable Axis Output
 *
 *  Enables or disables the voltage output of an axis.
 *  @param  device      Handle of the device to access
 *  @param  axisNo      Axis number (0 ... 2)
 *  @param  enable      Enables (1) or disables (0) the voltage output.
 *  @param  autoDisable If the voltage output is to be deactivated automatically
 *                      when end of travel is detected.
 *  @return             Error code
 */
ANC_API Int32 WINCC ANC_setAxisOutput( ANC_Handle device,
                                       Uit32      axisNo,
                                       Bln32      enable,
                                       Bln32      autoDisable );


/** @brief Set Amplitude
 *
 *  Sets the amplitude parameter for an axis
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  amplitude  Amplitude in V, internal resolution is 1 mV
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setAmplitude( ANC_Handle device,
                                      Uit32      axisNo,
                                      double     amplitude );


/** @brief Set Frequency
 *
 *  Sets the frequency parameter for an axis
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  frequency  Frequency in Hz, internal resolution is 1 Hz
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setFrequency( ANC_Handle device,
                                      Uit32      axisNo,
                                      double     frequency );


/** @brief Set DC Output Voltage
 *
 *  Sets the DC level on the voltage output when no sawtooth based
 *  motion and no feedback loop is active.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  voltage    DC output voltage [V], internal resolution is 1 mV
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setDcVoltage( ANC_Handle device,
                                      Uit32      axisNo,
                                      double     voltage );


/** @brief Read back Amplitude
 *
 *  Reads back the amplitude parameter of an axis.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  amplitude  Output: Amplitude V
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getAmplitude( ANC_Handle device,
                                      Uit32      axisNo,
                                      double   * amplitude );


/** @brief Read back Frequency
 *
 *  Reads back the frequency parameter of an axis.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  frequency  Output: Frequency in Hz
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getFrequency( ANC_Handle device,
                                      Uit32      axisNo,
                                      double   * frequency );


/** @brief Read back DC Output Voltage
 *
 *  Reads back the current DC level. It may be the level that has been set
 *  by @ref ANC_setDcVoltage or the value currently adjusted by the feedback
 *  controller.
 *  Currently the function is only available for RES devices.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  voltage    Output: DC output voltage [V]
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getDcVoltage( ANC_Handle device,
                                      Uit32      axisNo,
                                      double   * voltage );


/** @brief Single Step
 *
 *  Triggers a single step in desired direction.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  backward   If the step direction is forward (0) or backward (1)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_startSingleStep( ANC_Handle device,
                                         Uit32      axisNo,
                                         Bln32      backward );


/** @brief Continous Motion
 *
 *  Starts or stops continous motion in forward or backward direction.
 *  Other kinds of motion are stopped.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  start      Starts (1) or stops (0) the motion
 *  @param  backward   If the move direction is forward (0) or backward (1)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_startContinousMove( ANC_Handle device,
                                            Uit32      axisNo,
                                            Bln32      start,
                                            Bln32      backward );


/** @brief Set Automatic Motion
 *
 *  Switches automatic moving (i.e. following the target position) on or off
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  enable     Enables (1) or disables (0) automatic motion
 *  @param  relative   If the target position is to be interpreted
 *                     absolute (0) or relative to the current position (1)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_startAutoMove( ANC_Handle device,
                                       Uit32      axisNo,
                                       Bln32      enable,
                                       Bln32      relative );


/** @brief Set Target Position
 *
 *  Sets the target position for automatic motion, see @ref ANC_startAutoMove.
 *  For linear type actuators the position unit is m, for goniometers and
 *  rotators it is degree.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  target     Target position [m] or [°]. Internal resulution is
 *                     1 nm or 1 µ°.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setTargetPosition( ANC_Handle device,
                                           Uit32      axisNo,
                                           double     target );


/** @brief Set Target Range
 *
 *  Defines the range around the target position where the target is
 *  considered to be reached.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  targetRg   Target range [m] or [°]. Internal resulution is
 *                     1 nm or 1 µ°.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setTargetRange( ANC_Handle device,
                                        Uit32      axisNo,
                                        double     targetRg );


/** @brief Set Target Ground Flag
 *
 *  Sets or clears the Target GND Flag. It determines the action performed
 *  in automatic positioning mode when the target position is reached.
 *  If set, the DC output is set to 0V and the position control feedback
 *  loop is stopped.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  targetGnd  Target GND Flag
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_setTargetGround( ANC_Handle device,
                                         Uit32      axisNo,
                                         Bln32      targetGnd );


/** @brief Read Current Position
 *
 *  Retrieves the current actuator position.
 *  For linear type actuators the position unit is m; for goniometers and
 *  rotators it is degree.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  position   Output: Current position [m] or [°]
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getPosition( ANC_Handle device,
                                     Uit32      axisNo,
                                     double   * position );


/** @brief Firmware version
 *
 *  Retrieves the version of currently loaded firmware.
 *  @param  device     Handle of the device to access
 *  @param  version    Output: Version number
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getFirmwareVersion( ANC_Handle device,
                                            Int32    * version );


/** @brief Configure Trigger Input
 *
 *  Enables the input trigger for steps.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  mode       Disable (0), Quadratur (1), Trigger(2) for external triggering
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureExtTrigger( ANC_Handle device,
                                             Uit32      axisNo,
                                             Uit32      mode );


/** @brief Configure A-Quad-B Input
 *
 *  Enables and configures the A-Quad-B (quadrature) input
 *  for the target position.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  enable     Enable (1) or disable (0) A-Quad-B input
 *  @param  resolution A-Quad-B step width in m. Internal resolution
 *                     is 1 nm.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureAQuadBIn( ANC_Handle device,
                                           Uit32      axisNo,
                                           Bln32      enable,
                                           double     resolution );


/** @brief Configure A-Quad-B output
 *
 *  Enables and configures the A-Quad-B output of the current position.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  enable     Enable (1) or disable (0) A-Quad-B output
 *  @param  resolution A-Quad-B step width in m; internal resolution is 1 nm
 *  @param  clock      Clock of the A-Quad-B output [s]. Allowed range is
 *                     40ns ... 1.3ms; internal resulution is 20ns.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureAQuadBOut( ANC_Handle device,
                                            Uit32      axisNo,
                                            Bln32      enable,
                                            double     resolution,
                                            double     clock );


/** @brief Configure Polarity of Range Trigger
 *
 *  Configure lower position for range Trigger.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  polarity   Polarity of trigger signal when position is
 *                     between lower and upper Low(0) and High(1)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureRngTriggerPol( ANC_Handle device,
                                                Uit32      axisNo,
                                                Uit32      polarity);

/** @brief Configure Range Trigger
 *
 *  Configure lower position for range Trigger.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  lower	     Lower position for range trigger
 *  @param  upper	     Upper position for range trigger
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureRngTrigger( ANC_Handle device,
                                             Uit32      axisNo,
                                             Uit32      lower,
                                             Uit32      upper);

/** @brief Configure Epsilon of Range Trigger
 *
 *  Configure hysteresis for range Trigger.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  epsilon    hysteresis in nm / mdeg
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureRngTriggerEps( ANC_Handle device,
                                                Uit32      axisNo,
                                                Uit32      epsilon);

/** @brief Configure NSL Trigger
 *
 *  Enables NSL Input as Trigger Source.
 *  @param  device     Handle of the device to access
 *  @param  enable     disable(0), enable(1)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureNslTrigger( ANC_Handle device,
                                             Bln32      enable);

/** @brief Configure NSL Trigger Axis
 *
 *  Selects Axis for NSL Trigger.
 *  @param  device     Handle of the device to access
 *  @param  axisNo	   Axis number (0 ... 2)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_configureNslTriggerAxis( ANC_Handle device,
                                                 Uit32      axisNo);


/** @brief Select Actuator
 *
 *  Selects the actuator to be used for the axis from actuator presets.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  actuator   Actuator selection (0 ... 255)
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_selectActuator( ANC_Handle device,
                                        Uit32      axisNo,
                                        Uit32      actuator );


/** @brief Get Actuator Name
 *
 *  Get the name of the currently selected actuator
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  name       Output: Name of the actuator as NULL-terminated c-string.
 *                     The string buffer should be at least 20 bytes long.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getActuatorName( ANC_Handle device,
                                         Uit32      axisNo,
                                         Int8     * name );


/** @brief Get Actuator Type
 *
 *  Get the type of the currently selected actuator
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  type       Output: Type of the actuator
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getActuatorType( ANC_Handle         device, 
                                         Uit32              axisNo,
                                         ANC_ActuatorType * type );


/** @brief Get LUT Name
 *
 *  Get the name of the currently selected sensor lookup table.
 *  The function is only available in RES devices.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  name       Output: Name of the LUT as NULL-terminated c-string.
 *                     The string buffer should be at least 20 bytes long.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_getLutName( ANC_Handle device,
                                    Uit32      axisNo,
                                    Int8     * name );



/** @brief Measure Motor Capacitance
 *
 *  Performs a measurement of the capacitance of the piezo motor and
 *  returns the result. If no motor is connected, the result will be 0.
 *  The function doesn't return before the measurement is complete;
 *  this will take a few seconds of time.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  cap        Output: Capacitance [F]
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_measureCapacitance( ANC_Handle   device,
                                            Uit32        axisNo,
                                            double     * cap );


/** @brief Save Parameters
 *
 *  Saves parameters to persistent flash memory in the device.
 *  They will be present as defaults after the next power-on.
 *  The following parameters are affected:
 *  @ref ANC_setAmplitude "Amplitude",
 *  @ref ANC_setFrequency "frequency",
 *  @ref ANC_setTargetRange "targetRange",
 *  @ref ANC_setTargetGround "targetGround", 
 *  @ref ANC_selectActuator "actuator selections",
 *  as well as trigger and quadrature settings.
 *  @param  device     Handle of the device to access
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_saveParams( ANC_Handle device );


/** @brief Load Lookup Table
 *
 *  Loads a sensor lookup table from a file into the device.
 *  The function is only available for ANC350Res devices.
 *  @param  device     Handle of the device to access
 *  @param  axisNo     Axis number (0 ... 2)
 *  @param  fileName   Name of the LUT file to read, optionally with path.
 *  @return            Error code
 */
ANC_API Int32 WINCC ANC_loadLutFile( ANC_Handle   device,
                                     Uit32        axisNo,
                                     const char * fileName );

#endif 

