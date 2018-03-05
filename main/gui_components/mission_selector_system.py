'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: mission_selector_system
   :synopsis: Handles the missions, mission lists, and mission parameters.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Nov 17, 2014
:Description: These classes allow the user to save, update, and delete missions and their parameters.
'''
import Tkinter, tkFileDialog 
import previous_state_logging_system
import os, shutil, re

#logger = previous_state_logging_system.Log('gui_components/_GUI_Parameters_.txt')

kwargsValueList = {}
imageProcessingMissionList = []
indexTracker, previousIndex = None, None
missionTypeCounters = [0, 0, 0, 0, 0, 0, 0, 0, 0]
navigationIndex, buoyIndex, pathIndex, maneuveringIndex, torpedoIndex, dropperIndex, pegManipulationIndex, pingerIndex, pickUp = 0,0,0,0,0,0,0,0,0

#All mission and param names must not have spaces in them. Everytime your going to change params or mission names, you need to delete your _Last_Mission_List under the _Saved_Missions_ folder
missionNames = ["Navigation", "Buoy", "Path", "Maneuvering", "Torpedo", "Dropper", "Pinger", "PickUp"]
paramNames = {"{}".format(missionNames[0]):["Waypoint", "IgnoreDesiredOrientation", "HoldPositionTimer", "DrivingMode", "Timeout"],
              "{}".format(missionNames[1]):["CenteringTime", "RamTime", "Timeout"],
              "{}".format(missionNames[2]):["AcceptableAlignmentError", "Timeout"],
              "{}".format(missionNames[3]):["Timeout"],
              "{}".format(missionNames[4]):["Timeout"],
              "{}".format(missionNames[5]):["LiftLidIfExists", "DepthToLiftLid", "DropBallMode", "Timeout"],
              "{}".format(missionNames[6]):["Timeout"],
              "{}".format(missionNames[7]):["Timeout"]}
missionDescription = {missionNames[0]: "Navigation missions allow the vehicle to drive to certain waypoints in a particular way. \n\n"
                      "Parameters:\n\n"
                      "Waypoint-A waypoint that has been previously marked in manual mode pressing the start button.\n\n"
                      "IgnoreDesiredOrientation-Allows the vehicle to not take desired orientation into account when going to a waypoint. This is good when just passing by a waypoint.\n\n"
                      "HoldPositionTimer-How long in seconds to hold the final position until considered a successful mission.\n\n"
                      "DrivingMode-Different ways of how to get to the waypoint.\n" 
                      "    0-Drive Forward\n"
                      "    1-Drive Backwards\n"
                      "    2-Drive Clockwise\n"
                      "    3-Drive Counter Clockwise\n\n"
                      "Timeout-How long in seconds to continue to the next mission.", 
                      missionNames[1]: "Buoy missions use image processing for the top camera to track onto an object and hit it.\n\n"
                      "Parameters:\n\n"
                      "CenteringTime-How long in seconds it takes for the sub to have the buoy in the center of the screen before it enters 'RamMode'.\n\n"
                      "RamTime-How long in seconds to charge towards the buoy.\n\n"
                      "Timeout-How long in seconds to restart the last mission.", 
                      missionNames[2]: "Path missions use image processing for the bottom camera to track onto an object, align with it, and go forward.\n\n"
                      "Parameters:\n\n"
                      "AcceptableAlignmentError-How many degrees can the path be off by before considering it a successful alignment.\n\n"
                      "Timeout-How long in seconds to start the next mission.",
                      missionNames[3]: "", 
                      missionNames[4]: "", 
                      missionNames[5]: "", 
                      missionNames[6]: "", 
                      missionNames[7]: ""}

frontPreviousKwargsValueList, bottomPreviousKwargsValueList = None, None

class MissionSelector:
    '''
    Saves, updates, and retrieves the Mission Selector data. 
    '''
    def __init__(self, window):
        '''
        Initializes the main window as an instance attribute.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.window = window
        
    def updateParamValueLists(self):
        '''
        This function is responsible for updating the parameter and value lists in the mission selector tab when a mission in the mission
        list is highlighted.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return**\n
        '''
        global previousIndex, missionTypeCounters, indexTracker, navigationIndex, buoyIndex, pathIndex, maneuveringIndex, torpedoIndex, dropperIndex, pegManipulationIndex, pingerIndex, pickUp
        
        if (self.window.missionListBox.size() == 0): #If there is nothing in the list

            self.window.paramLabel.config(text = "Parameters")
            self.window.valueLabel.config(text = "Values")
            
            previousIndex = None
        
        for x in range(len(missionNames)):
            if (missionNames[x] in self.window.missionListBox.get("active") and previousIndex != indexTracker):
            
                self.window.discriptionText.config(state = "normal")
                self.window.discriptionText.delete("1.0", "end")
                self.window.discriptionText.insert("insert", missionDescription[missionNames[x]])
                self.window.discriptionText.config(state = "disable")
                
                missionCounter = [int(s) for s in self.window.missionListBox.get("active").split() if s.isdigit()][0]
                
                self.window.paramLabel.config(text = "{} {} Parameters".format(missionNames[x], missionCounter))
                self.window.valueLabel.config(text = "{} {} Values".format(missionNames[x], missionCounter))
                
                self.window.paramListBox.delete(0, "end")
                self.window.valueListBox.delete(0, "end")
                for y in range(len(paramNames[missionNames[x]])):
                    self.window.paramListBox.insert("end", paramNames[missionNames[x]][y])
                    self.window.valueListBox.insert("end", self.getSavedValues("{}{} {}".format(missionNames[x], paramNames[missionNames[x]][y], missionCounter))[0])
                
                previousIndex = indexTracker
                break #Acts as an else if statement
        
        indexTracker = self.window.missionListBox.index("active")
        
    def saveValues(self, name, value):
        '''
        Adds a key and value pair to a dictionary

        **Parameters**: \n
        * **name** - The key name.
        * **value** - The value corresponding to the key.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList
        
        kwargsValueList[name] = value
        
    def getSavedValues(self, *args):
        '''
        Retrieves the value from the key and value pair.
    
        **Parameters**: \n
        * **args** - The key names being asked for.
        
        **Returns**: \n
        * **valueList** - The values corresponding to the keys asked for.\n
        '''
        global kwargsValueList
        
        valueList = []
        for i, name in enumerate(args):
            if kwargsValueList.get(name) == None:
                valueList.append("None") 
            else:
                valueList.append(kwargsValueList.get(name))  
        return valueList
    
    def getAllMissionSelectorData(self):
        '''
        Returns all missions selected, all params, and all values to send over to external process
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **self.window.missionListBox.get(0, 'end')** - All the missions listed.
        * **missionSelectorData.paramValueList** - List containing the missions's parameter values.\n
        '''
        missionSelectorData = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get())).getParameters("paramValueList")
        
        return self.window.missionListBox.get(0, 'end'), missionSelectorData.paramValueList
        
class ImageProcessingMissionSelector:
    '''
    This class handles the image processing aspect of the mission selector system. 
    '''
    def __init__(self, window):
        '''
        Initializes the main window as an instance attribute.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.window = window
        
    def writeIPValuesToFile(self, camera):
        '''
        Saves the HSV values being searched in each mission.
        
        **Parameters**: \n
        * **camera** - String declaring whether it's the front or bottom camera.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global frontPreviousKwargsValueList, bottomPreviousKwargsValueList
        
        #Removing space in the drop down box value
        imageProcessingDropDownListValue = self.window.dropBoxImageProcessingValue.get().replace(" ", "") 
        
        frontKwargsValueList={'minHueFront': self.window.filterScales[0].get(), 'minSatFront': self.window.filterScales[1].get(), 'minValFront': self.window.filterScales[2].get(), 
                              'maxHueFront': self.window.filterScales[3].get(), 'maxSatFront': self.window.filterScales[4].get(), 'maxValFront': self.window.filterScales[5].get(), 
                              'operation1Front': self.window.filterScales[6].get(), 'iteration1Front': self.window.filterScales[7].get(), 'epsilonFront': self.window.filterScales[8].get(), 'minCurvesFront': self.window.filterScales[9].get(), 'maxCurvesFront': self.window.filterScales[10].get()}
        
        bottomKwargsValueList={'minHueBottom': self.window.filterScales[11].get(), 'minSatBottom': self.window.filterScales[12].get(), 'minValBottom': self.window.filterScales[13].get(), 
                               'maxHueBottom': self.window.filterScales[14].get(), 'maxSatBottom': self.window.filterScales[15].get(), 'maxValBottom': self.window.filterScales[16].get(), 
                               'operation1Bottom': self.window.filterScales[17].get(), 'iteration1Bottom': self.window.filterScales[18].get(), 'epsilonBottom': self.window.filterScales[19].get(), 'minCurvesBottom': self.window.filterScales[20].get(), 'maxCurvesBottom': self.window.filterScales[21].get()}
          
        #Checks if values are for front camera and check if sliders have been moved
        if camera == "Front" and frontKwargsValueList != frontPreviousKwargsValueList:

            tempList = {imageProcessingDropDownListValue+"Front": frontKwargsValueList}
            
            #Writing image processing mission list
            previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get())).writeParameters(**tempList)
            
            frontPreviousKwargsValueList = frontKwargsValueList
                
        if camera == "Bottom" and bottomKwargsValueList != bottomPreviousKwargsValueList:
            
            tempList = {imageProcessingDropDownListValue+"Bottom": bottomKwargsValueList}
            
            #Writing image processing mission list
            previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get())).writeParameters(**tempList)
            
            bottomPreviousKwargsValueList = bottomKwargsValueList
    
    def updateIPSliders(self):
        '''
        Updates the the HSV values being searched according to the current mission.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return**\n
        '''
        #Gets the logging file of the user
        missionListLog = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get())) 
        
        #Removing space in the drop down box value
        imageProcessingDropDownName = self.window.dropBoxImageProcessingValue.get().replace(" ", "")
        
        #Get all value objects in file that consist of the current IP drop down lost value with a Front/Bottom added to it
        frontValues = missionListLog.getParameters(imageProcessingDropDownName+"Front")
        bottomValues = missionListLog.getParameters(imageProcessingDropDownName+"Bottom")
        
        #Obtain actual values from objects
        frontKwargsValues = getattr(frontValues, self.window.dropBoxImageProcessingValue.get().replace(" ", "")+"Front") #Can not call method with string with dot operator, this is an elegant solution to this
        bottomKwargsValues = getattr(bottomValues, self.window.dropBoxImageProcessingValue.get().replace(" ", "")+"Bottom") #Can not call method with string with dot operator, this is an elegant solution to this
        
        if frontKwargsValues != 0:
            frontImageProcValues = [frontKwargsValues["minHueFront"], frontKwargsValues["minSatFront"], frontKwargsValues["minValFront"], frontKwargsValues["maxHueFront"], frontKwargsValues["maxSatFront"], frontKwargsValues["maxValFront"], 
                                    frontKwargsValues["operation1Front"], frontKwargsValues["iteration1Front"], frontKwargsValues["epsilonFront"], frontKwargsValues["minCurvesFront"], frontKwargsValues["maxCurvesFront"]]
        
            for x in range(len(frontImageProcValues)):
                self.window.filterScales[x].set(frontImageProcValues[x]) #Iterate through filter list for front camera and set sliders
        
        if bottomKwargsValues != 0:  
            bottomImageProcValues = [bottomKwargsValues["minHueBottom"], bottomKwargsValues["minSatBottom"], bottomKwargsValues["minValBottom"], bottomKwargsValues["maxHueBottom"], bottomKwargsValues["maxSatBottom"], bottomKwargsValues["maxValBottom"],
                                     bottomKwargsValues["operation1Bottom"], bottomKwargsValues["iteration1Bottom"], bottomKwargsValues["epsilonBottom"], bottomKwargsValues["minCurvesBottom"], bottomKwargsValues["maxCurvesBottom"]]
            
            for x in range(len(bottomImageProcValues)):
                self.window.filterScales[x+len(bottomImageProcValues)].set(bottomImageProcValues[x])
        
        
        #These statements make it so that when the IP drop down list is changed, is won't copy over the values from the previous drop down value
        numOfImageProcValueElements = 11 #Number of elements in frontImageProcValues or bottomImageProcValues (assuming they are the same size)
        if frontKwargsValues == 0:
            for x in range(numOfImageProcValueElements):
                self.window.filterScales[x].set(0)
                    
        if bottomKwargsValues == 0:  
            for x in range(numOfImageProcValueElements):
                self.window.filterScales[x+numOfImageProcValueElements].set(0)
                
    
    def updateIPDropDownList(self, *missionName):
        '''
        Updates the drop-down list in the Image Processing tab with the new missions.
        
        **Parameters**: \n
        * **missionName** - One or multiple strings with the names of missions being added.
        
        **Returns**: \n
        * **No Return**\n
        '''
        menu = self.window.optionMenu["menu"]
        
        if len(self.window.missionListBox.get(0, "end")) > 0:
            menu.delete(0, "end")
            for string in self.window.missionListBox.get(0, "end"):
                menu.add_command(label=string, command=lambda value=string:self.window.dropBoxImageProcessingValue.set(value))
              
            if len(missionName)>0:
                if missionName[0] != "None":
                    for x in range(len(self.window.missionListBox.get(0, "end"))):
                        if missionName[0] in self.window.missionListBox.get(0, "end")[x]:
                            self.window.dropBoxImageProcessingValue.set(self.window.missionListBox.get(0, "end")[x])
                            break
                else:
                    self.window.dropBoxImageProcessingValue.set(self.window.missionListBox.get(0, "end")[0])
            else:
                self.window.dropBoxImageProcessingValue.set(self.window.missionListBox.get(0, "end")[0])
            
        else:
            menu.delete(0, "end")
            self.window.dropBoxImageProcessingValue.set("")
            
class PreviousMissionListLogging:
    '''
    Exports and loads the mission list from previous sessions automatically from different user accounts. This is not to be confused with the
    export and load classes when the buttons are pressed so that the user can manually export and save missions
    '''
    
    def __init__(self, window):
        '''
        Initializes the main window as an instance attribute.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.window = window
        self.log = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()))
        
    def export(self):
        '''
        Saves the parameters for the current mission list or user.
        
        **Parameters**: \n
        * **No Input Parameters**
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList
        if not os.path.exists('_Saved_Missions_'):
            os.mkdir('_Saved_Missions_')
        
        try:
            self.log.writeParameters(missionList = str(self.window.missionListBox.get(0, "end")), paramValueList = kwargsValueList)
        except:
            pass
        
    def load(self, name):
        '''
        Updates the parameters to those of the desired mission list or user.
        
        **Parameters**: \n
        * **name** - The mission list or user name.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList, missionNames
        
        #Get rid of everything
        kwargsValueList = {}
        self.window.missionListBox.delete(0, "end")
        self.window.paramListBox.delete(0, "end")
        self.window.valueListBox.delete(0, "end")
        
        try:
            if not os.path.exists('_Saved_Missions_'):
                os.mkdir('_Saved_Missions_')
                        
            values = MissionSelector(self.window)

            logValues = self.log.getParameters("missionList", "paramValueList")
            savedMissionTypes = logValues.missionList
            savedMissionValues = logValues.paramValueList
            
            
            for x in range(len(savedMissionTypes)):
                self.window.missionListBox.insert(x, savedMissionTypes[x])
            for i, name in enumerate(savedMissionValues.keys()):
                values.saveValues(name, savedMissionValues[name])
                
            #Increments iteration counter when variable is loaded so when the same type of mission that was loaded in is added again, it wont forget to count the ones the user loaded in
            for x in range(self.window.missionListBox.size()):
                name = ''.join([i for i in self.window.missionListBox.get(x) if not i.isdigit()]).rstrip().partition(' ')[0]
                for y in range(len(missionNames)):
                    if name in missionNames[y]:
                        missionTypeCounters[y]+=1
              
            #Selects the first element on the list
            self.window.missionListBox.selection_set(0) 
            
        except:
            print "{} does not have a mission list from last session.".format(name)
            
  
