'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_tcb
   :synopsis: Handles communication with SIB.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Apr 25, 2015
:Description: Sends and receives data packets to Thruster Control Board.
'''

import data_packet_generator
import threading
import time, sys
import main.utility_package.utilities as utilities

reqestTimer = utilities.Timer()

class TCBDataPackets(data_packet_generator.DataPacket):
    def __init__(self, serialObject):
        '''
        Initializes the TCB object.
        
        **Parameters**: \n
        * **serialObject** - TCB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.TCBCom = serialObject
        
    def getMotorData(self, motorNum): #motorNum can only be values from 1-4
        '''
        Sends get request for the motor data. TCB1 and TCB2 can only do motor 1, 2, 3 and 4
        
        **Parameters**: \n
        * **motorNum** - The number of the requested motor, from 1-4.
         
        **Returns**: \n
        * **No Return.**\n
        '''

        self.clearPacket()
        self.setByteCount(0x06)
        self.setFrameID(motorNum) 
        self.calcCRC32Out()
        self.pack()
        self.send(self.TCBCom)
        
    def setMotorDirectionSpeed(self, motorNum, direction, speed): #motorNum can only be values from 1-4. speed can only be from 0-255
        '''
        Sends set request for the motor speed. TCB1 and TCB2 can only do motor 1, 2, 3 and 4.
        Receives desired direction, actual direction, desired pwm, actual pwm, HES LSB, HES MSB
        
        **Parameters**: \n
        * **motorNum** - The number of the requested motor from 1-4.
        * **direction** - A 0 or 1 setting the motor forwards or in reverse.
        * **speed** - Integer setting PWM between 0-255.

         
        **Returns**: \n
        * **No Return.**\n
        '''
        

        self.clearPacket()
        self.setByteCount(0x08)
        self.setFrameID(motorNum+160)
        self.setPayload(direction, speed)
        self.calcCRC32Out()
        self.pack()
        self.send(self.TCBCom)

     
class TCBResponse(data_packet_generator.DataPacket, threading.Thread):
    def __init__(self, serialObject, *debug):
        '''
        Initializes the TCB thread (starts thread process).
        
        **Parameters**: \n
        * **serialObject** - TCB serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.TCBCom = serialObject
        
        if len(debug):
            if debug[0].pop() == True:
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        
        self.tcbDataPackets = TCBDataPackets(self.TCBCom)
        
        self.requestTime = 0.5
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1 #No alerts exist for TCB, thus -1
        self.upperFrameIdForAlerts = -1
        
        self.alertList = []
        self.getList = []
    
    def run(self):
        '''
        Obtains TCB data and appends it to the instance's list attribute.
        
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
                    self.tcbDataPackets.getMotorData(1)
                    self.tcbDataPackets.getMotorData(2)
                    self.tcbDataPackets.getMotorData(3)
                    self.tcbDataPackets.getMotorData(4) 
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
            if self.TCBCom.inWaiting() != 0:
                self.dataPacketIn = []
                self.dataPacketIn.append(ord(self.TCBCom.read()))
                if self.dataPacketIn[0] >= 6 and self.dataPacketIn[0] <= 16: #If the byte count is between 6 and 16 (this is the min and max range of bytes in a data packet that we have...this could change in the future)
                    for x in range(1, self.dataPacketIn[0]):
                        self.dataPacketIn.append(ord(self.TCBCom.read()))
                    self.dataPacketIn = self.calcCRC32In(self.dataPacketIn)
                    return self.dataPacketIn
        except Exception as msg:
            print "Can't receive data from TCB:", msg
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False