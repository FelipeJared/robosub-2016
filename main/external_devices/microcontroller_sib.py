'''
Created on Mar 17, 2016

@author: jannainm
'''
'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_sib
   :synopsis: Handles communication with SIB.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Apr 25, 2015
:Description: Sends and receives data packets to Sensor Interface Board.
'''
import data_packet_generator
import threading
import time, sys
import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

class SIBDataPackets(data_packet_generator.DataPacket):
    def __init__(self, serialObject):
        '''
        Initializes the SIB object.
        
        **Parameters**: \n
        * **serialObject** - SIB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.SIBCom = serialObject
    
    '''
    DOES NOT USE    
    def getAnalogTemperature(self):
        
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6D)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getAnalogInternalPressure(self):
        
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6E)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
    '''
            
    def getAnalogExternalPressure(self):
        '''
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6F)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getDigitalTemperature(self):
        '''
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6A)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getDigitalInternalPressure(self):
        '''
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6B)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getDigitalInternalHumidity(self):
        '''
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6C)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
    '''    
    def getTemperature(self):
        Sends get request for the temperature.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6D)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getInternalPressure(self):
        Sends get request for the internal pressure.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6E)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        
    def getExternalPressure(self):
        
        Sends get request for the external pressure.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x6F)
        self.calcCRC32Out()
        self.pack()
        self.send(self.SIBCom)
        '''
     
class SIBResponse(data_packet_generator.DataPacket, threading.Thread):
    def __init__(self, serialObject, *debug):
        '''
        Initializes the SIB thread (starts thread process).
        
        **Parameters**: \n
        * **serialObject** - SIB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.SIBCom = serialObject
        
        self.sibDataPackets = SIBDataPackets(self.SIBCom)
        
        self.requestTime = 0.1
        
        if len(debug):
            if debug[0].pop() == True:
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1 #No alerts exist for SIB, thus -1
        self.upperFrameIdForAlerts = -1
        
        self.alertList = []
        self.getList = []
    
    def run(self):
        '''
        Obtains SIB data and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            
            #time.sleep(0.01) #Slows down thread to save some power
            
            netRequestTimer = reqestTimer.netTimer(reqestTimer.cpuClockTimeInSeconds())
            if netRequestTimer >= self.requestTime:
                if not self.debug:
                    '''self.sibDataPackets.getExternalPressure()
                    self.sibDataPackets.getInternalPressure()
                    self.sibDataPackets.getTemperature()
                    self.sibDataPackets.getAnalogTemperature()'''
                    self.sibDataPackets.getAnalogExternalPressure()
                    #self.sibDataPackets.getAnalogInternalPressure()
                    self.sibDataPackets.getDigitalTemperature()
                    self.sibDataPackets.getDigitalInternalPressure()
                    self.sibDataPackets.getDigitalInternalHumidity()
                reqestTimer.restartTimer()

            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
                if ((dataPacket[1] >= self.lowerFrameIdForAlerts) and (dataPacket[1] <= self.upperFrameIdForAlerts)):
                    self.alertList.append(dataPacket)
                else:
                    self.getList.append(dataPacket)
                    
    def unpack(self):
        '''
        Extracts the raw data from the transmission (collects all bytes into array).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw data transmission.\n
        '''
        try:
            if self.SIBCom.inWaiting() != 0:
                self.dataPacketIn = []
                self.dataPacketIn.append(ord(self.SIBCom.read()))
                if self.dataPacketIn[0] >= 6 and self.dataPacketIn[0] <= 16: #If the byte count is between 6 and 16 (this is the min and max range of bytes in a data packet that we have...this could change in the future)
                    for x in range(1, self.dataPacketIn[0]):
                        self.dataPacketIn.append(ord(self.SIBCom.read()))
                    self.dataPacketIn = self.calcCRC32In(self.dataPacketIn)
                    return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from SIB:", msg
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False
