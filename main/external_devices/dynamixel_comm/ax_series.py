'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: ax_series
   :synopsis: Lower level embedded systems serial communication library.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 30, 2015
:Description: Contains serial communication code for communicating to ax series Dynamixel servos.
'''

'''
Created on Nov 30, 2015

@author: Austin

'''

import dynamixel
import serial

dynamixel = dynamixel.Dynamixel

previousGoalPositionBytes = {}
servoResolution = 0.29 #Deg/tick #0.29 for ax series, 0.088 for mx series

class AXCommands(dynamixel):
    def __init__(self, servoSerialObject, appendPackets=False, *lineDriverSerialObject):
        super(AXCommands, self).__init__(servoSerialObject, appendPackets, *lineDriverSerialObject)
                
        self.functionCallList = None #List of getter functions that have been called with servoID in order. Not used for AXCommands instances

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
        
    def getTorqueEnable(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x18, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getTorqueEnable])
        
    def getLED(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x19, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getLED])
        
    def getCWComplianceMargin(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x1A, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCWComplianceMargin])
        
    def getCCWComplianceMargin(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x1B, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCCWComplianceMargin])
        
    def getCWComplianceSlope(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x1C, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCWComplianceSlope])
    
    def getCCWComplianceSlope(self, servoID):
        self.sendDataPacket(servoID, self.READ_DATA, 0x1D, 0x01)
        if self.functionCallList != None:
            self.functionCallList.append([servoID, self.getCCWComplianceSlope])
        
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
        
    def setTorqueEnable(self, servoID, torqueEnable):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x18, torqueEnable)
        
    def setLED(self, servoID, LED):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x19, LED)
        
    def setCWComplianceMargin(self, servoID, CWComplianceMargin):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1A, int(round(CWComplianceMargin/servoResolution)))
        
    def setCCWComplianceMargin(self, servoID, CCWComplianceMargin):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1B, int(round(CCWComplianceMargin/servoResolution)))
        
    def setCWComplianceSlope(self, servoID, CWComplianceSlope):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1C, 1 << CWComplianceSlope)
    
    def setCCWComplianceSlope(self, servoID, CCWComplianceSlope):
        self.sendDataPacket(servoID, self.WRITE_DATA, 0x1D, 1 << CCWComplianceSlope)
        
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


class AXCommandParse(AXCommands):
    def __init__(self, servoSerialObject, *lineDriverSerialObject):
        
        super(AXCommandParse, self).__init__(servoSerialObject, appendPackets = True, *lineDriverSerialObject)
        
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
        self.torqueEnableData = {}              #0-1 False/True
        self.ledData = {}                       #0-1 False/True
        self.CWComplianceMarginData = {}        #0-73.95 deg
        self.CCWComplianceMarginData = {}       #0-73.95 deg
        self.CWComplianceSlopeData = {}         #1-7 steps (refer to data sheet)
        self.CCWComplianceSlopeData = {}        #1-7 steps (refer to data sheet)
        self.goalPositionData = {}              #0-296.67 deg
        self.movingSpeedData = {}               #0-60 RPM
        self.torqueLimitData = {}               #0-100 %
        self.lockData = {}                      #0-1 False/True
        self.punchData = {}                     #32-1023 unitless
        

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
                    
                elif userCalledFunction == self.getTorqueEnable:
                    self.torqueEnableData[servoID] = params[0]
                    
                elif userCalledFunction == self.getLED:
                    self.ledData[servoID] = params[0]
                      
                elif userCalledFunction == self.getCWComplianceMargin:
                    self.CWComplianceMarginData[servoID] =  round(params[0]*servoResolution, 2)
                    
                elif userCalledFunction == self.getCCWComplianceMargin:
                    self.CCWComplianceMarginData[servoID] = round(params[0]*servoResolution, 2)
                    
                elif userCalledFunction == self.getCWComplianceSlope:
                    if params[0] == 0 or params[0] == 1:
                        self.CWComplianceSlopeData[servoID] = 1    
                    else:
                        for x in range(7):
                            maskedNum = (1 << 7-x) & params[0]
                            if maskedNum == (1 << 7-x):
                                self.CWComplianceSlopeData[servoID] = 7-x
                                break
                    
                elif userCalledFunction == self.getCCWComplianceSlope:
                    if params[0] == 0 or params[0] == 1:
                        self.CCWComplianceSlopeData[servoID] = 1    
                    else:
                        for x in range(7):
                            maskedNum = (1 << 7-x) & params[0]
                            if maskedNum == (1 << 7-x):
                                self.CCWComplianceSlopeData[servoID] = 7-x
                                break
                
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
                        
                        
if __name__ == "__main__":
    import time

    AX_Commands_Instance = True
    
    if AX_Commands_Instance == True:
        ax12a = AXCommands(serial.Serial("COM53", 1000000), appendPackets = True)
        ax12a.start()

        ax12a.setGoalPosition(2, 180)
        #ax12a.setID(1, 2)
    
    else:
        ax12a = AXCommandParse(serial.Serial("COM53", 1000000))
        ax12a.start()
        
        while True:
            
            time.sleep(0.3)
            
            ax12a.getPresentPosition(0)
            ax12a.getPresentPosition(1)
            ax12a.getPresentPosition(2)
            ax12a.getPresentPosition(3)
            ax12a.getPresentPosition(4)
            ax12a.getPresentPosition(5)
            ax12a.getPresentPosition(6)
            ax12a.getPresentPosition(7)
            
            '''
            ax12a.getPresentSpeed(1)
            ax12a.getPresentSpeed(2)
            ax12a.getPresentSpeed(3)
            ax12a.getPresentSpeed(4)
            ax12a.getPresentSpeed(5)
            
            ax12a.getPresentVoltage(1)
            ax12a.getPresentVoltage(2)
            ax12a.getPresentVoltage(3)
            ax12a.getPresentVoltage(4)
            ax12a.getPresentVoltage(5)
            
            ax12a.getPresentLoad(1)
            ax12a.getPresentLoad(2)
            ax12a.getPresentLoad(3)
            ax12a.getPresentLoad(4)
            ax12a.getPresentLoad(5)
            
            ax12a.getPresentTemperature(1)
            ax12a.getPresentTemperature(2)
            ax12a.getPresentTemperature(3)
            ax12a.getPresentTemperature(4)
            ax12a.getPresentTemperature(5)
            '''
            
            #print "Current Packet:", ax12a.currentDataPacket
            print "position:", ax12a.presentPositionData
            #print "speed:", ax12a.presentSpeedData
            #print "voltage:", ax12a.presentVoltageData
            #print "load:", ax12a.presentLoadData
            #print "temperature:", ax12a.presentTemperatureData
            #print "\n"
        
        
        