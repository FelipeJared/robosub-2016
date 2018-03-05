'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: _launch_gui_
   :synopsis: Creates Graphic User Interface (GUI) widgets.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Asst_Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Nov 8, 2014
:Description: This module creates and places widgets on a window to create the Graphic User Interface (GUI). If a widget needs to be created, this is usually the place to do it. 
'''

import psutil, os, sys#; psutil.Process(os.getpid()).set_nice(psutil.REALTIME_PRIORITY_CLASS) #Setting this process to real time for CPU
import multiprocessing
import Tkinter, ttk 
#import gui_components.roboarm.roboarm_controller as roboarmController
#import gui_components.roboarm.callback_functions as roboarmCF
import gui_components.event_handlers as event_handlers
import gui_components.update_gui as update_gui
import external_devices._navigation_management_system_ as _navigation_management_system_
import gui_components.mission_selector_system as mission_selector_system
import ctypes
import gui_components.previous_state_logging_system as previous_state_logging_system
from serial.tools import list_ports as lp
import gui_components.COMfinder as COMfinder
import main.gui_components.control_systems_tab as control_systems_tab
import main.gui_components.waypointManagement.waypointManagementModule as waypointManagement
import time 
import main.gui_components.data_graphing as graphing

DEBUG = True


screenRes = ctypes.windll.user32.GetSystemMetrics(0)-10, ctypes.windll.user32.GetSystemMetrics(1)-30
guiWidth, guiHeight, guiXPosition, guiYPosition = screenRes[0], screenRes[1], 0, 0
rawImgWidth, rawImgHeight = int(screenRes[0]/2.5), int(screenRes[1]/2)
processedImgWidth, processedImgHeight = int(screenRes[0]/3.4), int(screenRes[1]/3.45)
process = None; parent_conn = None #Variables for multiprocessing



window = Tkinter.Tk()

setattr(window, "DEBUG", DEBUG)
setattr(window, "screenRes", screenRes)

#Setting window object for tab packages
#roboarmController.setWindowObject(window)

eventHandlers = event_handlers.EventHandlers(guiWidth, rawImgWidth)

NMS = _navigation_management_system_.NavigationManagementSystem()

GUI = None #Initializing GUI

class StartVehicle:
    '''
    This class configures the Start and Stop buttons to set the sub on its autonmous missions, as well as DVL reset.
    '''
    def __init__(self, notebook, missionSelectorButtonList):
        '''
        Initializes the notebook and button list that were passed in
        
        **Parameters**: \n
        * **notebook** - Background where the buttons will be put.
        * **missionSelectorButtonList** - List containing the Start and Stop buttons.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.notebook = notebook
        self.missionSelectorButtonList = missionSelectorButtonList
          
    def start(self, startButton, stopButton):
        '''
        Starts the sub on its missions, disables the Start button, and enables the Stop button.
        
        **Parameters**: \n
        * **startButton** - Button which starts sub.
        * **stopButton** - Button which stops sub.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Disables Vehicle Tests tab
        self.notebook.tab(2, state = "disable") #2 indicates the tab index
        
        #Disable Up, Down, Add, Delete, and Load buttons
        for x in range(len(self.missionSelectorButtonList)):
            self.missionSelectorButtonList[x].config(state = "disable")
        
        #Disable start mission button
        startButton.config(state = "disable")
        
        #Enable abort mission button
        stopButton.config(state = "normal")
        
        window.sendMissionSelectorData = True
        window.startVehicle = True
    
    def stop(self, startButton, stopButton):
        '''
        Stops the sub, disables the Stop button, and enables the Start button.
        
        **Parameters**: \n
        * **startButton** - Button which starts sub.
        * **stopButton** - Button which stops sub.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Enable Vehicle Tests tab
        self.notebook.tab(2, state = "normal") #2 indicates the tab index
        
        #Enable Up, Down, Add, Delete, and Load buttons
        for x in range(len(self.missionSelectorButtonList)):
            self.missionSelectorButtonList[x].config(state = "normal")
        
        #Enable start mission button
        startButton.config(state = "normal")
        
        #Disable abort mission button
        stopButton.config(state = "disable")
        
        window.sendMissionSelectorData = False
        window.startVehicle = False
        
    def reset(self):
        '''
        Sends a command to the DVL to reset the origin at sub's current location.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Set DVL back to starting configuration
        window.resetDVL = True
     
class StartManual():
    '''
    This class handles Manual Control
    '''
    def __init__(self, window, tab, notebook, missionSelectorButtonList):
        '''
        Sends a command to the DVL to reset the origin at sub's current location.
        
        **Parameters**: \n
        * **window** - Main TKinter window.
        * **tab** - Tab in which Manual Control is set up.
        * **notebook** - Widget which contains the various tabs.
        * **missionSelectorButtonList** - List which contains the Manual start and stop buttons.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
        self.notebook = notebook
        self.missionSelectorButtonList = missionSelectorButtonList
        self.tab = tab
        self.controllerScreen = window.controllerScreen
        #self.control = ci.controller()
        
    def __controllerSetup__(self):
        '''
        Configures the manual feedback screen and starts Manual index at 0. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.controllerScreen.place(relx = 0.25, rely = 0, relwidth = 0.5, relheight = 1)
        self.window.setToManual = 0
        #self.control.run(self.controllerScreen, self.window)
        
    def start(self, manualButton, stopButton):
        '''
        Starts Manual Control, disables the start button, enables the stop button, sets up Manual screen, and increases Manual index.
        
        **Parameters**: \n
        * **manualButton** - Button which starts Manual Control.
        * **stopButton** - Button which stops Manual Control.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Disables Vehicle Tests tab
        self.notebook.tab(2, state = "disable") #2 indicates the tab index
        
        #Disable Up, Down, Add, Delete, and Load buttons
        for x in range(len(self.missionSelectorButtonList)):
            self.missionSelectorButtonList[x].config(state = "disable")
            
        #Enable controller select buttons
        stopButton.config(state = "normal")
        
        #Disable manual control button
        manualButton.config(state = "disable")
        
        #Joystick state to pass to external process
        self.window.manualModeEnabled = True
        
        #Setup controller screen
        self.__controllerSetup__()
        
    def stop(self, manualButton, stopButton):
        '''
        Stops Manual Control, disables the stop button, enables the start button, erases Manual screen, and increases Manual index.
        
        **Parameters**: \n
        * **manualButton** - Button which starts Manual Control.
        * **stopButton** - Button which stops Manual Control.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Enable Vehicle Tests tab
        self.notebook.tab(2, state = "normal") #2 indicates the tab index
        
        #Enable Up, Down, Add, Delete, and Load buttons
        for x in range(len(self.missionSelectorButtonList)):
            self.missionSelectorButtonList[x].config(state = "normal")
        
        #Enable manual control button
        manualButton.config(state = "normal")
        
        #Disable abort mission button
        stopButton.config(state = "disable")
        
        #Stop the controller
        self.window.setToManual = 2
        
        #Joystick state to pass to external process
        self.window.manualModeEnabled = False
                
        #Remove controller screen
        self.controllerScreen.place_forget()
        
class UpdateMenu():
    '''
    This class updates the available commands on the Comms Tab according to the selected board.
    '''
    def __init__(self, window):
        '''
        Initializes window as instance attribute.
        
        **Parameters**: \n
        * **window** - Main TKinter window.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
    def board_change(self, board):
        '''
        Updates a window attribute to selected board and updates methods available in the listbox based on the updated board.
        
        **Parameters**: \n
        * **board** - String containing the board selected by the user.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window.boardValue.set(board)
        COMfinder.UpdateBoard(self.window).update()

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

class clear:
    '''
    This class clears the GUI console.
    '''
    def __init__(self, consolText):
        '''
        Clears the GUI console.
        
        **Parameters**: \n
        * **consolText** - Strings contained in GUI console.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.text = consolText.delete("1.0", "end") #get text from line 1, character 0
        
