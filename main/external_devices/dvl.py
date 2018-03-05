'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: dvl
   :synopsis: Handles communication with DVL.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Asst_Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Apr 25, 2014
:Description: Defines the commands sent to DVL Computer to setup DVL, get feedback, and reset DVL before starting missions.
'''

import serial
import time
import threading
import data_packet_generator
import struct

class DVLDataPackets:
    def __init__(self, serialObject):
        '''
        Initializes the DVL object and sends commands to the DVL computer to set up the DVL.
        
        **Parameters**: \n
        * **serialObject** - DVL serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.DVLCom = serialObject
        
        #DVL WAKE UP
        self.DVLCom.write(bytearray(['+', '+', '+'])) #Sends Break and waits for 2 seconds for DVL to wake up.
        time.sleep(2) 
        
        #CONTROL SYSTEM COMMANDS
        self.DVLCom.write(bytearray(['C', 'R', '1', '\n'])) #Resets the ExplorerDVL command set to factory settings.
        self.DVLCom.write(bytearray(['C', 'B', '8', '1', '1', '\n'])) #Sets the RS-232/422 serial port communications parameters (Baud Rate/Parity/StopBits).
        self.DVLCom.write(bytearray(['C', 'F', '1', '1', '1', '1', '0', '\n'])) #Sets various ExplorerDVL data flow-control parameters.
        time.sleep(0.1)
        
        #BOTTOM TRACK COMMANDS
        self.DVLCom.write(bytearray(['B', 'P', '0', '0', '1', '\n'])) #Sets the number of bottom-track pings to average together in each data ensemble.
        self.DVLCom.write(bytearray(['B', 'X', '0', '0', '0', '6', '0', '\n'])) #Sets the maximum tracking depth in bottom-track mode.
        time.sleep(0.1)
        
        #ENVIRONMENTAL COMMANDS
        self.DVLCom.write(bytearray(['E', 'A', '-', '1', '3', '0', '0', '0', '\n'])) #Corrects for physical misalignment between Beam 3 and the heading reference.
        self.DVLCom.write(bytearray(['E', 'D', '0', '0', '0', '0', '\n'])) #Sets the ExplorerDVL transducer depth.
        self.DVLCom.write(bytearray(['E', 'S', '3', '5', '\n'])) #Sets the water's salinity value.
        self.DVLCom.write(bytearray(['E', 'X', '1', '1', '1', '1', '1', '\n'])) #Sets the coordinate transformation processing flags.
        self.DVLCom.write(bytearray(['E', 'Z', '2', '2', '2', '2', '2', '2', '2', '0', '\n'])) #Selects the source of environmental sensor data.
        time.sleep(0.1)
        
        #TIMING COMMANDS
        self.DVLCom.write(bytearray(['T', 'E', '0', '0', ':', '0', '0', ':', '0', '0', '.', '0', '0', '\n'])) #Sets the minimum interval between data collection cycles (data ensembles).
        self.DVLCom.write(bytearray(['T', 'P', '0', '0', ':', '0', '0', '.', '0', '5', '\n'])) #Sets the minimum time between pings.
        time.sleep(0.1)
        
        #EXPERT BOTTOM TRACK COMMANDS
        self.DVLCom.write(bytearray(['#', 'B', 'K', '0', '\n'])) #Selects the ping frequency of the water-mass layer ping.
        self.DVLCom.write(bytearray(['#', 'B', 'L', '2', '0', ',', '8', '0', ',', '1', '6', '0', '\n'])) #Sets bottom-track water-mass layer boundaries and minimum layer size.
        self.DVLCom.write(bytearray(['#', 'C', 'T', '1', '\n'])) #Allows the ExplorerDVL to initialize to predefined parameters and start pinging within 10 seconds after power is applied, or a break is received, if no command is entered.
        self.DVLCom.write(bytearray(['#', 'E', 'E', '0', '0', '0', '0', '0', '0', '0', '\n'])) #Controls output of specialized data types; controls whether a transform of velocity data to raw or nominal beam is done with associated corrections in the case of the phased array system.
        self.DVLCom.write(bytearray(['#', 'E', 'V', '0', '0', '0', '0', '0', '\n'])) #Corrects for electrical/magnetic bias between the ExplorerDVL heading value and the heading reference.
        self.DVLCom.write(bytearray(['#', 'P', 'D', '5', '\n'])) #Selecting output format of DVL data
        time.sleep(0.1)
        
        #START LISTINING TO EXTERNAL AHRS
        self.DVLCom.write(bytearray(['S', 'P', ' ', '2', ' ', '9', ' ', '1', '0', '0',  '\n']))
        
        #STARTING DVL
        self.DVLCom.write(bytearray(['C', 'K', '\n'])) #Save parameters to user file on DVL
        self.DVLCom.write(bytearray(['C', 'S', '\n'])) #Start DVL