#Needs to be a class since this piece of code is being activated by a widget in Tkinter
class MissionSelectorType:
    '''
    Allows the ability to select which mission type is desired when pressing the add button.
    '''
    def __init__(self, window, missionListBox):
        '''
        Initializes the main window as an instance attribute and sets up the pop-up for choosing the mission type. 
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        * **missionListBox** - TKinter listbox containing the saved missions.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global missionNames
        self.missionListBox = missionListBox
        self.window = window
        
        #Pop up window object and size
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("285x35+690+250")
        self.top.focus()

        #Pop up window
        missionLabel = Tkinter.Label(self.top, text = "Select a mission type:")
        missionLabel.grid(row = 0, column = 0)
        self.value = Tkinter.StringVar(self.top)
        self.value.set(missionNames[0]) # default value
        options = Tkinter.OptionMenu(self.top, self.value, *missionNames)
        options.grid(row = 0, column = 1)
        options.bind("<Button-1>", self.refresh) #This is to stop the gui from flickering
        self.top.bind("<Return>", self.ok) #Allows me to push enter instead of push OK if desired
        okButton = Tkinter.Button(self.top, text = "OK", command = self.ok)
        okButton.grid(row = 0, column = 2)
        
        
    def ok(self, *event):
        '''
        Inserts the new mission to the Mission Listbox with the appropriate index.
        
        **Parameters**: \n
        * **event** - Clicking the OK button on the pop-up or pressing enter.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global missionTypeCounters, missionNames
        
        for x in range(len(missionNames)):
            if self.value.get() == missionNames[x]:
                index = x
                missionTypeCounters[index]+=1
                #print self.value.get()+" 1", self.window.missionListBox.get(0, "end")
                if self.window.missionListBox.size() == 0:
                    missionTypeCounters[index] = 1
                
                #This block of code will make sure that the mission listbox will contain mission types with the lowest number
                for y in range(missionTypeCounters[index]+1):
                    if self.value.get()+" {}".format(y+1) not in self.window.missionListBox.get(0, "end") and self.window.missionListBox.size() != 0:
                        missionTypeCounters[index] -= (missionTypeCounters[index] - (y+1))
                        break
                
                #This block of code will make sure that the mission listbox will NOT contain mission types with duplicate numbers
                while self.value.get()+" "+str(missionTypeCounters[index]) in self.window.missionListBox.get(0, "end"):
                    missionTypeCounters[index]+=1
                        
        self.missionListBox.insert("end", self.value.get()+" "+str(missionTypeCounters[index]))   
        self.top.destroy()
        
        #Highlights and activates the last entry in the list
        self.window.missionListBox.select_clear(0, "end")
        self.window.missionListBox.select_set("end")
        self.window.missionListBox.activate("end")
        
        #Updating image processing list
        ImageProcessingMissionSelector(self.window).updateIPDropDownList()
        
        #Logs data in list to bring up last session when program restarts
        PreviousMissionListLogging(self.window).export()
        
    def refresh(self, *event):#This is to stop the gui from flickering
        '''
        Prevents the GUI from flickering.
        
        **Parameters**: \n
        * **event** - Clicking the mission type drop down.
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.window.update()
        
#Needs to be a class since this piece of code is being activated by a widget in Tkinter
class MissionSelectorValues:
    '''
    Allows the ability to select what values are desired when double clicking the items in the value list.
    '''
    def __init__(self, event, args):
        '''
        Sets up the pop-up for changing the desired value.
        
        **Parameters**: \n
        * **event** - Double-clicking on the parameter name
        * **args** - List containg the main window, the value listbox, and the parameter listbox.
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.window = args[0]
        self.valueListBox = args[1]
        self.paramListBox = args[2]
        
        
        #Pop up window object and size
        self.top = Tkinter.Toplevel(self.window)
        self.top.geometry("230x35+690+250")
        
        #Pop up window
        valueLabel = Tkinter.Label(self.top, text = "New Value: ")
        valueLabel.grid(row = 0, column = 0)
        self.valueEntry = Tkinter.Entry(self.top)
        self.valueEntry.grid(row = 0, column = 1)
        self.valueEntry.focus()
        self.top.bind("<Return>", self.ok) #Allows me to push enter instead of push OK if desired
        okButton = Tkinter.Button(self.top, text = "OK", command = self.ok)
        okButton.grid(row = 0, column = 2)
        
    def ok(self, *events):
        '''
        Updates and saves the new parameter value.
        
        **Parameters**: \n
        * **events** - Pressing enter or clicking OK on the pop-up.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList, missionTypeCounters, indexTracker, navigationIndex, buoyIndex, pathIndex, maneuveringIndex, torpedoIndex, dropperIndex, pegManipulationIndex, pingerIndex, pickUp
        
        values = MissionSelector(self.window)
        
        index = self.valueListBox.index("active")
        self.valueListBox.delete("active")
        try:
            if re.search('[a-zA-Z]', self.valueEntry.get()): #Checks if there are any letters in string
                newValue = self.valueEntry.get()
                
            elif float(self.valueEntry.get()).is_integer(): #Converst to int (no decimals)
                newValue = int(self.valueEntry.get())
            
            else:
                newValue = float(self.valueEntry.get())
        except:
            newValue = "Error"
            
        self.valueListBox.insert(index, newValue)
        
        missionCounter = [int(s) for s in self.window.missionListBox.get("active").split() if s.isdigit()][0]
        
        for x in range(len(missionNames)):
            if missionNames[x] in self.window.paramLabel.cget("text"): #If the parameter label name above the listbox equals "Navigation Parameters"
                for y in range(len(paramNames[missionNames[x]])):
                    if self.paramListBox.get(index) == paramNames[missionNames[x]][y]: #Once a value is selected, that index is put into the paramListBox.
                        values.saveValues("{}{} {}".format(missionNames[x], paramNames[missionNames[x]][y], missionCounter), newValue) #Save the values in an appending dictionary
                break #Acts like an else if statement
                
        #Logs data in list to bring up last session when program restarts
        PreviousMissionListLogging(self.window).export()
        
        self.top.destroy()
  
#Needs to be a class since this piece of code is being activated by a widget in Tkinter      
class MoveUpDown:
    '''
    Allows the ability change the order in which missions are executed when pressing the up or down button. This will also change 
    the order in the image processing drop down list in the image processing tab.
    '''
    def moveUp(self, window):
        '''
        Moves the selected mission up one slot in the mission list.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        #kwargsValueList = {key: value for key,value in kwargsValueList.iteritems() if window.missionListBox.index("active") not in key}
        #print kwargsValueList
        
        pos = window.missionListBox.index("active")
        if pos == 0: #Cant go any higher
            return #Break out of function
        missionTypeName = window.missionListBox.get(pos)
        window.missionListBox.delete(pos)
        window.missionListBox.insert(pos-1, missionTypeName)
        window.missionListBox.select_clear(pos-1)
        window.missionListBox.select_set(pos-1)
        window.missionListBox.activate(pos-1)
        
        #Updating image processing list
        ImageProcessingMissionSelector(window).updateIPDropDownList()
        
        #Logs data in list to bring up last session when program restarts
        PreviousMissionListLogging(window).export()
        
    def moveDown(self, window):
        '''
        Moves the selected mission down one slot in the mission list.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        #kwargsValueList = {key: value for key,value in kwargsValueList.iteritems() if window.missionListBox.index("active") not in key}
        #print kwargsValueList
        
        pos = window.missionListBox.index("active")
        if pos == window.missionListBox.size()-1: #Cant go any lower
            return #Break out of function
        missionTypeName = window.missionListBox.get(pos)
        window.missionListBox.delete(pos)
        window.missionListBox.insert(pos+1, missionTypeName)
        window.missionListBox.select_clear(pos+1)
        window.missionListBox.select_set(pos+1)
        window.missionListBox.activate(pos+1)
        
        #Updating image processing list
        ImageProcessingMissionSelector(window).updateIPDropDownList()
        
        #Logs data in list to bring up last session when program restarts
        PreviousMissionListLogging(window).export()

#Needs to be a class since this piece of code is being activated by a widget in Tkinter      
class DeleteMissionType:
    '''
    Allows the ability to press the delete button to delete missions from both the mission list and the image processing drop down list. 
    This will also remove the values in the logging system so that when missions are added back, you get to select mission and image 
    processing values from scratch.
    '''
    def __init__(self, window):
        '''
        Deletes the currently selected mission.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList, missionTypeCounters, previousIndex
        
        if window.missionListBox.size() > 0: #If there is something to delete
            number = str([int(s) for s in window.missionListBox.get("active").split() if s.isdigit()][0])
            name = ''.join([i for i in window.missionListBox.get("active") if not i.isdigit()]).rstrip().partition(' ')[0] #rstrip removes extra space, partition(' ')[0] just takes first word if the string is two words (peg manipulation)
                 
            #This line creates a new list but without any of the params or values saved from before that is associated with the mission type you deleted.
            #It is important to note that this method is assuming you stick to the naming convention of button the mission types name before each variable when you save it.
            print kwargsValueList
            kwargsValueList = {key: value for key,value in kwargsValueList.iteritems() if name not in key or number not in key}
            print kwargsValueList
            #Decrements iteration counter when variable is deleted so next time when the same type of mission that was deleted is added again, it wont count the one the user deleted
            for x in range(len(missionNames)): 
                if name in missionNames[x].lower():
                    missionTypeCounters[x]-=1
            
            #Delete lines in file
            f = open("_Saved_Missions_/_Last_Mission_List_({})".format(window.lastUser.get()), "r")
            lines = f.readlines()
            f.close()
            f = open("_Saved_Missions_/_Last_Mission_List_({})".format(window.lastUser.get()), "w")
            for line in lines:
                if window.missionListBox.get("active").replace(" ", "")+"Front" not in line and window.missionListBox.get("active").replace(" ", "")+"Bottom" not in line:
                    f.write(line)
            f.close()
            
            #If I didn't set previousIndex to None, the new variable would fall into the same index as the one I just deleted. 
            #This means I would not be able to view missions params or values because of the checks I do in MissionSelector class        
            previousIndex = None  
            index = window.missionListBox.index("active")
            window.missionListBox.delete(index)
            window.paramListBox.delete(0, "end")
            window.valueListBox.delete(0, "end") 
            window.missionListBox.selection_set("active") #Highlights the mission type that is now in the place of the last mission type
            
            #Updating image processing list
            ImageProcessingMissionSelector(window).updateIPDropDownList()
            
            #Logs data in list to bring up last session when program restarts
            PreviousMissionListLogging(window).export()