class export: #This is to export the console text to a file
    '''
    This class can export the console text to a file.
    '''
    def __init__(self, consolText):
        '''
        Collects GUI console output to be saved to a file.
        
        **Parameters**: \n
        * **consolText** - Strings contained in GUI console.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("220x30+690+250")
        self.text = consolText.get("1.0", "end") #get text from line 1, character 0
        if not os.path.exists('_Console_Logs_'):
            os.mkdir('_Console_Logs_')
        
        self.userInput = 0
        
        self.writeToFile()
        
    def writeToFile(self):
        '''
        Creates a pop-up for user to write the file name.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.userInput = Tkinter.Entry(self.top)
        self.userInput.grid(row=0, column=1)
        self.userInput.focus_set()

        popUp = Tkinter.Label(self.top, text = "File name:")
        popUp.grid(row=0, column=0)
        self.userInput.bind("<Return>", self.ok)
        
        button = Tkinter.Button(self.top, text="OK", command = self.ok)
        button.grid(row=0, column=3, columnspan=2)

    def ok(self, *event):
        '''
        Creates text file and writes GUI console output to it.
        
        **Parameters**: \n
        * **event** - Widget action of button being pressed, which activates this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        f = open('_Console_Logs_/'+self.userInput.get(), 'a')
        f.write(self.text)
        f.close()  
        self.top.destroy()
 
 
setWaypointToggle = False 
removeWaypointToggle = False    
class createWaypoint():
    '''
    Creates a popup to name a new waypoint and save it.
    '''
    def __init__(self, dvlPosition, orientation, depth):
        '''
        Initializes logging data and creates a new window.
        
        **Parameters**: \n
        * **dvlPosition** - NESW coordinates based on DVL origin point.
        * **orientation** - AHRS orientation data (yaw, pitch, roll).
        * **depth** - Depth data from the pressure transducers.

        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("220x30+690+250")
        self.dvlPosition = dvlPosition
        self.orientation = orientation
        self.depth = depth
        if not os.path.exists('_Saved_Missions_'):
            os.mkdir('_Saved_Missions_')
        self.missionSelectorData = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()))
            
        self.writeToFile()
            
    def writeToFile(self):
        '''
        Creates a label for user to write the file name.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.userInput = Tkinter.Entry(self.top)
        self.userInput.grid(row=0, column=1)
        self.userInput.focus_set()

        popUp = Tkinter.Label(self.top, text = "Waypoint Name:")
        popUp.grid(row=0, column=0)
        self.userInput.bind("<Return>", self.ok)
        self.userInput.bind("<Escape>", self.exit)
        self.top.protocol("WM_DELETE_WINDOW", self.exit)
        
        button = Tkinter.Button(self.top, text="OK", command = self.ok)
        button.grid(row=0, column=3, columnspan=2)

    def ok(self, *event):
        '''
        Creates text file and writes GUI console output to it.
        
        **Parameters**: \n
        * **event** - Widget action of button being pressed, which activates this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global setWaypointToggle #Need as global so it can be changed by the updateGUI function
        #waypoints={'bb': [[0, 0, 0, 0], [102.568359375, 5.9765625, 117.2021484375], -29.47]}
        userInputString = self.userInput.get()
        
        waypointsDictionary = self.missionSelectorData.getParameters("waypoints").waypoints #Returns 0 if "waypoints" not in list
        
        if waypointsDictionary != 0 and waypointsDictionary !=None: #If "waypoints" is in the list
            waypointsDictionary[userInputString] = [self.dvlPosition, self.orientation, self.depth] #Append on to it
        else: #Otherwise, start a new one
            waypointsDictionary = {userInputString: [self.dvlPosition, self.orientation, self.depth]}
            
        self.missionSelectorData.writeParameters(waypoints = waypointsDictionary) #Storing dictionary inside another dictionary "waypoints" 
        setWaypointToggle = False
        self.top.destroy()
        
    def exit(self, *event):
        '''
        Destroys popup and sets Waypoint Toggle to False.
        
        **Parameters**: \n
        * **event** - Widget action of button being pressed, which can activate this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global setWaypointToggle #Need as global so it can be changed by the updateGUI function
        self.top.destroy()
        #roboarmCF.closeWindow()
        setWaypointToggle = False
 
class removeWaypoint():
    '''
    Creates a popup to view saved waypoints and give options to copy or delete them.
    '''
    def __init__(self, *args):
        '''
        Creates popup displaying the saved waypoints and the remove/copy buttons.
        
        **Parameters**: \n
        * **args** - Depth data from the pressure transducers.

        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("238x450+815+150")
        self.top.title("Waypoint List")
        if not os.path.exists('_Saved_Missions_'):
            os.mkdir('_Saved_Missions_')
        self.missionSelectorData = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()))
        self.wayBar = Tkinter.Scrollbar(self.top)
        self.wayBar.grid(row = 0, column = 2, rowspan = 1, sticky='ns')
        self.waypointListBox = Tkinter.Listbox(self.top, yscrollcommand=self.wayBar.set, width = int(screenRes[0]/53), height = int(screenRes[1]/40))
        self.waypointListBox.grid(row = 0, column = 0, columnspan = 2)
        self.wayBar.config(command=self.waypointListBox.yview)
        
        self.waypointsDictionary = self.missionSelectorData.getParameters("waypoints").waypoints #Returns 0 if "waypoints" not in list
        if self.waypointsDictionary != 0 and self.waypointsDictionary !=None: #If "waypoints" is in the list
            for mission, params in self.waypointsDictionary.items():
                self.waypointListBox.insert("end", mission)
        removeButton = Tkinter.Button(self.top, text = "Remove Waypoint", command = self.remove)
        removeButton.grid(row = 1, column = 0) 
        copyButton = Tkinter.Button(self.top, text = "Copy Waypoint", command = self.copyName)
        copyButton.grid(row = 1, column = 1)
        
        self.missions = []
        self.waypointListBox.focus_set()
        self.waypointListBox.bind("<Escape>", self.exit)
        self.waypointListBox.bind("<Double-Button-1>", self.modify)
        self.top.protocol("WM_DELETE_WINDOW", self.exit)
        self.waypointListBox.select_set(0)
        
    def remove(self):
        '''
        Removes selected waypoint from the waypoint list and updates the list.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''
        if len(self.waypointListBox.curselection()) == 1:
            missionPoint = self.waypointListBox.get(self.waypointListBox.curselection()[0])
            with open('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()), "r") as f:
                lines = f.readlines()
                f.seek(0)
            
            for key1, value1 in self.waypointsDictionary.items():
                if key1 == missionPoint:
                    del self.waypointsDictionary[key1]
            self.missionSelectorData.writeParameters(waypoints = self.waypointsDictionary) #Storing dictionary inside another dictionary "waypoints"
            item = int(self.waypointListBox.curselection()[0])
            self.waypointListBox.delete(item, item)
            self.waypointListBox.select_set(item)
    
    def copyName(self):
        '''
        Creates the popup for the user to input the name for the copied waypoint.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.bottom = Tkinter.Toplevel(window)
        self.bottom.geometry("220x30+690+250")
        self.userInput = Tkinter.Entry(self.bottom)
        self.userInput.grid(row=0, column=1)
        self.userInput.focus_set()

        popUp = Tkinter.Label(self.bottom, text = "Copy's Waypoint Name:")
        popUp.grid(row=0, column=0)
        self.userInput.bind("<Return>", self.copy)
        self.userInput.bind("<Escape>", self.exitBottom)
        self.bottom.protocol("WM_DELETE_WINDOW", self.exitBottom)

           
    def copy(self, *event):
        '''
        Creates a copy of the selected waypoint with the input name.
        
        **Parameters**: \n
        * **event** - Clicking the OK button or pressing enter to activate this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        missionPoint = self.waypointListBox.get(self.waypointListBox.curselection()[0])
        with open('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()), "r") as f:
            lines = f.readlines()
            f.seek(0)
        
        userInputString = self.userInput.get()
        for key1, value1 in self.waypointsDictionary.items():
            if key1 == missionPoint:
                self.waypointsDictionary[userInputString] = value1
        self.missionSelectorData.writeParameters(waypoints = self.waypointsDictionary) #Storing dictionary inside another dictionary "waypoints"
        self.waypointListBox.insert(0, userInputString)
        self.bottom.destroy()
        
    def modify(self, *event):
        '''
        Creates a popup with an entry for each parameter in the selected waypoint for the user to modify.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''   
        self.bottom = Tkinter.Toplevel(window)
        self.bottom.geometry("1020x80+190+250")
        missionPoint = self.waypointListBox.get(self.waypointListBox.curselection()[0])
        self.bottom.title(missionPoint)
        with open('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()), "r") as f:
            lines = f.readlines()
            f.seek(0)
        self.wayValues = 0
        for key2, value2 in self.waypointsDictionary.items():
            if key2 == missionPoint:
                self.wayValues = value2
                
        changeButton = Tkinter.Button(self.bottom, text = "Change", command = lambda: self.finish(missionPoint))
        changeButton.grid(row = 2, column = 4)
        north, east, up, positionError, yaw, pitch, roll, depth = Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(), Tkinter.IntVar(),
        n, e, u, pE, y, p, r, d = self.wayValues[0][0], self.wayValues[0][1], self.wayValues[0][2], self.wayValues[0][3], self.wayValues[1][0], self.wayValues[1][1], self.wayValues[1][2], self.wayValues[2]
        
        northLabel = Tkinter.Label(self.bottom, text = "North")
        northLabel.grid(row = 0, column = 0)   
        self.northEntry = Tkinter.Entry(self.bottom)
        self.northEntry.insert(0, float(n))
        self.northEntry.grid(row = 1, column = 0)
        self.northEntry.bind("<Escape>", self.exitBottom)
        
        eastLabel = Tkinter.Label(self.bottom, text = "East") 
        eastLabel.grid(row = 0, column = 1)  
        self.eastEntry = Tkinter.Entry(self.bottom)
        self.eastEntry.insert(0, float(e))
        self.eastEntry.grid(row = 1, column = 1)
        self.eastEntry.bind("<Escape>", self.exitBottom)
        
        upLabel = Tkinter.Label(self.bottom, text = "Up")
        upLabel.grid(row = 0, column = 2)   
        self.upEntry = Tkinter.Entry(self.bottom)
        self.upEntry.insert(0, float(u))
        self.upEntry.grid(row = 1, column = 2)
        self.upEntry.bind("<Escape>", self.exitBottom)
        
        positionLabel = Tkinter.Label(self.bottom, text = "Position Error")
        positionLabel.grid(row = 0, column = 3)   
        self.positionEntry = Tkinter.Entry(self.bottom)
        self.positionEntry.insert(0, float(pE))
        self.positionEntry.grid(row = 1, column = 3)
        self.positionEntry.bind("<Escape>", self.exitBottom)
        
        yawLabel = Tkinter.Label(self.bottom, text = "Yaw")
        yawLabel.grid(row = 0, column = 4)   
        self.yawEntry = Tkinter.Entry(self.bottom)
        self.yawEntry.insert(0, float(y))
        self.yawEntry.grid(row = 1, column = 4)
        self.yawEntry.bind("<Escape>", self.exitBottom)
        
        pitchLabel = Tkinter.Label(self.bottom, text = "Pitch")
        pitchLabel.grid(row = 0, column = 5)   
        self.pitchEntry = Tkinter.Entry(self.bottom)
        self.pitchEntry.insert(0, float(p))
        self.pitchEntry.grid(row = 1, column = 5)
        self.pitchEntry.bind("<Escape>", self.exitBottom)
        
        rollLabel = Tkinter.Label(self.bottom, text = "Roll") 
        rollLabel.grid(row = 0, column = 6)  
        self.rollEntry = Tkinter.Entry(self.bottom)
        self.rollEntry.insert(0, float(r))
        self.rollEntry.grid(row = 1, column = 6)  
        self.rollEntry.bind("<Escape>", self.exitBottom)
        
        depthLabel = Tkinter.Label(self.bottom, text = "Depth") 
        depthLabel.grid(row = 0, column = 7)  
        self.depthEntry = Tkinter.Entry(self.bottom)
        self.depthEntry.insert(0, float(d))
        self.depthEntry.grid(row = 1, column = 7)  
        self.depthEntry.bind("<Escape>", self.exitBottom)
        
        self.northEntry.focus_set()
        
        self.bottom.protocol("WM_DELETE_WINDOW", self.exitBottom)
        
    def finish(self, missionPoint):
        '''
        Stores the modified waypoint data into the waypoint list.
        
        **Parameters**: \n
        * **missionPoint** - String of the selected waypoint.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        for key3, value3 in self.waypointsDictionary.items():
            if key3 == missionPoint:
                self.waypointsDictionary[missionPoint][0] = [float(self.northEntry.get()), float(self.eastEntry.get()), float(self.upEntry.get()), float(self.positionEntry.get())]
                self.waypointsDictionary[missionPoint][1] = [float(self.yawEntry.get()), float(self.pitchEntry.get()), float(self.rollEntry.get())]
                self.waypointsDictionary[missionPoint][2] = float(self.depthEntry.get())
        self.missionSelectorData.writeParameters(waypoints = self.waypointsDictionary) #Storing dictionary inside another dictionary "waypoints"
        self.exitBottom()
        
    def exit(self, *event):
        '''
        Destroys the waypoint display popup on exit.
        
        **Parameters**: \n
        * **event* - TKinter widget action activating this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global removeWaypointToggle #Need as global so it can be changed by the updateGUI function
        self.top.destroy()
        removeWaypointToggle = False 
        
    def exitBottom(self, *event):
        '''
        Destroys the appropiate popup on exit.
        
        **Parameters**: \n
        * **event** - TKinter widget action activating this method.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.bottom.destroy()       

class GuiCreation:
    def __init__(self):
        '''
        Initializes the variables for the process data pipe.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''   
        self.parent_conn = parent_conn
        self.process = process
        
    def setQuitFlag(self):
        '''
        Initializes quitFlag boolean as True.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''   
        window.quitFlag = True
        
    def menuCommands(self, window, *keys):
        '''
        Turns pressing the keyboard keys into TKinter events.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        * **keys** - The keys pressed on the keyboard.
        
        **Returns**: \n
        * **No Return.**\n
        '''   
        window.event_generate("<KeyPress>", keysym = keys[0])
        window.event_generate("<Key>", keysym = keys[1])
        #for key in keys:
        #    window.event_generate("<Key>", keysym = key)
        
    def updateGUI(self, window):
        '''
        Sends and receives data from the internal_navigation_system process through the pipe, updates the GUI accordingly and prevents the GUI from
        getting stuck.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        pidSliderValues = []
        length = len(window.pidScales)
        for i in range(0, length-1):
            pidSliderValues.append(window.pidScales[i].get())        
        
        
           
        global setWaypointToggle, removeWaypointToggle
        if window.quitFlag:
            window.destroy()  #This avoids the update event being in limbo
            if not window.DEBUG:
                mainProcessReadyFlag, turnOffDirtyPower = True, True
                
                self.parent_conn.send([mainProcessReadyFlag, window.startVehicle, turnOffDirtyPower, window.manualModeEnabled, None, None, setWaypointToggle, removeWaypointToggle, window.resetDVL, pidSliderValues])
    
        else:
            missionSelectorData, imageProcValues = GUI.run()
            
            #roboarmController.roboarmControllerUpdate(imageProcValues)
            
            if not window.sendMissionSelectorData: #Dont want to keep sending a bunch of data through the pipe if its not going to change. In the future, I may want to give the user the ability to control the vehicles parameters while it is still in operation, if so, comment out this line and the next
                missionSelectorData = None
            else:
                window.sendMissionSelectorData = False #Makes it so I dont keep sending mission selector data through pipe (only need it once)
                
            if not window.DEBUG:
                mainProcessReadyFlag, turnOffDirtyPower = True, False
                
                self.parent_conn.send([mainProcessReadyFlag, window.startVehicle, turnOffDirtyPower, window.manualModeEnabled, missionSelectorData, imageProcValues, setWaypointToggle, removeWaypointToggle, window.resetDVL, pidSliderValues])
                    
                #if self.parent_conn.poll() == True: #If there is data to receive #WARNING: poll() sometimes skips a few thus making the graphic gauges off sync
                window.externalDevicesData = self.parent_conn.recv() #Instead of checking if there is data in the pipe to get, waiting until there is data allows the graphic gauges to react faster to change, but the rest of the gui might slow down
                   
                #WAYPOINT CREATION 
                if window.externalDevicesData[7] == True and setWaypointToggle == False: #if setWaypoint is true and waypointtoggle is false
                    setWaypointToggle = True
                    dvlPositionData, orientationData, depth = window.externalDevicesData[5][0], window.externalDevicesData[1], window.externalDevicesData[0][2]
                    createWaypoint(dvlPositionData, orientationData, depth)
                    
                #WAYPOINT REMOVAL
                if window.externalDevicesData[8] == True and removeWaypointToggle == False:#if removeWaypoint is true and removewaypoint toggle is false
                    removeWaypointToggle = True
                    removeWaypoint()
                    
                #DVL Reset Toggle
                if window.resetDVL == True:#If a command to reset the DVL was sent, toggle it off
                    window.resetDVL = False
                    
            window.after(0, func=lambda: self.updateGUI(window))
        
    def guiSetup(self):
        '''
        Sets up the camera feeds and all the various tabs and their functions into events activated by buttons, clicks, or keys.
        
        **Parameters**: \n
        * **No Input Parameters* 
        
        **Returns**: \n
        * **No Return.**\n
        '''   
        global GUI
        
        #CREATE GUI OBJECT
        window.geometry(str(guiWidth)+"x"+str(guiHeight)+"+"+str(guiXPosition)+"+"+str(guiYPosition)) #"1590x870+0+0"
        window.title("Mechatronics RoboSub GUI")
        eventHandlers.initilizeGuiEvents(window)
        window.bind("<Key>", eventHandlers.guiKeyboardEvent)
        setattr(window, 'quitFlag', False) #A main Python function that gives functions new attributes/variables
        setattr(window, 'spaceBar', False)
        setattr(window, 'captureImg', [False, False])
        setattr(window, 'recordImg', [False, False])
        setattr(window, 'pictureCount', [0, 0])
        setattr(window, 'recordCount', [0, 0])
        setattr(window, 'secondsPerFrame', [0, 0])
        
        
        #CREATE TOOLBAR
        toolBar = Tkinter.Menu(window)
        window.config(menu=toolBar)
        
        fileMenu = Tkinter.Menu(toolBar)
        fileMenu.add_command(label="Freeze Raw Images                               space", command = lambda: window.event_generate("<Key>", keysym = "space"))
        fileMenu.add_command(label="Capture Front Image                            c", command = lambda: window.event_generate("<Key>", keysym = "c"))
        fileMenu.add_command(label="Capture Bottom Image                        shift+c", command = lambda: window.event_generate("<Key>", keysym = "C"))
        fileMenu.add_command(label="Record Front Image                              r", command = lambda: window.event_generate("<Key>", keysym = "r"))
        fileMenu.add_command(label="Record Bottom Image                          shift+r", command = lambda: window.event_generate("<Key>", keysym = "R"))
        fileMenu.add_command(label="Exit                                                          esc", command = lambda: window.event_generate("<Key>", keycode = 27))
        toolBar.add_cascade(label="Window", menu=fileMenu)
        
        fileMenu = Tkinter.Menu(toolBar)
        fileMenu.add_command(label="Add User             ctrl+a", command = lambda: window.event_generate("<Control-Key>", keysym = "a"))
        fileMenu.add_command(label="Delete User         ctrl+d", command = lambda: window.event_generate("<Control-Key>", keysym = "d"))
        toolBar.add_cascade(label="Users", menu=fileMenu)
        
        fileMenu = Tkinter.Menu(toolBar)
        toolBar.add_cascade(label="Help", menu=fileMenu)

        
        #LABEL FOR FRONT CAMERA
        frontRawImgLabel = Tkinter.Label(window, background = "gray")  #The raw image for the front camera will go here
        frontRawImgLabel.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 0.5) #Can only choose pack, grid, place, or grid & place in one Tk() instance only    
        eventHandlers.initilizeFrontRawImgEvents(frontRawImgLabel)
        frontRawImgLabel.bind("<Button-1>", eventHandlers.frontRawImgMouseEvent)
        frontRawImgLabel.bind("<ButtonRelease-1>", eventHandlers.frontRawImgMouseEvent)
        frontRawImgLabel.bind("<B1-Motion>", eventHandlers.frontRawImgDraw)
        setattr(window, "frontRawImgLabel", frontRawImgLabel)
        setattr(frontRawImgLabel, 'mouseDragLocation', [0, 0])
        setattr(frontRawImgLabel, 'boxPoint1', [0, 0])
        setattr(frontRawImgLabel, 'boxPoint2', [0, 0])
        setattr(frontRawImgLabel, 'buttonPressed', False)
        setattr(frontRawImgLabel, 'buttonReleased', False)
        
        #LABEL FOR BOTTOM CAMERA
        bottomRawImgLabel = Tkinter.Label(window, background = "gray")  #The raw image for the front camera will go here
        bottomRawImgLabel.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 0.5)
        eventHandlers.initilizeBottomRawImgEvents(bottomRawImgLabel)
        bottomRawImgLabel.bind("<Button-1>", eventHandlers.bottomRawImgMouseEvent)
        bottomRawImgLabel.bind("<ButtonRelease-1>", eventHandlers.bottomRawImgMouseEvent)
        bottomRawImgLabel.bind("<B1-Motion>", eventHandlers.bottomRawImgDraw)
        setattr(window, "bottomRawImgLabel", bottomRawImgLabel)
        setattr(bottomRawImgLabel, 'mouseDragLocation', [0, 0])
        setattr(bottomRawImgLabel, 'boxPoint1', [0, 0])
        setattr(bottomRawImgLabel, 'boxPoint2', [0, 0])
        setattr(bottomRawImgLabel, 'buttonPressed', False)
        setattr(bottomRawImgLabel, 'buttonReleased', False)
          
        #CREATING TABS
        notebook = ttk.Notebook(window)
        notebook.place(relx = 0, rely = 0.5, relwidth = 1, relheight = 0.5)
        
        tab1 = Tkinter.Frame(notebook, width=1000, height=200)
        tab1.place()
        notebook.add(tab1, text="Image Processing")
        
        tab2 = Tkinter.Frame(notebook, width=1000, height=200)
        tab2.place()
        notebook.add(tab2, text="Mission Selector")
        
        tab3 = Tkinter.Frame(notebook, width=1000, height=200)
        tab3.place()
        notebook.add(tab3, text="Communication")
        
        tab4 = Tkinter.Frame(notebook, width=1000, height=200)
        tab4.place()
        notebook.add(tab4, text="Console")
        
        tab5 = Tkinter.Frame(notebook, width=1000, height=200)
        tab5.place()
        notebook.add(tab5, text="Graphics Settings")
        
        tab6 = Tkinter.Frame(notebook, width=1000, height=200)
        tab6.place()
        notebook.add(tab6, text="Manual Control")
        
        tab8 = Tkinter.Frame(notebook, width=1000, height=200)
        tab8.place()
        notebook.add(tab8, text="Data Analysis")
        
        window.notebook = notebook
        
        #processed img 1
        filterScales = []
        filterNames = []
        frontProcessedImgFrame = Tkinter.Frame(tab1)
        frontProcessedImgFrame.place(relx = 0.22, rely = 0.52, anchor = "center")
        
        names = ["Min Hue", "Min Saturation", "Min Value", "Max Hue", "Max Saturation", "Max Value", "Erode 1/Dilate 1", "     Intensity 1", "       Epsilon", "  Min Curves", "     Max Curves"]
        for x in range(3):
            filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 0, to = 255, width = 15, orient = "horizontal")) #Creating sliders
            filterScales[x].grid(row = x*2, column = 0)
            filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[x], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[x].grid(row = x*2 + 1, column = 0)
            
        
        
        frontProcessedImgLabel = Tkinter.Label(frontProcessedImgFrame) #The processed image for the front camera will go here
        frontProcessedImgLabel.grid(row = 0, column = 1, rowspan = 6, columnspan = 5)
        setattr(window, "frontProcessedImgLabel", frontProcessedImgLabel)
        
        for x in range(3):
            filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 0, to = 255, width = 15, orient = "horizontal")) #Creating sliders
            filterScales[3+x].grid(row = x*2, column = 6)
            filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[x+3], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[3+x].grid(row = x*2 + 1, column = 6)
            
        filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 0, to = 3, width = 15, length=90)) #Creating sliders
        filterScales[6].grid(row = 7, column = 1)
        filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[6], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[6].grid(row = 8, column = 1)
        
        filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 0, to = 25, width = 15, length=90)) #Creating sliders
        filterScales[7].grid(row = 7, column = 2)
        filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[7], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[7].grid(row = 8, column = 2)
        
        filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 0, to = 100, width = 15, length=90)) #Creating sliders
        filterScales[8].grid(row = 7, column = 3)
        filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[8], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[8].grid(row = 8, column = 3)
        
        filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 3, to = 50, width = 15, length=90)) #Creating sliders
        filterScales[9].grid(row = 7, column = 4)
        filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[9], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[9].grid(row = 8, column = 4)
        
        filterScales.append(Tkinter.Scale(frontProcessedImgFrame, from_ = 3, to = 50, width = 15, length=90)) #Creating sliders
        filterScales[10].grid(row = 7, column = 5)
        filterNames.append(Tkinter.Label(frontProcessedImgFrame, text = names[10], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[10].grid(row = 8, column = 5)
        
        #drop down menu
        dropBoxImageProcessingValue = Tkinter.StringVar(tab1)
        dropBoxImageProcessingValue.set("") # default value
        optionMenu = Tkinter.OptionMenu(tab1, dropBoxImageProcessingValue, "")
        optionMenu.place(relx = 0.5, rely = 0.1, anchor = "center")
        optionMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args)) #This is to stop the gui from flickering
        
        setattr(window, "optionMenu", optionMenu) #This is so the mission selector system can update tab1
        setattr(window, "dropBoxImageProcessingValue", dropBoxImageProcessingValue) #This is so the mission selector system can update tab1

        #processed img 2
        bottomProcessedImgFrame = Tkinter.Frame(tab1)
        bottomProcessedImgFrame.place(relx = 0.78, rely = 0.52, anchor = "center")
        
        for x in range(3):
            filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 0, to = 255, width = 15, orient = "horizontal")) #Creating sliders
            filterScales[11+x].grid(row = x*2, column = 0)
            filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[x], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[11+x].grid(row = x*2 + 1, column = 0)
        
        bottomProcessedImgLabel = Tkinter.Label(bottomProcessedImgFrame) #The processed image for the bottom camera will go here
        bottomProcessedImgLabel.grid(row = 0, column = 1, rowspan = 6, columnspan = 5)
        setattr(window, "bottomProcessedImgLabel", bottomProcessedImgLabel)
        
        for x in range(3):
            filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 0, to = 255, width = 15, orient = "horizontal")) #Creating sliders
            filterScales[14+x].grid(row = x*2, column = 6)
            filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[x+3], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
            filterNames[14+x].grid(row = x*2 + 1, column = 6)
            
        filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 0, to = 3, width = 15, length=90)) #Creating sliders
        filterScales[17].grid(row = 7, column = 1)
        filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[6], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[17].grid(row = 8, column = 1)
        
        filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 0, to = 25, width = 15, length=90)) #Creating sliders
        filterScales[18].grid(row = 7, column = 2)
        filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[7], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[18].grid(row = 8, column = 2)
        
        filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 0, to = 100, width = 15, length=90)) #Creating sliders
        filterScales[19].grid(row = 7, column = 3)
        filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[8], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[19].grid(row = 8, column = 3)
        
        filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 3, to = 50, width = 15, length=90)) #Creating sliders
        filterScales[20].grid(row = 7, column = 4)
        filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[9], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[20].grid(row = 8, column = 4)
        
        filterScales.append(Tkinter.Scale(bottomProcessedImgFrame, from_ = 3, to = 50, width = 15, length=90)) #Creating sliders
        filterScales[21].grid(row = 7, column = 5)
        filterNames.append(Tkinter.Label(bottomProcessedImgFrame, text = names[10], font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        filterNames[21].grid(row = 8, column = 5)
            
        setattr(window, "filterScales", filterScales)

        #TAB 2 MISSION SELECTOR
        
        #mission selector frame
        missionSelectorFrame = Tkinter.Frame(tab2)
        missionSelectorFrame.grid(row = 0, column = 0, ipadx = int(screenRes[0]/15.9), sticky = "w")
        
        label = Tkinter.Label(missionSelectorFrame, text = "Mission Selector", font=("TkDefaultFont", int(round(screenRes[0]/176.667))))
        label.grid(row = 0, column = 0, columnspan = 4)
        scrollBars = Tkinter.Scrollbar(missionSelectorFrame)
        scrollBars.grid(row = 1, column = 5, rowspan = 9, sticky='ns')
        missionListBox = Tkinter.Listbox(missionSelectorFrame, yscrollcommand=scrollBars.set, width = int(screenRes[0]/53), height = int(screenRes[1]/40))
        missionListBox.grid(row = 1, column = 0, rowspan = 9, columnspan = 4)
        scrollBars.config(command=missionListBox.yview)
        
        #up/down button
        upButton = Tkinter.Button(missionSelectorFrame, text = "up", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.MoveUpDown().moveUp(window))
        upButton.grid(row = 4, column = 6, pady = int(screenRes[1]/174), sticky = "esw")
        downButton = Tkinter.Button(missionSelectorFrame, text = "dwn", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.MoveUpDown().moveDown(window))
        downButton.grid(row = 5, column = 6, pady = int(screenRes[1]/174), sticky = "new")
        waypointButton = Tkinter.Button(missionSelectorFrame, text = "Waypoints", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: removeWaypoint(True))
        waypointButton.grid(row = 3, column = 6, pady = int(screenRes[1]/200))
        
        #bottom buttons
        addButton = Tkinter.Button(missionSelectorFrame, text = "Add", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.MissionSelectorType(window, missionListBox))
        addButton.grid(row = 10, column = 0, pady = int(screenRes[1]/200))
        deleteButton = Tkinter.Button(missionSelectorFrame, text = "Delete", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.DeleteMissionType(window))
        deleteButton.grid(row = 10, column = 1, pady = int(screenRes[1]/200))
        loadButton = Tkinter.Button(missionSelectorFrame, text = "Load", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.loadList(window))
        loadButton.grid(row = 10, column = 2, pady = int(screenRes[1]/200))
        loadButton.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args)) #This is to stop the gui from flickering
        exportButton = Tkinter.Button(missionSelectorFrame, text = "Export", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: mission_selector_system.ExportList(window))
        exportButton.grid(row = 10, column = 3, pady = int(screenRes[1]/200))
        
        #mission selector buttons
        missionSelectorButtonList = [upButton, downButton, addButton, deleteButton, loadButton]
        
        #param/value frame
        paramFrame = Tkinter.Frame(tab2)
        paramFrame.grid(row = 0, column = 1, sticky = "n")
        
        paramLabel = Tkinter.Label(paramFrame, text = "Parameters", font=("TkDefaultFont", int(round(screenRes[0]/176.667))))
        paramLabel.grid(row = 0, column = 0)
        paramListBox = Tkinter.Listbox(paramFrame, width = int(screenRes[0]/39.75), height = int(screenRes[1]/39.5))
        paramListBox.grid(row = 1, column = 0)
        
        valueLabel = Tkinter.Label(paramFrame, text = "Values", font=("TkDefaultFont", int(round(screenRes[0]/176.667))))
        valueLabel.grid(row = 0, column = 1)
        valueListBox = Tkinter.Listbox(paramFrame, width = int(screenRes[0]/39.75), height = int(screenRes[1]/39.5))
        valueListBox.grid(row = 1, column = 1)
        valueListBox.bind("<Double-Button-1>", lambda event, args=[window, valueListBox, paramListBox]: mission_selector_system.MissionSelectorValues(event, args))
        valueListBox.bind("<Return>", lambda event, args=[window, valueListBox, paramListBox]: mission_selector_system.MissionSelectorValues(event, args))
        
        #description box
        descriptionFrame = Tkinter.Frame(tab2)
        descriptionFrame.grid(row = 0, column = 2, padx = int(screenRes[0]/7.95), sticky = "n")
        
        descriptionLabel = Tkinter.Label(descriptionFrame, text = "Description", font=("TkDefaultFont", int(round(screenRes[0]/176.667))))
        descriptionLabel.grid(row = 0, column = 0)
        scrollBar = Tkinter.Scrollbar(descriptionFrame)
        scrollBar.grid(row = 1, column = 1, sticky='ns')
        discriptionText = Tkinter.Text(descriptionFrame, yscrollcommand=scrollBar.set, borderwidth = 7, width = int(screenRes[0]/31.8), height = int(screenRes[1]/39.5), wrap="word")
        discriptionText.grid(row = 1, column = 0, sticky = "nesw")
        scrollBar.config(command=discriptionText.yview)
        
        text = ''.join(["This mission selector system is capable of adding various mission types to a list by ",
        "pressing the 'Add' button. The order of the missions that are placed in the list will be the order in which they are executed when ",
        "the vehicle starts. It is possible to change the order of missions after being added to the list by the 'Up' and 'Dwn' buttons. ",
        "It is possible to change the parameter values of a mission type by double clicking on its values in the value list box. ",
        "The 'Delete' button will delete the mission that is highlighted from the list and remove its parameters ",
        "and values. The 'Load' and 'Export' buttons can load in and export the list you created."])
        
        discriptionText.insert("insert", text)
        discriptionText.config(state = "disable")
        
        #attributes to gui
        setattr(window, "missionListBox", missionListBox)
        setattr(window, "paramListBox", paramListBox)
        setattr(window, "paramLabel", paramLabel)
        setattr(window, "valueListBox", valueListBox)
        setattr(window, "valueLabel", valueLabel)
        setattr(window, "discriptionText", discriptionText)
        
        
        #TAB 3 VHEICLE TESTS
        
        # BEGIN MIKE J. CHANGES 1/5/16:
        # LINES: 1260-1329
        
        commFrame = Tkinter.Frame(tab3)
        commFrame.grid(row = 0, column = 0, ipadx = int(screenRes[0]/15.9/5), sticky = "w")
        Tkinter.Label(commFrame, text = "Boards", font=("TkDefaultFont", 13)).grid(row = 0, column = 0, columnspan = 2)
        methodLabel = Tkinter.Label(commFrame, text = "Method Name", font=("TkDefaultFont", 13), width = int(screenRes[0]/50), height = int(screenRes[0]/700))
        methodLabel.grid(row = 0, column = 4, columnspan = 2)
        setattr(window, "methodLabel", methodLabel)
        available_ports = lp.comports()
        boards = []
        comPortList = {}
        
        setattr(window, "commFrame", commFrame)
        
        #boards.append("PMUD")
        #comPortList["PMUD"] = "COM3" # Insert COM# here for testing
        
        
        for port in available_ports:
            print port
            if port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUT6OLA\\0000':#if port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUT6OLA\\0000':
                print "AHRS 1 located on " + port[2]
                boards.append("AHRS1")
                comPortList["AHRS1"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTG5PLGLA\\0000':#elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTG5PLGLA\\0000':
                print "AHRS 2 located on " + port[2]
                boards.append("AHRS2")
                comPortList["AHRS2"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUUW8DA\\0000':
                print "AHRS 3 located on " + port[2]
                boards.append("AHRS3")
                comPortList["AHRS3"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&1\\0000': # My computer, RoboSub USB 3.0 left, RoboSub USB 3.0 right, RoboSub USB 2.0 inner, RoboSub USB 2.0 outer
                print "PMUD located on " + port[2]
                boards.append("PMUD")
                comPortList["PMUD"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&2\\0000':
                print "AUX located on " + port[2]
                boards.append("AUX")
                comPortList["AUX"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&3\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&3\\0000':
                print "TCB1 located on " + port[2]
                boards.append("TCB1")
                comPortList["TCB1"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&4\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&4\\0000':
                print "TCB2 located on " + port[2]
                boards.append("TCB2")
                comPortList["TCB2"] = port[0]
                '''elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&1\\0000':
                print "WCB located on " + port[2]
                boards.append("WCB")
                comPortList["WCB"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&2\\0000':
                print "HYDRAS located on " + port[2]
                boards.append("HYDRAS")
                comPortList["HYDRAS"] = port[0]'''
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&1\\0000':
                print "WCB located on " + port[2]
                boards.append("WCB")
                comPortList["WCB"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&2\\0000':
                print "HYDRAS located on " + port[2]
                boards.append("HYDRAS")
                comPortList["HYDRAS"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&3\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&3\\0000':
                print "DIB located on " + port[2]
                boards.append("DIB")
                comPortList["DIB"] = port[0]
            elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&4\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&4\\0000':
                print "SIB located on " + port[2]
                boards.append("SIB")
                comPortList["SIB"] = port[0]
                
        setattr(window, "comPortList", comPortList) #This is so the COMfinder can update the NMS with which boards are which coms
        
        '''boards.append("Sparton")
        boards.append("TCB1")
        boards.append("PMUD")
        boards.append("SIB")
        boards.append("MOVEMENT")'''
        
        board_value = Tkinter.StringVar()
        board_value.set("")
        boardOptions = Tkinter.OptionMenu(commFrame, board_value, "")
        boardOptions.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args)) #This is to stop the gui from flickering
        
        if len(boards) > 0:
            boardOptions["menu"].delete(0, "end")
            #boardOptions = apply(Tkinter.OptionMenu, (commFrame, board_value) + tuple(boards))
            for board in boards:
                boardOptions["menu"].add_command(label=board, command = lambda value=board: UpdateMenu(window).board_change(value))
                board_value.set(boards[0])
        else:
            boardOptions["menu"].delete(0, "end")
        boardOptions.grid(row=1,column=0, columnspan = 2)
        
        commandListBox = Tkinter.Listbox(commFrame, width = int(screenRes[0]/53), height = int(screenRes[1]/40))
        commandListBox.grid(row = 2, column = 0, rowspan = 10, columnspan = 2)
                
        setattr(window, "boardOptions", boardOptions) #This is so the COMfinder can update tab 3
        setattr(window, "boardValue", board_value) #This is so the COMfinder can update tab 3  
        setattr(window, "commandListBox", commandListBox)
        setattr(window, "optionList", None)
        commandListBox.bind('<<ListboxSelect>>', COMfinder.UpdateBoard(window).onselect)
        
        #loadScript = Tkinter.Button(buttonsFrame, text = "Load", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: gui_communication.TcbControl(window).commInterface())
        #loadScript.grid(row = 2, column = 2, pady = int(20))
        
        #exportScript = Tkinter.Button(commFrame, text = "Export", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: gui_communication.Hydra_Board(window).commInterface())
        #exportScript.place(relx = .075, rely = .435)
        #exportScript.grid(row = 4, column = 1, pady = int(20))

        scriptBar = Tkinter.Scrollbar(tab3)
        scriptBar.grid(row = 0, column = 2, rowspan = 10, sticky='ns')
        scriptText = Tkinter.Text(tab3, borderwidth = 7, yscrollcommand=scriptBar.set, width = int(screenRes[0]/11.367/2), height = int(screenRes[1]/38))
        scriptText.grid(row = 0, column = 1, rowspan = 10, sticky = "nesw")
        scriptBar.config(command=scriptText.yview)
        outBar = Tkinter.Scrollbar(tab3)
        outBar.grid(row = 0, column = 5, rowspan = 10, sticky='ns')
        scriptOut = Tkinter.Text(tab3, yscrollcommand=outBar.set, borderwidth = 7, width = int(screenRes[0]/31.8), height = int(screenRes[1]/39.5), wrap="word")
        outBar.config(command=scriptOut.yview)
        scriptOut.grid(row = 0, column = 4, rowspan = 10, sticky = "nesw")
        
        # COMMENT THIS OUT TO STOP CONSOL FROM PRINTING TO COMS TAB
        #sys.stdout = StdoutRedirector(scriptText)
        
        setattr(window, "scriptText", scriptText) #This is so the COMfinder can update tab 3
        setattr(window, "scriptOut", scriptOut) #This is so the COMfinder can update tab 3
        
        # BEGIN MIKE J. CHANGES 1/5/16:
        # LINES: 1260-1329
        
        scriptText.insert("insert", "\n\n\n--> Select the function.\n") # This text will appear in the tab3 scriptText upon opening the GUI - this provides user with instructions before running any commands
        scriptText.insert("insert", "--> Enter variables using \'<Return>\' key.\n")
        scriptText.insert("insert", "--> Add commands to the list with the button, then select run.\n")
        scriptText.insert("insert", "--> Checkbox removes time restrictions (disregard Hz).\n")
        scriptText.insert("insert", "--> Press clear all to clear the text and all variables.\n\n")
        scriptText.insert("insert", "*If number runs not entered, program runs once.\n")
        scriptText.insert("insert", "*100 Hz (on average) is max for getters.\n")
        scriptText.insert("insert", "*If Hz is not entered, program runs once per second.\n\n")
        
        addCommandButton = Tkinter.Button(commFrame, text = "Add Command", font= ("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: COMfinder.COMScript(window).addRunToListbox())
        addCommandButton.grid(row = 7, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        runMultipleScripts = Tkinter.Button(commFrame, text = "Run Multiple", font= ("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: COMfinder.COMScript(window).runMultipleScripts())
        runMultipleScripts.grid(row = 8, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        setattr(window, "runScriptButton", runMultipleScripts) # This allows COMfinder to edit the "bg" field of the button and set it to green/remove based on if run button can be used and has all correct parameters
        
        clearButton = Tkinter.Button(commFrame, text = "Clear All", font =("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: COMfinder.COMScript(window).clearCOMScript()) # Clears the scriptText and all other text fields, use the clear button to reset the state of the comms tab before running another function
        clearButton.grid(row = 9, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        def enterButtonEventMultipleText(event): # Binds the multiple runs text so the user can simply press enter to run the command
            window.multipleText.focus_set()
            return 'break' # Prevents the widget text from moving to the next line
            
        def enterButtonEventParamText(event):
            try:
                window.paramDictionary[window.param_value.get()] = int(window.paramValueText.get("1.0", "end"))
            except:
                print "\nPlease enter a valid parameter."
                window.paramValueText.focus_set()
                return
            window.paramValueText.focus_set()
            return 'break' # Prevents the widget text from moving to the next line
        
        def enterButtonHzText(event):
            try:
                window.numberOfHz = int(window.hzValueWidget.get("1.0", "end"))
            except:
                print "\nPlease enter a valid Hz value."
                window.hzValueWidget.focus_set()
                return
            window.hzValueWidget.focus_set()
            return 'break' # Prevents the widget text from moving to the next line
        
        def onTabKeyPressed(event):
            return 'break'
        
        def onButtonChecked(event):
            if window.speedRun == False:
                window.speedRun = True
                window.executionCounterLabel.grid_remove()
                window.hzValueWidget.grid_remove()
                window.hzLabelWidget.grid_remove()
            else:
                window.speedRun = False
                window.executionCounterLabel.grid()
                window.hzValueWidget.grid()
                window.hzLabelWidget.grid()
        
        numberOfHz = 0
        listOfHz = []
        
        hzLabelWidget = Tkinter.Label(commFrame, text = "Hz Value:", font = "TkDefaultFont")
        hzLabelWidget.grid(row = 4, column = 3, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        hzValueWidget = Tkinter.Text(commFrame, width = int(screenRes[0]/200), height = int(screenRes[0]/1000))
        hzValueWidget.grid(row = 4, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2)
        hzValueWidget.bind("<Return>", enterButtonHzText)
        hzValueWidget.bind("<Tab>", onTabKeyPressed)
        
        setattr(window, "numberOfHz", numberOfHz)
        setattr(window, "listOfHz", listOfHz)
        setattr(window, "hzValueWidget", hzValueWidget)
        setattr(window, "hzLabelWidget", hzLabelWidget)
        
        multipleTextLabel = Tkinter.Label(commFrame, text = "Number Runs:", font = "TkDefaultFont")
        multipleTextLabel.grid(row = 3, column = 3, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        multipleText = Tkinter.Text(commFrame, width = int(screenRes[0]/200), height = int(screenRes[0]/1000)) # User will enter the number of runs (for multiple runs) a script will do, or leave blank
        multipleText.grid(row = 3, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2)
        multipleText.bind("<Return>", enterButtonEventMultipleText)
        multipleText.bind("<Tab>", onTabKeyPressed)
        
        pLabelList = []
        pDict = {}
        
        setattr(window, "multipleText", multipleText) # This is so COMfinder can update tab 3
        setattr(window, "paramLabelList", pLabelList) # Will be populated with the names of the parameters
        setattr(window, "paramDictionary", pDict) # This will store pTextList and PLabelList values
        
        param_value = Tkinter.StringVar() # Names will be set via paramTextList
        param_value.set("")
        paramOptionMenu = Tkinter.OptionMenu(window.commFrame, param_value, "")
        paramOptionMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args)) # This is to stop the GUI from flickering
        paramOptionMenu.grid(row = 1, column = 4, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2)
        
        paramLabelWidget = Tkinter.Label(commFrame, text = "Parameter Value:", font = "TkDefaultFont")
        paramLabelWidget.grid(row = 2, column = 3, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        paramValueText = Tkinter.Text(commFrame, width = int(screenRes[0]/200), height = int(screenRes[0]/1000))
        paramValueText.grid(row = 2, column = 5, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2)
        paramValueText.bind("<Return>", enterButtonEventParamText)
        paramValueText.bind("<Tab>", onTabKeyPressed)
        
        orderOfRunListbox = Tkinter.Listbox(commFrame, width = int(screenRes[0]/65), height = int(screenRes[1]/100))
        orderOfRunListbox.grid(row = 7, column = 3, rowspan = 3, ipadx = int(screenRes[1]/800), pady = int(screenRes[1]/1000), columnspan = 2)
        
        executionTimeCounterLabel = Tkinter.Label(commFrame, text = "GUI will pause for 0 seconds to run command(s).", font = "TkDefaultFont")
        executionTimeCounterLabel.grid(row = 5, column = 4, ipadx = int(screenRes[1]/200), pady = int(screenRes[1]/200), columnspan = 2, sticky = 'ew')
        
        checkButtonVar = Tkinter.IntVar()
        checkButtonSpeedRun = Tkinter.Checkbutton(commFrame, text = "Max Speed", font = "TkDefaultFont", var = checkButtonVar)
        checkButtonSpeedRun.grid(row = 6, column = 4)
        checkButtonSpeedRun.bind("<Button-1>", onButtonChecked)
        
        runCommandsDictionaryList = []
        methodNameList = []
        numExecutionsList = []
        currentBoardNameList = []
        currentBoardName = ""
        deleteScriptText = True
        commsFirstRun = True
        speedRun = False
        executionCounter = 0
        
        setattr(window, "paramLabelWidget", paramLabelWidget) # This is so COMFinder can remove the label when no parameters exist
        setattr(window, "paramValueText", paramValueText) # This is so COMFinder can remove the text when no parameters exist
        setattr(window, 'paramOptionMenu', paramOptionMenu) # This is so COMfinder can update the number of parameter labels on option menu widget in conjunction with the StringVar attribute below
        setattr(window, "param_value", param_value) # This is so COMfinder can update the parameter labels on tab 3's option menu widget
        setattr(window, "orderOfRunListbox", orderOfRunListbox) # This is so COMfinder can update the listbox containing with a list of methods to be run
        setattr(window, "runCommandsDictionaryList", runCommandsDictionaryList) # List of dictionaries storing parameters and their values (for given function)
        setattr(window, "numExecutionsList", numExecutionsList) # List of number of times to execute each command
        setattr(window, "methodNameList", methodNameList) # List of the names of the methods
        setattr(window, "commsFirstRun", commsFirstRun) # Used in update gui to layout parameter labels
        setattr(window, "deleteScriptText", deleteScriptText) # This will trigger runScript() in COMfinder to delete the text instructions on its first run
        setattr(window, "executionCounterLabel", executionTimeCounterLabel) # This label will be updated by COMfinder to store the current expected # seconds commands in the list will take to run
        setattr(window, "executionCounter", executionCounter) # This is the integer that actually stores the # of seconds required
        setattr(window, "speedRun", speedRun) # If it is a speed run, hz are ignored
        setattr(window, "checkButtonVar", checkButtonVar) # Used by the bind function of the check button to change its states
        setattr(window, "currentBoardNameList", currentBoardNameList)
        setattr(window, "currentBoardName", currentBoardName)
        
        try:#CHANGE THE COM BOARDS HERE
            UpdateMenu(window).board_change(boards[0])
            com = comPortList["PMUD"]
            com = comPortList["TCB1"]
            com = comPortList["TCB2"]
            com = comPortList["SIB"]
            com = comPortList["DIB"]
            com = comPortList["WCB"]
            com = comPortList["HYDRAS"]
        except:      
            print "Some boards not detected."
            
        # END MIKE J. CHANGES 1/5/16
            
        #TAB 4 CONSOLE
        scrollBar = Tkinter.Scrollbar(tab4)
        scrollBar.grid(row = 0, column = 1, rowspan = 10, sticky='ns')
        consolText = Tkinter.Text(tab4, borderwidth = 7, yscrollcommand=scrollBar.set, width = int(screenRes[0]/11.367), height = int(screenRes[1]/38))
        consolText.grid(row = 0, column = 0, rowspan = 10, sticky = "nesw")
        #sys.stdout = StdoutRedirector(consolText) #COMMENT THIS LINE OUT TO STOP PRINTING TO GUI
        scrollBar.config(command=consolText.yview)
        
        #PRINT OPTIONS
        names = ["Heading, Pitch, Roll, Depth", "Position (x, y, z)", "Velocity (u, v, w)", "Battery 1 Status", "Battery 2 Status", "Temperature Status", "Current Rotation Matrix"]
        printOptionCheckbox = []
        printOptionCheckboxValues = []
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[0], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[0]))
        printOptionCheckbox[0].grid(row = 0, column = 2, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[1], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[1]))
        printOptionCheckbox[1].grid(row = 0, column = 3, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[2], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[2]))
        printOptionCheckbox[2].grid(row = 0, column = 4, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[3], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[3]))
        printOptionCheckbox[3].grid(row = 1, column = 2, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[4], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[4]))
        printOptionCheckbox[4].grid(row = 1, column = 3, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[5], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[5]))
        printOptionCheckbox[5].grid(row = 1, column = 4, sticky = "W", padx = int(screenRes[0]/795))
        
        printOptionCheckboxValues.append(Tkinter.IntVar())
        printOptionCheckbox.append(Tkinter.Checkbutton(tab4, text = names[6], font=("TkDefaultFont", int(round(screenRes[0]/176.667))), variable = printOptionCheckboxValues[6]))
        printOptionCheckbox[6].grid(row = 2, column = 2, columnspan = 2, sticky = "W", padx = int(screenRes[0]/795))
    
        setattr(window, 'printOptionCheckbox', printOptionCheckbox)
        setattr(window, 'printOptionCheckboxValues', printOptionCheckboxValues)
        
        clearButton = Tkinter.Button(tab4, width = int(screenRes[0]/227.143), text = "Clear", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: clear(consolText))
        clearButton.grid(row = 9, column=2, padx = int(screenRes[0]/63.6), sticky = "w")
        
        exportButton = Tkinter.Button(tab4, width = int(screenRes[0]/227.143), text = "Export", font=("TkDefaultFont", int(round(screenRes[0]/176.667))), command = lambda: export(consolText))
        exportButton.grid(row = 9, column=4, padx = int(screenRes[0]/63.6), sticky = "e")
            
        #TAB 5 SETTINGS
        configurationGaugeScales = []
        configurationGaugeNames = []
        configurationGaugeScales_CheckBoxes = []
        configurationGaugeScales_RadioButtons = []
        
        #CONFIG GAUGE SLIDERS
        graphicsOverlaySettingsFrame = Tkinter.Frame(tab5)
        graphicsOverlaySettingsFrame.grid(row = 0, column = 0)
        
        graphicsOverlayTitle = Tkinter.Label(graphicsOverlaySettingsFrame, text = "Graphics Configuration", font=("TkDefaultFont", int(round(screenRes[0]/176.667))))
        graphicsOverlayTitle.grid(row = 0, column = 2, columnspan = 10)
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[0]))
        configurationGaugeScales[0].grid(row = 1, column = 0, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Heading Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[0].grid(row = 2, column = 0, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 3, to = 10, width = 15, orient = "horizontal"))
        configurationGaugeScales[1].grid(row = 3, column = 0, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Heading Tick Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[1].grid(row = 4, column = 0, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 1, to = 60, width = 15, orient = "horizontal"))
        configurationGaugeScales[2].grid(row = 5, column = 0, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Heading Increment Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[2].grid(row = 6, column = 0, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 1, width = 15, orient = "horizontal"))
        configurationGaugeScales[3].grid(row = 7, column = 0, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Heading Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[3].grid(row = 8, column = 0, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 10, to = rawImgWidth, width = 15, orient = "horizontal"))
        configurationGaugeScales[4].grid(row = 9, column = 0, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Heading Width", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[4].grid(row = 10, column = 0, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[1]))
        configurationGaugeScales[5].grid(row = 1, column = 1, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Pitch Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[5].grid(row = 2, column = 1, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 3, to = 15, width = 15, orient = "horizontal"))
        configurationGaugeScales[6].grid(row = 3, column = 1, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Pitch Tick Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[6].grid(row = 4, column = 1, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 1, to = 15, width = 15, orient = "horizontal"))
        configurationGaugeScales[7].grid(row = 5, column = 1, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Pitch Increment Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[7].grid(row = 6, column = 1, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 15, to = rawImgHeight-140, width = 15, orient = "horizontal"))
        configurationGaugeScales[8].grid(row = 7, column = 1, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Pitch Length", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[8].grid(row = 8, column = 1, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[2]))
        configurationGaugeScales[9].grid(row = 1, column = 2, columnspan = 2, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[9].grid(row = 2, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 3, to = 13, width = 15, orient = "horizontal"))
        configurationGaugeScales[10].grid(row = 3, column = 2, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Tick Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[10].grid(row = 4, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_RadioButtons.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[0], text = "90", value = 0))
        configurationGaugeScales[11].grid(row = 5, column = 2, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Range Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[11].grid(row = 6, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[0], text = "180", value = 1))
        configurationGaugeScales[12].grid(row = 5, column = 3, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Range Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[12].grid(row = 6, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 1, width = 15, orient = "horizontal"))
        configurationGaugeScales[13].grid(row = 7, column = 2, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[13].grid(row = 8, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 2, to = rawImgWidth/2-39, width = 15, orient = "horizontal"))
        configurationGaugeScales[14].grid(row = 9, column = 2, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Roll Width", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[14].grid(row = 10, column = 2, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[3]))
        configurationGaugeScales[15].grid(row = 1, column = 4, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Depth Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[15].grid(row = 2, column = 4, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 3, to = 20, width = 15, orient = "horizontal"))
        configurationGaugeScales[16].grid(row = 3, column = 4, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Depth Tick Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[16].grid(row = 4, column = 4, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 1, to = 50, width = 15, orient = "horizontal"))
        configurationGaugeScales[17].grid(row = 5, column = 4, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Depth Increment Num", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[17].grid(row = 6, column = 4, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 1, width = 15, orient = "horizontal"))
        configurationGaugeScales[18].grid(row = 7, column = 4, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Depth Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[18].grid(row = 8, column = 4, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 20, to = rawImgHeight, width = 15, orient = "horizontal"))
        configurationGaugeScales[19].grid(row = 9, column = 4, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Depth Length", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[19].grid(row = 10, column = 4, sticky = "N",  padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[4]))
        configurationGaugeScales[20].grid(row = 1, column = 5, columnspan = 2, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Attitude Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[20].grid(row = 2, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 5, to = 50, width = 15, orient = "horizontal"))
        configurationGaugeScales[21].grid(row = 3, column = 5, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Attitude Length", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[21].grid(row = 4, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_RadioButtons.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[1], text = "Yes", value = 1))
        configurationGaugeScales[22].grid(row = 5, column = 5, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Display Pos/Vel", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[22].grid(row = 6, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[1], text = "No", value = 0))
        configurationGaugeScales[23].grid(row = 5, column = 6, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Display Pos/Vel", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[23].grid(row = 6, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 3, width = 15, orient = "horizontal"))
        configurationGaugeScales[24].grid(row = 7, column = 5, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Attitude Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[24].grid(row = 8, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 50, width = 15, orient = "horizontal"))
        configurationGaugeScales[25].grid(row = 9, column = 5, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Attitude Letter Size", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[25].grid(row = 10, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 10, width = 15, orient = "horizontal"))
        configurationGaugeScales[26].grid(row = 11, column = 5, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Attitude Letter Ratio", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[26].grid(row = 12, column = 5, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[5]))
        configurationGaugeScales[27].grid(row = 1, column = 7, columnspan = 2, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Battery Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[27].grid(row = 2, column = 7, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 1, to = 100, width = 15, orient = "horizontal"))
        configurationGaugeScales[28].grid(row = 3, column = 7, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Battery Length", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[28].grid(row = 4, column = 7, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_RadioButtons.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[2], text = "Yes", value = 1))
        configurationGaugeScales[29].grid(row = 5, column = 7, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Display Battery Current", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[29].grid(row = 6, column = 7, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        configurationGaugeScales.append(Tkinter.Radiobutton(graphicsOverlaySettingsFrame, variable=configurationGaugeScales_RadioButtons[2], text = "No", value = 0))
        configurationGaugeScales[30].grid(row = 5, column = 8, padx = int(screenRes[0]/318))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Display Battery Current", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[30].grid(row = 6, column = 7, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 3, width = 15, orient = "horizontal"))
        configurationGaugeScales[31].grid(row = 7, column = 7, columnspan = 2, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Battery Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[31].grid(row = 8, column = 7, columnspan = 2, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[6]))
        configurationGaugeScales[32].grid(row = 1, column = 9, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Temperature Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[32].grid(row = 2, column = 9, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 10, to = 50, width = 15, orient = "horizontal"))
        configurationGaugeScales[33].grid(row = 3, column = 9, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Temperature Size", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[33].grid(row = 4, column = 9, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 3, width = 15, orient = "horizontal"))
        configurationGaugeScales[34].grid(row = 5, column = 9, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Temperature Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[34].grid(row = 6, column = 9, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[7]))
        configurationGaugeScales[35].grid(row = 1, column = 10, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Motor Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[35].grid(row = 2, column = 10, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 10, to = 50, width = 15, orient = "horizontal"))
        configurationGaugeScales[36].grid(row = 3, column = 10, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Motor Size", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[36].grid(row = 4, column = 10, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 1, width = 15, orient = "horizontal"))
        configurationGaugeScales[37].grid(row = 5, column = 10, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Motor Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[37].grid(row = 6, column = 10, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales_CheckBoxes.append(Tkinter.IntVar())
        configurationGaugeScales.append(Tkinter.Checkbutton(graphicsOverlaySettingsFrame, variable = configurationGaugeScales_CheckBoxes[8]))
        configurationGaugeScales[38].grid(row = 1, column = 11, padx = int(screenRes[0]/795))
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Status Gauge", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[38].grid(row = 2, column = 11, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 3, width = 15, orient = "horizontal"))
        configurationGaugeScales[39].grid(row =  3, column = 11, padx = int(screenRes[0]/318)) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Status Position", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[39].grid(row = 4, column = 11, sticky = "N", padx = int(screenRes[0]/318))
        
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Color", font=("TkDefaultFont", int(round(screenRes[0]/100.667)))))
        configurationGaugeNames[40].grid(row = 1, column = 12, rowspan = 2, padx = int(screenRes[0]/318)+50)
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 255, width = 15, orient = "horizontal"))
        configurationGaugeScales[40].grid(row = 3, column = 12, padx = int(screenRes[0]/318)+50) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Red Gauge Color", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[41].grid(row = 4, column = 12, padx = int(screenRes[0]/318)+50)
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 255, width = 15, orient = "horizontal"))
        configurationGaugeScales[41].grid(row = 5, column = 12, columnspan = 4, padx = int(screenRes[0]/318)+50) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Green Gauge Color", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[42].grid(row = 6, column = 12, columnspan = 4, padx = int(screenRes[0]/318)+50)
        
        configurationGaugeScales.append(Tkinter.Scale(graphicsOverlaySettingsFrame, from_ = 0, to = 255, width = 15, orient = "horizontal"))
        configurationGaugeScales[42].grid(row = 7, column = 12, padx = int(screenRes[0]/318)+50) 
        configurationGaugeNames.append(Tkinter.Label(graphicsOverlaySettingsFrame, text = "Blue Gauge Color", font=("TkDefaultFont", int(round(screenRes[0]/176.667)))))
        configurationGaugeNames[43].grid(row = 8, column = 12, padx = int(screenRes[0]/318)+50)
        
        setattr(window, "configurationGaugeScales", configurationGaugeScales)
        setattr(window, "configurationGaugeScales_RadioButtons", configurationGaugeScales_RadioButtons)
        setattr(window, "configurationGaugeScales_CheckBoxes", configurationGaugeScales_CheckBoxes)

        #TAB 6 Manual Control
        setattr(window, "setToManual", 3)
        
        startManualButton = Tkinter.Button(tab6, text = "MANUAL CONTROL", width = screenRes[0]/73, height = screenRes[1]/180)
        startManualButton.place(relx = 0, rely = 0)
        
        stopManualButton = Tkinter.Button(tab6, text = "STOP", fg='black', width = screenRes[0]/73, height = screenRes[1]/180, state = "disable")
        stopManualButton.place(relx = 0, rely = 0.78)
        
        controllerScreen = Tkinter.Label(tab6, background = "gray")  #The raw image for the front camera will go here
        setattr(window, "controllerScreen", controllerScreen)
        
        setattr(window, "manualModeEnabled", False)
        
        startManualClass = StartManual(window, tab6, notebook, missionSelectorButtonList)
        startManualButton.config(command=lambda: startManualClass.start(startManualButton, stopManualButton))
        stopManualButton.config(command=lambda: startManualClass.stop(startManualButton, stopManualButton))
        
        #TAB 7 RoboArm
        #roboarmController.roboarmControllerTab(window, notebook)
        
        #TAB 7 DATA ANALYSIS
        
        window.testingData = [[],[],[],[],[],[],[],[],[],[],[],[],[
                                                                   [],[],[],[]],[
                                                                                 [],[],[],[],
                                                                                 [],[],[],[]]]
        window.circularBufferSize = 15
        window.circularTracker = 15
        window.startTime = time.time()
         
        i = 0
        s=''
        while True:
            s= "_Saved_Data_/Run_Number_"+str(i)+".csv"
            if(os.path.exists(s)):
                i+=1
            else:
                break
        file = open(s, "w")
        file.write("#Data from the run")
        file.close()
        window.saveDataLocation = s
         
         
        window.graph = graphing.GraphingModule(tab8, width= (screenRes[0]*5)/8, height = (screenRes[1]*3)/8, bd=2, relief=Tkinter.SUNKEN)
        window.graph.place(relx=.3, rely=.05)
         
        window.XIterationSlider = Tkinter.Scale(tab8, from_=1, to=10, orient=Tkinter.HORIZONTAL)
        window.YIterationSlider = Tkinter.Scale(tab8, from_=1, to=10, orient=Tkinter.HORIZONTAL)
        window.XIterationSlider.set(10)
        window.YIterationSlider.set(10)
         
        Tkinter.Label(tab8, text="X-Iteration Slider").place(relx=.03, rely=.45)
        Tkinter.Label(tab8, text="Y-Iteration Slider").place(relx=.15, rely=.45)
        window.XIterationSlider.place(relx=.03, rely=.5)
        window.YIterationSlider.place(relx=.15, rely=.5)
         
        setattr(window, "XAxisLabel", Tkinter.StringVar(tab8))
        setattr(window, "YAxisLabel", Tkinter.StringVar(tab8))
        setattr(window, "motorXAxisLabel", Tkinter.StringVar(tab8))
        setattr(window, "motorYAxisLabel", Tkinter.StringVar(tab8))
        setattr(window, "batteryXAxisLabel", Tkinter.StringVar(tab8))
        setattr(window, "batteryYAxisLabel", Tkinter.StringVar(tab8))

        window.showAllDataVar = Tkinter.IntVar()
        
        Tkinter.Checkbutton(tab8, text="Show all Data", variable=window.showAllDataVar).place(relx=.1, rely=.65)
        
         
        window.XAxisLabel.set("Time")
        window.YAxisLabel.set("Heading")            
               
        window.dataDictionary = {"Time":0, "Heading":1, "Pitch":2, "Roll":3,"X-Position":4,"Y-Position":5,"Z-Position":6,"X-Velocity":7,"Y-Velocity":8,"Z-Velocity":9,"Depth":10,"Temperature":11, "Battery":12,"Motor":13}
        window.motorDictionary = {"Motor 1":0,"Motor 2":1,"Motor 3":2,"Motor 4":3,"Motor 5":4,"Motor 6":5,"Motor 7":6,"Motor 8":7}
        window.batteryDictionary = {"Battery 1 Voltage":0, "Battery 1 Current":1,"Battery 2 Voltage":0, "Battery 2 Current":1}
        
        def showXMotorOption(p1):
            if p1 == "Motor":
                window.xMotorAxisMenu = Tkinter.OptionMenu(tab8, window.motorXAxisLabel, "Motor 1","Motor 2","Motor 3","Motor 4","Motor 5","Motor 6","Motor 7","Motor 8")
                window.xMotorAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
                window.xMotorAxisMenu.place(relx=.17, rely=.1)
            else:
                window.xMotorAxisMenu.destroy()
            if p1 == "Battery":
                window.xBatteryAxisMenu = Tkinter.OptionMenu(tab8, window.batteryXAxisLabel, "Battery 1 Voltage", "Battery 1 Current", "Battery 2 Voltage", "Battery 2 Current")
                window.xBatteryAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
                window.xBatteryAxisMenu.place(relx=.17, rely=.1)
            else:
                window.xBatteryAxisMenu.destroy()

        def showYMotorOption(p1):
            if p1 == "Motor":
                window.yMotorAxisMenu = Tkinter.OptionMenu(tab8, window.motorXAxisLabel, "Motor 1","Motor 2","Motor 3","Motor 4","Motor 5","Motor 6","Motor 7","Motor 8")
                window.yMotorAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
                window.yMotorAxisMenu.place(relx=.17, rely=.3)                
            else:
                window.yMotorAxisMenu.destroy()
            if p1 == "Battery":
                window.yBatteryAxisMenu = Tkinter.OptionMenu(tab8, window.batteryYAxisLabel, "Battery 1 Voltage", "Battery 1 Current", "Battery 2 Voltage", "Battery 2 Current")
                window.yBatteryAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
                window.yBatteryAxisMenu.place(relx=.17, rely=.3)
            else:
                window.yBatteryAxisMenu.destroy()
                
        
        window.xMotorAxisMenu = Tkinter.OptionMenu(tab8, window.motorXAxisLabel, "Motor 1","Motor 2","Motor 3","Motor 4","Motor 5","Motor 6","Motor 7","Motor 8")
        window.yMotorAxisMenu = Tkinter.OptionMenu(tab8, window.motorYAxisLabel, "Motor 1","Motor 2","Motor 3","Motor 4","Motor 5","Motor 6","Motor 7","Motor 8")
        window.xBatteryAxisMenu = Tkinter.OptionMenu(tab8, window.batteryYAxisLabel, "Battery 1 Voltage", "Battery 1 Current", "Battery 2 Voltage", "Battery 2 Current")
        window.yBatteryAxisMenu = Tkinter.OptionMenu(tab8, window.batteryYAxisLabel, "Battery 1 Voltage", "Battery 1 Current", "Battery 2 Voltage", "Battery 2 Current")
        window.xMotorAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        window.yMotorAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        window.xBatteryAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        window.yBatteryAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        window.motorXAxisLabel.set("Motor 1")
        window.motorYAxisLabel.set("Motor 1")
        window.batteryXAxisLabel.set("Battery 1 Voltage")
        window.batteryYAxisLabel.set("Battery 1 Voltage")
        
        Tkinter.Label(tab8,text="X Axis").place(relx=.01, rely=.04)
        xAxisMenu = Tkinter.OptionMenu(tab8, window.XAxisLabel, "Time", "Heading","Pitch", "Roll", "Battery", "Motor", "X-Position","Y-Position","Z-Position","X-Velocity","Y-Velocity","Z-Velocity","Depth","Temperature", command=showXMotorOption)
        Tkinter.Label(tab8, text="Y Axis").place(relx=.01, rely=.24)
        yAxisMenu = Tkinter.OptionMenu(tab8, window.YAxisLabel, "Time", "Heading","Pitch", "Roll", "Battery", "Motor","X-Position","Y-Position","Z-Position","X-Velocity","Y-Velocity","Z-Velocity","Depth","Temperature", command=showYMotorOption)
        
        xAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        yAxisMenu.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args))
        
        xAxisMenu.config(width=20)
        yAxisMenu.config(width=20)
         
        setattr(window, "xAxisMenu", xAxisMenu)
        setattr(window, "yAxisMenu", yAxisMenu)
         
        xAxisMenu.place(relx=.01, rely=.1)
        yAxisMenu.place(relx=.01, rely=.3)
        
        
        #TAB 8 Waypoint Modification 
        self.waypointManagment = waypointManagement.WaypointManagment(window)
        
        # Tab 8 Control Systems
        control_systems_tab.makeControlSystemsTab(window, notebook, screenRes)

        #AUV START/STOP
        if not window.DEBUG:
            #START ALL EXTERNAL PROCESSES
            self.parent_conn, child_conn = multiprocessing.Pipe() 
            self.process = multiprocessing.Process(target=NMS.start, args=(child_conn,))
            self.process.start()
            self.parent_conn.send(window.comPortList) #Tell NMS process all the COMs of each of the devices that are connected
            initialData = self.parent_conn.recv()
        else:
            initialData = None
            
        userLabel = Tkinter.Label(window, text = "User", font=("Calibri", int(screenRes[0]/123)), background = "gray", foreground = "black")
        userLabel.place(relx = 0.5, rely = 0.02, anchor="center")
        
        lastUserLog = previous_state_logging_system.Log('_Saved_Settings_/_Last_User_.txt') #Need to created separate file to keep track of last user so that I know what file to load in for all settings
        lastUserValues = lastUserLog.getParameters("lastUser") #Get the lastUser variable in file
        
        if lastUserValues.lastUser == 0: #If no value in _Last_User_.txt file...
            lastUserValues.lastUser = "Austin Owens"
                          
        dropBoxUserValue = Tkinter.StringVar(window)
        dropBoxUserValue.set(lastUserValues.lastUser) # default value
        options = Tkinter.OptionMenu(window, dropBoxUserValue, "Jared Guerrero","Austin Owens", "Josh Pritts", "Drew Smith", "Rodrigo Alvarez", "Maryann Ibrahim", "Jacob Marlay", "Matt Wnuk", "Joseph Clements", "Petar Tasev", "Akash Khatawate", "Osten Massa", "Ryan Mohedano")
        options.place(relx = 0.5, rely = 0.05, anchor="center")
        options.bind("<Button-1>", lambda event, args=[window]: Refresh(event, args)) #This is to stop the gui from flickering
        
        setattr(window, "lastUser", dropBoxUserValue) #This is so I can write the last user into a file in 'update gui' file
        setattr(window, "lastUserLog", lastUserLog) #This is so I can write the last user into a file in 'update gui' file
        
        startRobosubButton = Tkinter.Button(window, text = "START VEHICLE", width = screenRes[0]/73, height = screenRes[1]/180)
        startRobosubButton.place(relx = 0.5, rely = 0.15, anchor="center")
        stopRobosubButton = Tkinter.Button(window, text = "STOP VEHICLE", width = screenRes[0]/73, height = screenRes[1]/180, state = "disable")
        stopRobosubButton.place(relx = 0.5, rely = 0.25, anchor="center")
        resetDVLButton = Tkinter.Button(window, text = "RESET DVL", width = screenRes[0]/73, height = screenRes[1]/180)
        resetDVLButton.place(relx = 0.5, rely = 0.35, anchor="center")
        setattr(window, 'sendMissionSelectorData', False) #Starts in an off state
        setattr(window, 'startVehicle', False) #Starts in an off state
        setattr(window, "resetDVL", False)
        
        authorLabel = Tkinter.Label(window, text = "By: Austin Owens\n Jared Guerrero", font=("Calibri", int(screenRes[0]/123)), background = "gray", foreground = "black")
        authorLabel.place(relx = 0.5, rely = 0.46, anchor="center")
        
        copyrightLabel = Tkinter.Label(window, text = "Copyright 2015, Austin Owens & Jared Guerrero, All rights reserved.", font=("Calibri", int(screenRes[0]/123)-1), foreground = "black")
        copyrightLabel.place(relx = 0.5, rely = 0.984, anchor="center")
        
        
        
        frontRecording = Tkinter.Label(window, text = "Rec.", font=("Calibri", int(screenRes[0]/50)), background = "gray", foreground = "gray")
        frontRecording.place(relx = 0, rely = 0.05)
        bottomRecording = Tkinter.Label(window, text = "Rec.", font=("Calibri", int(screenRes[0]/50)), background = "gray", foreground = "gray")
        bottomRecording.place(relx = 1, rely = 0.07, anchor="e")
        setattr(window, "recording", [frontRecording, bottomRecording])
        
        startVehicleClass = StartVehicle(notebook, missionSelectorButtonList)
        startRobosubButton.config(command=lambda: startVehicleClass.start(startRobosubButton, stopRobosubButton))
        stopRobosubButton.config(command=lambda: startVehicleClass.stop(startRobosubButton, stopRobosubButton))
        resetDVLButton.config(command=lambda: startVehicleClass.reset())
        
        #CLAW
        setattr(window, "servoModel", None)
        
        #MAIN FUNCTION
        setattr(window, "externalDevicesData", initialData) #Setting initial externalDevicesData value to whatever I receive on the external process
        GUI = update_gui.UpdateGUI(window, rawImgWidth, rawImgHeight, processedImgWidth, processedImgHeight) #This needs to be here so that the 'window' variable has all its setattr
        window.after(0, func=lambda: self.updateGUI(window))
        
        #EXITING CONDITION
        window.protocol('WM_DELETE_WINDOW', self.setQuitFlag)  # avoid errors on exit

if __name__ == "__main__":
    gui = GuiCreation()
    gui.guiSetup()
    window.mainloop()