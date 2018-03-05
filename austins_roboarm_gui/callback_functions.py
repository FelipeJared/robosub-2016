'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: callback_functions
   :synopsis: Contains all the callback functions from various widgets such as buttons.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Dec 25, 2015
:Description: Oftentimes when certain widgets are set up, they require a dedicated function to call when the widget is activated, such as a button push. These type of widgets that require a function to be written and executed when the widget is activated is called a callback widget. The code for all callback widgets are located in the callback_widgets module. 
'''

import Tkinter, tkFileDialog, os
import previous_state_logging_system
import dynamixel_comm.ax_series as ax_series
import dynamixel_comm.mx_series as mx_series
import time

window = None
usb2DynamixelSerial = None

def setWindowObject(windowObj):
    global window
    window = windowObj
    
def setComPort(serialComPort):
    global usb2DynamixelSerial
    usb2DynamixelSerial = serialComPort
    
def licenseAgreement(window):
    #SETTING UP WINDOW
    window.geometry("500x580+0+0")
    window.title("Terms and Conditions")
    
    eulaFrame = Tkinter.Frame(window)
    eulaFrame.grid(row=0, column=0)
    
    scrollBar = Tkinter.Scrollbar(eulaFrame)
    scrollBar.grid(row = 0, column = 2, sticky='ns')
    consolText = Tkinter.Text(eulaFrame, borderwidth = 7, yscrollcommand=scrollBar.set, width = 58, height = 30)
    consolText.grid(row = 0, column = 0, columnspan=2)
    scrollBar.config(command=consolText.yview)
    with open('README.txt', 'r') as f:
        content = f.readlines()
        consolText.insert(1.0, "".join(content))
        consolText.config(state="disabled")
      
    def iAgreeToEULA():
        window.EULA = True
        eulaFrame.grid_remove() #Removes all widgets from EULA so they don't appear on the main application
        window.quit()
        
    def iDisagreeToEULA():
        window.destroy()
    
    iAcceptButton = Tkinter.Button(eulaFrame, text = "I Accept", width = 12, command = iAgreeToEULA)
    iAcceptButton.grid(row = 1, column = 0, pady = 10)
    cencelButton = Tkinter.Button(eulaFrame, text = "Cancel", width = 12, command = iDisagreeToEULA)
    cencelButton.grid(row = 1, column = 1, pady = 10)
    setattr(window, "EULA", False)
    
    copyrightLabel = Tkinter.Label(eulaFrame, text="Copyright (c) 2016, Austin Owens, All rights reserved.", font=("Calibri", 13), foreground = "black")
    copyrightLabel.grid(row=2, column=0, columnspan=2, sticky="nsew")
    
    window.update()
    window.mainloop()
            
def saveValuesToFile(servoModelName):
    previous_state_logging_system.Log('_Saved_Values_/Saved_{}_GUI&RAM_Values.txt'.format(servoModelName)).writeParameters(minHue = window.filterScales[0].get(), minSat = window.filterScales[1].get(), minVal = window.filterScales[2].get(), erodeDilate = window.filterScales[3].get(), maxHue = window.filterScales[4].get(), maxSat = window.filterScales[5].get(), maxVal = window.filterScales[6].get(), intensity = window.filterScales[7].get(),
                                                                                                                           positionCheckBox = window.printCheckBoxValArray[0].get(), speedCheckBox = window.printCheckBoxValArray[1].get(), voltageCheckBox = window.printCheckBoxValArray[2].get(), loadCheckBox = window.printCheckBoxValArray[3].get(), temperatureCheckBox = window.printCheckBoxValArray[4].get(), 
                                                                                                                           dropBoxServoNumVariable = window.dropBoxServoNumVariable.get(), dropBoxServoModelVariable = "'"+window.dropBoxServoModelVariable.get()+"'", #Adding tick marks here since apparently in the previous state logging system, it will think the letters are a variable that doesnt exsist instead of a string
                                                                                                                           dropBoxFwdKinematicsSelectorVariable = "'"+window.dropBoxFwdKinematicsSelectorVariable.get()+"'", dropBoxInvKinematicsSelectorVariable = "'"+window.dropBoxInvKinematicsSelectorVariable.get()+"'",
                                                                                                                           invKinSolutionNumber = "'"+window.invKinSolutionNumber.get()+"'",
                                                                                                                           movingSpeed1 = window.config1Scales[0][0].get(), movingSpeed2 = window.config1Scales[0][1].get(), movingSpeed3 = window.config1Scales[0][2].get(), movingSpeed4 = window.config1Scales[0][3].get(), movingSpeed5 = window.config1Scales[0][4].get(), movingSpeed6 = window.config1Scales[0][5].get(), movingSpeed7 = window.config1Scales[0][6].get(), movingSpeed8 = window.config1Scales[0][7].get(),
                                                                                                                           torqueLimit1 = window.config1Scales[1][0].get(), torqueLimit2 = window.config1Scales[1][1].get(), torqueLimit3 = window.config1Scales[1][2].get(), torqueLimit4 = window.config1Scales[1][3].get(), torqueLimit5 = window.config1Scales[1][4].get(), torqueLimit6 = window.config1Scales[1][5].get(), torqueLimit7 = window.config1Scales[1][6].get(), torqueLimit8 = window.config1Scales[1][7].get(),
                                                                                                                           ledEnable1 = window.config1Scales[6][0].get(), ledEnable2 = window.config1Scales[6][1].get(), ledEnable3 = window.config1Scales[6][2].get(), ledEnable4 = window.config1Scales[6][3].get(), ledEnable5 = window.config1Scales[6][4].get(), ledEnable6 = window.config1Scales[6][5].get(), ledEnable7 = window.config1Scales[6][6].get(), ledEnable8 = window.config1Scales[6][7].get(),
                                                                                                                           CWComplianceMarginScale1 = window.config2Scales[2][0].get(), CWComplianceMarginScale2 = window.config2Scales[2][1].get(), CWComplianceMarginScale3 = window.config2Scales[2][2].get(), CWComplianceMarginScale4 = window.config2Scales[2][3].get(), CWComplianceMarginScale5 = window.config2Scales[2][4].get(), CWComplianceMarginScale6 = window.config2Scales[2][5].get(), CWComplianceMarginScale7 = window.config2Scales[2][6].get(), CWComplianceMarginScale8 = window.config2Scales[2][7].get(),
                                                                                                                           CCWComplianceMarginScale1 = window.config2Scales[3][0].get(), CCWComplianceMarginScale2 = window.config2Scales[3][1].get(), CCWComplianceMarginScale3 = window.config2Scales[3][2].get(), CCWComplianceMarginScale4 = window.config2Scales[3][3].get(), CCWComplianceMarginScale5 = window.config2Scales[3][4].get(), CCWComplianceMarginScale6 = window.config2Scales[3][5].get(), CCWComplianceMarginScale7 = window.config2Scales[3][6].get(), CCWComplianceMarginScale8 = window.config2Scales[3][7].get(),
                                                                                                                           CWComplianceSlopeScale1 = window.config2Scales[4][0].get(), CWComplianceSlopeScale2 = window.config2Scales[4][1].get(), CWComplianceSlopeScale3 = window.config2Scales[4][2].get(), CWComplianceSlopeScale4 = window.config2Scales[4][3].get(), CWComplianceSlopeScale5 = window.config2Scales[4][4].get(), CWComplianceSlopeScale6 = window.config2Scales[4][5].get(), CWComplianceSlopeScale7 = window.config2Scales[4][6].get(), CWComplianceSlopeScale8 = window.config2Scales[4][7].get(),
                                                                                                                           CCWComplianceSlopeScale1 = window.config2Scales[5][0].get(), CCWComplianceSlopeScale2 = window.config2Scales[5][1].get(), CCWComplianceSlopeScale3 = window.config2Scales[5][2].get(), CCWComplianceSlopeScale4 = window.config2Scales[5][3].get(), CCWComplianceSlopeScale5 = window.config2Scales[5][4].get(), CCWComplianceSlopeScale6 = window.config2Scales[5][5].get(), CCWComplianceSlopeScale7 = window.config2Scales[5][6].get(), CCWComplianceSlopeScale8 = window.config2Scales[5][7].get(),
                                                                                                                           PScale1 = window.config2Scales[6][0].get(), PScale2 = window.config2Scales[6][1].get(), PScale3 = window.config2Scales[6][2].get(), PScale4 = window.config2Scales[6][3].get(), PScale5 = window.config2Scales[6][4].get(), PScale6 = window.config2Scales[6][5].get(), PScale7 = window.config2Scales[6][6].get(), PScale8 = window.config2Scales[6][7].get(),
                                                                                                                           IScale1 = window.config2Scales[7][0].get(), IScale2 = window.config2Scales[7][1].get(), IScale3 = window.config2Scales[7][2].get(), IScale4 = window.config2Scales[7][3].get(), IScale5 = window.config2Scales[7][4].get(), IScale6 = window.config2Scales[7][5].get(), IScale7 = window.config2Scales[7][6].get(), IScale8 = window.config2Scales[7][7].get(),
                                                                                                                           DScale1 = window.config2Scales[8][0].get(), DScale2 = window.config2Scales[8][1].get(), DScale3 = window.config2Scales[8][2].get(), DScale4 = window.config2Scales[8][3].get(), DScale5 = window.config2Scales[8][4].get(), DScale6 = window.config2Scales[8][5].get(), DScale7 = window.config2Scales[8][6].get(), DScale8 = window.config2Scales[8][7].get(),
                                                                                                                           punchScale1 = window.config2Scales[9][0].get(), punchScale2 = window.config2Scales[9][1].get(), punchScale3 = window.config2Scales[9][2].get(), punchScale4 = window.config2Scales[9][3].get(), punchScale5 = window.config2Scales[9][4].get(), punchScale6 = window.config2Scales[9][5].get(), punchScale7 = window.config2Scales[9][6].get(), punchScale8 = window.config2Scales[9][7].get(),
                                                                                                                           goalAccelerationScale1 = window.config3Scales[4][0].get(), goalAccelerationScale2 = window.config3Scales[4][1].get(), goalAccelerationScale3 = window.config3Scales[4][2].get(), goalAccelerationScale4 = window.config3Scales[4][3].get(), goalAccelerationScale5 = window.config3Scales[4][4].get(), goalAccelerationScale6 = window.config3Scales[4][5].get(), goalAccelerationScale7 = window.config3Scales[4][6].get(), goalAccelerationScale8 = window.config3Scales[4][7].get(),
                                                                                                                           sampleRate = window.sampleRate)
    
    
def escape(event):
    if event.keycode == 27: #Escape character; terminate program
        if not window.DEBUG and window.connectedToggleBool == True:
            window.servoModel.killThread()
        saveValuesToFile(window.dropBoxServoModelVariable.get())
        previous_state_logging_system.Log('_Saved_Values_/Last_Servo_Model_Used.txt').writeParameters(lastServoModel = "'"+window.dropBoxServoModelVariable.get()+"'")#Adding tick marks here since apparently in the previous state logging system, it will think the letters are a variable that doesnt exsist instead of a string
        window.quitFlag = True
        
def closeWindow():
    if not window.DEBUG and window.connectedToggleBool == True:
        window.servoModel.killThread()
    saveValuesToFile(window.dropBoxServoModelVariable.get())
    previous_state_logging_system.Log('_Saved_Values_/Last_Servo_Model_Used.txt').writeParameters(lastServoModel = "'"+window.dropBoxServoModelVariable.get()+"'")#Adding tick marks here since apparently in the previous state logging system, it will think the letters are a variable that doesnt exsist instead of a string
    window.quitFlag = True

def connectDisconnect():
    window.connectedToggleBool = not window.connectedToggleBool
    
    #CONNECT WITH SERVOS
    if window.connectedToggleBool == True:
        window.connectDisconnectButton.config(text="Connected", fg="green")
        window.dropBoxServoModel.config(state="disabled")
        window.dropBoxServoNum.config(state="disabled")
        window.dropBoxFwdKinematicSelector.config(state="disabled")
        window.dropBoxInvKinematicSelector.config(state="disabled")
        window.recordButton.config(state="active")
        window.playButton.config(state="active")
        usb2DynamixelSerial.flushInput(); usb2DynamixelSerial.flushOutput()
        
        if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
            window.servoModel = ax_series.AXCommandParse(usb2DynamixelSerial)
        elif window.dropBoxServoModelVariable.get() == 'MX-28':
            window.servoModel = mx_series.MXCommandParse(usb2DynamixelSerial)
        
        window.servoModel.start() #Start listener thread
        
        _updateEEPROMSliders()
        time.sleep(0.02) #This is so that the serial data has enough time to get sent to the servos and sent back before the connect/disconnect button is pressed again
                
    #DISCONNECT WITH SERVOS
    elif window.connectedToggleBool == False:
        window.connectDisconnectButton.config(text="Disconnected", fg="red")
        window.dropBoxServoModel.config(state="active")
        window.dropBoxServoNum.config(state="active")
        window.dropBoxFwdKinematicSelector.config(state="active")
        window.dropBoxInvKinematicSelector.config(state="active")
        window.recordButton.config(state="disabled")
        window.playButton.config(state="disabled")
        window.servoModel.killThread()
        usb2DynamixelSerial.flushInput(); usb2DynamixelSerial.flushOutput()
        
def _updateEEPROMSliders(): #Only used in the connectDisconnect function
    #Getting EEPROM values so sliders can be initially set when the connectDisconnect button is pressed since these values are not naturally pulled from a file like RAM values
    for servoID in range(1, window.dropBoxServoNumVariable.get()+1):
        if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18' or window.dropBoxServoModelVariable.get() == 'MX-28':
            window.servoModel.getPresentPosition(servoID)
            window.servoModel.getCWAngleLimit(servoID)
            window.servoModel.getCCWAngleLimit(servoID)
            window.servoModel.getLowestLimitVoltage(servoID)
            window.servoModel.getHighestLimitVoltage(servoID)
            window.servoModel.getHighestLimitTemperature(servoID)
            window.servoModel.getReturnDelayTime(servoID)
            window.servoModel.getAlarmLED(servoID)
            window.servoModel.getAlarmShutdown(servoID)
            
        if window.dropBoxServoModelVariable.get() == 'MX-28':
            window.servoModel.getMultiTurnOffset(servoID)
            window.servoModel.getResolutionDivider(servoID)
       
    
    #WHENEVER THE CONNECT/DISCONNECT BUTTON GOES INTO THE CONNECTED STATE, SET ALL EEPROM SLIDERS TO WHAT THE SERVO REGISTER VALUES IS
    #Config 3 EEPROM   
    alarmLEDScale, alarmShutdownScale, multiTurnOffsetScale, resolutionDividerScale = window.config3Scales[0], window.config3Scales[1], window.config3Scales[2], window.config3Scales[3]
    #Config 2 EEPROM
    CWLimitScale, CCWLimitScale = window.config2Scales[0], window.config2Scales[1]
    #Config 1 EEPROM
    lowestVoltageLimitScale, highestVoltageLimitScale, highestTemperatureLimitScale, returnDelayTimeScale = window.config1Scales[2], window.config1Scales[3], window.config1Scales[4], window.config1Scales[5]
    for x in range(8):
        
        if (x+1) <= len(window.servoModel.presentPositionData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            window.jointScales[x].set(window.servoModel.presentPositionData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            window.jointScales[x].set(0)
        
        #CONFIG 3
        if (x+1) <= len(window.servoModel.alarmLEDData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            alarmLEDScale[x].set(window.servoModel.alarmLEDData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            alarmLEDScale[x].set(0)
            
        if (x+1) <= len(window.servoModel.alarmShutdownData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            alarmShutdownScale[x].set(window.servoModel.alarmShutdownData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            alarmShutdownScale[x].set(0)
            
        if window.dropBoxServoModelVariable.get() == 'MX-28':
            if (x+1) <= len(window.servoModel.multiTurnOffsetData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
                multiTurnOffsetScale[x].set(window.servoModel.multiTurnOffsetData[x+1])
            else: #If there are less then 8 servos, the rest of the sliders will be set at default value
                multiTurnOffsetScale[x].set(0)
                
            if (x+1) <= len(window.servoModel.resolutionDividerData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
                resolutionDividerScale[x].set(window.servoModel.resolutionDividerData[x+1])
            else: #If there are less then 8 servos, the rest of the sliders will be set at default value
                resolutionDividerScale[x].set(0)
        
        #CONFIG 2        
        if (x+1) <= len(window.servoModel.CWAngleLimitData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            CWLimitScale[x].set(window.servoModel.CWAngleLimitData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            CWLimitScale[x].set(0)
            
        if (x+1) <= len(window.servoModel.CCWAngleLimitData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            CCWLimitScale[x].set(window.servoModel.CCWAngleLimitData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            CCWLimitScale[x].set(0)
            
        #CONFIG 1
        if (x+1) <= len(window.servoModel.lowestLimitVoltageData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            lowestVoltageLimitScale[x].set(window.servoModel.lowestLimitVoltageData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            lowestVoltageLimitScale[x].set(5)
            
        if (x+1) <= len(window.servoModel.highestLimitVoltageData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            highestVoltageLimitScale[x].set(window.servoModel.highestLimitVoltageData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            highestVoltageLimitScale[x].set(5)
            
        if (x+1) <= len(window.servoModel.highestLimitTemperatureData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            highestTemperatureLimitScale[x].set(window.servoModel.highestLimitTemperatureData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            highestTemperatureLimitScale[x].set(20)
            
        if (x+1) <= len(window.servoModel.returnDelayTimeData): #This statement is checking how many values were obtained from servos, essentially checking how many servos are actually connected
            returnDelayTimeScale[x].set(window.servoModel.returnDelayTimeData[x+1])
        else: #If there are less then 8 servos, the rest of the sliders will be set at default value
            returnDelayTimeScale[x].set(0)
    
def homeConfiguration(homeConfigArray):
    for x in range(len(homeConfigArray)):
        window.jointScales[x].set(homeConfigArray[x])
    
def trackObject():
    if window.trackObject == True: 
        window.trackObjectButton.config(text="Track Object")
        window.trackObject = False
        
    elif window.trackObject == False: 
        window.trackObjectButton.config(text="Untrack Object")
        window.trackObject = True
        
def samplingRateOk(*event):
    window.sampleRate = float(window.samplingRateText.get())
    window.samplingRateText.set(window.sampleRate)
    
def playBackRateMinus():
    if window.playbackLogValues.sampleRate > 5:
        window.playbackLogValues.sampleRate -= 5

def playBackRatePlus():
    window.playbackLogValues.sampleRate += 5

def playRecordedJointAnglesFile():
    try:
        if window.playButtonBool == False:
            #Placing widgets
            window.playBackModifier[0].place(relx = 0.51, rely = 0.45, anchor = "center")
            window.playBackModifier[1].place(relx = 0.49, rely = 0.49, anchor = "center")
            window.playBackModifier[2].place(relx = 0.53, rely = 0.49, anchor = "center")
            
            window.playbackLogValues = previous_state_logging_system.Log("_Saved_Values_/Recordings/"+window.playbackFileNameText.get()).getParameters("recordedJointValues", "sampleRate")
            window.playButton.config(text = "Stop")
            window.recordButton.config(state = "disabled")
            window.trackObjectButton.config(state = "disabled")
            window.playButtonBool = True
        elif window.playButtonBool == True:
            #Removing widgets
            window.playBackModifier[0].place_forget()
            window.playBackModifier[1].place_forget()
            window.playBackModifier[2].place_forget()
            
            window.playButton.config(text = "Play")
            window.recordButton.config(state = "normal")
            window.trackObjectButton.config(state = "normal")
            window.playButtonBool = False
        
    except:
        window.playBackModifier[0].place_forget()
        window.playBackModifier[1].place_forget()
        window.playBackModifier[2].place_forget()
        print "Could not read file."
        
    
    
        
def loadRecordedJointAnglesFile():
    fileLocation = tkFileDialog.askopenfilename()
    
    fileName = []
    try:
        for x in range(1, len(fileLocation)+1):
            if fileLocation[-x] != "/":
                fileName.append(fileLocation[-x])   
            else:
                break
            
        fileName.reverse()

        window.playbackFileNameText.set("".join(fileName))
            
    except:
        print "Can't open file."
        
def defaultRAMValues():
    config3DefaultRamValues = [0] #goalAcceleration
    for x in range(5, len(window.config3Scales)):
        for y in range(len(window.config3Scales[x])):
            window.config3Scales[x][y].set(config3DefaultRamValues[x-5])
    
    config2DefaultRamValues = [1, 1, 32, 32, 32, 0, 0, 0] #CWComplianceMarginScale, CCWComplianceMarginScale, CWComplianceSlopeScale, CCWComplianceSlopeScale, PScale, IScale, DScale, Punch
    for x in range(2, len(window.config2Scales)):
        for y in range(len(window.config2Scales[x])):
            window.config2Scales[x][y].set(config2DefaultRamValues[x-2])
           
    config1DefaultRamValues = [0, 100, 0] #movingSpeedScale, torqueLimitScale, ledEnableCheckbox
    for x in range(len(window.config1Scales)):
        for y in range(len(window.config1Scales[x])):
            if x == 0 or x == 1: #Positions where only RAM is
                window.config1Scales[x][y].set(config1DefaultRamValues[x])
            elif x == 6:
                window.config1Scales[x][y].set(config1DefaultRamValues[2])
            
def importConfigValues():
    fileLocation = tkFileDialog.askopenfilename()
    try:
        importedConfigValues = previous_state_logging_system.Log(fileLocation).getParameters("minHue", "minSat", "minVal", "erodeDilate", "maxHue", "maxSat", "maxVal", "intensity",
                                                                                             "positionCheckBox", "speedCheckBox", "voltageCheckBox", "loadCheckBox", "temperatureCheckBox",
                                                                                             "dropBoxFwdKinematicsSelectorVariable", "dropBoxInvKinematicsSelectorVariable",
                                                                                             "invKinSolutionNumber",
                                                                                             "movingSpeed1", "movingSpeed2", "movingSpeed3", "movingSpeed4", "movingSpeed5", "movingSpeed6", "movingSpeed7", "movingSpeed8",
                                                                                             "torqueLimit1", "torqueLimit2", "torqueLimit3", "torqueLimit4", "torqueLimit5", "torqueLimit6", "torqueLimit7", "torqueLimit8",
                                                                                             "lowestVoltageLimit1", "lowestVoltageLimit2", "lowestVoltageLimit3", "lowestVoltageLimit4", "lowestVoltageLimit5", "lowestVoltageLimit6", "lowestVoltageLimit7", "lowestVoltageLimit8",
                                                                                             "highestVoltageLimit1", "highestVoltageLimit2", "highestVoltageLimit3", "highestVoltageLimit4", "highestVoltageLimit5", "highestVoltageLimit6", "highestVoltageLimit7", "highestVoltageLimit8",
                                                                                             "highestTemperatureLimit1", "highestTemperatureLimit2", "highestTemperatureLimit3", "highestTemperatureLimit4", "highestTemperatureLimit5", "highestTemperatureLimit6", "highestTemperatureLimit7", "highestTemperatureLimit8",
                                                                                             "returnDelayTime1", "returnDelayTime2", "returnDelayTime3", "returnDelayTime4", "returnDelayTime5", "returnDelayTime6", "returnDelayTime7", "returnDelayTime8",
                                                                                             "ledEnable1", "ledEnable2", "ledEnable3", "ledEnable4", "ledEnable5", "ledEnable6", "ledEnable7", "ledEnable8",
                                                                                             "CWlimit1", "CWlimit2", "CWlimit3", "CWlimit4", "CWlimit5", "CWlimit6", "CWlimit7", "CWlimit8",
                                                                                             "CCWlimit1", "CCWlimit2", "CCWlimit3", "CCWlimit4", "CCWlimit5", "CCWlimit6", "CCWlimit7", "CCWlimit8",
                                                                                             "CWComplianceMarginScale1", "CWComplianceMarginScale2", "CWComplianceMarginScale3", "CWComplianceMarginScale4", "CWComplianceMarginScale5", "CWComplianceMarginScale6", "CWComplianceMarginScale7", "CWComplianceMarginScale8",
                                                                                             "CCWComplianceMarginScale1", "CCWComplianceMarginScale2", "CCWComplianceMarginScale3", "CCWComplianceMarginScale4", "CCWComplianceMarginScale5", "CCWComplianceMarginScale6", "CCWComplianceMarginScale7", "CCWComplianceMarginScale8",
                                                                                             "CWComplianceSlopeScale1", "CWComplianceSlopeScale2", "CWComplianceSlopeScale3", "CWComplianceSlopeScale4", "CWComplianceSlopeScale5", "CWComplianceSlopeScale6", "CWComplianceSlopeScale7", "CWComplianceSlopeScale8",
                                                                                             "CCWComplianceSlopeScale1", "CCWComplianceSlopeScale2", "CCWComplianceSlopeScale3", "CCWComplianceSlopeScale4", "CCWComplianceSlopeScale5", "CCWComplianceSlopeScale6", "CCWComplianceSlopeScale7", "CCWComplianceSlopeScale8",
                                                                                             "PScale1", "PScale2", "PScale3", "PScale4", "PScale5", "PScale6", "PScale7", "PScale8",
                                                                                             "IScale1", "IScale2", "IScale3", "IScale4", "IScale5", "IScale6", "IScale7", "IScale8",
                                                                                             "DScale1", "DScale2", "DScale3", "DScale4", "DScale5", "DScale6", "DScale7", "DScale8",
                                                                                             "punchScale1", "punchScale2", "punchScale3", "punchScale4", "punchScale5", "punchScale6", "punchScale7", "punchScale8",
                                                                                             "alarmLED1", "alarmLED2", "alarmLED3", "alarmLED4", "alarmLED5", "alarmLED6", "alarmLED7", "alarmLED8",
                                                                                             "alarmShutdown1", "alarmShutdown2", "alarmShutdown3", "alarmShutdown4", "alarmShutdown5", "alarmShutdown6", "alarmShutdown7", "alarmShutdown8",
                                                                                             "multiTurnOffsetScale1", "multiTurnOffsetScale2", "multiTurnOffsetScale3", "multiTurnOffsetScale4", "multiTurnOffsetScale5", "multiTurnOffsetScale6", "multiTurnOffsetScale7", "multiTurnOffsetScale8",
                                                                                             "resolutionDividerScale1", "resolutionDividerScale2", "resolutionDividerScale3", "resolutionDividerScale4", "resolutionDividerScale5", "resolutionDividerScale6", "resolutionDividerScale7", "resolutionDividerScale8",
                                                                                             "goalAccelerationScale1", "goalAccelerationScale2", "goalAccelerationScale3", "goalAccelerationScale4", "goalAccelerationScale5", "goalAccelerationScale6", "goalAccelerationScale7", "goalAccelerationScale8",
                                                                                             "sampleRate")
        
        importedConfig1List = [importedConfigValues.movingSpeed1, importedConfigValues.movingSpeed2, importedConfigValues.movingSpeed3, importedConfigValues.movingSpeed4, importedConfigValues.movingSpeed5, importedConfigValues.movingSpeed6, importedConfigValues.movingSpeed7, importedConfigValues.movingSpeed8,
                               importedConfigValues.torqueLimit1, importedConfigValues.torqueLimit2, importedConfigValues.torqueLimit3, importedConfigValues.torqueLimit4, importedConfigValues.torqueLimit5, importedConfigValues.torqueLimit6, importedConfigValues.torqueLimit7, importedConfigValues.torqueLimit8,
                               importedConfigValues.lowestVoltageLimit1, importedConfigValues.lowestVoltageLimit2, importedConfigValues.lowestVoltageLimit3, importedConfigValues.lowestVoltageLimit4, importedConfigValues.lowestVoltageLimit5, importedConfigValues.lowestVoltageLimit6, importedConfigValues.lowestVoltageLimit7, importedConfigValues.lowestVoltageLimit8,
                               importedConfigValues.highestVoltageLimit1, importedConfigValues.highestVoltageLimit2, importedConfigValues.highestVoltageLimit3, importedConfigValues.highestVoltageLimit4, importedConfigValues.highestVoltageLimit5, importedConfigValues.highestVoltageLimit6, importedConfigValues.highestVoltageLimit7, importedConfigValues.highestVoltageLimit8,
                               importedConfigValues.highestTemperatureLimit1, importedConfigValues.highestTemperatureLimit2, importedConfigValues.highestTemperatureLimit3, importedConfigValues.highestTemperatureLimit4, importedConfigValues.highestTemperatureLimit5, importedConfigValues.highestTemperatureLimit6, importedConfigValues.highestTemperatureLimit7, importedConfigValues.highestTemperatureLimit8,
                               importedConfigValues.returnDelayTime1, importedConfigValues.returnDelayTime2, importedConfigValues.returnDelayTime3, importedConfigValues.returnDelayTime4, importedConfigValues.returnDelayTime5, importedConfigValues.returnDelayTime6, importedConfigValues.returnDelayTime7, importedConfigValues.returnDelayTime8,
                               importedConfigValues.ledEnable1, importedConfigValues.ledEnable2, importedConfigValues.ledEnable3, importedConfigValues.ledEnable4, importedConfigValues.ledEnable5, importedConfigValues.ledEnable6, importedConfigValues.ledEnable7, importedConfigValues.ledEnable8]
        
        importedConfig2List = [importedConfigValues.CWlimit1, importedConfigValues.CWlimit2, importedConfigValues.CWlimit3, importedConfigValues.CWlimit4, importedConfigValues.CWlimit5, importedConfigValues.CWlimit6, importedConfigValues.CWlimit7, importedConfigValues.CWlimit8,
                               importedConfigValues.CCWlimit1, importedConfigValues.CCWlimit2, importedConfigValues.CCWlimit3, importedConfigValues.CCWlimit4, importedConfigValues.CCWlimit5, importedConfigValues.CCWlimit6, importedConfigValues.CCWlimit7, importedConfigValues.CCWlimit8,
                               importedConfigValues.CWComplianceMarginScale1, importedConfigValues.CWComplianceMarginScale2, importedConfigValues.CWComplianceMarginScale3, importedConfigValues.CWComplianceMarginScale4, importedConfigValues.CWComplianceMarginScale5, importedConfigValues.CWComplianceMarginScale6, importedConfigValues.CWComplianceMarginScale7, importedConfigValues.CWComplianceMarginScale8,
                               importedConfigValues.CCWComplianceMarginScale1, importedConfigValues.CCWComplianceMarginScale2, importedConfigValues.CCWComplianceMarginScale3, importedConfigValues.CCWComplianceMarginScale4, importedConfigValues.CCWComplianceMarginScale5, importedConfigValues.CCWComplianceMarginScale6, importedConfigValues.CCWComplianceMarginScale7, importedConfigValues.CCWComplianceMarginScale8,
                               importedConfigValues.CWComplianceSlopeScale1, importedConfigValues.CWComplianceSlopeScale2, importedConfigValues.CWComplianceSlopeScale3, importedConfigValues.CWComplianceSlopeScale4, importedConfigValues.CWComplianceSlopeScale5, importedConfigValues.CWComplianceSlopeScale6, importedConfigValues.CWComplianceSlopeScale7, importedConfigValues.CWComplianceSlopeScale8,
                               importedConfigValues.CCWComplianceSlopeScale1, importedConfigValues.CCWComplianceSlopeScale2, importedConfigValues.CCWComplianceSlopeScale3, importedConfigValues.CCWComplianceSlopeScale4, importedConfigValues.CCWComplianceSlopeScale5, importedConfigValues.CCWComplianceSlopeScale6, importedConfigValues.CCWComplianceSlopeScale7, importedConfigValues.CCWComplianceSlopeScale8,
                               importedConfigValues.PScale1, importedConfigValues.PScale2, importedConfigValues.PScale3, importedConfigValues.PScale4, importedConfigValues.PScale5, importedConfigValues.PScale6, importedConfigValues.PScale7, importedConfigValues.PScale8, 
                               importedConfigValues.IScale1, importedConfigValues.IScale2, importedConfigValues.IScale3, importedConfigValues.IScale4, importedConfigValues.IScale5, importedConfigValues.IScale6, importedConfigValues.IScale7, importedConfigValues.IScale8,
                               importedConfigValues.DScale1, importedConfigValues.DScale2, importedConfigValues.DScale3, importedConfigValues.DScale4, importedConfigValues.DScale5, importedConfigValues.DScale6, importedConfigValues.DScale7, importedConfigValues.DScale8,
                               importedConfigValues.punchScale1, importedConfigValues.punchScale2, importedConfigValues.punchScale3, importedConfigValues.punchScale4, importedConfigValues.punchScale5, importedConfigValues.punchScale6, importedConfigValues.punchScale7, importedConfigValues.punchScale8]
        
        importedConfig3List = [importedConfigValues.alarmLED1, importedConfigValues.alarmLED2, importedConfigValues.alarmLED3, importedConfigValues.alarmLED4, importedConfigValues.alarmLED5, importedConfigValues.alarmLED6, importedConfigValues.alarmLED7, importedConfigValues.alarmLED8,
                               importedConfigValues.alarmShutdown1, importedConfigValues.alarmShutdown2, importedConfigValues.alarmShutdown3, importedConfigValues.alarmShutdown4, importedConfigValues.alarmShutdown5, importedConfigValues.alarmShutdown6, importedConfigValues.alarmShutdown7, importedConfigValues.alarmShutdown8,
                               importedConfigValues.multiTurnOffsetScale1, importedConfigValues.multiTurnOffsetScale2, importedConfigValues.multiTurnOffsetScale3, importedConfigValues.multiTurnOffsetScale4, importedConfigValues.multiTurnOffsetScale5, importedConfigValues.multiTurnOffsetScale6, importedConfigValues.multiTurnOffsetScale7, importedConfigValues.multiTurnOffsetScale8,
                               importedConfigValues.resolutionDividerScale1, importedConfigValues.resolutionDividerScale2, importedConfigValues.resolutionDividerScale3, importedConfigValues.resolutionDividerScale4, importedConfigValues.resolutionDividerScale5, importedConfigValues.resolutionDividerScale6, importedConfigValues.resolutionDividerScale7, importedConfigValues.resolutionDividerScale8,
                               importedConfigValues.goalAccelerationScale1, importedConfigValues.goalAccelerationScale2, importedConfigValues.goalAccelerationScale3, importedConfigValues.goalAccelerationScale4, importedConfigValues.goalAccelerationScale5, importedConfigValues.goalAccelerationScale6, importedConfigValues.goalAccelerationScale7, importedConfigValues.goalAccelerationScale8]
        
        window.invKinSolutionNumber.set(importedConfigValues.invKinSolutionNumber)
        
        index = 0
        for x in range(len(window.config1Scales)):
            for y in range(len(window.config1Scales[x])):
                window.config1Scales[x][y].set(importedConfig1List[index])
                index+=1
                
        index = 0
        for x in range(len(window.config2Scales)):
            for y in range(len(window.config2Scales[x])):
                window.config2Scales[x][y].set(importedConfig2List[index])
                index+=1
                
        index = 0
        for x in range(len(window.config3Scales)):
            for y in range(len(window.config3Scales[x])):
                window.config3Scales[x][y].set(importedConfig3List[index])
                index+=1
    
    
    except:
        print "Can't open file."
        
class Refresh(): #This is to stop the gui from flickering. All drop downs that freezes the gui will have to bind with this. See below for examples.
    '''
    This class is to stop the gui from flickering. All drop downs that freeze the gui will have to bind with this.
    '''
    def __init__(self, event, args):
        '''
        Updates the window to avoid flickering
        
        **Parameters**: \n
        * **event** - The widget action to which the method is binded. 
        * **args** - Main TKinter window 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        args[0].update()
                
