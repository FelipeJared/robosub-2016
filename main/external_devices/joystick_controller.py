'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: joystick_controller
   :synopsis: Handles the joystick information sent from a separate laptop.
   
:Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Dec 25, 2014
:Description: Unpacks the joystick data sent through UDP packets from a separate laptop (Manual Control).
'''
import pygame
from pygame.locals import *
import os, sys
import threading
import time
import socket, select, pickle

class controllerResponse(threading.Thread):
    def __init__(self):
        '''
        Thread initialization.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Returns.**\n
        '''
        threading.Thread.__init__(self)
        self.runThread = True
        self.requestTime = 0.01 #How often I request data packets from device
        self.manualControlEnabled = False
        self.getList = []
        
    def run(self):
        '''
        Joystick data taken from UDP port, unpickled, and assigned to variable, and put in instance list attribute.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Returns.**\n
        '''
        UDP_IP = "0.0.0.0"
        UDP_PORT = 5006
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))# bind local port for receive
        is_readable = [sock]
        is_writable = []
        is_error = []
        r, w, e = select.select(is_readable, is_writable, is_error, 1.0)
        
        while self.runThread:
            
            #time.sleep(0.01) #Slows down thread to save some power
            
            if self.manualControlEnabled == True:
                if r:
                    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                    unpickled_data = pickle.loads(data)
                    name = unpickled_data[0]
                    axes = unpickled_data[1]
                    buttons = unpickled_data[2]
                    hats = unpickled_data[3]
                    self.getList.append([name, axes, buttons, hats])
                else:
                    try:
                        pygame.init()
                        pygame.event.get()                  
                        joystick_count = pygame.joystick.get_count()
                        # assume first joystick
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                        # Get the name from the OS for the controller/joystick
                        name = joystick.get_name()
                        # Usually axis run in pairs, up/down for one, and left/right for the other
                        num_axes = joystick.get_numaxes()    
                        num_buttons = joystick.get_numbuttons()
                        num_hats = joystick.get_numhats()
                        axes = []
                        buttons = []
                        hats = []
                        
                        for i in range(num_axes):
                            axis = joystick.get_axis( i )
                            axes.append(axis)
                            
                        for i in range(num_buttons):
                            button = joystick.get_button( i )
                            buttons.append(button)
                            
                        for i in range(num_hats):
                            hat = joystick.get_hat( i )
                            hats.append(hat)
                        
                        time.sleep(self.requestTime)
                        
                        self.getList.append([name, axes, buttons, hats])
                    except:
                        pass
                
    def updateManualControlMode(self, manualControlEnabled):
        '''
        Updates the manual control mode index.
        
        **Parameters**: \n
        * **manualControlEnabled** - Integer indicating which mode is on.
        
        **Returns**: \n
        * **No Returns.**\n
        '''
        self.manualControlEnabled = manualControlEnabled
        
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False
if __name__ == "__main__":
    # define network addresses
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5006
    # bind local port for receive
    print socket.gethostname()
    print socket.gethostbyname("RoboSub")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    #sock.sendto("asdd", ("192.168.2.89", 5006))

    while True:
        '''print socket.gethostbyname('Jared')
        print socket.gethostbyaddr("192.168.2.89")
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print data
        '''
        is_readable = [sock]
        is_writable = []
        is_error = []
        r, w, e = select.select(is_readable, is_writable, is_error, 1.0)
        if r:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            unpickled_data = pickle.loads(data)
            name = unpickled_data[0]
            axes = unpickled_data[1]
            buttons = unpickled_data[2]
            hats = unpickled_data[3]
            print unpickled_data
        else:
            print "Still waiting"