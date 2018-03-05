'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: mx_series
   :synopsis: Lower level embedded systems serial communication library.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 30, 2015
:Description: Contains serial communication code for communicating to mx series Dynamixel servos.
'''

import dynamixel
import serial

dynamixel = dynamixel.Dynamixel

previousGoalPositionBytes = {}
servoResolution = 0.088 #Deg/tick

class MXCommands(dynamixel):
    def __init__(self, servoSerialObject, appendPackets=False, *lineDriverSerialObject):
        super(MXCommands, self).__init__(servoSerialObject, appendPackets, *lineDriverSerialObject)
                
        self.functionCallList = None #List of getter functions that have been called with servoID in order. Not used for MXCommands instances

    #READ ONLY ACCESS
    def getModelNumber(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x00, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getModelNumber])
    
    def getFirmwareVersion(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x02, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getFirmwareVersion])
            
    def getPresentPosition(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x24, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPresentPosition])
        
    def getPresentSpeed(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x26, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPresentSpeed])
        
    def getPresentLoad(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x28, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPresentLoad])
        
    def getPresentVoltage(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x2A, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPresentVoltage])
        
    def getPresentTemperature(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x2B, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPresentTemperature])
            
    def getRegistered(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x2C, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getRegistered])
        
    def getMoving(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x2E, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getMoving])     
    
    #READ ACCESS
    def getID(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x03, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getID])
        
    def getBaudRate(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x04, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getBaudRate])
        
    def getReturnDelayTime(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x05, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getReturnDelayTime])
        
    def getCWAngleLimit(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x06, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCWAngleLimit])
        
    def getCCWAngleLimit(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x08, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCCWAngleLimit])
        
    def getHighestLimitTemperature(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x0B, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getHighestLimitTemperature])
        
    def getLowestLimitVoltage(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x0C, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getLowestLimitVoltage])
        
    def getHighestLimitVoltage(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x0D, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getHighestLimitVoltage])
        
    def getMaxTorque(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x0E, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getMaxTorque])
        
    def getStatusReturnLevel(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x10, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getStatusReturnLevel])
        
    def getAlarmLED(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x11, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getAlarmLED])
        
    def getAlarmShutdown(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x12, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getAlarmShutdown])
            
    def getMultiTurnOffset(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x14, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getMultiTurnOffset])
            
    def getResolutionDivider(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x16, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getResolutionDivider])
        
    def getTorqueEnable(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x18, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getTorqueEnable])
        
    def getLED(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x19, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getLED])
        
    def getD(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x1A, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getD])
        
    def getI(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x1B, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getI])
        
    def getP(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x1C, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getP])
    
    def getGoalPosition(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x1E, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getGoalPosition])
        
    def getMovingSpeed(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x20, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getMovingSpeed])
        
    def getTorqueLimit(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x22, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getTorqueLimit])
        
    def getLock(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x2F, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getLock])
    
    def getPunch(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x30, 0x02)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getPunch])
            
    def getGoalAcceleration(self, servoID): #Different from ax series
        self.sendDataPacket(servoID, self.READ_DATA, 0x49, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getGoalAcceleration])
    
    #WRITE ACCESS    
    def setID(self, servoID, ID):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x03, ID)
        
    def setBaudRate(self, servoID, baudRate):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x04, baudRate)
        
    def setReturnDelayTime(self, servoID, returnDelayTime):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x05, int(round(returnDelayTime*0.5)))
        
    def setCWAngleLimit(self, servoID, CWAngleLimit): #CWAngleLimit in degrees from 0-296.67 deg
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x06, int(round(CWAngleLimit/servoResolution)) & 0xFF, int(round(CWAngleLimit/servoResolution)) >> 8)
        
    def setCCWAngleLimit(self, servoID, CCWAngleLimit): #CCWAngleLimit in degrees from 0-296.67 deg
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x08, int(round(CCWAngleLimit/servoResolution)) & 0xFF, int(round(CCWAngleLimit/servoResolution)) >> 8)
        
    def setHighestLimitTemperature(self, servoID, highestLimitTemperature):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x0B, highestLimitTemperature)
        
    def setLowestLimitVoltage(self, servoID, lowestLimitVoltage):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x0C, int(round(lowestLimitVoltage*10)))
        
    def setHighestLimitVoltage(self, servoID, highestLimitVoltage):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x0D, int(round(highestLimitVoltage*10)))
        
    def setMaxTorque(self, servoID, maxTorque): #maxTorque in percent from 0-100%
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x0E, int(round((maxTorque*1023.0)/100.0)) & 0xFF, int(round((maxTorque*1023.0)/100.0)) >> 8)
        
    def setStatusReturnLevel(self, servoID, statusReturnLevel):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x10, statusReturnLevel)
        
    def setAlarmLED(self, servoID, alarmLED):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x11, alarmLED)
        
    def setAlarmShutdown(self, servoID, alarmShutdown):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x12, alarmShutdown)
        
    def setMultiTurnOffset(self, servoID, multiTurnOffset): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x14, multiTurnOffset)
        
    def setResolutionDivider(self, servoID, resolutionDivider): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x16, resolutionDivider)
        
    def setTorqueEnable(self, servoID, torqueEnable):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x18, torqueEnable)
        
    def setLED(self, servoID, LED):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x19, LED)
        
    def setD(self, servoID, D): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1A, D)
        
    def setI(self, servoID, I): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1B, I)
        
    def setP(self, servoID, P): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1C, P)
        
    def setGoalPosition(self, servoID, goalPosition): #goalPosition in degrees from 0-296.67 deg
        global previousGoalPositionBytes

        #Adds servos to previousGoalPositionBytes dictionary if servo does not already exist
        if servoID not in previousGoalPositionBytes:
            previousGoalPositionBytes[servoID] = [0, 0]
           
        msb, lsb = int(round(goalPosition/servoResolution)) >> 8, int(round(goalPosition/servoResolution)) & 0xFF 
           
        #Prevents from sending same data over again to servo
        if previousGoalPositionBytes[servoID] != [msb, lsb]:
            self.sendDataPacket(servoID, self.WRITE_DATA, 0x1E, lsb, msb)
        previousGoalPositionBytes[servoID] = [msb, lsb]
        
    def setMovingSpeed(self, servoID, movingSpeed): #movingSpeed in RPM from 0-60 RPM
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x20,  int(round((movingSpeed*1023.0)/114.0)) & 0xFF, int(round((movingSpeed*1023.0)/114.0)) >> 8)
        
    def setTorqueLimit(self, servoID, torqueLimit): #torqueLimit in percent from 0-100%
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x22, int(round((torqueLimit*1023.0)/100.0)) & 0xFF, int(round((torqueLimit*1023.0)/100.0)) >> 8)
        
    def setLock(self, servoID, lock):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x2F, lock)
    
    def setPunch(self, servoID, punch):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x30, punch & 0xFF, punch >> 8)
        
    def setGoalAcceleration(self, servoID, goalAcceleration): #Different from ax series
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x49, int(round(goalAcceleration/8.583)))


class MXCommandParse(MXCommands):
    def __init__(self, servoSerialObject, *lineDriverSerialObject):
        
        super(MXCommandParse, self).__init__(servoSerialObject, appendPackets = True, *lineDriverSerialObject)
        
        self.servoSerialObject = servoSerialObject
        
        self.setStatusReturnLevel(0xFE, 0x01) #Sets all servos to have a status return when only requesting getter functions. All servos must be in this mode in order for this class to work properly.
        self.setReturnDelayTime(0xFE, 500) #Sets all servos to have a return delay time of 500 us. All servos must speak at this speed in order for this class to work properly.
        
        self.appendPackets = True #Must be appending packets in order for this class to work properly
        self.functionCallList = [] #List of functions that have been called with servoID in order. This allows the program to know what packet belongs to which function call when it is recieved
        
        self.currentDataPacket = {}
        
        #Read Only Access Values
        self.modelNumberData = ()               #Should always be 12 for AX-12 series
        self.firmwareVersionData = {}           #Firmware Version Number
        self.presentPositionData = {}           #0-296.67 deg
        self.presentSpeedData = {}              #-114-114 RPM (CCW is positive, CW is negative)
        self.presentLoadData = {}               #-100-100 % (CCW is positive, CW is negative)
        self.presentVoltageData = {}            #0-25.5 V
        self.presentTemperatureData = {}        #0-255 C
        self.registeredData = {}                #0-1 False/True
        self.movingData = {}                    #0-1 False/True
        
        #Read/Write Access Values
        self.IDData = {}                        #Servo ID Number
        self.baudRateData = {}                  #Baud Rate Number
        self.returnDelayTimeData = {}           #0-508 us
        self.CWAngleLimitData = {}              #0-296.67 deg
        self.CCWAngleLimitData = {}             #0-296.67 deg
        self.highestLimitTemperatureData = {}   #20-70 C
        self.lowestLimitVoltageData = {}        #5-25 V
        self.highestLimitVoltageData = {}       #5-25 V
        self.maxTorqueData = {}                 #0-100 %
        self.statusReturnLevelData = {}         #0-2 unitless (refer to data sheet)
        self.alarmLEDData = {}                  #0-127 unitless (refer to data sheet)
        self.alarmShutdownData = {}             #0-127 unitless (refer to data sheet)
        self.multiTurnOffsetData = {}           #-24576-24576 (refer to data sheet)
        self.resolutionDividerData = {}         #1-4 (refer to data sheet)
        self.torqueEnableData = {}              #0-1 False/True
        self.ledData = {}                       #0-1 False/True
        self.DData = {}                         #0-255 Gain
        self.IData = {}                         #0-255 Gain
        self.PData = {}                         #0-255 Gain
        self.goalPositionData = {}              #0-360.36 deg
        self.movingSpeedData = {}               #0-67 RPM
        self.torqueLimitData = {}               #0-100 %
        self.lockData = {}                      #0-1 False/True
        self.punchData = {}                     #32-1023 unitless
        self.goalAccelerationData = {}          #0-2180.082 deg/sec^2
        

    def run(self):
        while self.runThread:
            self.recieveDataPacket(self.appendPackets)
            
            while len(self.data) != 0 and len(self.functionCallList) != 0: #A while statement to make sure data and functionCallList arn't growing enormously huge
                #Storing both function calls and data packets in list so I know what data packet belongs to which function call. This allows me to parse the data accordingly.
                userCalledServoID, userCalledFunction = self.functionCallList.pop(0)
                header1, header2, servoID, length, error, params, checksum = self.data.pop(0)
                self.currentDataPacket[servoID] = [header1, header2, servoID, length, error, params, checksum]
                
                #SORTING DATA
                #Read Only
                if userCalledFunction == self.getModelNumber:
                    self.modelNumberData[servoID] = params[1] << 8 | params[0]
                    
                elif userCalledFunction == self.getFirmwareVersion:
                    self.firmwareVersionData[servoID] = params[0]
                    
                elif userCalledFunction == self.getPresentPosition:
                    self.presentPositionData[servoID] = round((params[1] << 8 | params[0])*servoResolution, 2)
                    
                elif userCalledFunction == self.getPresentSpeed:
                    speedTicks = params[1] << 8 | params[0]
                    if speedTicks <= 1023:
                        self.presentSpeedData[servoID] = round((speedTicks*114.0)/1023.0, 2)
                    elif speedTicks > 1023:
                        self.presentSpeedData[servoID] = -round(((speedTicks-1023)*114.0)/1023.0, 2)
                
                elif userCalledFunction == self.getPresentLoad:
                    loadTicks = params[1] << 8 | params[0]
                    if loadTicks <= 1023:
                        self.presentLoadData[servoID] = round((loadTicks*100.0)/1023.0, 2)
                    elif loadTicks > 1023:
                        self.presentLoadData[servoID] = -round(((loadTicks-1023)*100.0)/1023.0, 2)        
                
                elif userCalledFunction == self.getPresentVoltage:
                    self.presentVoltageData[servoID] = params[0]/10.0
                    
                elif userCalledFunction == self.getPresentTemperature:
                    self.presentTemperatureData[servoID] = params[0]
                    
                elif userCalledFunction == self.getRegistered:
                    self.registeredData[servoID] = params[0]
                    
                elif userCalledFunction == self.getMoving:
                    self.movingData[servoID] = params[0]     
                
                #Read/Write
                elif userCalledFunction == self.getID:
                    self.IDData[servoID] = params[0]
                    
                elif userCalledFunction == self.getBaudRate:
                    self.baudRateData[servoID] = params[0]
                    
                elif userCalledFunction == self.getReturnDelayTime:
                    self.returnDelayTimeData[servoID] = params[0]*2
                
                elif userCalledFunction == self.getCWAngleLimit:
                    self.CWAngleLimitData[servoID] = round((params[1] << 8 | params[0])*servoResolution, 2)
                    
                elif userCalledFunction == self.getCCWAngleLimit:
                    self.CCWAngleLimitData[servoID] = round((params[1] << 8 | params[0])*servoResolution, 2)
                    
                elif userCalledFunction == self.getHighestLimitTemperature:
                    self.highestLimitTemperatureData[servoID] = params[0]
                
                elif userCalledFunction == self.getLowestLimitVoltage:
                    self.lowestLimitVoltageData[servoID] = params[0]*0.1
                    
                elif userCalledFunction == self.getHighestLimitVoltage:
                    self.highestLimitVoltageData[servoID] = params[0]*0.1
                    
                elif userCalledFunction == self.getMaxTorque:
                    self.maxTorqueData[servoID] = round(((params[1] << 8 | params[0])*100.0)/1023.0, 1)
                    
                elif userCalledFunction == self.getStatusReturnLevel:
                    self.statusReturnLevelData[servoID] =  params[0]
                    
                elif userCalledFunction == self.getAlarmLED:
                    self.alarmLEDData[servoID] = params[0]
                    
                elif userCalledFunction == self.getAlarmShutdown:
                    self.alarmShutdownData[servoID] = params[0]
                    
                elif userCalledFunction == self.getMultiTurnOffset:
                    self.multiTurnOffsetData[servoID] = params[1] << 8 | params[0]
                    
                elif userCalledFunction == self.getResolutionDivider:
                    self.resolutionDividerData[servoID] = params[0]

                elif userCalledFunction == self.getTorqueEnable:
                    self.torqueEnableData[servoID] = params[0]
                    
                elif userCalledFunction == self.getLED:
                    self.ledData[servoID] = params[0]
                    
                elif userCalledFunction == self.getD:
                    self.DData[servoID] = params[0]
                    
                elif userCalledFunction == self.getI:
                    self.IData[servoID] = params[0]
                    
                elif userCalledFunction == self.getP:
                    self.PData[servoID] = params[0]
                    
                elif userCalledFunction == self.getLED:
                    self.ledData[servoID] = params[0]
                    
                elif userCalledFunction == self.getLED:
                    self.ledData[servoID] = params[0]
                
                elif userCalledFunction == self.getGoalPosition:
                    self.goalPositionData[servoID] = round((params[1] << 8 | params[0])*servoResolution, 2)
                
                elif userCalledFunction == self.getMovingSpeed:
                    self.movingSpeedData[servoID] = round(((params[1] << 8 | params[0])*114.0)/1023.0, 2)
                    
                elif userCalledFunction == self.getTorqueLimit:
                    self.torqueLimitData[servoID] = round(((params[1] << 8 | params[0])*100.0)/1023.0, 1)    
                
                elif userCalledFunction == self.getLock:
                    self.lockData[servoID] = params[0]          
                    
                elif userCalledFunction == self.getPunch:
                    self.punchData[servoID] = params[1] << 8 | params[0]
                    
                elif userCalledFunction == self.getGoalAcceleration:
                    self.goalAccelerationData[servoID] = params[0]*8.583
                    
                    
if __name__ == "__main__":
    import time

    mx28 = MXCommandParse(serial.Serial("COM8", 1000000))
    mx28.start()
    
    while True:
        '''
        mx28.getPresentPosition(1)
        mx28.getPresentPosition(2)
        mx28.getPresentPosition(3)
        mx28.getPresentPosition(4)
        mx28.getPresentPosition(5)
        mx28.getPresentPosition(6)
        mx28.getPresentPosition(7)
        mx28.getPresentPosition(8)
        '''
        '''
        mx28.getCWAngleLimit(1)
        mx28.getCWAngleLimit(2)
        mx28.getCWAngleLimit(3)
        mx28.getCWAngleLimit(4)
        mx28.getCWAngleLimit(5)
        mx28.getCWAngleLimit(6)
        mx28.getCWAngleLimit(7)
        mx28.getCWAngleLimit(8)
        '''
        mx28.getReturnDelayTime(1)
        mx28.getReturnDelayTime(2)
        mx28.getReturnDelayTime(3)
        mx28.getReturnDelayTime(4)
        mx28.getReturnDelayTime(5)
        mx28.getReturnDelayTime(6)
        mx28.getReturnDelayTime(7)
        mx28.getReturnDelayTime(8)
        time.sleep(0.3)
        
        print mx28.returnDelayTimeData
        #print mx28.CWAngleLimitData
        
        