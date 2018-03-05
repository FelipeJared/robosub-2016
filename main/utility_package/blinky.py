'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: blinky
   :synopsis: Serial communication test

:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Apr 3, 2015
:Description: This module is a stand-alone program that tests the serial communication of various embedded devices. The device must have some echo test code flashed onto the chip in order for this module to work.
'''

import serial 
import Tkinter

ser1 = serial.Serial("COM30", 9600)
window = Tkinter.Tk()

def on():
    '''
        Sends a 3 to the embedded device.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
    '''
    ser1.write(bytearray([3]))
    
def off():
    ''''
        Sends a 2 to the embedded device.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
    '''
    ser1.write(bytearray([2]))
    
def setQuitFlag():
    '''
        Terminates the GUI.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
    '''
    window.quitFlag = True
    
def updateGUI(window):
    '''
        This class handles the aspects of the GUI which have to be updated.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
    '''
    if window.quitFlag:
        window.destroy()

    else:
        if ser1.inWaiting() != 0:
            print ord(ser1.read())
            
        window.update()
        window.after(0, func=lambda: updateGUI(window))

window.geometry("250x300+675+200") #"1590x870+0+0"
window.title("Mechatronics RoboSub GUI")

onButton = Tkinter.Button(window, text = "ON", width = 20, height = 7, command=lambda: on())
onButton.place(relx = 0.5, rely = 0.25, anchor="center")

offButton = Tkinter.Button(window, text = "OFF", fg='black', width = 20, height = 7, command=lambda: off())
offButton.place(relx = 0.5, rely = 0.75, anchor="center")

window.after(0, func=lambda: updateGUI(window))

setattr(window, 'quitFlag', False)
window.protocol('WM_DELETE_WINDOW', setQuitFlag)


window.mainloop()
