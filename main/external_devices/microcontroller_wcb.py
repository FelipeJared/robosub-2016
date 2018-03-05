'''
Copyright 2014, Austin Owens, All rights reserved.

   :synopsis: Controls the WCB board.

:Author: Austin Owens <sdsumechatronics@gmail.com>
:Editor: Michael Jannain <jannainm@gmail.com>
:Date: Created on May 3, 2014
:Description: This module's primary purpose is to handle all communication commands to the WCB board.

'''
import data_packet_generator
import threading
import time
import sys

import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

f4GettingReset = False

class WCBDataPackets(data_packet_generator.DataPacket):
    '''
    This class handles all WCB-specific getter and setter communication commands to/from the F0 board. It does not handle any protocol-specifications; these are inherited from *data_packet_generator*.
    '''
    def __init__(self, serialObject):
        '''
        Initializes the WCB object.
        
        **Parameters**: \n
        * **serialObject** - WCB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.WCBCom = serialObject
        
#     def setThrustersWeaponsEnablePower(self): #Enabling Power
#         '''
#         Sends an on setter signal to the thrusters.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0xF1)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def setThrustersWeaponsDiablePower(self): #Disabling Power
#         '''
#         Sends an off setter signal to the thrusters.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0xF2)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def getBattery1(self): #clean
#         '''
#         Sends getter request to battery 1 in order to get battery voltage.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x26)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def getBattery2(self): #Dirty
#         '''
#         Sends getter request to battery 2 in order to get battery voltage.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x27)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def getThrustersWeaponsPower(self): #Status
#         '''
#         Sends getter request for thruster (all) on/off status/ 
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x25)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def setStm32f4Reset(self):
#         '''
#         Sends reset command to the F4 board.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0xF4)
#         self.calcCRC32Out()
#         self.pack()
#         self.thrustersWeaponsDiablePowerSet() #Must disable power to thrusters so that reseting the f4 wont make the thrusters jerk.
#         time.sleep(.5)
#         self.WCBCom.close() #The F4 board must have its COM port closed or else windows OS will think a serial timeout has occurred. The port will be re-opened when the f0 sends back a confirmation
#         self.f4GettingReset = True
#         self.send(self.WCBCom)
        
#     def setDropperReset(self):
#         '''
#         Sends reset command to the dropper mechanism. 
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0xFE)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def setTorpedoReset(self):
#         '''
#         Sends reset command to the torpedo mechanism.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         ''' 
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0xFF)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
    
    def setClaw1Close(self):
        '''
        Sends a close command to claw 1.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0xC1)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
    def setClaw2Close(self):
        '''
        Sends a close command to claw 2.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0xC2)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
    
    def setTorpedo1Launch(self, position):
        '''
        Sends a launch command to torpedo 1.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x07)
        self.setFrameID(0xB3)
        self.setPayload(position)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
    def setTorpedo2Launch(self):
        '''
        Sends a launch command to torpedo 2.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0xC4)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
    def setDropper1Launch(self):
        '''
        Sends a launch command to dropper 1 (launches first ball).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0xB4)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
    def setDropper2Launch(self):
        '''
        Sends a launch command to dropper 2 (launches second ball).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0xC6)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
#     def getDropperStatus(self):
#         '''
#         Sends a getter request for the status of the dropper (how many balls have been dropped).
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x20)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
#     def getTorpedoStatus(self):
#         '''
#         Sends a getter request for the status of the torpedos (which torpedoes have been launched).
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x21)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
        
    def getClaw1Status(self):
        '''
        Sends a getter request for the status of claw 1 (claw open | closed).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x22)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
        
    def getClaw2Status(self):
        '''
        Sends a getter request for the status of claw 2 (claw open | closed).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(0x23)
        self.calcCRC32Out()
        self.pack()
        self.send(self.WCBCom)
 
#     def getTemperature(self):
#         '''
#         Sends a getter request for the temperature of the f0.
#         
#         **Parameters**: \n
#         * **No Input Parameters.**
#          
#         **Returns**: \n
#         * **No Return.**\n
#         '''
#         self.clearPacket()
#         self.setByteCount(0x06)
#         self.setFrameID(0x24)
#         self.calcCRC32Out()
#         self.pack()
#         self.send(self.WCBCom)
    
        
class WCBResponse(data_packet_generator.DataPacket, threading.Thread):
    '''
    This class which handles the data extraction from the data transmission
    '''
    def __init__(self, serialObject, *debug):
        '''
        Initializes storage data pack array.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.WCBCom = serialObject
        self.wcbDataPackets = WCBDataPackets(self.WCBCom)
        
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
        Obtains WCB data and appends it to the instance's list attribute.
        
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
                    try:
                        self.wcbDataPackets.getBattery1Data()
                    except:
                        print 
                    try:
                        self.wcbDataPackets.getBattery2Data() 
                    except:
                        pass
                    try:
                        self.wcbDataPackets.getPowerStatus()
                    except:
                        pass
                reqestTimer.restartTimer()

            dataPacket = self.unpack() #Reads in data packet
            if dataPacket != None and dataPacket != [0]:
                if ((dataPacket[1] >= self.lowerFrameIdForAlerts) and (dataPacket[1] <= self.upperFrameIdForAlerts)):
                    self.alertList.append(dataPacket)
                else:
                    self.getList.append(dataPacket)
        
    def unpack(self):
        '''
        Extracts the raw data from the transmission.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw data transmission (collects all bytes into array).\n
        '''
        try:
            if self.WCBCom.inWaiting() != 0:
                self.clearPacket()
                self.dataPacketIn.append(ord(self.WCBCom.read()))
                for x in range(1, self.dataPacketIn[0]):
                    self.dataPacketIn.append(ord(self.WCBCom.read()))
                self.dataPacketIn = WCBResponse.calcCRC32In(self, self.dataPacketIn)
                return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from F0. COM port is:", self.WCBCom.isOpen(), "Reason: ", msg
    
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False