class ExportConfigValues:
    def __init__(self):
        #Pop up window object and size
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("220x35+690+250")
        self.window = window
        
        #Pop up window
        fileNameLabel = Tkinter.Label(self.top, text = "File name:")
        fileNameLabel.grid(row = 0, column = 0)
        self.userInput = Tkinter.Entry(self.top)
        self.userInput.grid(row=0, column=1)
        self.userInput.focus_set()
        self.top.bind("<Return>", self.ok) #Allows me to push enter instead of push OK if desired
        okButton = Tkinter.Button(self.top, text = "OK", command = self.ok)
        okButton.grid(row = 0, column = 2)
        
        #Make file if not exist
        if not os.path.exists('_Saved_Values_/RAM_EEPROM_Config_Sliders'):
            os.mkdir('_Saved_Values_/RAM_EEPROM_Config_Sliders')
        
    def ok(self, *event):
        previous_state_logging_system.Log('_Saved_Values_/RAM_EEPROM_Config_Sliders/'+self.userInput.get()+'.txt').writeParameters(dropBoxFwdKinematicsSelectorVariable = "'"+window.dropBoxFwdKinematicsSelectorVariable.get()+"'", dropBoxInvKinematicsSelectorVariable = "'"+window.dropBoxInvKinematicsSelectorVariable.get()+"'",
                                                                                                                                   invKinSolutionNumber = "'"+window.invKinSolutionNumber.get()+"'",
                                                                                                                                   movingSpeed1 = window.config1Scales[0][0].get(), movingSpeed2 = window.config1Scales[0][1].get(), movingSpeed3 = window.config1Scales[0][2].get(), movingSpeed4 = window.config1Scales[0][3].get(), movingSpeed5 = window.config1Scales[0][4].get(), movingSpeed6 = window.config1Scales[0][5].get(), movingSpeed7 = window.config1Scales[0][6].get(), movingSpeed8 = window.config1Scales[0][7].get(),
                                                                                                                                   torqueLimit1 = window.config1Scales[1][0].get(), torqueLimit2 = window.config1Scales[1][1].get(), torqueLimit3 = window.config1Scales[1][2].get(), torqueLimit4 = window.config1Scales[1][3].get(), torqueLimit5 = window.config1Scales[1][4].get(), torqueLimit6 = window.config1Scales[1][5].get(), torqueLimit7 = window.config1Scales[1][6].get(), torqueLimit8 = window.config1Scales[1][7].get(),
                                                                                                                                   lowestVoltageLimit1 = window.config1Scales[2][0].get(), lowestVoltageLimit2 = window.config1Scales[2][1].get(), lowestVoltageLimit3 = window.config1Scales[2][2].get(), lowestVoltageLimit4 = window.config1Scales[2][3].get(), lowestVoltageLimit5 = window.config1Scales[2][4].get(), lowestVoltageLimit6 = window.config1Scales[2][5].get(), lowestVoltageLimit7 = window.config1Scales[2][6].get(), lowestVoltageLimit8 = window.config1Scales[2][7].get(),
                                                                                                                                   highestVoltageLimit1 = window.config1Scales[3][0].get(), highestVoltageLimit2 = window.config1Scales[3][1].get(), highestVoltageLimit3 = window.config1Scales[3][2].get(), highestVoltageLimit4 = window.config1Scales[3][3].get(), highestVoltageLimit5 = window.config1Scales[3][4].get(), highestVoltageLimit6 = window.config1Scales[3][5].get(), highestVoltageLimit7 = window.config1Scales[3][6].get(), highestVoltageLimit8 = window.config1Scales[3][7].get(),
                                                                                                                                   highestTemperatureLimit1 = window.config1Scales[4][0].get(), highestTemperatureLimit2 = window.config1Scales[4][1].get(), highestTemperatureLimit3 = window.config1Scales[4][2].get(), highestTemperatureLimit4 = window.config1Scales[4][3].get(), highestTemperatureLimit5 = window.config1Scales[4][4].get(), highestTemperatureLimit6 = window.config1Scales[4][5].get(), highestTemperatureLimit7 = window.config1Scales[4][6].get(), highestTemperatureLimit8 = window.config1Scales[4][7].get(),
                                                                                                                                   returnDelayTime1 = window.config1Scales[5][0].get(), returnDelayTime2 = window.config1Scales[5][1].get(), returnDelayTime3 = window.config1Scales[5][2].get(), returnDelayTime4 = window.config1Scales[5][3].get(), returnDelayTime5 = window.config1Scales[5][4].get(), returnDelayTime6 = window.config1Scales[5][5].get(), returnDelayTime7 = window.config1Scales[5][6].get(), returnDelayTime8 = window.config1Scales[5][7].get(),
                                                                                                                                   ledEnable1 = window.config1Scales[6][0].get(), ledEnable2 = window.config1Scales[6][1].get(), ledEnable3 = window.config1Scales[6][2].get(), ledEnable4 = window.config1Scales[6][3].get(), ledEnable5 = window.config1Scales[6][4].get(), ledEnable6 = window.config1Scales[6][5].get(), ledEnable7 = window.config1Scales[6][6].get(), ledEnable8 = window.config1Scales[6][7].get(),
                                                                                                                                   CWlimit1 = window.config2Scales[0][0].get(), CWlimit2 = window.config2Scales[0][1].get(), CWlimit3 = window.config2Scales[0][2].get(), CWlimit4 = window.config2Scales[0][3].get(), CWlimit5 = window.config2Scales[0][4].get(), CWlimit6 = window.config2Scales[0][5].get(), CWlimit7 = window.config2Scales[0][6].get(), CWlimit8 = window.config2Scales[0][7].get(),
                                                                                                                                   CCWlimit1 = window.config2Scales[1][0].get(), CCWlimit2 = window.config2Scales[1][1].get(), CCWlimit3 = window.config2Scales[1][2].get(), CCWlimit4 = window.config2Scales[1][3].get(), CCWlimit5 = window.config2Scales[1][4].get(), CCWlimit6 = window.config2Scales[1][5].get(), CCWlimit7 = window.config2Scales[1][6].get(), CCWlimit8 = window.config2Scales[1][7].get(),
                                                                                                                                   CWComplianceMarginScale1 = window.config2Scales[2][0].get(), CWComplianceMarginScale2 = window.config2Scales[2][1].get(), CWComplianceMarginScale3 = window.config2Scales[2][2].get(), CWComplianceMarginScale4 = window.config2Scales[2][3].get(), CWComplianceMarginScale5 = window.config2Scales[2][4].get(), CWComplianceMarginScale6 = window.config2Scales[2][5].get(), CWComplianceMarginScale7 = window.config2Scales[2][6].get(), CWComplianceMarginScale8 = window.config2Scales[2][7].get(),
                                                                                                                                   CCWComplianceMarginScale1 = window.config2Scales[3][0].get(), CCWComplianceMarginScale2 = window.config2Scales[3][1].get(), CCWComplianceMarginScale3 = window.config2Scales[3][2].get(), CCWComplianceMarginScale4 = window.config2Scales[3][3].get(), CCWComplianceMarginScale5 = window.config2Scales[3][4].get(), CCWComplianceMarginScale6 = window.config2Scales[3][5].get(), CCWComplianceMarginScale7 = window.config2Scales[3][6].get(), CCWComplianceMarginScale8 = window.config2Scales[3][7].get(),
                                                                                                                                   CWComplianceSlopeScale1 = window.config2Scales[4][0].get(), CWComplianceSlopeScale2 = window.config2Scales[4][1].get(), CWComplianceSlopeScale3 = window.config2Scales[4][2].get(), CWComplianceSlopeScale4 = window.config2Scales[4][3].get(), CWComplianceSlopeScale5 = window.config2Scales[4][4].get(), CWComplianceSlopeScale6 = window.config2Scales[4][5].get(), CWComplianceSlopeScale7 = window.config2Scales[4][6].get(), CWComplianceSlopeScale8 = window.config2Scales[4][7].get(),
                                                                                                                                   CCWComplianceSlopeScale1 = window.config2Scales[5][0].get(), CCWComplianceSlopeScale2 = window.config2Scales[5][1].get(), CCWComplianceSlopeScale3 = window.config2Scales[5][2].get(), CCWComplianceSlopeScale4 = window.config2Scales[5][3].get(), CCWComplianceSlopeScale5 = window.config2Scales[5][4].get(), CCWComplianceSlopeScale6 = window.config2Scales[5][5].get(), CCWComplianceSlopeScale7 = window.config2Scales[5][6].get(), CCWComplianceSlopeScale8 = window.config2Scales[5][7].get(),
                                                                                                                                   PScale1 = window.config2Scales[6][0].get(), PScale2 = window.config2Scales[6][1].get(), PScale3 = window.config2Scales[6][2].get(), PScale4 = window.config2Scales[6][3].get(), PScale5 = window.config2Scales[6][4].get(), PScale6 = window.config2Scales[6][5].get(), PScale7 = window.config2Scales[6][6].get(), PScale8 = window.config2Scales[6][7].get(),
                                                                                                                                   IScale1 = window.config2Scales[7][0].get(), IScale2 = window.config2Scales[7][1].get(), IScale3 = window.config2Scales[7][2].get(), IScale4 = window.config2Scales[7][3].get(), IScale5 = window.config2Scales[7][4].get(), IScale6 = window.config2Scales[7][5].get(), IScale7 = window.config2Scales[7][6].get(), IScale8 = window.config2Scales[7][7].get(),
                                                                                                                                   DScale1 = window.config2Scales[8][0].get(), DScale2 = window.config2Scales[8][1].get(), DScale3 = window.config2Scales[8][2].get(), DScale4 = window.config2Scales[8][3].get(), DScale5 = window.config2Scales[8][4].get(), DScale6 = window.config2Scales[8][5].get(), DScale7 = window.config2Scales[8][6].get(), DScale8 = window.config2Scales[8][7].get(),
                                                                                                                                   punchScale1 = window.config2Scales[9][0].get(), punchScale2 = window.config2Scales[9][1].get(), punchScale3 = window.config2Scales[9][2].get(), punchScale4 = window.config2Scales[9][3].get(), punchScale5 = window.config2Scales[9][4].get(), punchScale6 = window.config2Scales[9][5].get(), punchScale7 = window.config2Scales[9][6].get(), punchScale8 = window.config2Scales[9][7].get(),
                                                                                                                                   alarmLED1 = window.config3Scales[0][0].get(), alarmLED2 = window.config3Scales[0][1].get(), alarmLED3 = window.config3Scales[0][2].get(), alarmLED4 = window.config3Scales[0][3].get(), alarmLED5 = window.config3Scales[0][4].get(), alarmLED6 = window.config3Scales[0][5].get(), alarmLED7 = window.config3Scales[0][6].get(), alarmLED8 = window.config3Scales[0][7].get(),
                                                                                                                                   alarmShutdown1 = window.config3Scales[1][0].get(), alarmShutdown2 = window.config3Scales[1][1].get(), alarmShutdown3 = window.config3Scales[1][2].get(), alarmShutdown4 = window.config3Scales[1][3].get(), alarmShutdown5 = window.config3Scales[1][4].get(), alarmShutdown6 = window.config3Scales[1][5].get(), alarmShutdown7 = window.config3Scales[1][6].get(), alarmShutdown8 = window.config3Scales[1][7].get(),
                                                                                                                                   multiTurnOffsetScale1 = window.config3Scales[2][0].get(), multiTurnOffsetScale2 = window.config3Scales[2][1].get(), multiTurnOffsetScale3 = window.config3Scales[2][2].get(), multiTurnOffsetScale4 = window.config3Scales[2][3].get(), multiTurnOffsetScale5 = window.config3Scales[2][4].get(), multiTurnOffsetScale6 = window.config3Scales[2][5].get(), multiTurnOffsetScale7 = window.config3Scales[2][6].get(), multiTurnOffsetScale8 = window.config3Scales[2][7].get(),
                                                                                                                                   resolutionDividerScale1 = window.config3Scales[3][0].get(), resolutionDividerScale2 = window.config3Scales[3][1].get(), resolutionDividerScale3 = window.config3Scales[3][2].get(), resolutionDividerScale4 = window.config3Scales[3][3].get(), resolutionDividerScale5 = window.config3Scales[3][4].get(), resolutionDividerScale6 = window.config3Scales[3][5].get(), resolutionDividerScale7 = window.config3Scales[3][6].get(), resolutionDividerScale8 = window.config3Scales[3][7].get(),
                                                                                                                                   goalAccelerationScale1 = window.config3Scales[4][0].get(), goalAccelerationScale2 = window.config3Scales[4][1].get(), goalAccelerationScale3 = window.config3Scales[4][2].get(), goalAccelerationScale4 = window.config3Scales[4][3].get(), goalAccelerationScale5 = window.config3Scales[4][4].get(), goalAccelerationScale6 = window.config3Scales[4][5].get(), goalAccelerationScale7 = window.config3Scales[4][6].get(), goalAccelerationScale8 = window.config3Scales[4][7].get())
        
        #saveValuesToFile('RAM_EEPROM_Config_Sliders/'+self.userInput.get())

        self.top.destroy()   

