'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: COMfinder
   :synopsis: Detects which daughter cards are connected and sets up Comms Tab accordingly.
   
:Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Assistant: Michael Jannain <jannainm@gmail.com>
:Date: Created on April 10, 2015; Edit on January 05, 2016
:Description: Runs the function and sets up the board drop-down, method listbox, and consoles based on the connected board.
'''

import sys
import glob
import serial
import previous_state_logging_system
from serial.tools import list_ports as lp
import Tkinter, ttk
import inspect
import imp
import main.external_devices.sparton_ahrs as sparton
import main.external_devices.microcontroller_sib as sib
import main.external_devices.microcontroller_tcb as tcb
import main.external_devices.microcontroller_pmud as pmud
import main.external_devices.microcontroller_dib as dib
import main.external_devices.microcontroller_hydras as hydras
import main.external_devices.microcontroller_wcb as wcb
import main.external_devices.movement as movement
import time


class COMScript():
    '''
    This class detects connected boards and updates command dictionary list to run commands.
    '''
    def __init__(self, window):
        '''
        Initializes the COMScript object.
        
        **Parameters**: \n
        * **window** -main Tkinter root object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
    
    def addRunToListbox(self):
        '''
        Adds dictionary of command parameters to the list in tab3.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.window.currentBoardNameList.append(self.window.boardValue.get())
        
        if len(self.window.paramLabelList) > 0:
            try:
                self.window.paramDictionary[self.window.param_value.get()] = int(self.window.paramValueText.get("1.0", "end"))
            except:
                self.window.scriptText.insert("insert", "FAILED: One or more parameters invalid/not entered.\n")
                print "FAILED: One or more parameters invalid/not entered."
                return
            if not len(self.window.paramLabelList) == len(self.window.paramDictionary): # Length of both should be the same; meaning all parameters entered (after grabbing last one above)
                self.window.scriptText.insert("insert", "FAILED: One or more parameters invalid/not entered.\n")
                print "FAILED: One or more parameters invalid/not entered."
                return
            
        methodNameOfRun = self.window.methodLabel.cget("text").strip() 
        if methodNameOfRun == "Method Name":
            self.window.scriptText.insert("insert", "Please select a method to run...\n")
            print "Please select a method to run..."
            return
        
        numExeOfRun = self.window.multipleText.get("1.0", "end")
        if not numExeOfRun == "\n":
            try:
                numExeOfRun = int(numExeOfRun)
            except:
                self.window.scriptText.insert("insert", "FAILED: Invalid input in the \'Number Runs\' field...\n")
                print "FAILED: Invalid input in the \'Number Runs\' field..."
                return
        else:
            numExeOfRun = 1
            self.window.multipleText.insert("insert", 1)
        
        self.window.executionCounter += numExeOfRun # Increments number of seconds all commands added so far will take to run
        self.window.executionCounterLabel.config(text = "GUI will pause for "+str(self.window.executionCounter)+" seconds to run command(s).") # Assigns the value in seconds to the label to inform the user
            
        numHzOfRun = self.window.hzValueWidget.get("1.0", "end")    
        if not numHzOfRun == "\n":
            try:
                numHzOfRun = int(numHzOfRun)
            except:
                self.window.scriptText.insert("insert", "FAILED: Invalid input in the \'Hz Value\' field...\n")
                print "FAILED: Invalid input in the \'Hz Value\' field..."
                return
        else:
            numHzOfRun = 1
            self.window.hzValueWidget.insert("insert", 1)
            self.window.numberOfHz = 1 # Have to change the window attribute directly as well for Hz
        
        self.window.listOfHz.append(numHzOfRun)
        self.window.numExecutionsList.append(numExeOfRun)
        self.window.methodNameList.append(methodNameOfRun)
        self.window.runCommandsDictionaryList.append(self.window.paramDictionary)
        
        self.window.paramDictionary = {} # Clear the dictionary so new parameters can be added next run
        
        self.window.orderOfRunListbox.delete(0, "end")
        for x in self.window.methodNameList:
            self.window.orderOfRunListbox.insert("end", x)
            
        if len(self.window.runCommandsDictionaryList) >= 1: # Shows the user when the listBox has at least 1 command in it and can be run
            self.window.runScriptButton.config(bg="green")
        
    def runMultipleScripts(self):
        '''
        Runs the list of dictionaries containing the commands for the
        specified board and prints the data packets.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        if len(self.window.runCommandsDictionaryList) < 1: # Must check - even though add command button's function does - if run is pressed first this will return
            self.window.scriptText.insert("insert", "Please add a command.\n")
            print "Please add a command."
            return
        
        tempDictList = []
        for x in self.window.runCommandsDictionaryList:
            tempDictList.append(x)
        tempNumExeList = []
        for x in self.window.numExecutionsList:
            tempNumExeList.append(x)
        tempMethodList = []
        for x in self.window.methodNameList:
            tempMethodList.append(x)
        tempHzList = []
        for x in self.window.listOfHz:
            tempHzList.append(x)
        tempBoardList = []
        for x in self.window.currentBoardNameList:
            tempBoardList.append(x)
        
        for x in self.window.runCommandsDictionaryList:
            self.window.paramDictionary = {}
            self.window.paramLabelList = []
            self.window.multipleText.delete("1.0", "end")
            self.window.currentBoardName = tempBoardList.pop(0)
            tempSingleDict = tempDictList.pop(0)
            for y in tempSingleDict:
                self.window.paramLabelList.append(y)
            self.window.numberOfHz = tempHzList.pop(0)
            self.window.paramDictionary = tempSingleDict
            self.window.multipleText.insert("insert", tempNumExeList.pop(0))
            self.window.methodLabel.config(text = tempMethodList.pop(0))
            COMScript(self.window).executeBoardScript()
        
        #self.window.paramDictionary = {} # Must clear the dictionary so it is free to take in new commands
        
        self.window.scriptText.insert("insert", " ####### FINISHED EXECUTION #######\n\n")
        self.window.scriptText.see("end")
    
    def executeBoardScript(self):
        '''
        Builds the serial connection and other background items
        needed to run the given boards command.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        def buildScript(cWindowDebug, cBoardName, cComPort, cIsGetter, cMethodName, cNumberOfExecutions, cMethodArguments ):
            '''
            Builds the script specific elements, selecting the board and serial object.
            
            **Parameters**: \n
            * **cWindowDebug** - window.DEBUG.
            * **cBoardName** - Name of the board.
            * **cComPort** - Comm port for the given board.
            * **cIsGetter** - Specifies if the command has response.
            * **cMethodName** - Name of the method to be called.
            * **cNumberOfExecutions** - Number of times to run the command.
            * **cMethodArguments** - Arguments for the given function (if any).
             
            **Returns**: \n
            * **No Return.**\n
            '''
            def setupSerialScript(cDebug, cBoaNam, cComPor, cIsGet, cMetNam):
                '''
                This area specifically sets up serial object.
                
                **Parameters**: \n
                * **cDebug** - window.DEBUG.
                * **cBoaNam** - Name of the board.
                * **cComPor** - Comm port for the given board.
                * **cIsGet** - Specifies if the command has response.
                * **cMetNam** - Name of the method to be called.
                 
                **Returns**: \n
                * **cMethodToCall** - Executable object for given method.
                * **responseThread** - Board.ResponseThread.
                '''
                responseThread = None
                if cBoaNam == "PMUD":
                    ser = serial.Serial(cComPor, 9600)
                    PMUD = pmud.PMUDDataPackets(ser) 
                    cMethodToCall = getattr(PMUD, cMetNam) 
                    if cIsGet: 
                        responseThread = pmud.PMUDResponse(ser, cDebug)
                        responseThread.start() 
                elif cBoaNam == "TCB": 
                    ser = serial.Serial(cComPor, 9600)
                    TCB = tcb.TCBDataPackets(ser)
                    cMethodToCall = getattr(TCB, cMetNam)
                    if cIsGet:
                        responseThread = tcb.TCBResponse(ser, cDebug)
                        responseThread.start()
                elif cBoaNam == "SIB":
                    ser = serial.Serial(cComPor, 9600)
                    SIB = sib.SIBDataPackets(ser)
                    cMethodToCall = getattr(SIB, cMetNam)
                    if cIsGet:
                        responseThread = sib.SIBResponse(ser, cDebug)
                        responseThread.start()
                elif cBoaNam == "DIB":
                    ser = serial.Serial(cComPor, 9600)
                    DIB = dib.DIBDataPackets(ser)
                    cMethodToCall = getattr(DIB, cMetNam)
                    if cIsGet:
                        responseThread = dib.DIBResponse(ser, cDebug)
                        responseThread.start()
                elif cBoaNam == "HYDRAS":
                    ser = serial.Serial(cComPor, 115200)
                    HYDRAS = hydras.HydrasDataPackets(ser)
                    cMethodToCall = getattr(HYDRAS, cMetNam)
                    if cIsGet:
                        responseThread = hydras.HydrasResponse(ser, cDebug)
                        responseThread.start()
                elif cBoaNam == "WCB": 
                    ser = serial.Serial(cComPor, 9600)
                    WCB = wcb.WCBDataPackets(ser)
                    cMethodToCall = getattr(WCB, cMetNam) 
                    if cIsGet:
                        responseThread = hydras.HydrasResponse(ser, cDebug)
                        responseThread.start()
                return cMethodToCall, responseThread
            
            debug = [] # First line of buildScript()
            if cIsGetter: 
                debug.append(cWindowDebug)
            
            try:
                methodToCall, repThr = setupSerialScript(debug, cBoardName, cComPort, cIsGetter, cMethodName)
            except serial.SerialException:
                time.sleep(0.3)
                methodToCall, repThr = setupSerialScript(debug, cBoardName, cComPort, cIsGetter, cMethodName)
            
            def runHzLoop(): 
                sTimeStart = time.time()
                methodToCall(*cMethodArguments)
                self.window.sTime += time.time() - sTimeStart
                rTimeStart = time.time()
                if cIsGetter: 
                    if not repThr == None:
                        while not len(repThr.getList):
                            pass
                        self.window.listOfDataPackets.append(repThr.getList.pop())
                self.window.rTime += time.time() - rTimeStart
                
            def startHzLoop(startTimeOfLoop, increment):
                while(True):
                    currentTimeOfLoop = time.time() - startTimeOfLoop
                    if currentTimeOfLoop >= increment * (1.0/self.window.numberOfHz):
                        runHzLoop()
                        return
                    else:
                        pass            
            
            sTime = 0.0
            rTime = 0.0
            listOfDataPackets = []
            
            setattr(self.window, "sTime", sTime)
            setattr(self.window, "rTime", rTime)
            setattr(self.window, "listOfDataPackets", listOfDataPackets)
            
            timeBeforeEntireLoop = time.time()
            
            if self.window.speedRun == True: # No time restriction, run commands at max speed.
                try:
                    for x in range(self.window.numberOfHz*cNumberOfExecutions):
                        runHzLoop()
                except serial.SerialException:
                    self.window.scriptText.insert("insert", "\n***SERIAL EXCEPTION; Press clear and try with less Hz.\n")
                    return
                timeAfterEntireLoop = time.time() - timeBeforeEntireLoop
            else: # Time each command run based on the # of Hz
                try:
                    for x in range(self.window.numberOfHz*cNumberOfExecutions): # Run it number of times per second (Hz) times number of runs (window.multipleText)
                        startHzLoop(timeBeforeEntireLoop, x)
                except serial.SerialException:
                    self.window.scriptText.insert("insert", "\n***SERIAL EXCEPTION; Press clear and try with less Hz.\n")
                    return
                timeAfterEntireLoop = time.time() - timeBeforeEntireLoop
                if timeAfterEntireLoop < cNumberOfExecutions:
                    time.sleep(cNumberOfExecutions-timeAfterEntireLoop)
                    timeAfterEntireLoop = time.time() - timeBeforeEntireLoop
            for x in self.window.listOfDataPackets:
                self.window.scriptText.insert("insert", x); self.window.scriptText.insert("insert", "\n")
            if cIsGetter:
                repThr.killThread()
                if self.window.speedRun == False:
                    self.window.scriptText.insert("insert", "--- PER SEC: %s command(s). ---\n" % (self.window.numberOfHz))
                self.window.scriptText.insert("insert", "--- EXPECTED TIME: %.7s second(s). ---\n" % (cNumberOfExecutions*1.0))
                self.window.scriptText.insert("insert", "--- TOTAL CMDS: %s command(s). ---\n" % (cNumberOfExecutions*self.window.numberOfHz))
                self.window.scriptText.insert("insert", "--- TOTAL TIME: %.7s second(s). ---\n" % (timeAfterEntireLoop))
                self.window.scriptText.insert("insert", "--- RECV TIME: %.7s second(s). ---\n" % (self.window.rTime))
                self.window.scriptText.insert("insert", "--- SEND TIME: %.7s second(s). ---\n" % (self.window.sTime))
                if timeAfterEntireLoop-self.window.rTime-self.window.sTime >= 0.1 or cNumberOfExecutions-self.window.rTime-self.window.sTime >= 0.1:
                    extraTime = timeAfterEntireLoop-self.window.rTime-self.window.sTime
                    if extraTime < 0:
                        extraTime *= -1
                    if timeAfterEntireLoop-self.window.rTime-self.window.sTime != 0.0:
                        self.window.scriptText.insert("insert", "--- EXTRA TIME: %.7s second(s). ---\n--- NOTES: Commands can run faster. ---\n" % (extraTime))
                else:
                    self.window.scriptText.insert("insert", "--- NOTES: Commands are running close to/at max Hz.\n")
                differenceOfTime = cNumberOfExecutions-timeAfterEntireLoop
                if cNumberOfExecutions-timeAfterEntireLoop >= 0.1 or cNumberOfExecutions-timeAfterEntireLoop <= -0.1 and self.window.speedRun == False:
                    if differenceOfTime < 0:
                        differenceOfTime *= -1 # Gives absolute value before printing
                    self.window.scriptText.insert("insert", "--- Expected-Actual Time Difference: %.7s second(s). ---\n" % (differenceOfTime))
                self.window.scriptText.insert("insert", "\n")
                self.window.scriptText.see(Tkinter.END)
            else:
                self.window.scriptText.insert("insert", "Setter commands do not have data packets to print.\n")
                if self.window.speedRun == False:
                    self.window.scriptText.insert("insert", "--- PER SEC: %s command(s). ---\n" % (self.window.numberOfHz))
                self.window.scriptText.insert("insert", "--- EXPECTED TIME: %.7s second(s). ---\n" % (cNumberOfExecutions*1.0))
                self.window.scriptText.insert("insert", "--- TOTAL CMDS: %s command(s). ---\n" % (cNumberOfExecutions*self.window.numberOfHz))
                self.window.scriptText.insert("insert", "--- TOTAL TIME: %.7s second(s). ---\n" % (timeAfterEntireLoop))
                self.window.scriptText.insert("insert", "--- RECV TIME: %.7s second(s). ---\n" % (self.window.rTime))
                self.window.scriptText.insert("insert", "--- SEND TIME: %.7s second(s). ---\n" % (self.window.sTime))
                if timeAfterEntireLoop-self.window.rTime-self.window.sTime >= 0.1 or cNumberOfExecutions-self.window.rTime-self.window.sTime >= 0.1: 
                    extraTime = timeAfterEntireLoop-self.window.rTime-self.window.sTime
                    if extraTime < 0:
                        extraTime *= -1
                    if timeAfterEntireLoop-self.window.rTime-self.window.sTime != 0.0:
                        self.window.scriptText.insert("insert", "--- EXTRA TIME: %.7s second(s). ---\n--- NOTES: Commands can run faster. ---\n" % (extraTime))
                else:
                    self.window.scriptText.insert("insert", "--- NOTES: Commands are running close to/at max Hz.\n")
                differenceOfTime = cNumberOfExecutions-timeAfterEntireLoop
                if cNumberOfExecutions-timeAfterEntireLoop >= 0.1 or cNumberOfExecutions-timeAfterEntireLoop <= -0.1 and self.window.speedRun == False:
                    if differenceOfTime < 0:
                        differenceOfTime *= -1 # Gives absolute value before printing
                    self.window.scriptText.insert("insert", "--- Expected-Actual Time Difference: %.7s second(s). ---\n" % (differenceOfTime))
                self.window.scriptText.insert("insert", "\n")
                self.window.scriptText.see(Tkinter.END)
            defaultWindowColor = self.window["bg"] # "Disarm" the run command button after commands have been run; it is re-enabled if 1 more command is added to the dictionary
            self.window.runScriptButton.config(bg=defaultWindowColor)
            return # End of runScript()
            
                        
        if self.window.deleteScriptText == True: # First line of runScript(); deletes the text in scriptOut on first run
            self.window.deleteScriptText = False
            self.window.scriptText.delete("1.0", "end")
        
        methodName = self.window.methodLabel.cget("text").strip()
        
        currentBoardName = self.window.currentBoardName
        currentComPort = self.window.comPortList[currentBoardName]
    
        if currentBoardName == "TCB1" or currentBoardName == "TCB2": # Converts board name to name usable for calling its functions
            currentBoardName = "TCB"
        elif currentBoardName == "Sparton" or currentBoardName == "Sparton6E":
            currentBoardName = "SpartonAhrs"
        
        numberOfExecutions = self.window.multipleText.get("1.0", "end")
        
        if not numberOfExecutions == "\n":
            try:
                numberOfExecutions = int(numberOfExecutions)
            except:
                self.window.scriptText.insert("insert", "FAILED: Invalid input in the \'Number Runs\' field...\n")
                print "FAILED: Invalid input in the \'Number Runs\' field..."
                return
        else:
            numberOfExecutions = 1
            
        if self.window.numberOfHz == 0: # Run at least once per second even if user entered 0
                self.window.numberOfHz = 1
                self.window.hzValueWidget.delete("1.0", "end"); self.window.hzValueWidget.insert("insert", 1)
        
        if numberOfExecutions == 0: # Run at least once even if user entered 0
            numberOfExecutions = 1
            self.window.multipleText.delete("1.0", "end"); self.window.multipleText.insert("insert", 1)
        
        if "get" in methodName:
            isGetter = True
        else:
            isGetter = False
        
        methodArguments = []
        
        try:
            for x in self.window.paramLabelList:
                methodArguments.append(int(self.window.paramDictionary[x]))
        except:
            pass
        
        buildScript(self.window.DEBUG, currentBoardName, currentComPort, isGetter, methodName, numberOfExecutions, methodArguments) # Last line of runScript()
    
    def clearCOMScript(self):
        '''
        Clears the tab3 window script-related attributes to start from fresh state.
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window.scriptText.delete("1.0", "end") 
        self.window.multipleText.delete("1.0", "end")
        self.window.paramValueText.delete("1.0", "end")
        self.window.paramDictionary = {}
        self.window.orderOfRunListbox.delete(0, "end")
        self.window.currentBoardName = ""
        self.window.currentBoardNameList = []
        self.window.runCommandsDictionaryList = []
        self.window.numExecutionsList = []
        self.window.methodNameList = []
        self.window.hzValueWidget.delete("1.0", "end"); self.window.numberOfHz = 0; self.window.listOfHz = []
        self.window.executionCounterLabel.config(text = "GUI will pause for 0 seconds to run command(s)."); self.window.executionCounter = 0    
        