#Needs to be a class since this piece of code is being activated by a widget in Tkinter       
class ExportList:
    '''
    Allows the ability to export both the mission/parameter/value lists and the image processing drop down list and values by
    clicking on the export button.
    '''
    def __init__(self, window):
        '''
        Sets up the pop-up for naming the copy of the current parameters.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        #Pop up window object and size
        self.top = Tkinter.Toplevel(window)
        self.top.geometry("220x35+690+250")
        self.window = window
        
        #Pop up window
        missionLabel = Tkinter.Label(self.top, text = "File name:")
        missionLabel.grid(row = 0, column = 0)
        self.userInput = Tkinter.Entry(self.top)
        self.userInput.grid(row=0, column=1)
        self.userInput.focus_set()
        self.top.bind("<Return>", self.ok) #Allows me to push enter instead of push OK if desired
        okButton = Tkinter.Button(self.top, text = "OK", command = self.ok)
        okButton.grid(row = 0, column = 2)
        
        #Make file if not exist
        if not os.path.exists('_Saved_Missions_'):
            os.mkdir('_Saved_Missions_')
        
    def ok(self, *event):
        '''
        Saves the current parameters to the specified file in Saved Missions.
        
        **Parameters**: \n
        * **event** - Pressing enter or clicking OK on the pop-up.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList
        
        #Copying data from _Last_Mission_List_ to saved file
        shutil.copy('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()), '_Saved_Missions_/'+self.userInput.get())

        self.top.destroy()

#Needs to be a class since this piece of code is being activated by a widget in Tkinter       
class loadList:
    '''
    Allows the ability to load in both the mission/parameter/value lists and the image processing drop down list and values by
    clicking on the load button.
    '''
    def __init__(self, window):
        '''
        Loads the parameters from the desired mission list.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global kwargsValueList, missionNames
        fileLocation = tkFileDialog.askopenfilename()
        
        try:
            log = previous_state_logging_system.Log(fileLocation)
            values = MissionSelector(window)
            
            
            logValues = log.getParameters("missionList", "paramValueList")
            savedMissionTypes = logValues.missionList #Need a literal eval or else ill be getting characters
            savedMissionValues = logValues.paramValueList
            
            #Get rid of everything
            kwargsValueList = {}
            window.missionListBox.delete(0, "end")
            window.paramListBox.delete(0, "end")
            window.valueListBox.delete(0, "end")
    
            for x in range(len(savedMissionTypes)):
                window.missionListBox.insert(x, savedMissionTypes[x])
            for i, name in enumerate(savedMissionValues.keys()):
                values.saveValues(name, savedMissionValues[name])
                
            #Increments iteration counter when variable is loaded so when the same type of mission that was loaded in is added again, it wont forget to count the ones the user loaded in
            for x in range(window.missionListBox.size()):
                name = ''.join([i for i in window.missionListBox.get(x) if not i.isdigit()]).rstrip().partition(' ')[0]
                for y in range(len(missionNames)):
                    if name in missionNames[y]:
                        missionTypeCounters[y]+=1
            
            #Copying data from saved file to _Last_Mission_List_ 
            shutil.copy(fileLocation, '_Saved_Missions_/_Last_Mission_List_({})'.format(window.lastUser.get()))
            
            window.missionListBox.selection_set(0) #Selects the first element on the list
            
            #Updating image processing list
            ImageProcessingMissionSelector(window).updateIPDropDownList()
            
            #Logs data in list to bring up last session when program restarts
            PreviousMissionListLogging(window).export()
                
        except:
            print "Can't open file."

