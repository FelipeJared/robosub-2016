'''
Created on Sep 4, 2015

@author: Austin
'''

import serial 
import time
import Tkinter

window = Tkinter.Tk()

#Instructions
PING = 0x01 #No execution. It is used when controller is ready to receive Status Packet
READ_DATA = 0x02 #This command reads data from Dynamixel
WRITE_DATA = 0x03 #This command writes data to Dynamixel
REG_WRITE = 0x04 #It is similar to WRITE_DATA, but it remains in the standby state without being executed until the ACTION command arrives.
ACTION = 0x05 #This command initiates motions registered with REG WRITE
RESET = 0x06 #This command restores the state of Dynamixel to the factory default setting.
SYNC_WRITE = 0x83 #This command is used to control several Dynamixels simultaneously at a time.


arduino = serial.Serial("COM6", 1000000); time.sleep(2)
servo = serial.Serial("COM4", 1000000)

previousBasePosition, previousSecondJointPosition, previousThirdJointPosition, previousWristPosition, previouseEndEffectorPosition = 0, 0, 0, 0, 0
currentDataPacket = {}
setInitialPosition = True

def servoInstruction(servoID, instruction, *servoParams):
    arduino.write('1')#TX Enabled/RX Disabled
    
    dataPacket = [0xFF, 0xFF, servoID, len(servoParams)+2, instruction]
    
    for index, value in enumerate(servoParams):
        dataPacket.append(value)
        
    CRCValue = ~(sum(dataPacket[2:]) & 0xFF) & 0xFF
    dataPacket.append(CRCValue)
    
    servo.write(bytearray(dataPacket))
    
    arduino.write('0')#RX Enabled/TX Disabled
    time.sleep(0.01)

def updateGUI(window):
    global setInitialPosition, currentDataPacket, previousBasePosition, previousSecondJointPosition, previousThirdJointPosition, previousWristPosition, previouseEndEffectorPosition
    
    if window.quitFlag:
        window.destroy()  #This avoids the update event being in limbo
    else:
        if servo.inWaiting() >= 5: #Minimum bytes in a data packet
            if ord(servo.read()) == 0xFF and ord(servo.read()) == 0xFF:
                servoId = ord(servo.read())
                length = ord(servo.read())
                error = ord(servo.read())
                parameters = []
                for x in range(length-2): #-2 because not including length or error
                    parameters.append(ord(servo.read()))
                CRC = ord(servo.read())
                currentDataPacket[servoId] = [0xFF, 0xFF, servoId, length, error, parameters, CRC]
                
                print currentDataPacket
                
                if setInitialPosition == True and len(currentDataPacket) == 5:
                    window.jointScales[0].set((currentDataPacket[1][5][1] << 8) | currentDataPacket[1][5][0])
                    window.jointScales[1].set((currentDataPacket[2][5][1] << 8) | currentDataPacket[2][5][0])
                    window.jointScales[2].set((currentDataPacket[3][5][1] << 8) | currentDataPacket[3][5][0])
                    window.jointScales[3].set((currentDataPacket[4][5][1] << 8) | currentDataPacket[4][5][0])
                    window.jointScales[4].set((currentDataPacket[5][5][1] << 8) | currentDataPacket[5][5][0])
                    setInitialPosition = False
        
        basePosition = window.jointScales[0].get()
        secondJointPosition = window.jointScales[1].get() 
        thirdJointPosition = window.jointScales[2].get()   
        wristPosition = window.jointScales[3].get()  
        endEffectorPosition = window.jointScales[4].get()
        
        if basePosition != previousBasePosition:
            servoInstruction(0x01, WRITE_DATA, 0x01E, basePosition & 0xFF, basePosition >> 8)
        previousBasePosition = basePosition
        
        if secondJointPosition != previousSecondJointPosition:
            servoInstruction(0x02, WRITE_DATA, 0x01E, secondJointPosition & 0xFF, secondJointPosition >> 8)
        previousSecondJointPosition = secondJointPosition
        
        if thirdJointPosition != previousThirdJointPosition:
            servoInstruction(0x03, WRITE_DATA, 0x01E, thirdJointPosition & 0xFF, thirdJointPosition >> 8)
        previousThirdJointPosition = thirdJointPosition
        
        if wristPosition != previousWristPosition:
            servoInstruction(0x04, WRITE_DATA, 0x01E, wristPosition & 0xFF, wristPosition >> 8)
        previousWristPosition = wristPosition
        
        if endEffectorPosition != previouseEndEffectorPosition:
            servoInstruction(0x05, WRITE_DATA, 0x01E, endEffectorPosition & 0xFF, endEffectorPosition >> 8)
        previouseEndEffectorPosition = endEffectorPosition
        
        
        
        window.update()
        window.after(0, func=lambda: updateGUI(window))
                       