class StdoutRedirector(object): #This is to take the stdout away from eclipse and give it to the GUI
    '''
    This class takes the stdout away from eclipse and gives it to the GUI
    '''
    def __init__(self,text_widget):
        '''
        Initilizes text widget.
        
        **Parameters**: \n
        * **text_widget** - Console on which output will be redirected to.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.text_space = text_widget

    def write(self,string):
        '''
        Writes output to GUI console.
        
        **Parameters**: \n
        * **event** - The widget action to which the method is binded. 
        * **args** - Main TKinter window 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.text_space.insert('end', string)
        self.text_space.see('end')        
 
previousSampleRate = 0   
class RecordJointAngles:
    def __init__(self):
        
        if window.recordButtonBool == False:
            #Pop up window object and size
            self.top = Tkinter.Toplevel(window)
            self.top.geometry("240x95+690+250")
            self.window = window
            
            #Pop up window
            fileNameLabel = Tkinter.Label(self.top, text = "File name:")
            fileNameLabel.grid(row = 0, column = 0, sticky = "E")
            self.userInput1 = Tkinter.Entry(self.top)
            self.userInput1.grid(row=0, column=1)
            self.userInput1.focus_set()
            
            SampleSpeedLabel = Tkinter.Label(self.top, text = "Sample Rate (Hz):")
            SampleSpeedLabel.grid(row = 1, column = 0)
            self.userInput2 = Tkinter.Entry(self.top)
            self.userInput2.grid(row=1, column=1)
            
            window.disableTorqueVar = Tkinter.IntVar()
            disableTorqueCheckbox = Tkinter.Checkbutton(self.top, text="Disable Torque", variable = window.disableTorqueVar)
            disableTorqueCheckbox.grid(row = 2, column = 0, columnspan = 2)
            
            self.top.bind("<Return>", self.ok) #Allows me to push enter instead of push OK if desired
            okButton = Tkinter.Button(self.top, text = "OK", command = self.ok)
            okButton.grid(row = 3, column = 0, columnspan = 2)
            
            #Make file if not exist
            if not os.path.exists('_Saved_Values_/Recordings'):
                os.mkdir('_Saved_Values_/Recordings')
                
        elif window.recordButtonBool == True:
            previous_state_logging_system.Log('_Saved_Values_/Recordings/'+window.recordedFileNameText+'.txt').writeParameters(recordedJointValues = window.recordedJointAnglesArray, sampleRate = window.sampleRate)
            window.recordedJointAnglesArray = [] #Resets the recordedJointAnglesArray list
            window.sampleRate = previousSampleRate #Back to normal sampling rate
            window.samplingRateText.set(previousSampleRate)
            window.recordButton.config(text="Record")
            window.playButton.config(state = "normal")
            window.trackObjectButton.config(state = "normal")
            window.recordButtonBool = False
            
            for x in range(8):
                window.servoModel.setTorqueEnable(x+1, 1)
            
            
        
    def ok(self, *event):
        global previousSampleRate

        window.recordedFileNameText = self.userInput1.get()
        
        previousSampleRate = float(window.samplingRateText.get())
        window.samplingRateText.set(self.userInput2.get())
        window.sampleRate = float(self.userInput2.get())
        
        
        if window.disableTorqueVar.get() == 1:
            for x in range(8):
                window.servoModel.setTorqueEnable(x+1, 0)

        window.recordButton.config(text="Stop Recording")
        window.playButton.config(state = "disabled")
        window.trackObjectButton.config(state = "disabled")
        window.recordButtonBool = True
        
        self.top.destroy()

