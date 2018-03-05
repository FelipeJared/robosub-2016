'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: _launch_gui_
   :synopsis: Launches the main program and initiates the Graphic User Interface (GUI).

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Sep 4, 2015
:Description: This module is responsible for almost all of the aesthetics/widgets that are seen on the GUI as well as updating the program when the widgets are controlled by user input.
'''

import Tkinter, ttk, sys, ctypes
import serial
import inspect, kinematics
from austins_roboarm_gui import callback_functions as CF
import image_processing, event_handlers, utilities, previous_state_logging_system
from austins_roboarm_gui import IP_movement_algorithms

window = Tkinter.Tk()
CF.setWindowObject(window)
setattr(window, "DEBUG", False)

#RETRIEVE SAVED VALUES FROM FILE LAST SERVO MODEL
GUIAndRAMStrings = ("minHue", "minSat", "minVal", "erodeDilate", "maxHue", "maxSat", "maxVal", "intensity",
                    "positionCheckBox", "speedCheckBox", "voltageCheckBox", "loadCheckBox", "temperatureCheckBox",
                    "dropBoxServoNumVariable", "dropBoxServoModelVariable",
                    "dropBoxFwdKinematicsSelectorVariable", "dropBoxInvKinematicsSelectorVariable",
                    "invKinSolutionNumber",
                    "movingSpeed1", "movingSpeed2", "movingSpeed3", "movingSpeed4", "movingSpeed5", "movingSpeed6", "movingSpeed7", "movingSpeed8", 
                    "torqueLimit1", "torqueLimit2", "torqueLimit3", "torqueLimit4", "torqueLimit5", "torqueLimit6", "torqueLimit7", "torqueLimit8",
                    "ledEnable1", "ledEnable2", "ledEnable3", "ledEnable4", "ledEnable5", "ledEnable6", "ledEnable7", "ledEnable8",
                    "CWComplianceMarginScale1", "CWComplianceMarginScale2", "CWComplianceMarginScale3", "CWComplianceMarginScale4", "CWComplianceMarginScale5", "CWComplianceMarginScale6", "CWComplianceMarginScale7", "CWComplianceMarginScale8",
                    "CCWComplianceMarginScale1", "CCWComplianceMarginScale2", "CCWComplianceMarginScale3", "CCWComplianceMarginScale4", "CCWComplianceMarginScale5", "CCWComplianceMarginScale6", "CCWComplianceMarginScale7", "CCWComplianceMarginScale8",
                    "CWComplianceSlopeScale1", "CWComplianceSlopeScale2", "CWComplianceSlopeScale3", "CWComplianceSlopeScale4", "CWComplianceSlopeScale5", "CWComplianceSlopeScale6", "CWComplianceSlopeScale7", "CWComplianceSlopeScale8",
                    "CCWComplianceSlopeScale1", "CCWComplianceSlopeScale2", "CCWComplianceSlopeScale3", "CCWComplianceSlopeScale4", "CCWComplianceSlopeScale5", "CCWComplianceSlopeScale6", "CCWComplianceSlopeScale7", "CCWComplianceSlopeScale8",
                    "PScale1", "PScale2", "PScale3", "PScale4", "PScale5", "PScale6", "PScale7", "PScale8",
                    "IScale1", "IScale2", "IScale3", "IScale4", "IScale5", "IScale6", "IScale7", "IScale8",
                    "DScale1", "DScale2", "DScale3", "DScale4", "DScale5", "DScale6", "DScale7", "DScale8",
                    "punchScale1", "punchScale2", "punchScale3", "punchScale4", "punchScale5", "punchScale6", "punchScale7", "punchScale8",
                    "goalAccelerationScale1", "goalAccelerationScale2", "goalAccelerationScale3", "goalAccelerationScale4", "goalAccelerationScale5", "goalAccelerationScale6", "goalAccelerationScale7", "goalAccelerationScale8",
                    "sampleRate")

#lastServoModel is so that values can be loaded into the sliders from the last servo model instead of just the last previous session
savedServoModel = previous_state_logging_system.Log('_Saved_Values_/Last_Servo_Model_Used.txt').getParameters("lastServoModel") #Last used servo model
savedValues = previous_state_logging_system.Log('_Saved_Values_/Saved_{}_GUI&RAM_Values.txt'.format(savedServoModel.lastServoModel)).getParameters(*GUIAndRAMStrings) #Gets config params based on last used servo model

#TIMERS
sampleTimer, recordPlaybackTimer = utilities.Timer(), utilities.Timer()

#SCREEN/IMAGE SIZING
screenRes = ctypes.windll.user32.GetSystemMetrics(0)-10, ctypes.windll.user32.GetSystemMetrics(1)-30
guiWidth, guiHeight, guiXPosition, guiYPosition = screenRes[0]-5, screenRes[1], 0, 0
imgWidth, imgHeight = int(screenRes[0]/3.0), int(screenRes[1]/2.4) #481, 310
setattr(window, "imgWidth", imgWidth); setattr(window, "imgHeight", imgHeight)
eventHandlers = event_handlers.EventHandlers(guiWidth, window.imgWidth)

#KINEMATICS VARIABLES
fKin, iKin = kinematics.ForwardKinematics(), kinematics.InverseKinematics()
userForwardKinFunction, userInverseKinFunction = None, None #Placeholder for the users kinematic functions
initializeForwardKinFlag, initializeInverseKinFlag = True, True

#SERIAL COMMUNICATION/INSTANTILIZING INITIAL LAST SERVO MODEL CLASS
if not window.DEBUG:
    usb2DynamixelSerial = serial.Serial("COM3", 1000000) #COM8 Austins computer
    CF.setComPort(usb2DynamixelSerial)
    
setattr(window, "servoModel", None)

#GLOBAL VARIABLES
IPMovementMode, maximumReachXYZ, previousDesiredJointAngles, previousDesiredEEPositions, previosDropBoxVariable, previosDropBoxFwdKinematicsSelectorVariable, previosDropBoxInvKinematicsSelectorVariable, previosDropBoxServoNumVariable, previosDropBoxServoModelVariable, previousInvKinSolution = None, [0, 0, 0], [0]*8, [0]*3, None, None, None, 8, None, 1

def updateGUIConfigSliders():
    global previousConfig1Scales, previousConfig2Scales, previousConfig3Scales, previosDropBoxServoModelVariable
            
    _displayHideConfigSliderRows()
                    
    #HIDES/SHOWS/CHANGES SLIDERS WHEN CHANGING SERVO MODEL OR SERVO NUMBER AND RECALLS PREVIOUS RAM VALUES FROM SPECIFIC SERVO MODELS
    if window.dropBoxServoModelVariable.get() != previosDropBoxServoModelVariable:#If the user changes the servo model, add/remove/change sliders accordingly.
        
        #This chunk of code may seem a little out of context, but it is for the updateServosWithConfigParams function. Because different model servos have different size config scales, I need to initialize the previousConfigScales accordingly.
        if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
            previousConfig1Scales, previousConfig2Scales, previousConfig3Scales = [[-1]*8]*7, [[-1]*8]*7, [[-1]*8]*2
        elif window.dropBoxServoModelVariable.get() == 'MX-28':
            previousConfig1Scales, previousConfig2Scales, previousConfig3Scales = [[-1]*8]*7, [[-1]*8]*10, [[-1]*8]*5
    
        #SAVES PREVIOUS SERVO MODEL RAM SLIDERS TO FILE SO THAT IT CAN BE RECALLED ONCE THE USER SELECTS THAT SERVO MODEL AGAIN
        CF.saveValuesToFile(previosDropBoxServoModelVariable) #Since servo model is going to be changed, this saves the RAM sliders current values for the previous servo model before the sliders get updated, modified, added, or removed
        
        #MODIFYING, DISPLAYING OR HIDING THE GUI SLIDERS ACCORDINGLY (NOTE: MODIFYING IN THIS CONTEXT ONLY MEANS INCREASING/DECREASING ITS RANGE, NOT UPDATING THE SLIDER WITH NEW VALUES. THATS WHAT THE _UPDATERAMSLIDERSFROMSERVOMODELFILE FUNCTION DOES)
        _modifyDisplayHideConfigSlidersColumns()
        
        #UPDATES THE RAM SLIDERS FROM THE APPROPRIATE SERVO MODEL FILE 
        _updateRAMSlidersFromServoModelFile()
        
    #HIDES/SHOWS SLIDERS WITH CONFIGURATION DROPBOX VARIABLE 
    _displayHideAllConfigSliders()
     
    #ACTIVATES/DISABLES POSITION SLIDERS AND INVERSE KINEMATIC SOLUTION NUMBERS AS WELL AS CREATES THE USERS KINEMATIC FUNCTIONS       
    _kinematicsSelector()
        
    previosDropBoxServoModelVariable = window.dropBoxServoModelVariable.get()
  
def _displayHideConfigSliderRows():
    '''
    This function displays or hides the config sliders accordingly depending on HOW MANY SERVOS are selected
    '''
    global previosDropBoxServoNumVariable
    
    #HIDES/SHOWS SLIDERS WHEN CHANGING SERVO NUMBER 
    if window.dropBoxServoNumVariable.get() != previosDropBoxServoNumVariable: #If the user changes the servo number, add/remove rows of sliders accordingly
    
        if window.connectedToggleBool == True:
            window.servoModel.presentPositionData = {}#{(x+1):5 for x in range(window.dropBoxServoNumVariable.get())} #This is to satisfy updateServosWithPosition condition in the updateServosWithPosition function. This refreshes the currentPosition variable
        
        if (window.dropBoxServoNumVariable.get()-previosDropBoxServoNumVariable) < 0: #removing sliders
            #HIDE ALL SLIDERS OVER THE dropBoxServoNumVariable NUMBER
            for x in range(8-window.dropBoxServoNumVariable.get()):
                window.jointScales[-(x+1)].grid_remove()
                window.jointLabels[x].grid_remove()
                    
            for x in range(len(window.config1ScaleObjects)):
                for y in range(8-window.dropBoxServoNumVariable.get()):
                    window.config1ScaleObjects[x][-(y+1)].grid_remove()
            
            for x in range(len(window.config2Scales)):
                for y in range(8-window.dropBoxServoNumVariable.get()):
                    window.config2Scales[x][-(y+1)].grid_remove()
                    
            for x in range(len(window.config3Scales)):
                for y in range(8-window.dropBoxServoNumVariable.get()):
                    window.config3Scales[x][-(y+1)].grid_remove()
        
        elif (window.dropBoxServoNumVariable.get()-previosDropBoxServoNumVariable) > 0: #adding sliders        
            #SHOW ALL SLIDERS EQUAL TO AND UNDER THE dropBoxServoNumVariable NUMBER
            for x in range(window.dropBoxServoNumVariable.get()):
                window.jointScales[x].grid()
                window.jointLabels[-(x+1)].grid()
                    
            for x in range(len(window.config1ScaleObjects)):
                for y in range(window.dropBoxServoNumVariable.get()):
                    window.config1ScaleObjects[x][y].grid()
            
            for x in range(len(window.config2Scales)):
                for y in range(window.dropBoxServoNumVariable.get()):
                    window.config2Scales[x][y].grid()
                    
            for x in range(len(window.config3Scales)):
                for y in range(window.dropBoxServoNumVariable.get()):
                    window.config3Scales[x][y].grid()
                    
    previosDropBoxServoNumVariable = window.dropBoxServoNumVariable.get()
    
def _modifyDisplayHideConfigSlidersColumns(): #Only used in the updateGUIConfigSliders function
    '''
    This function modifies, displays, or hides the config sliders accordingly depending on WHAT SERVO MODEL is selected.
    Note: modifying in this context only means increasing/decreasing its range, not updating the slider with new values. 
    That's what the _updateRAMSlidersFromServoModelFile function does.
    '''
    
    #Labels that change/remove/add with model or servo num changes
    CWComplianceMarginLabel, CCWComplianceMarginLabel, CWComplianceSlopeLabel, CCWComplianceSlopeLabel = window.config2Labels[2], window.config2Labels[3], window.config2Labels[4], window.config2Labels[5]
    PLabel, ILabel, DLabel = window.config2Labels[6], window.config2Labels[7], window.config2Labels[8]
    multiTurnOffsetLabel, resolutionDividerLabel, goalAccelerationLabel = window.config3Labels[2], window.config3Labels[3], window.config3Labels[4]
    
    #Sliders that change/remove/add with model or servo num changes
    movingSpeedScale, lowestVoltageLimitScale, highestVoltageLimitScale, highestTemperatureLimitScale = window.config1ScaleObjects[0], window.config1ScaleObjects[2], window.config1ScaleObjects[3], window.config1ScaleObjects[4]
    CWLimitScale, CCWLimitScale, CWComplianceMarginScale, CCWComplianceMarginScale, CWComplianceSlopeScale, CCWComplianceSlopeScale = window.config2Scales[0], window.config2Scales[1], window.config2Scales[2], window.config2Scales[3], window.config2Scales[4], window.config2Scales[5]
    PScale, IScale, DScale = window.config2Scales[6], window.config2Scales[7], window.config2Scales[8]
    multiTurnOffsetScale, resolutionDividerScale, goalAccelerationScale = window.config3Scales[2], window.config3Scales[3], window.config3Scales[4]
    
    if window.dropBoxServoModelVariable.get() == 'AX-12': #If model is AX-12, instantiate the proper class and modify, remove, or add sliders accordingly
        
        #Adding Labels
        CWComplianceMarginLabel.grid(); CCWComplianceMarginLabel.grid(); CWComplianceSlopeLabel.grid(); CCWComplianceSlopeLabel.grid()
        
        #Removing Labels
        PLabel.grid_remove(); ILabel.grid_remove(); DLabel.grid_remove()
        multiTurnOffsetLabel.grid_remove(); resolutionDividerLabel.grid_remove(); goalAccelerationLabel.grid_remove()
        
        for x in range(window.dropBoxServoNumVariable.get()): #Modify, remove, or add sliders accordingly
            
            #Modifying Sliders
            window.jointScales[x].config(to = 296.67)
            movingSpeedScale[x].config(to = 60); lowestVoltageLimitScale[x].config(from_ = 5, to = 14); highestVoltageLimitScale[x].config(from_ = 5, to = 14); highestTemperatureLimitScale[x].config(to = 70)
            CWLimitScale[x].config(to = 296.67); CCWLimitScale[x].config(to = 296.67)
            
            #Adding Sliders
            CWComplianceMarginScale[x].grid(); CCWComplianceMarginScale[x].grid(); CWComplianceSlopeScale[x].grid(); CCWComplianceSlopeScale[x].grid()
            
            #Removing Sliders
            PScale[x].grid_remove(); IScale[x].grid_remove(); DScale[x].grid_remove()
            multiTurnOffsetScale[x].grid_remove(); resolutionDividerScale[x].grid_remove(); goalAccelerationScale[x].grid_remove()
            
    elif window.dropBoxServoModelVariable.get() == 'AX-18': #If model is AX-18, instantiate the proper class and modify, remove, or add sliders accordingly
          
        #Adding Labels
        CWComplianceMarginLabel.grid(); CCWComplianceMarginLabel.grid(); CWComplianceSlopeLabel.grid(); CCWComplianceSlopeLabel.grid()
        
        #Removing Labels
        PLabel.grid_remove(); ILabel.grid_remove(); DLabel.grid_remove()
        multiTurnOffsetLabel.grid_remove(); resolutionDividerLabel.grid_remove(); goalAccelerationLabel.grid_remove()
            
        for x in range(window.dropBoxServoNumVariable.get()): #Modify, remove, or add sliders accordingly
            
            #Modifying Sliders
            window.jointScales[x].config(to = 296.67)
            movingSpeedScale[x].config(to = 97); lowestVoltageLimitScale[x].config(from_ = 5, to = 14); highestVoltageLimitScale[x].config(from_ = 5, to = 14); highestTemperatureLimitScale[x].config(to = 75)
            CWLimitScale[x].config(to = 296.67); CCWLimitScale[x].config(to = 296.67)
            
            #Adding Sliders
            CWComplianceMarginScale[x].grid(); CCWComplianceMarginScale[x].grid(); CWComplianceSlopeScale[x].grid(); CCWComplianceSlopeScale[x].grid()
            
            #Removing Sliders
            PScale[x].grid_remove(); IScale[x].grid_remove(); DScale[x].grid_remove(); 
            multiTurnOffsetScale[x].grid_remove(); resolutionDividerScale[x].grid_remove(); goalAccelerationScale[x].grid_remove()
            
    elif window.dropBoxServoModelVariable.get() == 'MX-28': #If model is MX-28, instantiate the proper class and modify, remove, or add sliders accordingly
          
        #Adding Labels
        PLabel.grid(); ILabel.grid(); DLabel.grid()
        multiTurnOffsetLabel.grid(); resolutionDividerLabel.grid(); goalAccelerationLabel.grid()
        
        #Removing Labels
        CWComplianceMarginLabel.grid_remove(); CCWComplianceMarginLabel.grid_remove(); CWComplianceSlopeLabel.grid_remove(); CCWComplianceSlopeLabel.grid_remove()
            
        for x in range(window.dropBoxServoNumVariable.get()): #Modify, remove, or add sliders accordingly
            
            #Modifying Sliders
            window.jointScales[x].config(to = 360.36)
            movingSpeedScale[x].config(to = 67); lowestVoltageLimitScale[x].config(from_ = 6, to = 16); highestVoltageLimitScale[x].config(from_ = 6, to = 16); highestTemperatureLimitScale[x].config(to = 80)
            CWLimitScale[x].config(to = 360.36); CCWLimitScale[x].config(to = 360.36)
            
            #Adding Sliders
            PScale[x].grid(); IScale[x].grid(); DScale[x].grid()
            multiTurnOffsetScale[x].grid(); resolutionDividerScale[x].grid(); goalAccelerationScale[x].grid()
            
            #Removing Sliders
            CWComplianceMarginScale[x].grid_remove(); CCWComplianceMarginScale[x].grid_remove(); CWComplianceSlopeScale[x].grid_remove(); CCWComplianceSlopeScale[x].grid_remove()
            
def _updateRAMSlidersFromServoModelFile(): #Only used in the updateGUIConfigSliders function
    '''
    This function updates the RAM sliders from the appropriate servo model file 
    '''
    
    #Gets the saved values from the specific servo models file so that when the user changes the servo model, the sliders will update to the last values the sliders were at for that model
    savedValues = previous_state_logging_system.Log('_Saved_Values_/Saved_{}_GUI&RAM_Values.txt'.format(window.dropBoxServoModelVariable.get())).getParameters(*GUIAndRAMStrings)
    
    #UPDATE RAM SLIDERS
    #Config 3
    savedGoalAccelerationScaleVals = [savedValues.goalAccelerationScale1, savedValues.goalAccelerationScale2, savedValues.goalAccelerationScale3, savedValues.goalAccelerationScale4, savedValues.goalAccelerationScale5, savedValues.goalAccelerationScale6, savedValues.goalAccelerationScale7, savedValues.goalAccelerationScale8]
    
    #Config 2
    savedCWComplianceMarginScaleVals = [savedValues.CWComplianceMarginScale1, savedValues.CWComplianceMarginScale2, savedValues.CWComplianceMarginScale3, savedValues.CWComplianceMarginScale4, savedValues.CWComplianceMarginScale5, savedValues.CWComplianceMarginScale6, savedValues.CWComplianceMarginScale7, savedValues.CWComplianceMarginScale8]
    savedCCWComplianceMarginScaleVals = [savedValues.CCWComplianceMarginScale1, savedValues.CCWComplianceMarginScale2, savedValues.CCWComplianceMarginScale3, savedValues.CCWComplianceMarginScale4, savedValues.CCWComplianceMarginScale5, savedValues.CCWComplianceMarginScale6, savedValues.CCWComplianceMarginScale7, savedValues.CCWComplianceMarginScale8]
    savedCWComplianceSlopeScaleVals = [savedValues.CWComplianceSlopeScale1, savedValues.CWComplianceSlopeScale2, savedValues.CWComplianceSlopeScale3, savedValues.CWComplianceSlopeScale4, savedValues.CWComplianceSlopeScale5, savedValues.CWComplianceSlopeScale6, savedValues.CWComplianceSlopeScale7, savedValues.CWComplianceSlopeScale8]
    savedCCWComplianceSlopeScaleVals = [savedValues.CCWComplianceSlopeScale1, savedValues.CCWComplianceSlopeScale2, savedValues.CCWComplianceSlopeScale3, savedValues.CCWComplianceSlopeScale4, savedValues.CCWComplianceSlopeScale5, savedValues.CCWComplianceSlopeScale6, savedValues.CCWComplianceSlopeScale7, savedValues.CCWComplianceSlopeScale8]
    savedPScaleVals = [savedValues.PScale1, savedValues.PScale2, savedValues.PScale3, savedValues.PScale4, savedValues.PScale5, savedValues.PScale6, savedValues.PScale7, savedValues.PScale8]
    savedIScaleVals = [savedValues.IScale1, savedValues.IScale2, savedValues.IScale3, savedValues.IScale4, savedValues.IScale5, savedValues.IScale6, savedValues.IScale7, savedValues.IScale8]
    savedDScaleVals = [savedValues.DScale1, savedValues.DScale2, savedValues.DScale3, savedValues.DScale4, savedValues.DScale5, savedValues.DScale6, savedValues.DScale7, savedValues.DScale8]
    savedPunchScaleVals = [savedValues.punchScale1, savedValues.punchScale2, savedValues.punchScale3, savedValues.punchScale4, savedValues.punchScale5, savedValues.punchScale6, savedValues.punchScale7, savedValues.punchScale8]
    
    #Config 1
    savedMovingSpeedVals = [savedValues.movingSpeed1, savedValues.movingSpeed2, savedValues.movingSpeed3, savedValues.movingSpeed4, savedValues.movingSpeed5, savedValues.movingSpeed6, savedValues.movingSpeed7, savedValues.movingSpeed8]
    savedTorqueLimitVals = [savedValues.torqueLimit1, savedValues.torqueLimit2, savedValues.torqueLimit3, savedValues.torqueLimit4, savedValues.torqueLimit5, savedValues.torqueLimit6, savedValues.torqueLimit7, savedValues.torqueLimit8]
    savedLedEnableCheckboxVals = [savedValues.ledEnable1, savedValues.ledEnable2, savedValues.ledEnable3, savedValues.ledEnable4, savedValues.ledEnable5, savedValues.ledEnable6, savedValues.ledEnable7, savedValues.ledEnable8]

    #Scales
    #Config 3
    goalAccelerationScale = window.config3Scales[4]
    
    #Config 2
    CWComplianceMarginScale, CCWComplianceMarginScale, CWComplianceSlopeScale, CCWComplianceSlopeScale, PScale, IScale, DScale, punchScale = window.config2Scales[2], window.config2Scales[3], window.config2Scales[4], window.config2Scales[5], window.config2Scales[6], window.config2Scales[7], window.config2Scales[8], window.config2Scales[9]
    
    #Config 1
    movingSpeedScale, torqueLimitScale, ledEnableCheckbox = window.config1ScaleObjects[0], window.config1ScaleObjects[1], window.config1ScaleObjects[6]
    
    for x in range(8):
        #Config 3
        goalAccelerationScale[x].set(savedGoalAccelerationScaleVals[x])
        
        #Config 2
        CWComplianceMarginScale[x].set(savedCWComplianceMarginScaleVals[x])
        CCWComplianceMarginScale[x].set(savedCCWComplianceMarginScaleVals[x])
        CWComplianceSlopeScale[x].set(savedCWComplianceSlopeScaleVals[x])
        CCWComplianceSlopeScale[x].set(savedCCWComplianceSlopeScaleVals[x])
        PScale[x].set(savedPScaleVals[x])
        IScale[x].set(savedIScaleVals[x])
        DScale[x].set(savedDScaleVals[x])
        punchScale[x].set(savedPunchScaleVals[x])
        
        #Config 1
        movingSpeedScale[x].set(savedMovingSpeedVals[x])
        torqueLimitScale[x].set(savedTorqueLimitVals[x])
        if savedLedEnableCheckboxVals[x] == 1:
            ledEnableCheckbox[x].select()
        else:
            ledEnableCheckbox[x].deselect()
            
    #UPDATE MISC DROP DOWNS/SLIDERS
    window.invKinSolutionNumber.set(savedValues.invKinSolutionNumber)
    window.dropBoxFwdKinematicsSelectorVariable.set(savedValues.dropBoxFwdKinematicsSelectorVariable)
    window.dropBoxInvKinematicsSelectorVariable.set(savedValues.dropBoxInvKinematicsSelectorVariable)
    
def _displayHideAllConfigSliders(): #Only used in the updateGUIConfigSliders function
    global previosDropBoxVariable
    
    #HIDES/SHOWS SLIDERS WITH CONFIGURATION DROPBOX VARIABLE 
    if window.dropBoxVariable.get() != previosDropBoxVariable:
        if window.dropBoxVariable.get() == "Configuration 1":
            window.config3Frame.grid_remove()
            window.config2Frame.grid_remove()
            window.config1Frame.grid()

        elif window.dropBoxVariable.get() == "Configuration 2":
            window.config3Frame.grid_remove()
            window.config2Frame.grid()
            window.config1Frame.grid_remove()
            
        elif window.dropBoxVariable.get() == "Configuration 3":
            window.config3Frame.grid()
            window.config2Frame.grid_remove()
            window.config1Frame.grid_remove()
            
    previosDropBoxVariable = window.dropBoxVariable.get()
    
def _kinematicsSelector(): #Only used in the updateGUIConfigSliders function
    global IPMovementMode, userForwardKinFunction, userInverseKinFunction, initializeForwardKinFlag, initializeInverseKinFlag, previosDropBoxFwdKinematicsSelectorVariable, previosDropBoxInvKinematicsSelectorVariable
    
    #ACTIVATES/DISABLES POSITION SLIDERS AND INVERSE KINEMATIC SOLUTION NUMBERS AS WELL AS CREATES THE USERS KINEMATIC FUNCTIONS
    if window.dropBoxFwdKinematicsSelectorVariable.get() != previosDropBoxFwdKinematicsSelectorVariable: #If the user changes the INV Kinematics, activate/disable position sliders and solution number dropbox
        if window.dropBoxFwdKinematicsSelectorVariable.get() != "FWD Kinematics":
            #Modify position sliders accordingly
            window.positionScales[0].config(fg="#000000"); window.positionScales[1].config(fg="#000000"); window.positionScales[2].config(fg="#000000")
            
            #Initializes flag so that X, Y, Z position sliders can update in updateServosWithPosition function when kinematic selector drop down changes
            initializeForwardKinFlag = True
            
            #Finding the appropriate forward kinematic function according to the name that is in the kinematic selector drop down
            fwdKinfunctionNames, fwdKinFunctionObjects = window.fwdKinematicFunctions
            for index, functionName in enumerate(fwdKinfunctionNames):
                if functionName == window.dropBoxFwdKinematicsSelectorVariable.get():
                    userForwardKinFunction = fwdKinFunctionObjects[index]
              
            #Putting in random theta data to obtain the maximum reach so the position sliders can be adjusted accordingly. Don't care about returned X, Y, Z  
            fwdKinReturnedData = userForwardKinFunction(*[0]*8)
                  
            #Extracts maximumReachXYZ and sets the position sliders accordingly
            maximumReachXYZ = fwdKinReturnedData[3]
            window.positionScales[0].config(from_=-maximumReachXYZ[0], to=maximumReachXYZ[0]); window.positionScales[1].config(from_=-maximumReachXYZ[1], to=maximumReachXYZ[1]); window.positionScales[2].config(from_=-maximumReachXYZ[2], to=maximumReachXYZ[2])
            
        elif window.dropBoxFwdKinematicsSelectorVariable.get() == "FWD Kinematics":
            #Modify position sliders accordingly
            window.positionScales[0].config(fg="#555555"); window.positionScales[1].config(fg="#555555"); window.positionScales[2].config(fg="#555555")
            
    if window.dropBoxInvKinematicsSelectorVariable.get() != previosDropBoxInvKinematicsSelectorVariable: #If the user changes the INV Kinematics, activate/disable position sliders and solution number dropbox
        
        if window.dropBoxInvKinematicsSelectorVariable.get() != "INV Kinematics": #If the drop down doesn't read "INV Kinematics" (Meaning user must have selected the kinematics)
            #Modify position sliders accordingly
            window.positionLabels[0].config(state="active"); window.positionLabels[1].config(state="active"); window.positionLabels[2].config(state="active")
            window.positionScales[0].config(state="active"); window.positionScales[1].config(state="active"); window.positionScales[2].config(state="active")
            window.dropBoxInvKinematicSolutionMenu.config(state="active")
            
            #Initializes flag so that theta sliders can update in updateServosWithPosition function when kinematic selector drop down changes
            initializeInverseKinFlag = True
            
            #Finding the appropriate inverse kinematic function according to the name that is in the kinematic selector drop down
            invKinFunctionNames, invKinFunctionObjects = window.invKinematicFunctions
            for index, functionName in enumerate(invKinFunctionNames):
                if functionName == window.dropBoxInvKinematicsSelectorVariable.get():
                    userInverseKinFunction = invKinFunctionObjects[index]
                    #Putting in random X, Y, Z data to obtain the maximum reach so the position sliders can be adjusted accordingly. Don't care about returned thetas
                    invKinReturnedData = userInverseKinFunction(0, 0, 0)
                  
            #IP_MOVEMENT_ALGORITHMS MODULE  
            #Checking to see if the drop down inverse kinematics are the inverse kinematics thats set up for image processing in the IP_movement_algorithms module. This code would need to be extended for inverse kinematics that user makes image processing capable.
            if window.dropBoxInvKinematicsSelectorVariable.get() == "get4DOFCamRef":
                IPMovementMode = IP_movement_algorithms.IP4DOFCamRefModes(window, invKinReturnedData[2], invKinReturnedData[3])
                window.trackObjectButton.config(state="active")
                
            elif window.dropBoxInvKinematicsSelectorVariable.get() != "get4DOFCamRef":
                window.trackObjectButton.config(state="disabled")
            
            #Extracts maximumReachXYZ and sets the position sliders accordingly
            maximumReachXYZ = invKinReturnedData[1]
            window.positionScales[0].config(from_=-maximumReachXYZ[0], to=maximumReachXYZ[0]); window.positionScales[1].config(from_=-maximumReachXYZ[1], to=maximumReachXYZ[1]); window.positionScales[2].config(from_=-maximumReachXYZ[2], to=maximumReachXYZ[2])
            
            #Extracts thetas
            thetas = invKinReturnedData[0]
            
            #Update solution number drop down with correct amount of solutions
            amountOfSolutions = max(len(theta) for theta in thetas if isinstance(theta, list)) #Finds the largest array in invKinReturnedData[0]
            window.dropBoxInvKinematicSolutionMenu["menu"].delete(0, "end")
            for solutionName in (["Solution {}".format(x+1) for x in range(amountOfSolutions)]):
                window.dropBoxInvKinematicSolutionMenu["menu"].add_command(label=solutionName, command=lambda v=solutionName: window.invKinSolutionNumber.set(v))
                
        elif window.dropBoxInvKinematicsSelectorVariable.get() == "INV Kinematics": #If the drop down does read "INV Kinematics" (Meaning user must not have selected any kinematics)
            #Modify position sliders accordingly
            window.positionLabels[0].config(state="disable"); window.positionLabels[1].config(state="disable"); window.positionLabels[2].config(state="disable")
            window.positionScales[0].config(state="disable"); window.positionScales[1].config(state="disable"); window.positionScales[2].config(state="disable")
            window.dropBoxInvKinematicSolutionMenu.config(state="disable")
            
            #IP_MOVEMENT_ALGORITHMS MODULE  
            #Since no inverse kineamtics are selected, then there is no way that any movement can occur for image processing
            window.trackObjectButton.config(state="disabled")
    
    previosDropBoxFwdKinematicsSelectorVariable = window.dropBoxFwdKinematicsSelectorVariable.get()
    previosDropBoxInvKinematicsSelectorVariable = window.dropBoxInvKinematicsSelectorVariable.get()
    
def sampleData():
    for servoID in range(1, window.dropBoxServoNumVariable.get()+1):
        window.servoModel.getPresentPosition(servoID)
        if window.printCheckBoxValArray[1].get() == True:
            window.servoModel.getPresentSpeed(servoID)
        if window.printCheckBoxValArray[2].get() == True:
            window.servoModel.getPresentVoltage(servoID)
        if window.printCheckBoxValArray[3].get() == True:
            window.servoModel.getPresentLoad(servoID)
        if window.printCheckBoxValArray[4].get() == True:
            window.servoModel.getPresentTemperature(servoID)

def printToConsole():
    window.consolText.delete(1.0, 'end')
    
    if window.playButtonBool == True:
        print "Playback Rate: {} Hz".format(window.playbackLogValues.sampleRate)
    if window.printCheckBoxValArray[0].get() == True:
        print "Current Position:", window.servoModel.presentPositionData
    if window.printCheckBoxValArray[1].get() == True:
        print "Current Speed:", window.servoModel.presentSpeedData
    if window.printCheckBoxValArray[2].get() == True:
        print "Current Voltage:", window.servoModel.presentVoltageData
    if window.printCheckBoxValArray[3].get() == True:
        print "Current Load:", window.servoModel.presentLoadData
    if window.printCheckBoxValArray[4].get() == True:
        print "Current Temperature:", window.servoModel.presentTemperatureData 
        
def recordPlayback():
    if window.recordButtonBool == True:
        netRecordPlaybackTimer = recordPlaybackTimer.netTimer(recordPlaybackTimer.cpuClockTimeInSeconds()) 
        if netRecordPlaybackTimer >= 1/window.sampleRate:
            if window.disableTorqueVar.get() == 1: #If torque is disabled user must want not want to use joint sliders for recording purposes, therefore, keep updating the sliders when the user is not trying to move them.
                for servoID in range(1, window.dropBoxServoNumVariable.get()+1):
                    window.jointScales[servoID-1].set(window.servoModel.presentPositionData[servoID])
            window.recordedJointAnglesArray.append([window.servoModel.presentPositionData[x+1] for x in range(window.dropBoxServoNumVariable.get())])
            recordPlaybackTimer.restartTimer()
                
    if window.playButtonBool == True:
        netRecordPlaybackTimer = recordPlaybackTimer.netTimer(recordPlaybackTimer.cpuClockTimeInSeconds()) 
        if netRecordPlaybackTimer >= 1/window.playbackLogValues.sampleRate:
            if len(window.playbackLogValues.recordedJointValues) > 0:
                jointAngles = window.playbackLogValues.recordedJointValues.pop(0)
                for servoID in range(1, window.dropBoxServoNumVariable.get()+1):
                    window.jointScales[servoID-1].set(jointAngles[servoID-1])
                    #window.servoModel.setGoalPosition(servoID, jointAngles[servoID-1])

            else:
                #Removing widgets
                window.playBackModifier[0].place_forget(); window.playBackModifier[1].place_forget(); window.playBackModifier[2].place_forget()
                window.playButtonBool = False
                window.playButton.config(text = "Play")
                window.recordButton.config(state = "normal")
                window.trackObjectButton.config(state = "normal")
            recordPlaybackTimer.restartTimer()
            
def updateServosWithPosition():
    '''
    Updates servos.
    '''
    
    global maximumReachXYZ, userForwardKinFunction, userInverseKinFunction, initializeForwardKinFlag, initializeInverseKinFlag, previousDesiredJointAngles, previousDesiredEEPositions, previousInvKinSolution
    
    newDesiredEEPosition = [window.positionScales[0].get(), window.positionScales[1].get(), window.positionScales[2].get()]
    newDesiredJointAngles = [window.jointScales[x].get() for x in range(window.dropBoxServoNumVariable.get())]
    
    #MOVING POSITION SLIDERS
    invKinSolution = int(filter(str.isdigit, window.invKinSolutionNumber.get())) #Extracting number from string
    if newDesiredEEPosition != previousDesiredEEPositions or invKinSolution != previousInvKinSolution or initializeInverseKinFlag == True: #Checks for unique values or if the sliders need to be initially set
        #Calls user function and sets sliders accordingly if the user selects inverse kinematics from the kinematic selector dropdown
        if window.dropBoxInvKinematicsSelectorVariable.get() != "INV Kinematics": 
            invKinReturnedData = userInverseKinFunction(newDesiredEEPosition[0], newDesiredEEPosition[1], newDesiredEEPosition[2])
            thetas = invKinReturnedData[0]
            
            #Loops through thetas and repackages the thetas variable with the solution that is selected in the GUI
            for x in range(len(thetas)):
                if isinstance(thetas[x], list):
                    thetas[x] = round((thetas[x][invKinSolution-1])%360, 2)
                else:
                    thetas[x] = round((thetas[x])%360, 2)
            
            #Checks if the joint angle passes the maximum joint angle limit of the servo model
            if window.dropBoxServoModelVariable.get() == "AX-12" or window.dropBoxServoModelVariable.get() == "AX-18":
                for index, theta in enumerate(thetas):
                    if theta > 296.67:
                        thetas[index] = 296.67         
            elif window.dropBoxServoModelVariable.get() == "MX-28":
                for index, theta in enumerate(thetas):
                    if theta > 360.36:
                        thetas[index] = 360.36
            
            #Sends the desired theta values to ther servos
            if window.connectedToggleBool == True:
                for index, theta in enumerate(thetas):
                    window.servoModel.setGoalPosition(index+1, theta)
            
            #Updates the joint sliders accordingly 
            for index, theta in enumerate(thetas):
                window.jointScales[index].set(theta)
            
            #Updating previousDesiredEEPositions and previousDesiredJointAngles otherwise it will constantly re-send the same joint angle values to the servos
            previousDesiredEEPositions = newDesiredEEPosition
            previousDesiredJointAngles[0:len(thetas)] = thetas
        initializeInverseKinFlag = False
    
    #MOVING JOINT ANGLE SLIDERS
    elif newDesiredJointAngles != previousDesiredJointAngles or initializeForwardKinFlag == True: #Checks for unique values
        #Sends the desired joint angles to the servos if the connect button is activated
        if window.connectedToggleBool == True and not window.DEBUG:
            for x in range(len(window.servoModel.presentPositionData)):
                if newDesiredJointAngles[x] != window.servoModel.presentPositionData[x+1]: #Setting individual sliders.
                    if window.recordButtonBool == False or window.disableTorqueVar.get() == 0: #if not recording, or if torque is not disabled by recording options, then send goal joint position. When a goal joint position is sent to the servo, it turns back on torque; without this, some servos kept freezing up because the joint sliders got moved
                        window.servoModel.setGoalPosition(x+1, newDesiredJointAngles[x])
        
        #Calls user function and sets sliders accordingly if the user selects forward kinematics from the kinematic selector dropdown
        if window.dropBoxFwdKinematicsSelectorVariable.get() != "FWD Kinematics":
            fwdKinReturnedData = userForwardKinFunction(*newDesiredJointAngles)
            X, Y, Z, maximumReachXYZ = fwdKinReturnedData[0:4]
            
            window.positionScales[0].config(state="active"); window.positionScales[1].config(state="active"); window.positionScales[2].config(state="active")
            window.positionScales[0].set(X); window.positionScales[1].set(Y); window.positionScales[2].set(Z)
            if window.dropBoxInvKinematicsSelectorVariable.get() == "INV Kinematics": #This is to check if the position sliders need to go back to being disabled
                window.positionScales[0].config(state="disable"); window.positionScales[1].config(state="disable"); window.positionScales[2].config(state="disable")
            previousDesiredEEPositions = [round(X, 2), round(Y, 2), round(Z, 2)] #Updating previousDesiredEEPositions otherwise it will constantly re-send the same joint angle values to the servos

        previousDesiredJointAngles = newDesiredJointAngles #Updating previousDesiredJointAngles otherwise it will constantly re-send the same joint angle values to the servos
        initializeForwardKinFlag = False
    previousInvKinSolution = invKinSolution
        
def updateServosWithConfigParams():
    '''
    Updates servos
    '''
    global previousConfig1Scales, previousConfig2Scales, previousConfig3Scales
    
    
    #These function lists make it easier
    if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
        config1FunctionList = [window.servoModel.setMovingSpeed, window.servoModel.setTorqueLimit, window.servoModel.setLowestLimitVoltage, window.servoModel.setHighestLimitVoltage, window.servoModel.setHighestLimitTemperature, window.servoModel.setReturnDelayTime, window.servoModel.setLED]
        config2FunctionList = [window.servoModel.setCWAngleLimit, window.servoModel.setCCWAngleLimit, window.servoModel.setCWComplianceMargin, window.servoModel.setCCWComplianceMargin, window.servoModel.setCWComplianceSlope, window.servoModel.setCCWComplianceSlope, window.servoModel.setPunch]
        config3FunctionList = [window.servoModel.setAlarmLED, window.servoModel.setAlarmShutdown]
        
        config1Scales = [[window.config1Scales[0][0].get(), window.config1Scales[0][1].get(), window.config1Scales[0][2].get(), window.config1Scales[0][3].get(), window.config1Scales[0][4].get(), window.config1Scales[0][5].get(), window.config1Scales[0][6].get(), window.config1Scales[0][7].get()],
                         [window.config1Scales[1][0].get(), window.config1Scales[1][1].get(), window.config1Scales[1][2].get(), window.config1Scales[1][3].get(), window.config1Scales[1][4].get(), window.config1Scales[1][5].get(), window.config1Scales[1][6].get(), window.config1Scales[1][7].get()],
                         [window.config1Scales[2][0].get(), window.config1Scales[2][1].get(), window.config1Scales[2][2].get(), window.config1Scales[2][3].get(), window.config1Scales[2][4].get(), window.config1Scales[2][5].get(), window.config1Scales[2][6].get(), window.config1Scales[2][7].get()],
                         [window.config1Scales[3][0].get(), window.config1Scales[3][1].get(), window.config1Scales[3][2].get(), window.config1Scales[3][3].get(), window.config1Scales[3][4].get(), window.config1Scales[3][5].get(), window.config1Scales[3][6].get(), window.config1Scales[3][7].get()],
                         [window.config1Scales[4][0].get(), window.config1Scales[4][1].get(), window.config1Scales[4][2].get(), window.config1Scales[4][3].get(), window.config1Scales[4][4].get(), window.config1Scales[4][5].get(), window.config1Scales[4][6].get(), window.config1Scales[4][7].get()],
                         [window.config1Scales[5][0].get(), window.config1Scales[5][1].get(), window.config1Scales[5][2].get(), window.config1Scales[5][3].get(), window.config1Scales[5][4].get(), window.config1Scales[5][5].get(), window.config1Scales[5][6].get(), window.config1Scales[5][7].get()],
                         [window.config1Scales[6][0].get(), window.config1Scales[6][1].get(), window.config1Scales[6][2].get(), window.config1Scales[6][3].get(), window.config1Scales[6][4].get(), window.config1Scales[6][5].get(), window.config1Scales[6][6].get(), window.config1Scales[6][7].get()]]

        config2Scales = [[window.config2Scales[0][0].get(), window.config2Scales[0][1].get(), window.config2Scales[0][2].get(), window.config2Scales[0][3].get(), window.config2Scales[0][4].get(), window.config2Scales[0][5].get(), window.config2Scales[0][6].get(), window.config2Scales[0][7].get()],
                         [window.config2Scales[1][0].get(), window.config2Scales[1][1].get(), window.config2Scales[1][2].get(), window.config2Scales[1][3].get(), window.config2Scales[1][4].get(), window.config2Scales[1][5].get(), window.config2Scales[1][6].get(), window.config2Scales[1][7].get()],
                         [window.config2Scales[2][0].get(), window.config2Scales[2][1].get(), window.config2Scales[2][2].get(), window.config2Scales[2][3].get(), window.config2Scales[2][4].get(), window.config2Scales[2][5].get(), window.config2Scales[2][6].get(), window.config2Scales[2][7].get()],
                         [window.config2Scales[3][0].get(), window.config2Scales[3][1].get(), window.config2Scales[3][2].get(), window.config2Scales[3][3].get(), window.config2Scales[3][4].get(), window.config2Scales[3][5].get(), window.config2Scales[3][6].get(), window.config2Scales[3][7].get()],
                         [window.config2Scales[4][0].get(), window.config2Scales[4][1].get(), window.config2Scales[4][2].get(), window.config2Scales[4][3].get(), window.config2Scales[4][4].get(), window.config2Scales[4][5].get(), window.config2Scales[4][6].get(), window.config2Scales[4][7].get()],
                         [window.config2Scales[5][0].get(), window.config2Scales[5][1].get(), window.config2Scales[5][2].get(), window.config2Scales[5][3].get(), window.config2Scales[5][4].get(), window.config2Scales[5][5].get(), window.config2Scales[5][6].get(), window.config2Scales[5][7].get()],
                         [window.config2Scales[6][0].get(), window.config2Scales[6][1].get(), window.config2Scales[6][2].get(), window.config2Scales[6][3].get(), window.config2Scales[6][4].get(), window.config2Scales[6][5].get(), window.config2Scales[6][6].get(), window.config2Scales[6][7].get()]]

        config3Scales = [[window.config3Scales[0][0].get(), window.config3Scales[0][1].get(), window.config3Scales[0][2].get(), window.config3Scales[0][3].get(), window.config3Scales[0][4].get(), window.config3Scales[0][5].get(), window.config3Scales[0][6].get(), window.config3Scales[0][7].get()],
                         [window.config3Scales[1][0].get(), window.config3Scales[1][1].get(), window.config3Scales[1][2].get(), window.config3Scales[1][3].get(), window.config3Scales[1][4].get(), window.config3Scales[1][5].get(), window.config3Scales[1][6].get(), window.config3Scales[1][7].get()]]


    elif window.dropBoxServoModelVariable.get() == 'MX-28':
        config1FunctionList = [window.servoModel.setMovingSpeed, window.servoModel.setTorqueLimit, window.servoModel.setLowestLimitVoltage, window.servoModel.setHighestLimitVoltage, window.servoModel.setHighestLimitTemperature, window.servoModel.setReturnDelayTime, window.servoModel.setLED]
        config2FunctionList = [window.servoModel.setCWAngleLimit, window.servoModel.setCCWAngleLimit, window.servoModel.setP, window.servoModel.setI, window.servoModel.setD, window.servoModel.setPunch]
        config3FunctionList = [window.servoModel.setAlarmLED, window.servoModel.setAlarmShutdown, window.servoModel.setMultiTurnOffset, window.servoModel.setResolutionDivider, window.servoModel.setGoalAcceleration]
        
        config1Scales = [[window.config1Scales[0][0].get(), window.config1Scales[0][1].get(), window.config1Scales[0][2].get(), window.config1Scales[0][3].get(), window.config1Scales[0][4].get(), window.config1Scales[0][5].get(), window.config1Scales[0][6].get(), window.config1Scales[0][7].get()],
                         [window.config1Scales[1][0].get(), window.config1Scales[1][1].get(), window.config1Scales[1][2].get(), window.config1Scales[1][3].get(), window.config1Scales[1][4].get(), window.config1Scales[1][5].get(), window.config1Scales[1][6].get(), window.config1Scales[1][7].get()],
                         [window.config1Scales[2][0].get(), window.config1Scales[2][1].get(), window.config1Scales[2][2].get(), window.config1Scales[2][3].get(), window.config1Scales[2][4].get(), window.config1Scales[2][5].get(), window.config1Scales[2][6].get(), window.config1Scales[2][7].get()],
                         [window.config1Scales[3][0].get(), window.config1Scales[3][1].get(), window.config1Scales[3][2].get(), window.config1Scales[3][3].get(), window.config1Scales[3][4].get(), window.config1Scales[3][5].get(), window.config1Scales[3][6].get(), window.config1Scales[3][7].get()],
                         [window.config1Scales[4][0].get(), window.config1Scales[4][1].get(), window.config1Scales[4][2].get(), window.config1Scales[4][3].get(), window.config1Scales[4][4].get(), window.config1Scales[4][5].get(), window.config1Scales[4][6].get(), window.config1Scales[4][7].get()],
                         [window.config1Scales[5][0].get(), window.config1Scales[5][1].get(), window.config1Scales[5][2].get(), window.config1Scales[5][3].get(), window.config1Scales[5][4].get(), window.config1Scales[5][5].get(), window.config1Scales[5][6].get(), window.config1Scales[5][7].get()],
                         [window.config1Scales[6][0].get(), window.config1Scales[6][1].get(), window.config1Scales[6][2].get(), window.config1Scales[6][3].get(), window.config1Scales[6][4].get(), window.config1Scales[6][5].get(), window.config1Scales[6][6].get(), window.config1Scales[6][7].get()]]

        config2Scales = [[window.config2Scales[0][0].get(), window.config2Scales[0][1].get(), window.config2Scales[0][2].get(), window.config2Scales[0][3].get(), window.config2Scales[0][4].get(), window.config2Scales[0][5].get(), window.config2Scales[0][6].get(), window.config2Scales[0][7].get()],
                         [window.config2Scales[1][0].get(), window.config2Scales[1][1].get(), window.config2Scales[1][2].get(), window.config2Scales[1][3].get(), window.config2Scales[1][4].get(), window.config2Scales[1][5].get(), window.config2Scales[1][6].get(), window.config2Scales[1][7].get()],
                         [window.config2Scales[6][0].get(), window.config2Scales[6][1].get(), window.config2Scales[6][2].get(), window.config2Scales[6][3].get(), window.config2Scales[6][4].get(), window.config2Scales[6][5].get(), window.config2Scales[6][6].get(), window.config2Scales[6][7].get()],
                         [window.config2Scales[7][0].get(), window.config2Scales[7][1].get(), window.config2Scales[7][2].get(), window.config2Scales[7][3].get(), window.config2Scales[7][4].get(), window.config2Scales[7][5].get(), window.config2Scales[7][6].get(), window.config2Scales[7][7].get()],
                         [window.config2Scales[8][0].get(), window.config2Scales[8][1].get(), window.config2Scales[8][2].get(), window.config2Scales[8][3].get(), window.config2Scales[8][4].get(), window.config2Scales[8][5].get(), window.config2Scales[8][6].get(), window.config2Scales[8][7].get()],
                         [window.config2Scales[9][0].get(), window.config2Scales[9][1].get(), window.config2Scales[9][2].get(), window.config2Scales[9][3].get(), window.config2Scales[9][4].get(), window.config2Scales[9][5].get(), window.config2Scales[9][6].get(), window.config2Scales[9][7].get()]]

        config3Scales = [[window.config3Scales[0][0].get(), window.config3Scales[0][1].get(), window.config3Scales[0][2].get(), window.config3Scales[0][3].get(), window.config3Scales[0][4].get(), window.config3Scales[0][5].get(), window.config3Scales[0][6].get(), window.config3Scales[0][7].get()],
                         [window.config3Scales[1][0].get(), window.config3Scales[1][1].get(), window.config3Scales[1][2].get(), window.config3Scales[1][3].get(), window.config3Scales[1][4].get(), window.config3Scales[1][5].get(), window.config3Scales[1][6].get(), window.config3Scales[1][7].get()],
                         [window.config3Scales[2][0].get(), window.config3Scales[2][1].get(), window.config3Scales[2][2].get(), window.config3Scales[2][3].get(), window.config3Scales[2][4].get(), window.config3Scales[2][5].get(), window.config3Scales[2][6].get(), window.config3Scales[2][7].get()],
                         [window.config3Scales[3][0].get(), window.config3Scales[3][1].get(), window.config3Scales[3][2].get(), window.config3Scales[3][3].get(), window.config3Scales[3][4].get(), window.config3Scales[3][5].get(), window.config3Scales[3][6].get(), window.config3Scales[3][7].get()],
                         [window.config3Scales[4][0].get(), window.config3Scales[4][1].get(), window.config3Scales[4][2].get(), window.config3Scales[4][3].get(), window.config3Scales[4][4].get(), window.config3Scales[4][5].get(), window.config3Scales[4][6].get(), window.config3Scales[4][7].get()]]
    
    
    for x in range(len(config1Scales)):
        for y in range(len(config1Scales[x])):
            if config1Scales[x][y] != previousConfig1Scales[x][y]:
                config1FunctionList[x](y+1, config1Scales[x][y])

    for x in range(len(config2Scales)):
        for y in range(len(config2Scales[x])):
            if config2Scales[x][y] != previousConfig2Scales[x][y]:
                config2FunctionList[x](y+1, config2Scales[x][y])
    
    for x in range(len(config3Scales)):
        for y in range(len(config3Scales[x])):
            if config3Scales[x][y] != previousConfig3Scales[x][y]:
                config3FunctionList[x](y+1, config3Scales[x][y])
                
    previousConfig1Scales = config1Scales
    previousConfig2Scales = config2Scales
    previousConfig3Scales = config3Scales
    
class GuiCreation: 
    def updateProgram(self, window):
        global IPMovementMode
        
        if window.quitFlag:
            window.destroy()  #This avoids the update event being in limbo
        else:
            if window.playButtonBool == False and window.recordButtonBool == False: #Image processing uses up too much resources that recording and play back quality is reduced
                imageProcessingData = imgProc.updateImageProcessing()
            else: #Need to call update when recording or play back since the update isn't being called in the GUI.run() function
                window.update() 
            
            updateGUIConfigSliders()
            
            if not window.DEBUG and window.connectedToggleBool == True:
                netSampleTimer = sampleTimer.netTimer(sampleTimer.cpuClockTimeInSeconds())
                if netSampleTimer >= 1/window.sampleRate:
                    sampleData()
                    printToConsole()
                    sampleTimer.restartTimer()
                
                recordPlayback()
                
                if window.trackObject == True:
                    #IPMovementMode.XYActiveTrack(imageProcessingData, window.positionScales[2].get())
                    
                    #IPMovementMode.XYZActiveTrack(imageProcessingData, 63.75, 12.14)
                    
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 11.84, 36.41) #Green Cap
                    IPMovementMode.XYZTimedTrack(imageProcessingData, 10.91, 20.74) #Red Marker Cap
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 23.94, 85.72) #Green Flash Light 
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 7.5, 150) #Pencil
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 27.33, 145.22) #Remove Before Flight
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 90, 114) #Blue Cup
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 100, 132.42) #Banana
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 63, 46.94) #Joystick Memory Pack
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 110, 40.5) #Joystick
                    #IPMovementMode.XYZTimedTrack(imageProcessingData, 48, 90) #Red Tape
                    
                updateServosWithConfigParams()
                
            updateServosWithPosition()
                  
            window.after(0, func=lambda: self.updateProgram(window))
                          
    def guiSetup(self):
        global imgProc
        
        #SETTING UP WINDOW
        window.geometry(str(guiWidth)+"x"+str(guiHeight)+"+"+str(guiXPosition)+"+"+str(guiYPosition)) #"1590x870+0+0"
        window.title("Robotic Arm Controller")
        setattr(window, "quitFlag", False)
        window.protocol('WM_DELETE_WINDOW', CF.closeWindow)
        window.bind("<Key>", CF.escape)
        
        #FRAME FOR SLIDERS AND IMAGE
        imgFrame = Tkinter.Frame(window)
        imgFrame.place(relx = 0, rely = 0.05, relwidth = 0.5, relheight = 0.5)
        
        #Image Processing Sliders
        filterScales = []
        filterNames = []
        
        names = ["Min Hue", "Min Saturation", "Min Value", "Erode/Dilate", "Max Hue", "Max Saturation", "Max Value", "Intensity"]
        savedImageProcessingVals = [savedValues.minHue, savedValues.minSat, savedValues.minVal, savedValues.erodeDilate, savedValues.maxHue, savedValues.maxSat, savedValues.maxVal, savedValues.intensity]
        for x in range(4):
            filterScales.append(Tkinter.Scale(imgFrame, from_ = 0, to = 255 - 252*int(x/3), width = 15, orient = "horizontal")) #Creating sliders
            filterScales[x].grid(row = x*2, column = 0)
            filterScales[x].set(savedImageProcessingVals[x])
            filterNames.append(Tkinter.Label(imgFrame, text = names[x], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[x].grid(row = x*2 + 1, column = 0)
        
        #Label For Image
        frontImgLabel = Tkinter.Label(imgFrame, background = "gray")  #The raw image for the front camera will go here
        frontImgLabel.grid(row = 0, column = 1, rowspan = 7, columnspan = 5)  
        eventHandlers.initilizeFrontRawImgEvents(frontImgLabel)
        frontImgLabel.bind("<Button-1>", eventHandlers.frontRawImgMouseEvent)
        frontImgLabel.bind("<ButtonRelease-1>", eventHandlers.frontRawImgMouseEvent)
        frontImgLabel.bind("<B1-Motion>", eventHandlers.frontRawImgDraw)
        setattr(window, "frontImgLabel", frontImgLabel)
        setattr(frontImgLabel, 'mouseDragLocation', [0, 0])
        setattr(frontImgLabel, 'boxPoint1', [0, 0])
        setattr(frontImgLabel, 'boxPoint2', [0, 0])
        setattr(frontImgLabel, 'buttonPressed', False)
        setattr(frontImgLabel, 'buttonReleased', False)
        
        #Image Processing Sliders
        for x in range(4):
            filterScales.append(Tkinter.Scale(imgFrame, from_ = 0, to = 255 - 235*int(x/3), width = 15, orient = "horizontal")) #Creating sliders
            filterScales[4+x].grid(row = x*2, column = 6)
            filterScales[4+x].set(savedImageProcessingVals[4+x])
            filterNames.append(Tkinter.Label(imgFrame, text = names[x+4], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[4+x].grid(row = x*2 + 1, column = 6)
        
        setattr(window, "filterScales", filterScales)

        
        #TRACK OBJECT BUTTON
        trackObjectButton = Tkinter.Button(window, text="Track Object", command = CF.trackObject, width = 11)
        trackObjectButton.place(relx = 0.508, rely = 0.25, anchor = "center")
        setattr(window, "trackObject", False)
        setattr(window, "trackObjectButton", trackObjectButton)
        
        #CONSOLE FRAME
        consoleFrame = Tkinter.Frame(window)
        consoleFrame.place(relx = 0.545, rely = 0.03)
        
        #Check Boxes
        printCheckBoxValArray = [Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar()]
        
        names = ["Position (Deg)", "Speed (RPM)\nCCW: +\nCW: -", "Voltage (V)", "Load (%)\nCCW: +\nCW: -", "Temperature (C)"]
        savedCheckBoxVals = [savedValues.positionCheckBox, savedValues.speedCheckBox, savedValues.voltageCheckBox, savedValues.loadCheckBox, savedValues.temperatureCheckBox]
        printCheckBoxes = []
        for x in range(5):
            printCheckBoxes.append(Tkinter.Checkbutton(consoleFrame, text=names[x], variable = printCheckBoxValArray[x]))
            printCheckBoxes[x].grid(row = x+1, column = 0, sticky = "W")
            if savedCheckBoxVals[x] == 1:
                printCheckBoxes[x].select()
            
        setattr(window, "printCheckBoxValArray", printCheckBoxValArray)
        
        #Sample Rate
        sampleRateLabel = Tkinter.Label(consoleFrame, text = "Sample Rate (Hz):")
        sampleRateLabel.grid(row = 0, column = 2, sticky = "E")
        samplingRateText = Tkinter.StringVar()
        samplingRateEntry = Tkinter.Entry(consoleFrame, textvariable = samplingRateText, width = 8, justify = "center"); samplingRateText.set(savedValues.sampleRate)
        samplingRateEntry.bind("<Return>", CF.samplingRateOk)
        samplingRateEntry.grid(row = 0, column = 3, sticky = "W")
        sampleRateOkButton = Tkinter.Button(consoleFrame, text = "OK", command = CF.samplingRateOk)
        sampleRateOkButton.grid(row = 0, column = 3, sticky = "E")
        setattr(window, "samplingRateText", samplingRateText)
        
        #Console
        consolText = Tkinter.Text(consoleFrame, borderwidth = 7, width = int(screenRes[0]/21.7), height = int(screenRes[1]/38))
        consolText.grid(row = 1, column = 1, rowspan = 5, columnspan = 5)
        sys.stdout = CF.StdoutRedirector(consolText) #COMMENT THIS LINE OUT TO STOP PRINTING TO GUI
        setattr(window, "consolText", consolText)
        
        #record/play back
        recordButton = Tkinter.Button(consoleFrame, text="Record", command = lambda: CF.RecordJointAngles(), width = 12)
        recordButton.grid(row = 6, column = 1)
        recordButton.config(state="disabled")
        
        playButton = Tkinter.Button(consoleFrame, text="Play", command = CF.playRecordedJointAnglesFile, width = 12)
        playButton.grid(row = 6, column = 2)
        playButton.config(state="disabled")
        
        playbackFileNameText = Tkinter.StringVar()
        playBackFileName = Tkinter.Label(consoleFrame, text = "File Name:") 
        playBackFileName.grid(row = 6, column = 3, sticky = "E")
        fileNameTextEntry = Tkinter.Entry(consoleFrame, textvariable=playbackFileNameText, state="readonly")
        fileNameTextEntry.grid(row = 6, column = 4, sticky = "EW")
        
        loadButton = Tkinter.Button(consoleFrame, text="Load", command = CF.loadRecordedJointAnglesFile)
        loadButton.grid(row = 6, column = 5, sticky = "W", padx = 10)
        
        playBackRateLabel = Tkinter.Label(window, text = "Playback Rate:", font = "Helvetica 10 bold")
        minusPlayBackButton = Tkinter.Button(window, width = 2, text = "-", font = "Helvetica 15 bold", command = CF.playBackRateMinus)
        plusPlayBackButton = Tkinter.Button(window, width = 2, text = "+", font = "Helvetica 15 bold", command = CF.playBackRatePlus)
        setattr(window, "playBackModifier", [playBackRateLabel, minusPlayBackButton, plusPlayBackButton])
        
        setattr(window, "disableTorqueVar", None)
        setattr(window, "recordButton", recordButton)
        setattr(window, "recordButtonBool", False)
        setattr(window, "recordedFileNameText", None)
        setattr(window, "sampleRate", savedValues.sampleRate)
        setattr(window, "recordedJointAnglesArray", [])
        
        setattr(window, "playButton", playButton)
        setattr(window, "playButtonBool", False)
        setattr(window, "playbackFileNameText", playbackFileNameText)
        setattr(window, "playbackLogValues", None)
        
        #TABS
        notebook = ttk.Notebook(window)
        notebook.place(relx = 0, rely = 0.52, relwidth = 1, relheight = 0.5)
        
        tab1 = Tkinter.Frame(notebook, width=1000, height=200)
        tab1.place()
        notebook.add(tab1, text="Servo Control")
        
        #This could be a second potential tab. Uncomment the bellow code to see a second tab in the code
        #tab2 = Tkinter.Frame(notebook, width=1000, height=200)
        #tab2.place()
        #notebook.add(tab2, text="Update Me")
        
        #SERVO NUM & MODEL, CONNECT/DISCONNECT, SERVO CONFIG DROPBOX, IMPORT/EXPORT, HOME CONFIGURATION, DEFAULT RAM, SLIDER POSITION & INV SOLUTION NUMBER FRAME
        scalePositionFrame = Tkinter.Frame(tab1)
        scalePositionFrame.grid(row = 0, column = 0, padx = 10, sticky = "N")
        
        #Servo Num
        servoNumLabel = Tkinter.Label(scalePositionFrame, text = "Servo\nNumber:")
        servoNumLabel.grid(row = 0, column = 0, sticky="SE")
        
        dropBoxServoNumVariable = Tkinter.IntVar(window)
        dropBoxServoNumVariable.set(savedValues.dropBoxServoNumVariable) # default value
        dropBoxServoNum = Tkinter.OptionMenu(scalePositionFrame, dropBoxServoNumVariable, "1", "2", "3", "4", "5", "6", "7", "8")
        dropBoxServoNum.grid(row = 0, column = 1, pady = 5)
        dropBoxServoNum.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "dropBoxServoNum", dropBoxServoNum)
        setattr(window, "dropBoxServoNumVariable", dropBoxServoNumVariable)
        
        #Servo Model
        servoModelLabel = Tkinter.Label(scalePositionFrame, text = "Servo\nModel:")
        servoModelLabel.grid(row = 0, column = 2, sticky="SE")
        
        dropBoxServoModelVariable = Tkinter.StringVar(window)
        dropBoxServoModelVariable.set(savedValues.dropBoxServoModelVariable) # default value
        dropBoxServoModel = Tkinter.OptionMenu(scalePositionFrame, dropBoxServoModelVariable, "AX-12", "AX-18", "MX-28"); dropBoxServoModel.config(width=5)
        dropBoxServoModel.grid(row = 0, column = 3, pady = 5)
        dropBoxServoModel.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "dropBoxServoModel", dropBoxServoModel)
        setattr(window, "dropBoxServoModelVariable", dropBoxServoModelVariable)
        
        #Connect/Disconnect button
        connectDisconnectButton = Tkinter.Button(scalePositionFrame, text="Disconnected", fg="red", font = "TkDefaultFont 9 bold", width = 35, command = CF.connectDisconnect)
        connectDisconnectButton.grid(row = 1, column = 0, columnspan = 4, padx = 2, pady = 3)
        setattr(window, "connectDisconnectButton", connectDisconnectButton)
        setattr(window, "connectedToggleBool", False)
        
        #Servo Config Dropbox
        dropBoxVariable = Tkinter.StringVar(window)
        dropBoxVariable.set("Configuration 1") # default value
        dropBox = Tkinter.OptionMenu(scalePositionFrame, dropBoxVariable, "Configuration 1", "Configuration 2", "Configuration 3")
        dropBox.grid(row = 2, column = 0, columnspan = 4, padx = 2, pady = 3)
        dropBox.config(width = 36)
        dropBox.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "dropBoxVariable", dropBoxVariable)
        
        #Home Configuration
        homeConfigButton = Tkinter.Button(scalePositionFrame, text="Home Configuration", width = 16, command = lambda: CF.homeConfiguration([])) #Put joint angles in this empty array to signify where the joint slider will go to when the home configuration button is pressed
        homeConfigButton.grid(row = 3, column = 0, columnspan = 2, pady = 2)
        
        #Default Ram Values
        defaultRamValButton = Tkinter.Button(scalePositionFrame, text="Default RAM Values", width = 16, command = CF.defaultRAMValues)
        defaultRamValButton.grid(row = 3, column = 2, columnspan = 2, pady = 2)
        
        #Import/Export RAM Values
        importRamButton = Tkinter.Button(scalePositionFrame, text = "Import Config", width = 16, command = CF.importConfigValues)
        importRamButton.grid(row = 4, column = 0, columnspan = 2, padx = 1, pady = 5)
        importRamButton.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        
        exportRamButton = Tkinter.Button(scalePositionFrame, text = "Export Config", width = 16, command = lambda: CF.ExportConfigValues())
        exportRamButton.grid(row = 4, column = 2, columnspan = 2, padx = 1, pady = 5)
        exportRamButton.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        
        #Kinematics Selector
        fwdKinematicFunctionNames = []
        fwdKinematicFunctionObjects = []
        for name, obj in inspect.getmembers(fKin):
            if inspect.ismethod(obj):
                if not (name.startswith("__")):
                    fwdKinematicFunctionNames.append(name)
                    fwdKinematicFunctionObjects.append(obj)
        setattr(window, "fwdKinematicFunctions", [fwdKinematicFunctionNames, fwdKinematicFunctionObjects])
        
        dropBoxFwdKinematicsSelectorVariable = Tkinter.StringVar(window)
        dropBoxFwdKinematicsSelectorVariable.set(savedValues.dropBoxFwdKinematicsSelectorVariable) # default value
        dropBoxFwdKinematicSelector = Tkinter.OptionMenu(scalePositionFrame, dropBoxFwdKinematicsSelectorVariable, "FWD Kinematics", *fwdKinematicFunctionNames)
        dropBoxFwdKinematicSelector.grid(row = 5, column = 0, columnspan = 2, padx = 2, pady = 5)
        dropBoxFwdKinematicSelector.config(width = 14)
        dropBoxFwdKinematicSelector.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "dropBoxFwdKinematicSelector", dropBoxFwdKinematicSelector)
        setattr(window, "dropBoxFwdKinematicsSelectorVariable", dropBoxFwdKinematicsSelectorVariable)
        
        invKinematicFunctionNames = []
        invKinematicFunctionObjects = []
        for name, obj in inspect.getmembers(iKin):
            if inspect.ismethod(obj):
                if not (name.startswith("__")):
                    invKinematicFunctionNames.append(name)
                    invKinematicFunctionObjects.append(obj)
        setattr(window, "invKinematicFunctions", [invKinematicFunctionNames, invKinematicFunctionObjects])
        
        dropBoxInvKinematicsSelectorVariable = Tkinter.StringVar(window)
        dropBoxInvKinematicsSelectorVariable.set(savedValues.dropBoxInvKinematicsSelectorVariable) # default value
        dropBoxInvKinematicSelector = Tkinter.OptionMenu(scalePositionFrame, dropBoxInvKinematicsSelectorVariable, "INV Kinematics", *invKinematicFunctionNames)
        dropBoxInvKinematicSelector.grid(row = 5, column = 2, columnspan = 2, padx = 2, pady = 5)
        dropBoxInvKinematicSelector.config(width = 14)
        dropBoxInvKinematicSelector.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "dropBoxInvKinematicSelector", dropBoxInvKinematicSelector)
        setattr(window, "dropBoxInvKinematicsSelectorVariable", dropBoxInvKinematicsSelectorVariable)
        
        #INV Kinematics Solution Number
        invKinSolutionNumber = Tkinter.StringVar(window)
        invKinSolutionNumber.set(savedValues.invKinSolutionNumber) # default value
        dropBoxInvKinematicSolutionMenu = Tkinter.OptionMenu(scalePositionFrame, invKinSolutionNumber, "Solution 1")
        dropBoxInvKinematicSolutionMenu.grid(row = 6, column = 0, columnspan = 4, padx = 2, pady = 3)
        dropBoxInvKinematicSolutionMenu.config(width = 36, state="disabled")
        dropBoxInvKinematicSolutionMenu.bind("<Button-1>", lambda event, args=[window]: CF.Refresh(event, args))
        setattr(window, "invKinSolutionNumber", invKinSolutionNumber)
        setattr(window, "dropBoxInvKinematicSolutionMenu", dropBoxInvKinematicSolutionMenu)
        
        #Position Sliders
        XLabel = Tkinter.Label(scalePositionFrame, state="disabled", text = "X:")
        XLabel.grid(row = 7, column = 0, sticky="SW")
        XScale = Tkinter.Scale(scalePositionFrame, state="disabled", from_ = -0, to = 0, resolution = 0.01, width = 15, length = 230, orient = "horizontal") #Creating sliders
        XScale.grid(row = 7, column = 0, columnspan = 4)
        
        YLabel = Tkinter.Label(scalePositionFrame, state="disabled", text = "Y:")
        YLabel.grid(row = 8, column = 0, sticky="SW")
        YScale = Tkinter.Scale(scalePositionFrame, state="disabled", from_ = -0, to = 0, resolution = 0.01, width = 15, length = 230, orient = "horizontal") #Creating sliders
        YScale.grid(row = 8, column = 0, columnspan = 4)
        
        ZLabel = Tkinter.Label(scalePositionFrame, state="disabled", text = "Z:")
        ZLabel.grid(row = 9, column = 0, sticky="SW")
        ZScale = Tkinter.Scale(scalePositionFrame, state="disabled", from_ = -0, to = 0, resolution = 0.01, width = 15, length = 230, orient = "horizontal") #Creating sliders
        ZScale.grid(row = 9, column = 0, columnspan = 4)
        
        positionLabels = [XLabel, YLabel, ZLabel]
        positionScales = [XScale, YScale, ZScale]
        setattr(window, "positionLabels", positionLabels)
        setattr(window, "positionScales", positionScales)
            
        #INDIVIDUAL SERVO CONTROL FRAME
        individualServoControlFrame = Tkinter.Frame(tab1)
        individualServoControlFrame.grid(row = 0, column = 1, sticky = "N")
        individualMotorControlLabel = Tkinter.Label(individualServoControlFrame, text = "Angular Displacement (deg)\n", font = "Helvetica 8 bold")
        individualMotorControlLabel.grid(row = 0, column = 1)
        
        #Name Labels and Angular Displacement Sliders
        names = ["Servo {}:".format(8-x) for x in range(8)]
        jointLabels = []
        jointScales = []
        for x in range(8):
            jointLabels.append(Tkinter.Label(individualServoControlFrame, text = names[x]))
            jointLabels[x].grid(row = x+1, column = 0, sticky="SE")
            if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
                jointScales.append(Tkinter.Scale(individualServoControlFrame, from_ = 0, to = 296.67, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                jointScales.append(Tkinter.Scale(individualServoControlFrame, from_ = 0, to = 360.36, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
                
            jointScales[x].grid(row = 8-x, column = 1)
            
        setattr(window, "jointScales", jointScales)
        setattr(window, "jointLabels", jointLabels)
        
        #CONFIG 3 FRAME
        config3Frame = Tkinter.Frame(tab1)
        config3Frame.grid(row = 0, column = 2, sticky = "N")
        
        #Alarm LED
        alarmLEDLabel = Tkinter.Label(config3Frame, text = "Alarm LED (bin)\n(EEPROM)", font = "Helvetica 8 bold")
        alarmLEDLabel.grid(row = 0, column = 0)
        alarmLEDScale = []
        for x in range(8):
            alarmLEDScale.append(Tkinter.Scale(config3Frame, from_ = 0, to = 127, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            alarmLEDScale[x].grid(row = 8-x, column = 0)
            
        #Alarm Shutdown
        alarmShutdownLabel = Tkinter.Label(config3Frame, text = "Alarm Shutdown (bin)\n(EEPROM)", font = "Helvetica 8 bold")
        alarmShutdownLabel.grid(row = 0, column = 1)
        alarmShutdownScale = []
        for x in range(8):
            alarmShutdownScale.append(Tkinter.Scale(config3Frame, from_ = 0, to = 127, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            alarmShutdownScale[x].grid(row = 8-x, column = 1)
                    
        #Multi Turn Offset
        multiTurnOffsetLabel = Tkinter.Label(config3Frame, text = "Multi Turn Offset (bin)\n(EEPROM)", font = "Helvetica 8 bold")
        multiTurnOffsetLabel.grid(row = 0, column = 2)
        multiTurnOffsetScale = []
        for x in range(8):
            multiTurnOffsetScale.append(Tkinter.Scale(config3Frame, from_ = 0, to = 1024, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            multiTurnOffsetScale[x].grid(row = 8-x, column = 2)
                    
        #Resolution Divider
        resolutionDividerLabel = Tkinter.Label(config3Frame, text = "Resolution Divider (N/A)\n(EEPROM)", font = "Helvetica 8 bold")
        resolutionDividerLabel.grid(row = 0, column = 3)
        resolutionDividerScale = []
        for x in range(8):
            resolutionDividerScale.append(Tkinter.Scale(config3Frame, from_ = 1, to = 4, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            resolutionDividerScale[x].grid(row = 8-x, column = 3)
                    
        #Goal Acceleration
        goalAccelerationLabel = Tkinter.Label(config3Frame, text = "Goal Acceleration (deg/sec^2)\n(RAM)", font = "Helvetica 8 bold")
        goalAccelerationLabel.grid(row = 0, column = 4)
        savedGoalAccelerationScaleVals = [savedValues.goalAccelerationScale1, savedValues.goalAccelerationScale2, savedValues.goalAccelerationScale3, savedValues.goalAccelerationScale4, savedValues.goalAccelerationScale5, savedValues.goalAccelerationScale6, savedValues.goalAccelerationScale7, savedValues.goalAccelerationScale8]
        goalAccelerationScale = []
        for x in range(8):
            goalAccelerationScale.append(Tkinter.Scale(config3Frame, from_ = 0, to = 2180.082, resolution = 8.583, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            goalAccelerationScale[x].grid(row = 8-x, column = 4)
            goalAccelerationScale[x].set(savedGoalAccelerationScaleVals[x])
        
        config3Scales = [alarmLEDScale, alarmShutdownScale, multiTurnOffsetScale, resolutionDividerScale, goalAccelerationScale]
        config3Labels = [alarmLEDLabel, alarmShutdownLabel, multiTurnOffsetLabel, resolutionDividerLabel, goalAccelerationLabel]           
        setattr(window, "config3Scales", config3Scales)
        setattr(window, "config3Labels", config3Labels)
        setattr(window, "config3Frame", config3Frame)
                    
        #CONFIG 2 FRAME
        config2Frame = Tkinter.Frame(tab1)
        config2Frame.grid(row = 0, column = 2, sticky = "N")
        
        #CW Limit Config Sliders
        CWLimitLabel = Tkinter.Label(config2Frame, text = "CW Limit (deg)\n(EEPROM)", font = "Helvetica 8 bold")
        CWLimitLabel.grid(row = 0, column = 0)
        CWLimitScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
                CWLimitScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 296.67, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                CWLimitScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 360.36, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders

            CWLimitScale[x].grid(row = 8-x, column = 0)
            
        #CCW Limit Config Sliders
        CCWLimitLabel = Tkinter.Label(config2Frame, text = "CCW Limit (deg)\n(EEPROM)", font = "Helvetica 8 bold")
        CCWLimitLabel.grid(row = 0, column = 1)
        CCWLimitScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
                CCWLimitScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 296.67, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                CCWLimitScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 360.36, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
                
            CCWLimitScale[x].grid(row = 8-x, column = 1)
            
        #CW Compliance Margin Sliders
        CWComplianceMarginLabel = Tkinter.Label(config2Frame, text = "CW Compliance Margin\n(RAM)", font = "Helvetica 8 bold")
        CWComplianceMarginLabel.grid(row = 0, column = 2)
        savedCWComplianceMarginScaleVals = [savedValues.CWComplianceMarginScale1, savedValues.CWComplianceMarginScale2, savedValues.CWComplianceMarginScale3, savedValues.CWComplianceMarginScale4, savedValues.CWComplianceMarginScale5, savedValues.CWComplianceMarginScale6, savedValues.CWComplianceMarginScale7, savedValues.CWComplianceMarginScale8]
        CWComplianceMarginScale = []
        for x in range(8):
            CWComplianceMarginScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 73.95, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            CWComplianceMarginScale[x].grid(row = 8-x, column = 2)
            CWComplianceMarginScale[x].set(savedCWComplianceMarginScaleVals[x])
        
        #CCW Compliance Margin Sliders
        CCWComplianceMarginLabel = Tkinter.Label(config2Frame, text = "CCW Compliance Margin\n(RAM)", font = "Helvetica 8 bold")
        CCWComplianceMarginLabel.grid(row = 0, column = 3)
        savedCCWComplianceMarginScaleVals = [savedValues.CCWComplianceMarginScale1, savedValues.CCWComplianceMarginScale2, savedValues.CCWComplianceMarginScale3, savedValues.CCWComplianceMarginScale4, savedValues.CCWComplianceMarginScale5, savedValues.CCWComplianceMarginScale6, savedValues.CCWComplianceMarginScale7, savedValues.CCWComplianceMarginScale8]
        CCWComplianceMarginScale = []
        for x in range(8):
            CCWComplianceMarginScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 73.95, resolution = 0.01, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            CCWComplianceMarginScale[x].grid(row = 8-x, column = 3)
            CCWComplianceMarginScale[x].set(savedCCWComplianceMarginScaleVals[x])
            
        #CW Compliance Slope Sliders
        CWComplianceSlopeLabel = Tkinter.Label(config2Frame, text = "CW Compliance Slope\n(RAM)", font = "Helvetica 8 bold")
        CWComplianceSlopeLabel.grid(row = 0, column = 4)
        savedCWComplianceSlopeScaleVals = [savedValues.CWComplianceSlopeScale1, savedValues.CWComplianceSlopeScale2, savedValues.CWComplianceSlopeScale3, savedValues.CWComplianceSlopeScale4, savedValues.CWComplianceSlopeScale5, savedValues.CWComplianceSlopeScale6, savedValues.CWComplianceSlopeScale7, savedValues.CWComplianceSlopeScale8]
        CWComplianceSlopeScale = []
        for x in range(8):
            CWComplianceSlopeScale.append(Tkinter.Scale(config2Frame, from_ = 1, to = 7, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            CWComplianceSlopeScale[x].grid(row = 8-x, column = 4)
            CWComplianceSlopeScale[x].set(savedCWComplianceSlopeScaleVals[x])
        
        #CCW Compliance Slope Sliders
        CCWComplianceSlopeLabel = Tkinter.Label(config2Frame, text = "CCW Compliance Slope\n(RAM)", font = "Helvetica 8 bold")
        CCWComplianceSlopeLabel.grid(row = 0, column = 5)
        savedCCWComplianceSlopeScaleVals = [savedValues.CCWComplianceSlopeScale1, savedValues.CCWComplianceSlopeScale2, savedValues.CCWComplianceSlopeScale3, savedValues.CCWComplianceSlopeScale4, savedValues.CCWComplianceSlopeScale5, savedValues.CCWComplianceSlopeScale6, savedValues.CCWComplianceSlopeScale7, savedValues.CCWComplianceSlopeScale8]
        CCWComplianceSlopeScale = []
        for x in range(8):
            CCWComplianceSlopeScale.append(Tkinter.Scale(config2Frame, from_ = 1, to = 7, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            CCWComplianceSlopeScale[x].grid(row = 8-x, column = 5)
            CCWComplianceSlopeScale[x].set(savedCCWComplianceSlopeScaleVals[x])
            
        #P Sliders
        PLabel = Tkinter.Label(config2Frame, text = "P\n(RAM)", font = "Helvetica 8 bold")
        PLabel.grid(row = 0, column = 2)
        savedPScaleVals = [savedValues.PScale1, savedValues.PScale2, savedValues.PScale3, savedValues.PScale4, savedValues.PScale5, savedValues.PScale6, savedValues.PScale7, savedValues.PScale8]
        PScale = []
        for x in range(8):
            PScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 255, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            PScale[x].grid(row = 8-x, column = 2)
            PScale[x].set(savedPScaleVals[x])
        
        #I Sliders
        ILabel = Tkinter.Label(config2Frame, text = "I\n(RAM)", font = "Helvetica 8 bold")
        ILabel.grid(row = 0, column = 3)
        savedIScaleVals = [savedValues.IScale1, savedValues.IScale2, savedValues.IScale3, savedValues.IScale4, savedValues.IScale5, savedValues.IScale6, savedValues.IScale7, savedValues.IScale8]
        IScale = []
        for x in range(8):
            IScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 255, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            IScale[x].grid(row = 8-x, column = 3)
            IScale[x].set(savedIScaleVals[x])
        
        #D Sliders
        DLabel = Tkinter.Label(config2Frame, text = "D\n(RAM)", font = "Helvetica 8 bold")
        DLabel.grid(row = 0, column = 4)
        savedDScaleVals = [savedValues.DScale1, savedValues.DScale2, savedValues.DScale3, savedValues.DScale4, savedValues.DScale5, savedValues.DScale6, savedValues.DScale7, savedValues.DScale8]
        DScale = []
        for x in range(8):
            DScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 255, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            DScale[x].grid(row = 8-x, column = 4)
            DScale[x].set(savedDScaleVals[x])
        
        #Punch Sliders
        punchLabel = Tkinter.Label(config2Frame, text = "Punch\n(RAM)", font = "Helvetica 8 bold")
        punchLabel.grid(row = 0, column = 6)
        savedPunchScaleVals = [savedValues.punchScale1, savedValues.punchScale2, savedValues.punchScale3, savedValues.punchScale4, savedValues.punchScale5, savedValues.punchScale6, savedValues.punchScale7, savedValues.punchScale8]
        punchScale = []
        for x in range(8):
            punchScale.append(Tkinter.Scale(config2Frame, from_ = 0, to = 1023, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            punchScale[x].grid(row = 8-x, column = 6)
            punchScale[x].set(savedPunchScaleVals[x])
        
        config2Scales = [CWLimitScale, CCWLimitScale, CWComplianceMarginScale, CCWComplianceMarginScale, CWComplianceSlopeScale, CCWComplianceSlopeScale, PScale, IScale, DScale, punchScale]
        config2Labels = [CWLimitLabel, CCWLimitLabel, CWComplianceMarginLabel, CCWComplianceMarginLabel, CWComplianceSlopeLabel, CCWComplianceSlopeLabel, PLabel, ILabel, DLabel, punchLabel]
        setattr(window, "config2Scales", config2Scales)
        setattr(window, "config2Labels", config2Labels)
        setattr(window, "config2Frame", config2Frame)
        
        #CONFIG 1 FRAME
        config1Frame = Tkinter.Frame(tab1)
        config1Frame.grid(row = 0, column = 2, sticky = "N")
        
        #Speed Limit
        movingSpeedLabel = Tkinter.Label(config1Frame, text = "Speed Limit (RPM)\n(RAM)", font = "Helvetica 8 bold")
        movingSpeedLabel.grid(row = 0, column = 0)
        savedMovingSpeedVals = [savedValues.movingSpeed1, savedValues.movingSpeed2, savedValues.movingSpeed3, savedValues.movingSpeed4, savedValues.movingSpeed5, savedValues.movingSpeed6, savedValues.movingSpeed7, savedValues.movingSpeed8]
        movingSpeedScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12':
                movingSpeedScale.append(Tkinter.Scale(config1Frame, from_ = 0, to = 60, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'AX-18':
                movingSpeedScale.append(Tkinter.Scale(config1Frame, from_ = 0, to = 97, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                movingSpeedScale.append(Tkinter.Scale(config1Frame, from_ = 0, to = 67, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            
            movingSpeedScale[x].grid(row = 8-x, column = 0)
            movingSpeedScale[x].set(savedMovingSpeedVals[x])
            
        #Torque Limit
        torqueLimitLabel = Tkinter.Label(config1Frame, text = "Torque Limit (%)\n(RAM)", font = "Helvetica 8 bold")
        torqueLimitLabel.grid(row = 0, column = 1)
        savedTorqueLimitVals = [savedValues.torqueLimit1, savedValues.torqueLimit2, savedValues.torqueLimit3, savedValues.torqueLimit4, savedValues.torqueLimit5, savedValues.torqueLimit6, savedValues.torqueLimit7, savedValues.torqueLimit8]
        torqueLimitScale = []
        for x in range(8):
            torqueLimitScale.append(Tkinter.Scale(config1Frame, from_ = 0, to = 100, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            torqueLimitScale[x].grid(row = 8-x, column = 1)
            torqueLimitScale[x].set(savedTorqueLimitVals[x])
            
        #Lowest Voltage Limit
        lowestVoltageLimitLabel = Tkinter.Label(config1Frame, text = "Lowest Voltage Limit (V)\n(EEPROM)", font = "Helvetica 8 bold")
        lowestVoltageLimitLabel.grid(row = 0, column = 2)
        lowestVoltageLimitScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
                lowestVoltageLimitScale.append(Tkinter.Scale(config1Frame, from_ = 5, to = 14, resolution = 0.1, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                lowestVoltageLimitScale.append(Tkinter.Scale(config1Frame, from_ = 6, to = 16, resolution = 0.1, width = 15, length = 150, orient = "horizontal")) #Creating sliders
                
            lowestVoltageLimitScale[x].grid(row = 8-x, column = 2)
            
        #Highest Voltage Limit
        highestVoltageLimitLabel = Tkinter.Label(config1Frame, text = "Highest Voltage Limit (V)\n(EEPROM)", font = "Helvetica 8 bold")
        highestVoltageLimitLabel.grid(row = 0, column = 3)
        highestVoltageLimitScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12' or window.dropBoxServoModelVariable.get() == 'AX-18':
                highestVoltageLimitScale.append(Tkinter.Scale(config1Frame, from_ = 5, to = 14, resolution = 0.1, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                highestVoltageLimitScale.append(Tkinter.Scale(config1Frame, from_ = 6, to = 16, resolution = 0.1, width = 15, length = 150, orient = "horizontal")) #Creating sliders

            highestVoltageLimitScale[x].grid(row = 8-x, column = 3)
            
        #Highest Temperature Limit
        highestTemperatureLimitLabel = Tkinter.Label(config1Frame, text = "Highest Temperature Limit (C)\n(EEPROM)", font = "Helvetica 8 bold")
        highestTemperatureLimitLabel.grid(row = 0, column = 4)
        highestTemperatureLimitScale = []
        for x in range(8):
            if window.dropBoxServoModelVariable.get() == 'AX-12':
                highestTemperatureLimitScale.append(Tkinter.Scale(config1Frame, from_ = 20, to = 70, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'AX-18':
                highestTemperatureLimitScale.append(Tkinter.Scale(config1Frame, from_ = 20, to = 75, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            elif window.dropBoxServoModelVariable.get() == 'MX-28':
                highestTemperatureLimitScale.append(Tkinter.Scale(config1Frame, from_ = 20, to = 80, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            
            highestTemperatureLimitScale[x].grid(row = 8-x, column = 4)
        
        #Return Delay Time
        returnDelayTimeLabel = Tkinter.Label(config1Frame, text = "Return Delay Time (usec)\n(EEPROM)", font = "Helvetica 8 bold")
        returnDelayTimeLabel.grid(row = 0, column = 5)
        returnDelayTimeScale = []
        for x in range(8):
            returnDelayTimeScale.append(Tkinter.Scale(config1Frame, from_ = 0, to = 508, width = 15, length = 150, orient = "horizontal")) #Creating sliders
            returnDelayTimeScale[x].grid(row = 8-x, column = 5)
            
        #LED Enable
        ledEnableLabel = Tkinter.Label(config1Frame, text = "LED Enable\n(RAM)", font = "Helvetica 8 bold")
        ledEnableLabel.grid(row = 0, column = 6, padx = 40)
        
        ledEnableCheckboxValArray = [Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar()]
        savedLedEnableCheckboxVals = [savedValues.ledEnable1, savedValues.ledEnable2, savedValues.ledEnable3, savedValues.ledEnable4, savedValues.ledEnable5, savedValues.ledEnable6, savedValues.ledEnable7, savedValues.ledEnable8]
        ledEnableCheckbox = []
        for x in range(8):
            ledEnableCheckbox.append(Tkinter.Checkbutton(config1Frame, variable = ledEnableCheckboxValArray[x]))
            ledEnableCheckbox[x].grid(row = 8-x, column = 6, padx = 40, sticky = "s")
            if savedLedEnableCheckboxVals[x] == 1:
                ledEnableCheckbox[x].select()
        
        
        config1Scales = [movingSpeedScale, torqueLimitScale, lowestVoltageLimitScale, highestVoltageLimitScale, highestTemperatureLimitScale, returnDelayTimeScale, ledEnableCheckboxValArray]
        config1ScaleObjects = [movingSpeedScale, torqueLimitScale, lowestVoltageLimitScale, highestVoltageLimitScale, highestTemperatureLimitScale, returnDelayTimeScale, ledEnableCheckbox] #The last element of config1Scales, ledEnableCheckboxValArray, is not checkbox objects. As a result, I am remaking the array with the checkbox widget object
        config1Labels = [movingSpeedLabel, torqueLimitLabel, lowestVoltageLimitLabel, highestVoltageLimitLabel, highestTemperatureLimitLabel, returnDelayTimeLabel, ledEnableLabel]
        setattr(window, "config1Scales", config1Scales)
        setattr(window, "config1ScaleObjects", config1ScaleObjects)
        setattr(window, "config1Labels", config1Labels)
        setattr(window, "config1Frame", config1Frame)
        
        
        #HIDE ALL SLIDERS OVER THE INITIAL dropBoxServoNumVariable NUMBER
        #This block of code doesnt need to be here since the sliders get dynamically updated, but without this code, you would breifly see all the sliders before it dyanamically updated. Basically this code makes things look smoother upon startup
        for x in range(8-window.dropBoxServoNumVariable.get()):
            window.jointScales[-(x+1)].grid_remove()
            window.jointLabels[x].grid_remove()
                
        for x in range(len(window.config1ScaleObjects)):
            for y in range(8-window.dropBoxServoNumVariable.get()):
                window.config1ScaleObjects[x][-(y+1)].grid_remove()
        
        for x in range(len(window.config2Scales)):
            for y in range(8-window.dropBoxServoNumVariable.get()):
                window.config2Scales[x][-(y+1)].grid_remove()
                
        for x in range(len(window.config3Scales)):
            for y in range(8-window.dropBoxServoNumVariable.get()):
                window.config3Scales[x][-(y+1)].grid_remove()
        
        
        #IMAGE PROCESSING
        imgProc = image_processing.ImageProcessing(window) #This needs to be here so that the 'window' variable has all its setattr
        
        copyrightLabel = Tkinter.Label(window, text="Copyright (c) 2016, Austin Owens, All rights reserved.", font=("Calibri", int(screenRes[0]/123)), foreground = "black")
        copyrightLabel.place(relx = 0.5, rely = 0.984, anchor="center")
        
        window.after(0, func=lambda: self.updateProgram(window))
        window.mainloop()
     
if __name__ == "__main__":
    
    #CF.licenseAgreement(window)
    
    #if window.EULA == True:
    gui = GuiCreation()
    gui.guiSetup()
    window.mainloop()