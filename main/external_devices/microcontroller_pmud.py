'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_pmud
   :synopsis: Handles communication with PMUD.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Apr 25, 2015
:Description: Sends and receives data packets to Power Monitoring and Undervoltage Detection Board.
'''
import data_packet_generator
import threading
import sys
import time

import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

class PMUDDataPackets(data_packet_generator.DataPacket):
    def __init__(self, serialObject):
        '''
        Initializes the PMUD object.
        
        **Parameters**: \n
        * **serialObject** -PMUD serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.PMUDCom = serialObject
        
    def getPowerStatus(self):
        '''
        Sends get request for the power status 0 is disabled 1 is enabled.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x25)
        self.calcCRC32Out()
        self.pack()
        self.send(self.PMUDCom)
        
    def getBattery1Data(self):
        '''
        Sends get request for battery 1 voltage and current.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x26)
        self.calcCRC32Out()
        self.pack()
        self.send(self.PMUDCom)
        
    def getBattery2Data(self):
        '''
        Sends get request for battery 2 voltage and current.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x27)
        self.calcCRC32Out()
        self.pack()
        self.send(self.PMUDCom)
        
    def setPowerStatus(self, status):
        '''
        Sends set request for weapons. 0 for disable, 1 for enable
        
        **Parameters**: \n
        * **status** - A 0 to disable weapons or a 1 to enable them.
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x07)
        self.setFrameID(0xC5)
        self.setPayload(status)
        self.calcCRC32Out()
        self.pack()
        self.send(self.PMUDCom)

     
class PMUDResponse(data_packet_generator.DataPacket, threading.Thread):
    def __init__(self, serialObject, *debug):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **serialObject** - PMUD serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.PMUDCom = serialObject
        self.pmudDataPackets = PMUDDataPackets(self.PMUDCom)
        
        self.requestTime = 0.5
        
        if len(debug):
            if debug[0].pop() == True:
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1
        self.upperFrameIdForAlerts = -1
        
        self.alertList = []
        self.getList = []
    
    def run(self, *debug):
        '''
        Obtains PMUD data and appends it to the instance's list attribute.
        
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
                    self.pmudDataPackets.getBattery1Data()
                    self.pmudDataPackets.getBattery2Data()
                    self.pmudDataPackets.getPowerStatus()
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
            if self.PMUDCom.inWaiting() != 0:
                self.dataPacketIn = []
                self.dataPacketIn.append(ord(self.PMUDCom.read()))
                if self.dataPacketIn[0] >= 6 and self.dataPacketIn[0] <= 16: #If the byte count is between 6 and 16 (this is the min and max range of bytes in a data packet that we have...this could change in the future)
                    for x in range(1, self.dataPacketIn[0]):
                        self.dataPacketIn.append(ord(self.PMUDCom.read()))
                    self.dataPacketIn = self.calcCRC32In(self.dataPacketIn)
                    return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from PMUD:", msg
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False