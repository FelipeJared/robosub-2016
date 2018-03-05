'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: dynamixel
   :synopsis: Lower level embedded systems serial communication library.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 17, 2015
:Description: Contains generic serial communication code that can be inherited by several Dynamixel servo models.
'''


import serial
import threading
import time

class Dynamixel(threading.Thread):
    def __init__(self, servoSerialObject, appendPackets=True, *lineDriverSerialObject):
        '''
        Takes in Serial objects to use throughout the class.
        **Parameters**: \n
        * **servoSerialObject** - The Serial object that communicates to the Dynamixel Servo.
        * **lineDriverSerialObject** - If a USB2Dynamixel device is not being used, a line driver can be used when using Half Duplex UART. lineDriverSerialObject is the Serial object for the line driver (optional parameter).
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.appendPackets = appendPackets
        
        self.runThread = True

        if self.appendPackets == False:
            self.data = {}
        else:
            self.data = []
        
        #Dynamixel Instructions
        self.PING = 0x01 #No execution. It is used wh en controller is ready to receive Status Packet
        self.READ_DATA = 0x02 #This command reads data from Dynamixel
        self.WRITE_DATA = 0x03 #This command writes data to Dynamixel
        self.REG_WRITE = 0x04 #It is similar to WRITE_DATA, but it remains in the standby state without being executed until the ACTION command arrives.
        self.ACTION = 0x05 #This command initiates motions registered with REG WRITE
        self.RESET = 0x06 #This command restores the state of Dynamixel to the factory default setting.
        self.SYNC_WRITE = 0x83 #This command is used to control several Dynamixels simultaneously at a time.

        if type(servoSerialObject) is not serial.Serial:
            raise TypeError("servoSerialObject not of type Serial")
        
        if len(lineDriverSerialObject) > 1:
            raise TypeError(" __init__() takes at most 2 arguments ({} given)".format(1+len(lineDriverSerialObject)))
            
        self.servoSerialObject = servoSerialObject
        
        if len(lineDriverSerialObject) == 1:
            if type(lineDriverSerialObject) is not serial.Serial:
                raise TypeError("lineDriverSerialObject not of type Serial")
            
            self.lineDriverSerialObject = lineDriverSerialObject[0]
            
        
        elif len(lineDriverSerialObject) == 0:
            self.lineDriverSerialObject = None
            
            

    def sendDataPacket(self, servoID, instruction, *servoParams):
        '''
        Generates and sends a data packet to a Dynamixel.
        **Parameters**: \n
        * **servoID** - The ID of the Dynamixel to communicate with.
        * **instruction** - Gives an instruction to Dynamixel.
        * **servoParams** - Parameters to pass to the Dynamixel.
        **Returns**: \n
        * **No Return.**\n
        '''
        
        if self.lineDriverSerialObject != None:
            self.lineDriverSerialObject.write('1') #TX Enabled/RX Disabled
        
        dataPacket = [0xFF, 0xFF, servoID, len(servoParams)+2, instruction]
        
        for index, value in enumerate(servoParams):
            dataPacket.append(value)
            
        
        CRCValue = ~sum(dataPacket[2:]) & 0xFF
        dataPacket.append(CRCValue)
        
        self.servoSerialObject.write(bytearray(dataPacket))
        
        if self.lineDriverSerialObject != None:
            self.lineDriverSerialObject.write('0')#RX Enabled/TX Disabled
        
        time.sleep(0.005)

    def recieveDataPacket(self, appendPackets = False):
        
            
        if self.servoSerialObject.inWaiting() >= 5: #Minimum bytes in a data packet
            if ord(self.servoSerialObject.read()) == 0xFF and ord(self.servoSerialObject.read()) == 0xFF:
                servoID = ord(self.servoSerialObject.read())
                length = ord(self.servoSerialObject.read())
                error = ord(self.servoSerialObject.read())
                parameters = []
                for x in range(length-2): #-2 because not including length or error
                    parameters.append(ord(self.servoSerialObject.read()))
                CRC = ord(self.servoSerialObject.read())
                if appendPackets == True:
                    self.data.append([0xFF, 0xFF, servoID, length, error, parameters, CRC])
                else:
                    self.data[servoID] = [0xFF, 0xFF, servoID, length, error, parameters, CRC]
                
    def run(self):
        while self.runThread:
            self.recieveDataPacket(self.appendPackets)
        
            
    def killThread(self):
        self.runThread = False
    
    
if __name__ == "__main__":
    
    ax12a = Dynamixel(serial.Serial("COM8", 1000000), appendPackets=True)
    ax12a.start()
    
    ax12a.sendDataPacket(0x01, ax12a.READ_DATA, 0x24, 0x02)
    
    time.sleep(0.05)
    
    print ax12a.data
    
    