'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: data_packet_generator
   :synopsis: A generic module for data packets so that other modules can inherit from these classes.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Mar 1, 2014
:Description: Defines communication protocol for all communications EXCLUDING THE SPARTAN.
'''

import crcmod
import struct


#CRC
CRC16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
CRC32 = crcmod.mkCrcFun(0x104C11DB7, rev=True, initCrc=0x00000000, xorOut=0xFFFFFFFF)


class DataPacket:
    '''
    This class is an easy and generic way to populate and send a serial data packet.
    '''
    def __init__(self):
        '''
        Initializes data packet elements.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.byteCount = 0
        self.frameID = 0
        self.payload = 0
        self.crc = 0
        self.dataPacketOut = []
        
    def setByteCount(self, *byteCount):
        '''
        Determines the size (in bytes) of the data packet.
        
        **Parameters**: \n
        * **byteCount** - Unlimited amount of input parameters are allowed to be passed in.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.byteCount = self.singleListMerge(byteCount)
         
    def setFrameID(self, frameID):
        '''
        Defines the frameID for the output data packet.
        
        **Parameters**: \n
        * **frameID** - Desired frameID for output data packet. 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.frameID = frameID
        
    def setPayload(self, *payload):
        '''
        Defines the primary information (within the data packet) for the external device to carry out its requested task.
        
        **Parameters**: \n
        * ***payload** - Unlimited amount of input parameters which defines specific request.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.payload = self.singleListMerge(payload)
        
    def calcCRC16Out(self): #For AHRS
        '''
        Calculates the output checksum for AHRS (16-bit communication).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        if (self.payload > 0): 
            dataPacket = self.byteCount, self.frameID, self.payload 
        else:
            dataPacket = self.byteCount, self.frameID      
        
        byteList = self.singleListMerge(dataPacket) #Because the variable dataPacket could be lists, or single elements, I need to break them all down into single elements before the CRC is calculated
        
        # Output checksum polynomial calulation
        checksum = CRC16(str(bytearray(byteList)))
        checksumToInts = [int(ord(b)) for b in struct.pack('>H',checksum)]
        self.crc = [checksumToInts[0], checksumToInts[1]]
        
    def calcCRC16In(self, dataPacket): #For AHRS
        '''
        Decrypt the checksum from the AHRS (16-bit communication).
        
        **Parameters**: \n
        * **dataPacket** - Input checksum from AHRS
        
        **Returns**: \n
        * **dataPacket** - The complete data packet\n
        '''
        
        if dataPacket != [0] and dataPacket != None:
            
            try:
                checksum = CRC16(str(bytearray(dataPacket[0:len(dataPacket)-2])))
                CRCIn = dataPacket[-2] << 8 | dataPacket[-1] << 0
                if checksum != CRCIn:
                    print "BAD AHRS DATAPACKET BY CRC CALCULATION", dataPacket
                    dataPacket = None
            
            except:
                print "Data Packet was cut off in calcCRC16In."
                dataPacket = None
                
                
        return dataPacket
        
    def calcCRC32Out(self): #For F0, F4
        '''
        Calculates the checksum from the F0 & F4 boards (32-bit communication).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        if (self.payload > 0):
            dataPacket = self.byteCount, self.frameID, self.payload
        else:
            dataPacket = self.byteCount, self.frameID
               
        byteList = self.singleListMerge(dataPacket)
        
        checksum = CRC32(str(bytearray(byteList)))
        checksumToInts = [int(ord(b)) for b in struct.pack('>L',checksum)]
        self.crc = [checksumToInts[3], checksumToInts[2], checksumToInts[1], checksumToInts[0]]
        
    def calcCRC32In(self, dataPacket): #For F0, F4
        '''
        Decrypt the checksum from the F0 & F4 boards (32-bit communication).
        
        **Parameters**: \n
        * **dataPacket** - Input data packet from F0 & F4 boards.
        
        **Returns**: \n
        * **dataPacket** - The complete data packet.\n
        '''
        
        if dataPacket != [0] and dataPacket != None:
            
            try:
                checksum = CRC32(str(bytearray(dataPacket[0:len(dataPacket)-4])))
                CRCIn = dataPacket[-1] << 24 | dataPacket[-2] << 16 | dataPacket[-3] << 8 | dataPacket[-4] << 0
                
                if checksum != CRCIn and dataPacket[1] != 37: #There is a bug in the CRC library on either the python or the PIC side. Accommodating for this by putting 'dataPacket[1] != 37'
                    print "BAD F0/F4 DATAPACKET BY CRC CALCULATION", dataPacket
                    dataPacket = None #This doesnt work, need to fix
            
            except:
                print "Data Packet was cut off in calcCRC32In."
                dataPacket = None
                
            return dataPacket
     
    def pack(self): 
        '''
        Assembles each element into the packet for transmission.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No return.**\n
        '''
        
        #pack the message
        for i, v in enumerate(self.byteCount):
            self.dataPacketOut.append(v)
        self.dataPacketOut.append(self.frameID)
        if (self.payload > 0):
            for i, v in enumerate(self.payload):
                self.dataPacketOut.append(v)
        for i, v in enumerate(self.crc): 
            self.dataPacketOut.append(v)
        
    def send(self, ser):
        '''
        Sends assembled data packet.
        
        **Parameters**: \n
        * **ser** - Serial port object.
        
        **Returns**: \n
        * **No Return.**\n
        '''

        try:
            ser.write(bytearray(self.dataPacketOut))
                      
        except Exception as msg:
            print "Serial timeout on port:", ser.getPort(), msg
            
    
    def clearPacket(self):
        '''
        Initializes (clears contents of) data packet.  
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.byteCount = 0
        self.frameID = 0
        self.payload = 0
        self.crc = 0
        self.dataPacketOut = []
    
    def info(self):
        '''
        Useful information about the data packets that can be called anywhere in the program.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        if self.byteCount == 0:
            print "The byte count needs to be set before viewing data packet structure.\n"
        else:
            print "Byte count - Byte 1 :", self.byteCount
            print "Frame ID - Byte 2 :", self.frameID
            if self.payload == 0:
                print "Payload is missing", self.byteCount-6, "bytes"
            else:
                try:
                    for x in range(0, self.byteCount-6):
                        print "Payload - Byte", x+3, ":", self.payload[x]
                except:
                    print "ERROR: The byte count specified does not match how many bytes are in the data packet."     
            print "CRC - Byte", self.byteCount-3, ":", self.crc1
            print "CRC - Byte", self.byteCount-2, ":", self.crc2
            print "CRC - Byte", self.byteCount-1, ":", self.crc3
            print "CRC - Byte", self.byteCount, ":", self.crc4
            print "Outgoing data packet :", self.dataPacketOut, "\n"
    
    def singleListMerge(self, listOfLists):
        '''
        This function combines lists of lists into one single list
        
        **Parameters**: \n
        * **listOfLists** - Any list of lists, Tuples, etc. 
        
        **Returns**: \n
        * **singleList** -  Single list containing all input elements from variable *listOfLists*.\n
        '''
        
        singleList = []
        for element in list(listOfLists): 
            if isinstance(element, list):
                for single in element:
                    singleList.append(single)
            else:
                singleList.append(element)
                
        return singleList
        
        