if __name__ == "__main__":
    servoInstruction(0x01, READ_DATA, 0x24, 0x02)
    servoInstruction(0x02, READ_DATA, 0x24, 0x02)
    servoInstruction(0x03, READ_DATA, 0x24, 0x02)
    servoInstruction(0x04, READ_DATA, 0x24, 0x02)
    servoInstruction(0x05, READ_DATA, 0x24, 0x02)
    
    #Setting up window
    guiWidth, guiHeight, guiXPosition, guiYPosition = 300, 225, 500, 500
    window.geometry(str(guiWidth)+"x"+str(guiHeight)+"+"+str(guiXPosition)+"+"+str(guiYPosition)) #"1590x870+0+0"
    window.title("Mechatronics Claw GUI")
    setattr(window, "quitFlag", False)
    
    #Slider Frame
    scaleFrame = Tkinter.Frame(window)
    scaleFrame.grid(row = 0, column = 0)
    
    #Sliders
    endEffectorLabel = Tkinter.Label(scaleFrame, text = "End Effector:")
    endEffectorLabel.grid(row = 0, column = 0, sticky="SE")
    endEffectorScale = Tkinter.Scale(scaleFrame, from_ = 0, to = 1023, width = 15, orient = "horizontal") #Creating sliders
    endEffectorScale.grid(row = 0, column = 1)
    
    wristLabel = Tkinter.Label(scaleFrame, text = "Wrist:")
    wristLabel.grid(row = 1, column = 0, sticky="SE")
    wristScale = Tkinter.Scale(scaleFrame, from_ = 0, to = 1023, width = 15, orient = "horizontal") #Creating sliders
    wristScale.grid(row = 1, column = 1)
    
    thirdJointLabel = Tkinter.Label(scaleFrame, text = "Third Joint:")
    thirdJointLabel.grid(row = 2, column = 0, sticky="SE")
    thirdJointScale = Tkinter.Scale(scaleFrame, from_ = 0, to = 1023, width = 15, orient = "horizontal") #Creating sliders
    thirdJointScale.grid(row = 2, column = 1)
    
    secondJointLabel = Tkinter.Label(scaleFrame, text = "Second Joint:")
    secondJointLabel.grid(row = 3, column = 0, sticky="SE")
    secondJointScale = Tkinter.Scale(scaleFrame, from_ = 0, to = 1023, width = 15, orient = "horizontal") #Creating sliders
    secondJointScale.grid(row = 3, column = 1)
    
    baseLabel = Tkinter.Label(scaleFrame, text = "Base:")
    baseLabel.grid(row = 4, column = 0, sticky="SE")
    baseJointScale = Tkinter.Scale(scaleFrame, from_ = 0, to = 1023, width = 15, orient = "horizontal") #Creating sliders
    baseJointScale.grid(row = 4, column = 1)
    
    jointScales = [baseJointScale, secondJointScale, thirdJointScale, wristScale, endEffectorScale]
    setattr(window, "jointScales", jointScales)
    
    
    window.after(0, func=lambda: updateGUI(window))
    window.mainloop()
            