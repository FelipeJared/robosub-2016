'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_dib
   :synopsis: Handles communication with DIB.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Editor: Michael Jannain <jannainm@gmail.com>
:Date: Created on Apr 25, 2015
:Description: Sends and receives data packets to Diver Interaction Board.
'''
import data_packet_generator
import threading
import sys
import time

import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

class DIBDataPackets(data_packet_generator.DataPacket):
    def __init__(self, serialObject):
        '''
        Initializes the DIB object.
        
        **Parameters**: \n
        * **serialObject** - DIB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.DIBCom = serialObject
        
    def getPowerStatus(self):
        '''
        Sends get request for the power status 0 is disabled 1 is enabled.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06) # NEED TO CHANGE THESE TO REAL VALUES FOR DIB
        self.setFrameID(0x25) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.calcCRC32Out()
        self.pack()
        self.send(self.DIBCom)
        
    def getBattery1Data(self):
        '''
        Sends get request for battery 1 voltage and current.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.setFrameID(0x26) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.calcCRC32Out()
        self.pack()
        self.send(self.DIBCom)
        
    def getBattery2Data(self):
        '''
        Sends get request for battery 2 voltage and current.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.setFrameID(0x27) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.calcCRC32Out()
        self.pack()
        self.send(self.DIBCom)
        
    def setPowerStatus(self, status):
        '''
        Sends set request for weapons. 0 for disable, 1 for enable
        
        **Parameters**: \n
        * **status** - A 0 to disable weapons or a 1 to enable them.
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x07) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.setFrameID(0xC5) # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.setPayload(status)
        self.calcCRC32Out()
        self.pack()
        self.send(self.DIBCom)

     
class DIBResponse(data_packet_generator.DataPacket, threading.Thread):
    def __init__(self, serialObject, *debug):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **serialObject** - DIB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.DIBCom = serialObject
        self.dibDataPackets = DIBDataPackets(self.DIBCom)
        
        self.requestTime = 0.5
        
        if len(debug):
            if debug[0].pop() == True:
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1 # NEED TO CHANGE TO REAL VALUES FOR DIB
        self.upperFrameIdForAlerts = -1 # NEED TO CHANGE TO REAL VALUES FOR DIB
        
        self.alertList = []
        self.getList = []
    
    def run(self, *debug):
        '''
        Obtains DIB data and appends it to the instance's list attribute.
        
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
                    self.dibDataPackets.getBattery1Data()
                    self.dibDataPackets.getBattery2Data()
                    self.dibDataPackets.getPowerStatus()
                reqestTimer.restartTimer()

            dataPacket = self.unpack() #Reads in data packet
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
            if self.DIBCom.inWaiting() != 0:
                self.dataPacketIn = []
                self.dataPacketIn.append(ord(self.DIBCom.read()))
                if self.dataPacketIn[0] >= 6 and self.dataPacketIn[0] <= 16: #If the byte count is between 6 and 16 (this is the min and max range of bytes in a data packet that we have...this could change in the future)
                    for x in range(1, self.dataPacketIn[0]):
                        self.dataPacketIn.append(ord(self.DIBCom.read()))
                    self.dataPacketIn = self.calcCRC32In(self.dataPacketIn)
                    return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from DIB:", msg
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False