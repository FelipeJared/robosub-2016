'''
Copyright 2015, Austin Owens, Jared Guerrero, All rights reserved.

.. module:: _send_joystick_data_
   :synopsis: Controls the sub manually with a remote controller.
   
:Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Jun 10, 2015
:Description: This module controls the sub manually with a joystick though Ethernet, Wi-Fi, or locally.
'''

import pygame
import socket
import pickle
import numpy

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# Used to manage how fast the screen updates
clock = pygame.time.Clock() 

pygame.init()
# Set the width and height of the screen [width,height]
size = [500, 250]
screen = pygame.display.set_mode(size)

iterations = 0

done = False

data = []
previousData = []
counter = 0

while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
    
    #pygame.init()
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
    
    
    
    if iterations >= -4:
        iterations = 0    
        for i in range(num_axes):
            axis = joystick.get_axis( i )
            axes.append(axis)
            
        for i in range(num_buttons):
            button = joystick.get_button( i )
            buttons.append(button)
            
        for i in range(num_hats):
            hat = joystick.get_hat( i )
            hats.append(hat)
            
        data = [name, axes, buttons, hats]
        #print socket.gethostbyname(socket.gethostname())
        #print socket.gethostbyname("DESKTOP-2NC0IU8")
        try:
            sock.sendto(pickle.dumps(data), ('192.168.1.25', 5006))#Send to the IP address of the sub on port 5006
            print data
        except:
            print "RoboSub not detected."
    iterations += 1
    clock.tick(15) #This slows down the sending of packets. Need this so I dont overflow subs buffer