class UpdateBoard:
    '''
    This class detects connected boards and updates commands available on the Comms Tab.
    '''
    def __init__(self, window):
        '''
        Initializes log file and sets window as instance attribute.
        
        **Parameters**: \n
        * **window** - Main Tkinter window..
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.log = previous_state_logging_system.Log('_Saved_Settings_/_Device_ID_/_Board_Command_List_.txt')
        self.window = window  
                                  
    def update(self):
        '''
        Upadtes the methods in the listbox to match the selected board.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        board = self.window.boardValue.get()
        self.window.commandListBox.delete(0, "end")

        optionList = []
        if board == "Sparton" or board == "Sparton6E":
            for name, obj in inspect.getmembers(sparton.SpartonAhrsDataPacket):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])

        if board == "TCB1" or board == "TCB2":
            for name, obj in inspect.getmembers(tcb.TCBDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])

        if board == "SIB":
            for name, obj in inspect.getmembers(sib.SIBDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
                        
        if board == "PMUD":
            for name, obj in inspect.getmembers(pmud.PMUDDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
        
        if board == "DIB":
            for name, obj in inspect.getmembers(dib.DIBDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
                        
        if board == "HYDRAS":
            for name, obj in inspect.getmembers(hydras.HydrasDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
                        
        if board == "WCB":
            for name, obj in inspect.getmembers(wcb.WCBDataPackets):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
                        
        if board == "MOVEMENT":
            for name, obj in inspect.getmembers(movement.MovementController):
                if inspect.ismethod(obj):
                    if not (name.startswith("__")):
                        optionList.append([name, obj])
                        
        self.window.optionList = optionList
        for option in optionList:
            self.window.commandListBox.insert("end", option[0])
        
    def onselect(self, event):
        '''
        Puts method documentation on Comms output console when method is selected and updates the parameter values
        entered by the user.
        
        **Parameters**: \n
        * **event** - Event when selected command changes.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        param_value = self.window.param_value 
        paramValueText = self.window.paramValueText 
        paramLabel = self.window.paramLabelWidget 
        paramOptionMenu = self.window.paramOptionMenu 
        
        paramValueText.delete("1.0", "end") 
        
        self.window.paramDictionary = {}
        self.window.paramLabelList = []
        paramDict = self.window.paramDictionary
        paramLabelList = self.window.paramLabelList
        
        def updateScriptOut(commandToDocument): # Updates the scriptOut text with the selected commands documentation on tab3
            self.window.scriptOut.delete("1.0", "end")
            try:
                self.window.scriptOut.insert("insert", commandToDocument.__doc__)
            except:
                return
        
        def changeParamLabels(): # Updates the window variable paramLabelList with the names of parameters
            w = self.window.commandListBox
            self.window.methodLabel.config(text = ""+w.get(w.curselection()[0]))
            for name, command in self.window.optionList:
                if self.window.methodLabel.cget("text").strip() == name:
                    updateScriptOut(command)
                    new_args = inspect.getargspec(command)
                    for i, parameter in enumerate(new_args[0]):
                        if not parameter == "self":
                            paramLabelList.append(parameter)
        
        def updateParamOptionMenu():
            if len(paramLabelList) > 0:
                paramValueText.grid()
                paramLabel.grid()
                paramOptionMenu.grid()
                paramOptionMenu["menu"].delete(0, "end")
                for paramName in paramLabelList:
                    paramOptionMenu["menu"].add_command(label = paramName, command = lambda value = paramName: updateParamDictionary(value, paramValueText.get("1.0", "end")))
                param_value.set(paramLabelList[0])
            else:
                paramValueText.grid_remove()
                paramLabel.grid_remove()
                paramOptionMenu.grid_remove()
                paramOptionMenu["menu"].delete(0, "end")
        
        changeParamLabels() # Updates parameters labels from given command selected
        
        updateParamOptionMenu()
                           
        def updateParamDictionary(pName, pValue): # Stores parameter label and values in the dictionary which will be used in Comfinder.runScript() 
            if not pValue == "\n":
                paramDict[param_value.get()] = int(pValue)
            else:
                pass
            param_value.set(pName)
            paramValueText.delete("1.0", "end")
            try:
                paramValueText.insert("insert", paramDict[pName])
            except:
                pass
            
        
if __name__ == '__main__':
    pass
        