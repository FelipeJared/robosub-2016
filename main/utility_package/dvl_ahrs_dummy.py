'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: dvl_ahrs_dummy
   :synopsis: Sends AHRS data to the DVL.

:Author: Austin Owens <felipejaredgm@gmail.com>
:Date: Created on Jul 1, 2015
:Description: Simulates an AHRS to make the DVL think it's receiving data from one.
'''
import serial
import struct
import main.external_devices.data_packet_generator as data_packet_generator
import main.external_devices.sparton_ahrs as sparton_ahrs

datapacket = []
DVLPort = serial.Serial("COM20", 38400)
spartonResponseThread = sparton_ahrs.SpartonAhrsResponse("COM29")
spartonResponseThread.start()

ahrsData = [0, 0, 0]
headingToInts = [0, 0, 0, 0]
pitchToInts = [0, 0, 0, 0]
rollToInts = [0, 0, 0, 0]

class AHRSDummyCommunicator(data_packet_generator.DataPacket):
    def sendID(self):
        '''
        Sends an ID to the DVL to make it think an AHRS is connected. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0, 13)
        self.setFrameID(2) #233 is the offset
        self.setPayload('T', 'R', 'A', 'X', 0x50, 0x37, 0x33, 0x34)
        self.calcCRC16Out()
        self.pack()
        self.send(DVLPort)
        
    def sendAHRSData(self, headingBytes, pitchBytes, rollBytes):
        '''
        Passes over the AHRS data to the DVL.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0, 26)
        self.setFrameID(5) #233 is the offset
        self.setPayload(4, 7, 0x41, 0xda, 0x66, 0x66, 5, headingBytes[0], headingBytes[1], headingBytes[2], headingBytes[3], 24, pitchBytes[0], pitchBytes[1], pitchBytes[2], pitchBytes[3], 25, rollBytes[0], rollBytes[1], rollBytes[2], rollBytes[3])#27.3
        self.calcCRC16Out()
        self.pack()
        self.send(DVLPort)
         
    def unpack(self):       
        '''
        Reads in the raw transmission and extracts all bytes of the packet
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw transmission packet.\n
        '''
        if DVLPort.inWaiting() != 0:
            self.dataPacketIn = []
            self.dataPacketIn.append(ord(DVLPort.read()))
            self.dataPacketIn.append(ord(DVLPort.read()))
            for x in range(2, self.dataPacketIn[1]):
                self.dataPacketIn.append(ord(DVLPort.read()))
            self.dataPacketIn = self.calcCRC16In(self.dataPacketIn)
            return self.dataPacketIn
       
dvl = AHRSDummyCommunicator()

while True:
    while len(spartonResponseThread.getList) > 0:
        ahrsData = spartonResponseThread.getList.pop(0)
        headingToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[0])]
        pitchToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[1])]
        rollToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[2])]
    
    dataPacket = dvl.unpack()
    
    if dataPacket != None:
        print dataPacket
        
        if dataPacket[2] == 1: #kGetModInfo
            dvl.sendID()
            
        if dataPacket[2] == 4: #kGetData
            headingBytes = headingToInts
            pitchBytes = pitchToInts
            rollBytes = rollToInts
            dvl.sendAHRSData(headingBytes, pitchBytes, rollBytes)
            
