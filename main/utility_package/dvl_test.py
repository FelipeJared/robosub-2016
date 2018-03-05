'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: dvl_test
   :synopsis: Tests the DVL if properly functioning.


:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Oct 24, 2014
:Description: This module is a stand-alone program that uploads various commands and reads various sensor input to and from the DVL to make sure the sensor is working properly.
'''

import serial
import time
import struct

DVLPort = serial.Serial("COM23", 115200)

#DVL WAKE UP
DVLPort.write(bytearray(['+', '+', '+'])) #Sends Break and waits for 2 seconds for DVL to wake up.
time.sleep(2) 

#CONTROL SYSTEM COMMANDS
DVLPort.write(bytearray(['C', 'R', '1', '\n'])) #Resets the ExplorerDVL command set to factory settings.
DVLPort.write(bytearray(['C', 'B', '8', '1', '1', '\n'])) #Sets the RS-232/422 serial port communications parameters (Baud Rate/Parity/StopBits).
DVLPort.write(bytearray(['C', 'F', '1', '1', '1', '1', '0', '\n'])) #Sets various ExplorerDVL data flow-control parameters.
time.sleep(0.2)
#BOTTOM TRACK COMMANDS
DVLPort.write(bytearray(['B', 'P', '0', '0', '1', '\n'])) #Sets the number of bottom-track pings to average together in each data ensemble.
DVLPort.write(bytearray(['B', 'X', '0', '0', '0', '6', '0', '\n'])) #Sets the maximum tracking depth in bottom-track mode.
time.sleep(0.2)
#ENVIRONMENTAL COMMANDS
DVLPort.write(bytearray(['E', 'A', '0', '0', '0', '0', '0', '\n'])) #Corrects for physical misalignment between Beam 3 and the heading reference.
DVLPort.write(bytearray(['E', 'D', '0', '0', '0', '0', '\n'])) #Sets the ExplorerDVL transducer depth.
DVLPort.write(bytearray(['E', 'S', '3', '5', '\n'])) #Sets the water's salinity value.
DVLPort.write(bytearray(['E', 'X', '1', '1', '1', '1', '1', '\n'])) #Sets the coordinate transformation processing flags.
DVLPort.write(bytearray(['E', 'Z', '2', '2', '2', '2', '2', '2', '2', '0', '\n'])) #Selects the source of environmental sensor data.
time.sleep(0.2)
#TIMING COMMANDS
DVLPort.write(bytearray(['T', 'E', '0', '0', ':', '0', '0', ':', '0', '0', '.', '0', '0', '\n'])) #Sets the minimum interval between data collection cycles (data ensembles).
DVLPort.write(bytearray(['T', 'P', '0', '0', ':', '0', '0', '.', '0', '5', '\n'])) #Sets the minimum time between pings.
time.sleep(0.2)
#EXPERT BOTTOM TRACK COMMANDS
DVLPort.write(bytearray(['#', 'B', 'K', '0', '\n'])) #Selects the ping frequency of the water-mass layer ping.
DVLPort.write(bytearray(['#', 'B', 'L', '2', '0', ',', '8', '0', ',', '1', '6', '0', '\n'])) #Sets bottom-track water-mass layer boundaries and minimum layer size.
DVLPort.write(bytearray(['#', 'C', 'T', '1', '\n'])) #Allows the ExplorerDVL to initialize to predefined parameters and start pinging within 10 seconds after power is applied, or a break is received, if no command is entered.
DVLPort.write(bytearray(['#', 'E', 'E', '0', '0', '0', '0', '0', '0', '0', '\n'])) #Controls output of specialized data types; controls whether a transform of velocity data to raw or nominal beam is done with associated corrections in the case of the phased array system.
DVLPort.write(bytearray(['#', 'E', 'V', '0', '0', '0', '0', '0', '\n'])) #Corrects for electrical/magnetic bias between the ExplorerDVL heading value and the heading reference.
DVLPort.write(bytearray(['#', 'P', 'D', '5', '\n'])) #Selecting output format of DVL data
time.sleep(0.2)
#STARTING DVL
DVLPort.write(bytearray(['C', 'K', '\n'])) #Save parameters to user file on DVL
DVLPort.write(bytearray(['C', 'S', '\n'])) #Start DVL
time.sleep(0.2)

DVLPort.flushInput()
while True:
    if DVLPort.inWaiting() != 0:
        ID = hex(ord(DVLPort.read()))
        if ID == "0x7d":
            ensemble = [] #Clear list
            
            outputFormat = ord(DVLPort.read()) #0 if using PD4 output format, 1 if using PD5 output format
            byteNumLSB = ord(DVLPort.read()) #How many bytes in ensemble
            byteNumMSB = ord(DVLPort.read()) #How many bytes in ensemble
            
            ensemble = [ID, outputFormat, byteNumLSB, byteNumMSB]
            for x in range(byteNumMSB << 8 | byteNumLSB):
                ensemble.append(ord(DVLPort.read()))
              
            eastPosition = struct.unpack('h', struct.pack('H', ensemble[57] << 24 | ensemble[56] << 16 | ensemble[55] << 8 | ensemble[54]))[0]
            northPosition = struct.unpack('h', struct.pack('H', ensemble[61] << 24 | ensemble[60] << 16 | ensemble[59] << 8 | ensemble[58]))[0]
            upPosition = struct.unpack('h', struct.pack('H', ensemble[65] << 24 | ensemble[64] << 16 | ensemble[63] << 8 | ensemble[62]))[0]
            positionError = struct.unpack('h', struct.pack('H', ensemble[69] << 24 | ensemble[68] << 16 | ensemble[67] << 8 | ensemble[66]))[0]
              
            xVel = struct.unpack('h', struct.pack('H', ensemble[6] << 8 | ensemble[5]))[0]
            yVel = struct.unpack('h', struct.pack('H', ensemble[8] << 8 | ensemble[7]))[0]
            zVel = struct.unpack('h', struct.pack('H', ensemble[10] << 8 | ensemble[9]))[0]
            
            heading = struct.unpack('h', struct.pack('H', ensemble[53] << 8 | ensemble[52]))[0]
            pitch = struct.unpack('h', struct.pack('H', ensemble[49] << 8 | ensemble[48]))[0]
            roll = struct.unpack('h', struct.pack('H', ensemble[51] << 8 | ensemble[50]))[0]
            depth = struct.unpack('h', struct.pack('H', ensemble[47] << 8 | ensemble[46]))[0]/10
            
            elevation = struct.unpack('h', struct.pack('H', ensemble[12] << 8 | ensemble[11]))[0]
            speedOfSound = struct.unpack('h', struct.pack('H', ensemble[42] << 8 | ensemble[41]))[0]
            waterTemp = struct.unpack('h', struct.pack('H', ensemble[44] << 8 | ensemble[43]))[0]/100.0 #deg c
            
            print "Positions(mm) (North, East, Up, Error)", northPosition, eastPosition, upPosition, positionError
            print "Velocities(mm/s) (X, Y, Z):", xVel, yVel, zVel
            print "Yaw, Pitch, Roll, Depth (deg, deg, deg, m):", heading, pitch, roll, depth
            print "Elevation Velocity, Speed Of Sound, Water Temp: (mm/s, m/s, deg C)", elevation, speedOfSound, waterTemp
            print "\n"
                
                
                
                
                
                
                
                