class DVLResponse(threading.Thread):
    def __init__(self, serialObject):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.DVLCom = serialObject
        
        self.runThread = True
        
        self.lowerFrameIdForAlerts = -1
        self.upperFrameIdForAlerts = -1
        
        self.alertList = []
        self.getList = []
    
    def run(self):
        '''
        Obtains DVL data and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            
            #time.sleep(0.01) #Slows down thread to save some power
                
            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
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
            if self.DVLCom.inWaiting() != 0:
                ID = hex(ord(self.DVLCom.read()))
                if ID == "0x7d":
                    ensemble = [] #Clear list
                    
                    outputFormat = ord(self.DVLCom.read()) #0 if using PD4 output format, 1 if using PD5 output format
                    byteNumLSB = ord(self.DVLCom.read()) #How many bytes in ensemble
                    byteNumMSB = ord(self.DVLCom.read()) #How many bytes in ensemble
                    
                    ensemble = [ID, outputFormat, byteNumLSB, byteNumMSB]
                    for x in range(byteNumMSB << 8 | byteNumLSB):
                        ensemble.append(ord(self.DVLCom.read()))
                    
                    return ensemble
                
                else:
                    self.DVLCom.flushInput()
                    
        except Exception as msg:
            print "Can't receive data from DVL:", msg
        
            
    def clearDistanceTraveled(self):
        '''
        Resets the DVL's origin point to its current position.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #DVL WAKE UP
        self.DVLCom.write(bytearray(['+', '+', '+'])) #Sends Break and waits for 2 seconds for DVL to wake up.
        time.sleep(2)     
        
        self.DVLCom.write(bytearray(['#', 'B', 'S', '\n'])) # Resets the current locations to 0
        
        self.DVLCom.write(bytearray(['C', 'S', '\n'])) # Starts DVL
        time.sleep(2) 
        
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False     
        
class AHRSDummyCommunicator(threading.Thread, data_packet_generator.DataPacket):
    '''
    Sends data to the DVL making it think an AHRS is sending the data.
    '''
    def __init__(self, dvlAhrsComPortObject):
        '''
        Initializes the AHRS Dummy thread (starts thread process).
        
        **Parameters**: \n
        * **dvlAhrsComPortObject** - Serial object used to trick DVL.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        #data_packet_generator.DataPacket.__init__(self)
        self.dvlAhrsSerialComObject = dvlAhrsComPortObject
        
        self.runThread = True
        
        self.headingToInts = [0x41, 0xda, 0x66, 0x66]
        self.pitchToInts = [0x41, 0xda, 0x66, 0x66]
        self.rollToInts = [0x41, 0xda, 0x66, 0x66]
        
    def run(self):
        '''
        Sends ID and AHRS data to the DVL.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            dataPacket = self.unpack()
            
            if dataPacket != None:
                #print dataPacket
                if dataPacket[2] == 1: #kGetModInfo
                    self.sendID()
                    
                if dataPacket[2] == 4: #kGetData If the frame id is a 4...
                    self.sendAHRSData()
            
    
    
    def sendID(self):
        '''
        Sends data packet containing ID data.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0, 13)
        self.setFrameID(2) #233 is the offset
        self.setPayload('T', 'R', 'A', 'X', 0x50, 0x37, 0x33, 0x34)
        self.calcCRC16Out()
        self.pack()
        self.send(self.dvlAhrsSerialComObject)
        
    def sendAHRSData(self):
        '''
        Sends AHRS data to DVL and flushes input to ensure the data is sent.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        self.clearPacket()
        self.setByteCount(0, 26)
        self.setFrameID(5) #233 is the offset
        self.setPayload(4, 7, 0x41, 0xda, 0x66, 0x66, 5, self.headingToInts[0], self.headingToInts[1], self.headingToInts[2], self.headingToInts[3], 24, self.pitchToInts[0], self.pitchToInts[1], self.pitchToInts[2], self.pitchToInts[3], 25, self.rollToInts[0], self.rollToInts[1], self.rollToInts[2], self.rollToInts[3])#27.3
        self.calcCRC16Out()
        self.pack()
        self.send(self.dvlAhrsSerialComObject)
        self.dvlAhrsSerialComObject.flushInput()

    def unpack(self): 
        '''
        Extracts the raw data from the transmission (collects all bytes into array).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw data transmission.\n
        '''
        if self.dvlAhrsSerialComObject.inWaiting() != 0:
            self.dataPacketIn = []
            self.dataPacketIn.append(ord(self.dvlAhrsSerialComObject.read()))
            self.dataPacketIn.append(ord(self.dvlAhrsSerialComObject.read()))
            for x in range(2, self.dataPacketIn[1]):
                self.dataPacketIn.append(ord(self.dvlAhrsSerialComObject.read()))
            self.dataPacketIn = self.calcCRC16In(self.dataPacketIn)
            return self.dataPacketIn   
        
    def updateAhrsValues(self, ahrsData):
        '''
        Updates the fake AHRS data with actual AHRS readings. 
        
        **Parameters**: \n
        * **ahrsData** - Orientation data from the AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.headingToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[0])]
        self.pitchToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[1])]
        self.rollToInts = [int(ord(b)) for b in struct.pack('>f', ahrsData[2])]
        
        #print struct.unpack('f', struct.pack('I' , self.headingToInts[0] << 24 | self.headingToInts[1] << 16 | self.headingToInts[2] << 8 | self.headingToInts[3] << 0))[0], struct.unpack('f', struct.pack('I' , self.pitchToInts[0] << 24 | self.pitchToInts[1] << 16 | self.pitchToInts[2] << 8 | self.pitchToInts[3] << 0))[0], struct.unpack('f', struct.pack('I' , self.rollToInts[0] << 24 | self.rollToInts[1] << 16 | self.rollToInts[2] << 8 | self.rollToInts[3] << 0))[0]
        
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False   