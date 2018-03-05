'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_hydras
   :synopsis: Handles communication with HYDRAS.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Jul 14, 2015
:Description: Sends and receives data packets to the Hydrophone Direction Analysis System.
'''
import data_packet_generator
import threading
import time, sys
import main.utility_package.utilities as utilities
import struct

reqestTimer = utilities.Timer()

class HydrasDataPackets(data_packet_generator.DataPacket):
    def __init__(self, serialObject):
        '''
        Initializes the HYDRAS object.
        
        **Parameters**: \n
        * **serialObject** - HYDRAS serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.HYDRASCom = serialObject
        
    def getPingerHeading1(self):
        '''
        Sends get request for the 1st pinger heading.
         
        **Parameters**: \n
        * **No Input Parameters.**
          
        **Returns**:  \n
        * **No Return.**\n
        '''
 
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x62)
        self.calcCRC32Out()
        self.pack()
        self.send(self.HYDRASCom)
         
    def getPingerHeading2(self):
        '''
        Sends get request for the 2nd pinger heading.
         
        **Parameters**: \n
        * **No Input Parameters.**
          
        **Returns**: \n
        * **No Return.**\n
        '''
 
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x61)
        self.calcCRC32Out()
        self.pack()
        self.send(self.HYDRASCom)
        
        
    def setInitialData(self, speedOfSoundInWater, frequency):
        '''
        Sends set request for the speed of sound in the water.
         
        **Parameters**: \n
        * **speedOfSoundInWater** - DVL data on speed of sound in water.
        * **frequency** - Frequency being searched for.
          
        **Returns**: \n
        * **No Return.**\n
        '''
 
        self.clearPacket()
        self.setByteCount(0x09)
        self.setFrameID(0xF0)
        speedOfSoundInWaterToBytes = [int(ord(b)) for b in struct.pack('<H',speedOfSoundInWater)]
        self.setPayload(speedOfSoundInWaterToBytes[0], speedOfSoundInWaterToBytes[1], frequency)
        self.calcCRC32Out()
        self.pack()
        self.send(self.HYDRASCom)
     
class HydrasResponse(data_packet_generator.DataPacket, threading.Thread):
    def __init__(self, serialObject, *debug):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **serialObject** - HYDRAS serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.HYDRASCom = serialObject
        
        self.hydrasDataPackets = HydrasDataPackets(self.HYDRASCom)
        
        
        if len(debug):
            if debug[0].pop() == True:
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        
        #if not self.debug:
            #self.hydrasDataPackets.setInitialData(1250, 30) #Speed of sound in water, frequency 
        
        self.requestTime = 0.1
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1 #No alerts exist for HYDRAS, thus -1
        self.upperFrameIdForAlerts = -1
        
        self.alertList = []
        self.getList = []
    
    def run(self, *debug):  
        '''
        Obtains HYDRAS data and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        ''' 
        while self.runThread:
            netRequestTimer = reqestTimer.netTimer(reqestTimer.cpuClockTimeInSeconds())
            if netRequestTimer >= self.requestTime:
                if not self.debug:
                    self.hydrasDataPackets.getPingerHeading1()
                    self.hydrasDataPackets.getPingerHeading2()
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
            if self.HYDRASCom.inWaiting() != 0:
                self.dataPacketIn = []
                self.dataPacketIn.append(ord(self.HYDRASCom.read()))
                if self.dataPacketIn[0] >= 6 and self.dataPacketIn[0] <= 16: #If the byte count is between 6 and 16 (this is the min and max range of bytes in a data packet that we have...this could change in the future)
                    for x in range(1, self.dataPacketIn[0]):
                        self.dataPacketIn.append(ord(self.HYDRASCom.read()))
                    self.dataPacketIn = self.calcCRC32In(self.dataPacketIn)
                    return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from HYDRAS:", msg
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False