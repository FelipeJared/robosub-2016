'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: external_sparton_ahrs
   :synopsis: Sparton Altitude Heading Reference System (AHRS) device communication.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on May 28, 2014
:Description: This module contains the commands for all the functions that can be called with the legacy protocol for the Sparton AHRS

'''

import serial
import threading
import time
import struct
import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

class SpartonAhrsDataPacket():
    '''
    This class contains setters and getters commands for the Sparton AHRS in Legacy format. It only handles the sending values.
    '''
    def __init__(self, comPort):
        '''
        Initializes the Sparton AHRS and array of location values.
        
        **Parameters**: \n
        * **comPort** - Serial port number that the Sparton AHRS is connected to.
        
        **Return**: \n
        * **No Return.**\n
        '''
        self.SPARTON_AHRS = serial.Serial(comPort, 115200)
        self.locationArray = [[0x01, 9], [0x02, 5], [0x09, 5], [0x83, 5], [0x0F, 5], [0x8B, 5], [0x8C, 5], [0x8D, 5], [0x8E, 5], [0x04, 11], [0x56, 4], [0x08, 5], [0x05, 9], [0x06, 7], [0x07, 11], [0x11, 5], [0x57, 4], [0x4A, 4]]
        
    def rawMagneticsGet(self):
        '''
        Reads current magnetics directly from magnetometers (Mx, My, and Mz). 
        These are raw sensor readings and do not yet have any calibration parameters applied.
        
        Send: 3 Byte (0xA4,0x01,0xA0)
        
        Response: 9 Bytes (0xA4,0x01,<Mx>,<My>,<Mz as 16-bit integers MS byte first>,0xA0)
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x01, 0xA0]))
        
    def trueHeadingGet(self):
        '''
        Reads the current true heading. The heading is compensated for platform tilt. 
        True heading is the magnetic heading corrected for magnetic variation.
        
        Send: 3 Byte (0xA4,0x02,0xA0)
        
        Response: 5 Bytes (0xA4,0x02,<Heading as a 16-bit signed integer>,0xA0)
        Heading (degrees) = (16-bit Heading value)*360/4096
        Heading Range = 0.0 to +359.9
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x02, 0xA0]))
        
    def magneticHeadingGet(self):
        '''
        Reads the current magnetic heading. The heading is compensated for platform tilt.
        
        Send: 3 Bytes (0xA4,0x09,0xA0)
       
        Response: 5 Bytes (0xA4,0x09,<Heading as a 16-bit signed integer>,0xA0)
        Heading (degrees) = (16-bit Heading value)*360/4096
        Heading Range = 0.0 to +359.9
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x09, 0xA0]))
        
    def magneticVariationSet(self, byte1, byte2):
        '''
        Set the magnetic variation angle. The heading will be adjusted to indicate true north
        instead of magnetic north. Magnetic variation angles >+180 and <-180 will be limited to +180 and -180 respectively.
        
        Send: 5 Bytes (0xA4,0x83,<16-bit signed integer value MSB first>,0xA0)
        
        Response: 5 Bytes (0xA4,0x83,<16-bit signed Variation>,0xA0)
        16-bit signed integer = (Magnetic Variation)*10.0
        
        **Parameters**: \n
        * **byte1** - The first byte of the setter variation angle.
        * **byte2** - The second byte of the setter variation angle.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x83, byte1, byte2, 0xA0]))
        
    def automaticMagneticVariationGet(self):
        '''
        Latitude, Longitude, Altitude, and Day should be programmed separately using their 
        respective commands before issuing this command. Automatic variation will compute the local 
        magnetic variation based on the device's current geographical location 
        (geodetic coordinate system referenced to the WGS 84 ellipsoid). Once the computation is 
        complete, the magnetic variation will be updated in the compass. NOTE: TO RETAIN MAGNETIC 
        VARIATION ACCURACY, THE MAGNETIC MODEL MUST BE UPDATED EVERY FIVE YEARS. A SEPARATE PROGRAM 
        IS AVAILABLE ON THE SUPPLIED CD WHICH WILL ASSIST IN DOWNLOADING NEW COEFFICIENTS INTO THE 
        DIGITAL COMPASS. THIS ONLY AFFECTS THE CALCULATION OF TRUE HEADING AND DOES NOT AFFECT MAGNETIC 
        HEADING ACCURACY. NOTE: Resetting the magnetic parameters to the factory default does not affect 
        the magnetic variation information. To clear out the magnetic variation, manually set the 
        magnetic variation to zero
        
        Send: 3 Byte (0xA4,0x0F,0xA0)
        
        Response: 5 Bytes (0xA4,0x0F,<Variation as a 16-bit signed integer>,0xA0)
        16-bit signed integer = (Magnetic Variation)*10.0
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''        
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x0F, 0xA0]))
        
    def latitudeSet(self, byte1, byte2):
        '''
        Set the geodetic latitude angle in degrees (geodetic coordinate system referenced 
        to the WGS 84 ellipsoid). The magnetic variation will not change until latitude, longitude, 
        altitude, and day have been programmed and the Automatic Variation command is issued. 
        Latitude >+90 or <-90 will be limited to +90 and -90 respectively.
        
        Send: 5 Bytes (0xA4,0x8B,<16-bit signed integer value MSB first>,0xA0)
        
        Response: 5 Bytes (0xA4,0x8B,<16-bit Latitude>,0xA0)
        16-bit signed integer = (North(+) or South(-) Latitude in degrees)*100.0
        
        **Parameters**: \n
        * **byte1** - The first byte of the setter geodetic latitude angle in degrees.
        * **byte2** - The second byte of the setter geodetic latitude angle in degrees.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x8B, byte1, byte2, 0xA0]))
        
    def longitudeSet(self, byte1, byte2):
        '''
        Set the geodetic longitude angle in degrees (geodetic coordinate system referenced 
        to the WGS 84 ellipsoid). The magnetic variation will not change until latitude, longitude, 
        altitude, and day have been programmed and the Automatic Variation command is issued. . 
        Latitude >+180 or <-180 will be limited to +180 and -180 respectively.
        
        Send: 5 Bytes (0xA4,0x8C, 16-bit signed integer value MSB first,0xA0)
        
        Response: 5 Bytes (0xA4,0x8C, 16-bit signed Longitude,0xA0)
        16-bit signed integer = (East(+) or West(-) Longitude in degrees)*100.0
        
        **Parameters**: \n
        * **byte1** - The first byte of the setter geodetic longitude angle in degrees.
        * **byte2** - The second byte of the setter geodetic longitude angle in degrees.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x8C, byte1, byte2, 0xA0]))
        
    def altitudeSet(self, byte1, byte2):
        '''
        Set the geodetic altitude in meters above sea level (geodetic coordinate system 
        referenced to the WGS 84 ellipsoid). The magnetic variation will not change until latitude, 
        longitude, altitude, and day have been programmed and the Automatic Variation command is 
        issued. Altitude >+32767 or <-32767 will be limited to +32767 and -32767 respectively.
        
        Send: 5 Bytes (0xA4,0x8D, 16-bit signed integer value MSB first,0xA0)
        
        Response: 5 Bytes (0xA4,0x8D, 16-bit signed Altitude,0xA0)
        16-bit signed integer = +/- Altitude in meters
        
        **Parameters**: \n
        * **byte1** - The first byte of the setter geodetic altitude in meters above sea level.
        * **byte2** - The second byte of the setter geodetic altitude in meters above sea level.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x8D, byte1, byte2, 0xA0]))
        
    def daySet(self, byte1, byte2):
        '''
        The day is entered as a fractional year based on the current day of the year 
        (i.e. February 15 is the 46th day of the 2008. In fractional terms, this would be 46/365 = 0.126. 
        The Fractional Day value for February 15, 2008 would then be 2008.1 (resolution beyond a 
        tenth causes negligible change in variation). The magnetic variation will not change until 
        latitude, longitude, altitude, and day have been programmed and the Automatic Variation 
        command is issued. Day < 2005 will be limited to 2005.

        Send: 5 Bytes (0xA4,0x8E, 16-bit unsigned integer value MSB first,0xA0)
        
        Response: 5 Bytes (0xA4,0x8E, 16-bit unsigned Day,0xA0)
        16-bit unsigned integer = (Fractional Day)*10.0
        
        **Parameters**: \n
        * **byte1** - The first byte of the setter day-of-year.
        * **byte2** - The second byte of the setter day-of-year.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x8E, byte1, byte2, 0xA0]))
        
    def magneticVectorGet(self):
        '''
        Measures the magnetic field strength along each axis (X, Y, and Z) and total 
        absolute field strength (MAtotal) in milligauss.
        
        Send: 3 Bytes (0xA4,0x04,0xA0)
        
        Response: 11 Bytes (0xA4, 0x04, MAx, MAy, MAz, MAtotal as 16-bit integers, 0xA0)
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x04, 0xA0]))
        
    def magneticCalibrationSet(self, byte1):
        '''
        The method for calibration matches the description in the NMEA section of this document.
        
        Send: 4 Bytes (0xA4,0x56, 8-bit configuration {0x00=OFF,0x01=3D,0x02=2D,0x03 = User,0xFF = RESET},0xA0) 
        
        Response: 4 Bytes (0xA4,0x56, 8-bit configuration,0xA0)
        
        **Parameters**: \n
        * **byte1** - Magnetic calibration set value.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x56, byte1, 0xA0]))
        
    def magneticAdaptionErrorGet(self):
        '''
        Indicates quality of the adaptive magnetic calibration process. Smaller 
        values represent better magnetic calibration. Adaption error is limited to the range 0 to 10,000.
        
        Send: 3 Byte (0xA4,0x08,0xA0)
        
        Response: 5 Bytes (0xA4,0x08, Error as a 16-bit unsigned integer,0xA0)
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x08, 0xA0]))
        
    def rawAccelerationGet(self):
        '''
        Reads current acceleration directly from accelerometers (AccelX, AccelY, AccelZ). 
        These are raw sensor readings and do not yet have any calibration parameters applied.
        
        Send: 3 Bytes (0xA4,0x05,0xA0)
        
        Response: 9 Bytes (0xA4,0x05, AccelX, AccelY, AccelZ as 16-bit integers,0xA0)
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x05, 0xA0]))
        
    def pitchAndRollGet(self):
        '''
        Reads the current platform orientation (Pitch and Roll).
        
        Send: 3 Byte (0xA4,0x06,0xA0)
        
        Response: 7 Bytes (0xA4,0x06, Pitch, Roll as 16-bit signed integers,0xA0)
        Pitch (in degrees) = (Response Value)*90/4096
        Pitch Range = -90 to +90
        Roll (in degrees) = (Response Value)*180/4096
        Acceleration Vector Roll Range = -180 to +180
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x06, 0xA0]))
        
    def accelerationVectorGet(self):
        '''
        Measures the acceleration along each axis (X, Y, and Z) and total absolute 
        strength (Atotal) in milli-g.
        
        Send: 3 Byte (0xA4,0x07,0xA0)
        
        Response: 11 Bytes (0xA4,0x07, Ax, Ay, Az, Atotal as 16-bit integers,0xA0)
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x07, 0xA0]))
        
    def temperatureGet(self):
        '''
        Description: Reads the internal temperature channel of the on-board microcontroller. 
        This measurement is calibrated at the factory, though not required by the compass in 
        determining an accurate heading.
        
        Send: 3 Bytes (0xA4,0x11,0xA0)
        
        Response: 5 Bytes (0xA4,0x11, Temperature as 16-bit signed integer MSB first,0xA0)
        Temperature_C = (Temperature_MSB*256 + Temperature_LSB)/10.0
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x11, 0xA0]))
        
    def baudRateSet(self, byte1):
        '''
        The factory default BAUD setting is 115200 Baud (0x08). When the baud rate 
        command is issued on the UART, the compass will echo back the command once at the current 
        baud rate and then again at the new baud rate. The baud rate will be stored in EEPROM and 
        will become the new operating communication rate for the UART. The baud rate will apply to 
        Legacy, RFS, NorthTek and NMEA commands issued on the UART.
        
        Send: 4 Bytes (0xA4,0x57, 8-bit BAUD value MSB first,0xA0)
        
        Response: 4 Bytes (0xA4,0x57, 8-bit BAUD value,0xA0)
        Acceptable Baud Rate Values:
        0x01 = 1200 Baud
        0x02 = 2400 Baud
        0x03 = 4800 Baud
        0x04 = 9600 Baud
        0x05 = 19.2 kBaud
        0x06 = 38.4 kBaud
        0x07 = 57.6 kBaud
        0x08 = 115.2 kBaud
        
        **Parameters**: \n
        * **byte1** - Desired baud rate value.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x57, byte1, 0xA0]))
        
    def mountingConfigurationSet(self, byte1):
        '''
        Sets the mounting orientation of the compass platform. The default 
        orientation is horizontal. For vertical orientations consult the particular device's 
        data sheet. To determine the orientation setting, read the acceleration vector. When 
        in a static level condition, Az should be approximately +1000mg and Ax and Ay should 
        be close to zero.
        
        Send: 4 Bytes (0xA4,0x4A, 8-bit orientation {0x00=Horizontal,0x01=Vertical},0xA0)
        
        Response: 4 Bytes (0xA4,0x4A, 8-bit orientation,0xA0)
        
        **Parameters**: \n
        * **byte1** - Desired mounting orientation of the compass platform.
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.SPARTON_AHRS.write(bytearray([0xA4, 0x4A, byte1, 0xA0]))
        
    
    def extractSensorData(self, spartonAhrsDataPacket):
        '''
        Reads in the raw transmission and extracts all bytes of the packet
        
        **Parameters**: \n
        * **spartonAhrsDataPacket** - The raw data packet transmission. It includes all meta-data and protocol-specific junk.
         
        **Returns**: \n
        * **sensorValues** - The meaningful data (the payload).\n
        '''
        
        sensorValues = []
        if (spartonAhrsDataPacket[1] == 0x01):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            sensorValues.append(spartonAhrsDataPacket[4] << 8 | spartonAhrsDataPacket[5] << 0)
            sensorValues.append(spartonAhrsDataPacket[6] << 8 | spartonAhrsDataPacket[7] << 0) 
        
        elif (spartonAhrsDataPacket[1] == 0x02):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*360.0/4096)
            
        elif (spartonAhrsDataPacket[1] == 0x09):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*360.0/4096)
            
        elif (spartonAhrsDataPacket[1] == 0x83):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*10.0)
            
        elif (spartonAhrsDataPacket[1] == 0x0F):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*10.0)
            
        elif (spartonAhrsDataPacket[1] == 0x8B):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*100.0)
            
        elif (spartonAhrsDataPacket[1] == 0x8C):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x8D):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x8E):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)*10.0)
            
        elif (spartonAhrsDataPacket[1] == 0x04):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            sensorValues.append(spartonAhrsDataPacket[4] << 8 | spartonAhrsDataPacket[5] << 0)
            sensorValues.append(spartonAhrsDataPacket[6] << 8 | spartonAhrsDataPacket[7] << 0)
            sensorValues.append(spartonAhrsDataPacket[8] << 8 | spartonAhrsDataPacket[9] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x56):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2])
            
        elif (spartonAhrsDataPacket[1] == 0x08):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x05):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            sensorValues.append(spartonAhrsDataPacket[4] << 8 | spartonAhrsDataPacket[5] << 0)
            sensorValues.append(spartonAhrsDataPacket[6] << 8 | spartonAhrsDataPacket[7] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x06):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(((struct.unpack('h', struct.pack('H', spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)))[0]*90.0/4096))
            sensorValues.append(((struct.unpack('h', struct.pack('H', spartonAhrsDataPacket[4] << 8 | spartonAhrsDataPacket[5] << 0)))[0]*180.0/4096))
            
        elif (spartonAhrsDataPacket[1] == 0x07):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2] << 8 | spartonAhrsDataPacket[3] << 0)
            sensorValues.append(spartonAhrsDataPacket[4] << 8 | spartonAhrsDataPacket[5] << 0)
            sensorValues.append(spartonAhrsDataPacket[6] << 8 | spartonAhrsDataPacket[7] << 0)
            sensorValues.append(spartonAhrsDataPacket[8] << 8 | spartonAhrsDataPacket[9] << 0)
            
        elif (spartonAhrsDataPacket[1] == 0x11):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append((spartonAhrsDataPacket[2]*256 + spartonAhrsDataPacket[3])/10.0)
            
        elif (spartonAhrsDataPacket[1] == 0x57):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2])
            
        elif (spartonAhrsDataPacket[1] == 0x4A):
            sensorValues.append(spartonAhrsDataPacket[1])
            sensorValues.append(spartonAhrsDataPacket[2])
            
        
        return sensorValues
    
    def netHeading(self, headingValue):
        '''
        Initializes the heading such the the initial heading upon start is defined to be "0".
        
        **Parameters**: \n
        * **headingValue** - The current heading value from AHRS. 
         
        **Returns**: \n
        * **self.netValue** - The difference between the current heading and the initial heading (heading at start).\n
        '''
        
        global netValueIteration
        
        if netValueIteration == 0: 
            self.initialValue = headingValue
              
        self.netValue = headingValue - self.initialValue
        
        #This if statement will give you net value. Will go from 0 to 360, if gone over 360, will loop back to 0
        if self.netValue < 0:
            self.netValue = self.netValue + 360
            
        #This if statement will go from 0 to 180, if gone over 180, will loop to -179  
        if self.netValue >= 180:
            self.netValue = self.netValue - 360

        netValueIteration += 1
        
        return self.netValue
        
class SpartonAhrsResponse(threading.Thread):
    def __init__(self, comPort):
        '''
        Initializes the Sparton AHRS thread (starts thread process).
        
        **Parameters**: \n
        * **comPort** - Serial port number that the Sparton AHRS is connected to.
        
        **Return**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        self.comPort = comPort
        self.spartonAhrs = SpartonAhrsDataPacket(comPort) 
        self.runThread = True
        self.requestTime = 0.02 #How often I request data packets from device (100 hz/0.01 seconds is the fastest for Sparton)
        
        self.getList = []
        
    def run(self):
        '''
        Obtains heading, roll, and pitch data from the AHRS and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **comPort** - Serial port number that the Sparton AHRS is connected to.
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            
            time.sleep(0.02) #Slows down thread to save some power
            
            netRequestTimer = reqestTimer.netTimer(reqestTimer.cpuClockTimeInSeconds())
            if netRequestTimer >= self.requestTime:
                self.spartonAhrs.trueHeadingGet()
                self.spartonAhrs.pitchAndRollGet()
                reqestTimer.restartTimer()
            
            
            
            headingDataPacket = self.unpack()
            pitchRollDataPacket = self.unpack()
            
            try:
                if headingDataPacket != None or pitchRollDataPacket != None:
                    headingData = self.spartonAhrs.extractSensorData(headingDataPacket)
                    pitchRollData = self.spartonAhrs.extractSensorData(pitchRollDataPacket)

                    self.getList.append([headingData[1], pitchRollData[1], pitchRollData[2]])
            except:
                pass
                print "Couldn't get AHRS data packet."
    
    def unpack(self):
        '''
        Reads in the raw transmission and extracts all bytes of the packet
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **dataPacketIn** - The raw transmission packet.\n
        '''
        dataPacketIn = []
        if self.spartonAhrs.SPARTON_AHRS.inWaiting() != 0:
            dataPacketIn.append(ord(self.spartonAhrs.SPARTON_AHRS.read()))
            dataPacketIn.append(ord(self.spartonAhrs.SPARTON_AHRS.read()))
            
            for x in range(0, 18):
                if self.spartonAhrs.locationArray[x][0] == dataPacketIn[1]: # Determines which type of transmission it is (the size of the entire transmission).
                    for y in range(0, self.spartonAhrs.locationArray[x][1]-2): # Reads in the transmission
                        dataPacketIn.append(ord(self.spartonAhrs.SPARTON_AHRS.read()))
                    break
                
            if dataPacketIn[0] != 0xA4: #Checks if the data packet is good
                dataPacketIn = None

            return dataPacketIn
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False
