'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_sib
   :synopsis: Handles the missions the Sub will perform.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on May 29, 2015
:Description: Receives mission parameters from the GUI Mission Selector and performs missions accordingly.
'''
import main.gui_components.previous_state_logging_system as previous_state_logging_system
import main.utility_package.utilities as utilities
import time
from main.external_devices.movement import JoystickMovementController,\
    MovementController


class missions:
    '''
    Contains all the behaviors the sub will take on while on each individual mission.
    '''
    def __init__(self):
        '''
        Initializes the variables used across all missions, such as thrusters, index counters, and mission outcomes.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #These values will be updated by the updateMissions function
        self.missionSelectorMissions = None 
        self.missionSelectorParams = {}
        self.missionSelectorParamsTemp = {}
        self.movementController = None
        self.imageProcValues = None
        self.dvlData = None
        self.ahrsData = None
        self.medianDepth = None
        self.arduinoCom = None
        
        #Update this value when you think mission was a success
        self.missionSuccessful = False 
        
        #Determines what mission is currently being executed in the function executeMissions
        self.missionIndex = 0
        
        #Updates the GUI of what the thruster duty cycles are
        self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
        
        #Sends flags to the image processing module of update GUI
        self.flagsToGUI = [False, False, False]
        
        #General initializer for any function to use. Gets reset after a mission is successful so another mission can reuse these variables
        self.subsetParams = {}
        self.completedMissionSelectorParams = {}
        self.initialize = True
        self.desiredMissionOrientation = [False, 0, 0, 0, 0]
        self.desiredMissionPosition = [False, 0, 0, 0]
        
        
        #DROPPER EVENT
        self.dropperCounter = 0 #This variable is not in __initializeDropper__() because it needs to be maintained throughout all the events. This counter will let me know how many bins I've gone to so that when I found the one with the lid, I know how many missions to skip
        
        self.__initializeNavigation__()
        self.__initializeBuoys__()
        self.__initializePath__()
        self.__initializeDropper__()
        self.__initializeTorpedoes__()
        
    def __initializeNavigation__(self):
        '''
        Initializes the variables and loads the parameters used in Navigations missions.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #NAVIGATION
        #Put navigation instance variables here
        self.holdPositionTimer = utilities.Timer()
        lastUserLog = previous_state_logging_system.Log('_Saved_Settings_/_Last_User_.txt')
        lastUserValue = lastUserLog.getParameters("lastUser").lastUser #Get the lastUser variable in file
        missionSelectorData = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(lastUserValue))
        
        self.navigationTimeout = utilities.Timer()
        self.waypointList = missionSelectorData.getParameters("waypoints").waypoints #Will be a 0 if no waypoints are in list
        
    def __initializeBuoys__(self):
        '''
        Initializes the variables and loads the parameters used in Buoy missions.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #BUOYS
        #Put buoy instance variables here
        self.desiredPose = []
        self.initializeBuoyPose = True
        self.previouslyTracked = False
        self.goStraightFlag = False
        self.desiredAdjustmentsPoseForGui = [False, 0, 0, 0, 0]
        self.buoyInCenterTimer = utilities.Timer()
        self.noBuoySeenTimer = utilities.Timer()
        self.buoyTimeout = utilities.Timer()
        self.previousTrackTimer = utilities.Timer() #Because the previous mission carries over to the next mission, you need to give the main process thread some time to update its image processing values
        self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = False, False, False, False, False, False, False, False
        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = False, False, False, False, False, False, False, False
        
    def __initializePath__(self):
        '''
        Initializes the variables and loads the parameters used in Path missions.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #PATH
        self.desiredPose = []
        self.initializePathPose = True
        self.previouslyTracked = False
        self.goStraightFlag = False
        self.desiredAdjustmentsPoseForGui = [False, 0, 0, 0, 0]
        self.pathInCenterTimer = utilities.Timer()
        self.noPathSeenTimer = utilities.Timer()
        self.pathTimeout = utilities.Timer()
        self.previousTrackTimer = utilities.Timer() #Because the previous mission carries over to the next mission, you need to give the main process thread some time to update its image processing values
        self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = False, False, False, False, False, False, False, False
        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = False, False, False, False, False, False, False, False
     
    def __initializeTorpedoes__(self):
        '''
        Initializes the variables and loads the parameters used in Torpedoe missions.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        #TORPEDO 
        self.desiredPose = []
        self.smallSquaresCounter = 0
        self.bigSquaresCounter = 0
        self.axis1 = 0
        self.startDistanceAway = 0
        self.foundAllFour = False
        self.targetSeen = False
        self.initializeTorpedoPose = True
        self.initialServoSend = True
        self.previouslyTracked = False
        self.goStraightFlag = False
        self.completedUpperLeftSmallSquare = False
        self.completedUpperRightBigSquare = False
        self.completedBottomLeftBigSquare = False
        self.completedBottomRightSmallSquare = False
        self.desiredAdjustmentsPoseForGui = [False, 0, 0, 0, 0]
        self.desiredMoveDepth = None
        self.desiredMovePitch = None
        self.desiredMoveYaw = None
        self.desiredMoveRoll = None
        self.torpedoTargetsInCenterTimer = utilities.Timer()
        self.noTorpedoTargetSeenTimer = utilities.Timer()
        self.torpedoTimeout = utilities.Timer()
        self.previousTrackTimer = utilities.Timer()
        self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = False, False, False, False, False, False, False, False
        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = False, False, False, False, False, False, False, False
        
        
    def __initializeDropper__(self):
        '''
        Initializes the variables and loads the parameters used in Dropper missions.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #DROPPER
        self.desiredPose = []
        self.initializeDropperPose = True
        self.initialServoSend = True
        self.hookLidFlag = False
        self.desiredAdjustmentsPoseForGui = [False, 0, 0, 0, 0]
        self.dropperInCenterTimer = utilities.Timer()
        self.noDropperSeenTimer = utilities.Timer()
        self.dropperTimeout = utilities.Timer()
        self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = False, False, False, False, False, False, False, False
        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = False, False, False, False, False, False, False, False
        
    def updateMissions(self, missionSelectorData, movementController, joystickMovementController, lockedMovementController, imageProcValues, dvlData, ahrsData, medianDepth, arduinoCom): #This function is getting called in the _navigation_management_system to update important values used to complete the missions
        '''
        Updates the mission data, sensor data, image processing values, and controller objects. It then checks if all the data went through.
        
        **Parameters**: \n
        * **missionSelectorData** - Mission names and parameters obtained from the GUI.
        * **movementController** - Object which handles sub movement.
        * **joystickMovementController** - Object which handles sub movement in a more rudimentary manner.
        * **lockedMovementController** - Contains various types of movement for the Sub in autonomous mode, including an advanced move for  using NESW coordinates.
        * **imageProcValues** - Image processing values taken with current mission parameters.
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **arduinoCom** - Serial object for Arduino controlling the dropper.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.arduinoCom = arduinoCom
        self.missionSelectorData = missionSelectorData
        self.missionSelectorMissions, self.missionSelectorParams = self.missionSelectorData #self.missionSelectorMissions and self.missionSelectorParams will continue to be the same until the user changes anything into the mission list or params and selects "Start Vehicle".
        self.movementController = movementController #Controller object for moving the vehicle
        self.joystickMovementController = joystickMovementController #Using joystick movement cmds
        self.lockedMovementController = lockedMovementController#Locked move with coordindates
        self.imageProcValues = imageProcValues #trackBoxFrontImg, trackBoxBottomImg, shape_centerFrontImg, shape_centerBottomImg, targetsFrontImg, targetsBottomImg
        self.dvlData = dvlData #Position, velocity, orientation, misc
        self.ahrsData = ahrsData #Yaw, pitch, roll
        self.medianDepth = medianDepth #Depth in feet
        
        self.sensorDataExsists = self.missionSelectorParams != None and self.movementController != None and self.imageProcValues != None and self.dvlData != None and self.ahrsData != None and self.medianDepth != None #If these values successfully made it through the pipe, continue with the mission
        
    def executeMissions(self):
        '''
        Updates the mission data, sensor data, image processing values, and controller objects. It then checks if all the data went through.
        
        **Parameters**: \n
        * **No Input Parameters*
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #Creates a subset params list of the master params list for the according mission type
        def initializer(missionType):
            '''
            Initializes the parameters for the desired mission, and returns the desired orientation and thruster PWM based on the mission criteria.
            
            **Parameters**: \n
            * **missionType** - String naming the type of mission being performed.
            
            **Returns**: \n
            * **self.thrusterPWMs** - Movement object setting the thruster direction and speed through PWM.
            * **self.missionSelectorMissions[self.missionIndex]** - The current mission parameters.
            * **self.desiredMissionOrientation** - The heading, pitch, and roll values the sub will try to maintain.\n
            '''
            if self.initialize == True:
                #INITIALIZERS
                self.subsetParams = {} #Clear subsetParams for next mission param list
                self.__initializeBuoys__()
                self.__initializeNavigation__()
                self.__initializePath__()
                self.__initializeDropper__()
                self.__initializeTorpedoes__()
                
                #This block of code will loop through all of the parameters taking each key and value and store them in a list catered just towards Navigation
                identifierNum = self.missionSelectorMissions[self.missionIndex].partition(' ')[-1] #Tells what number the navigation is so I can select the params from the entire param list accordingly. #partition(' ')[0] takes first word/number of the string separated by a space
                if len(self.missionSelectorParamsTemp) != 0:
                    self.missionSelectorParams = self.missionSelectorParamsTemp
                    
                self.missionSelectorParamsTemp = {}
                for x in range(len(self.missionSelectorParams)):
                    
                    key, value = self.missionSelectorParams.popitem()
                    
                    if missionType in key and int(identifierNum) == int(key.partition(' ')[-1]): #If the word "Navigation" and the identifierNum is in the key...
                        self.subsetParams[key.partition(' ')[0].replace(missionType, "")] = value #partition(' ')[0] takes first word/number of the string separated by a space. replace("Navigation", "") removes Navigation from the string
                    #else: #Otherwise, put keys and values back into dictionary
                    self.missionSelectorParamsTemp[key] = value
                        
                self.initialize = False
                
                
            
        if self.missionSuccessful == True:
            self.missionIndex += 1 #Increments a counter that goes to the next mission in the mission list when a mission is successful
            self.missionSuccessful = False #Restarts missionSuccessful flag for the next mission
            self.initialize = True #Initialize the next missions params list
                
        if len(self.missionSelectorMissions) > 0 and self.missionIndex < len(self.missionSelectorMissions): 
            if "Navigation" in self.missionSelectorMissions[self.missionIndex]:
                initializer("Navigation")
                self.desiredMissionOrientation = self.navigation(self.subsetParams, self.movementController, self.dvlData, self.ahrsData, self.medianDepth, self.waypointList)
                
            elif "Buoy" in self.missionSelectorMissions[self.missionIndex]:
                initializer("Buoy")
                self.desiredMissionOrientation = self.buoy(self.subsetParams, self.joystickMovementController, self.movementController, self.imageProcValues, self.dvlData, self.ahrsData, self.medianDepth)
               
            elif "Path" in self.missionSelectorMissions[self.missionIndex]:
                initializer("Path")
                self.desiredMissionOrientation = self.path(self.subsetParams, self.joystickMovementController, self.imageProcValues, self.dvlData, self.ahrsData, self.medianDepth)
            
            elif "Dropper" in self.missionSelectorMissions[self.missionIndex]:
                initializer("Dropper")   
                self.desiredMissionOrientation = self.dropper(self.subsetParams, self.joystickMovementController, self.imageProcValues, self.dvlData, self.ahrsData, self.medianDepth)
                
            elif "Torpedo" in self.missionSelectorMissions[self.missionIndex]:
                initializer("Torpedo")   
                self.desiredMissionOrientation = self.torpedo(self.subsetParams, self.movementController, self.joystickMovementController, self.imageProcValues, self.dvlData, self.ahrsData, self.medianDepth)

                
            return self.thrusterPWMs, self.missionSelectorMissions[self.missionIndex], self.desiredMissionOrientation #The executeMissions function returns anything useful that the GUI may want to have access to
            
        else:
            print "All missions completed!!!"
            self.thrusterPWMs = self.movementController.move(1, 1, 1, 1, 1, 1)
            return self.thrusterPWMs, "None", [False, 0, 0, 0, 0]
            
    def navigation(self, navigationParams, movementController, dvlData, ahrsData, medianDepth, waypointList):
        '''
        Sets the thruster PWM necessary to orient and get the Sub to its desired waypoint.
        
        **Parameters**: \n
        * **navigationParams** - Parameters including the waypoint, whether to arrive in a certain orientation, end timer, driving mode, and timeout.
        * **movementController** - Object for controlling the sub's movement.
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **waypointList** - List of waypoints and their coordinates.
        
        **Returns**: \n
        * **[True, desiredMissionYaw, desiredPose[1], desiredPose[2], desiredPose[4]]** - Pose data for self.desiredMissionOrientation. \n
        '''
        if self.sensorDataExsists:
            #print "navigation params: ", navigationParams
            #print "navigation waypoints: ", waypointList
            netNavigationTimeout = self.navigationTimeout.netTimer(self.navigationTimeout.cpuClockTimeInSeconds())
            if netNavigationTimeout <= navigationParams["Timeout"]:
                
                userWaypointString = navigationParams['Waypoint'] #The string that the user entered into the mission selector to ask for the waypoint that was logged previously 
                desiredPosition, desiredOrientation, desiredDepth =  waypointList[str(userWaypointString)]
                
                desiredYaw, desiredPitch, desiredRoll = desiredOrientation[0], desiredOrientation[1], desiredOrientation[2]
                desiredX, desiredY, desiredZ = desiredPosition[1], desiredPosition[2], desiredPosition[0]
                desiredY = desiredDepth #Comment out this line if wanting to use DVL Depth
                desiredPose = [desiredYaw, desiredPitch, desiredRoll, desiredX, desiredY, desiredZ]
                
                currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                currentY = medianDepth #Comment out this line if wanting to use DVL Depth
                currentPose = [currentYaw, currentPitch, currentRoll, currentX, currentY, currentZ]
                
                #print "Current Pose: ", currentPose
                #print "Desired Pose: ", desiredPose
                
                
                #movementController.faceInWaypointDirection = True
                #print desiredX, desiredY, desiredZ
                self.thrusterPWMs, error, desiredMissionYaw = movementController.advancedMove(currentPose, desiredX, desiredY, desiredZ, desiredPitch, desiredYaw, desiredRoll, navigationParams['DrivingMode'])
                
                xError, yError, zError = error[0], error[1], error[2]
                pitchError, yawError, rollError = error[3], error[4], error[5]
                
                netHoldPositionTimer = self.holdPositionTimer.netTimer(self.holdPositionTimer.cpuClockTimeInSeconds())
                if navigationParams['IgnoreDesiredOrientation'] == 0:
                    if abs(xError) < 1 and abs(yError) < 1 and abs(zError) < 1 and abs(pitchError) < 6 and abs(yawError) < 5 and abs(rollError) < 5:
                        if netHoldPositionTimer >= navigationParams['HoldPositionTimer']:
                            self.missionSuccessful = True
                    else:
                        self.holdPositionTimer.restartTimer()
                else:
                    if abs(xError) < 1 and abs(yError) < 1 and abs(zError) < 1:
                        if netHoldPositionTimer >= navigationParams['HoldPositionTimer']:
                            self.missionSuccessful = True
                    else:
                        self.holdPositionTimer.restartTimer()
                #print desiredMissionYaw, desiredYaw
                return [True, desiredMissionYaw, desiredPose[1], desiredPose[2], desiredPose[4], desiredX, desiredY, desiredZ]
            
            else: #Timeout, just go to next mission
                self.missionSuccessful = True 
            
        else: #What to do if vehicle can't get proper data to execute the mission
            print "navigation() sensorDataExsists check failed"
            
            return [False, 0, 0, 0, 0, 0, 0, 0]
    
    def buoy(self, buoyParams, joystickMovementController, imageProcValues, dvlData, ahrsData, medianDepth):
        '''
        Detects the correctly colored GUI and orients the Sub to ram into it.
        
        **Parameters**: \n
        * **buoyParams** - Parameters including the centering time, ram time, and timeout.
        * **joystickMovementController** - Object for controlling the sub's movement.
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **waypointList** - List of waypoints and their coordinates.
        
        **Returns**: \n
        * **self.desiredAdjustmentsPoseForGui** - Desired pose data for the GUI to display. \n
        '''
        def initilizeScreenQuadrants(screenWidth, screenHeight, x, y):
            '''
            This function initializes the screen into 9 quadrants.
            
            **Parameters**: \n
            * **screenWidth** - The screen width of the images.
            * **screenHeight** - The screen height of the images.
            * **x** - X position of tracked object.
            * **y** - Y position of tracked object.
            
            **Returns**: \n
            * **objectIsRight** - A boolean value describing if the object is to the right.
            * **objectIsUp** - A boolean value describing if the object is up.
            * **objectIsLeft** - A boolean value describing if the object is to the left.
            * **objectIsDown** - A boolean value describing if the object is down.
            * **objectIsStraight** - A boolean value describing if the object is in the center panel.
            * **objectIsNotInSight** - A boolean value describing if the object is in sight.
            '''
            left = (screenWidth/3)
            right = ((screenWidth*2)/3)
            up = (screenHeight/3)
            down = ((screenHeight*2)/3)
            
            objectIsNotInSight = (x == 0) and (y == 0)
            objectIsInSight = not objectIsNotInSight
            objectIsRight = (x >= right) and objectIsInSight
            objectIsUp = (y <= up) and objectIsInSight
            objectIsLeft = (x <= left) and objectIsInSight
            objectIsDown = (y >= down) and objectIsInSight
            objectIsMiddle = (x >= left) and (x <= right) and objectIsInSight
            objectIsStraight = (x >= left) and (x <= right) and (y <= down) and (y >= up) and objectIsInSight
            
            
            return objectIsRight, objectIsUp, objectIsLeft, objectIsDown, objectIsMiddle, objectIsStraight, objectIsInSight, objectIsNotInSight 
        
        if self.sensorDataExsists:
            netBuoyTimeout = self.buoyTimeout.netTimer(self.buoyTimeout.cpuClockTimeInSeconds())
            if netBuoyTimeout <= buoyParams["Timeout"] or self.goStraightFlag == True:

                xFront, yFront = imageProcValues[0][0][0], imageProcValues[0][0][1]
                ellipseWidthFront, ellipseHeightFront = imageProcValues[0][1][0], imageProcValues[0][1][1]
                orientationFront = imageProcValues[0][2]
                
                screenWidth, screenHeight = imageProcValues[2][0], imageProcValues[2][1]
                
                currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                currentY = medianDepth #Comment out this line if wanting to use DVL Depth
                
                currentPose = [currentYaw, currentPitch, currentRoll, currentY]
                
                if self.initializeBuoyPose == True:
                    self.desiredPose = [currentY, currentPitch, currentYaw, currentRoll]
                    self.initializeBuoyPose = False
                
                if self.goStraightFlag == False:
                    self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                    if self.objectIsInSight:
                        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight
                        
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (1*self.objectIsDown) + (-1*self.objectIsUp)] #True, yaw, pitch, roll, depth
                        #                                                                                X PWM                                                          Y Desired           Z PWM             PITCH DESIRED                        YAW DESIRED                     ROLL DESIRED
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredAdjustmentsPoseForGui[4], 50, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        
                        
                        
                        if self.objectIsMiddle and (ellipseWidthFront >= 30 or ellipseHeightFront >= 30):
                            netBuoyInCenterTimer = self.buoyInCenterTimer.netTimer(self.buoyInCenterTimer.cpuClockTimeInSeconds())
                            
                            if netBuoyInCenterTimer > buoyParams["CenteringTime"]:
                                self.goStraightFlag = True
                                self.buoyInCenterTimer.restartTimer() #Re-using timer for how long I go straight to run into buoy
                                
                        else:
                            self.buoyInCenterTimer.restartTimer()
                            
                        self.desiredPose = [self.desiredPose[0], currentPitch, currentYaw, currentRoll]
                          
                        netPreviousTrackTimer = self.previousTrackTimer.netTimer(self.previousTrackTimer.cpuClockTimeInSeconds()) #Because the previous mission carries over to the next mission, you need to give the main process thread some time to update its image processing values 
                        if netPreviousTrackTimer >= 0.3: 
                            self.previouslyTracked = True
                        
                    elif self.objectIsNotInSight:
                        self.buoyInCenterTimer.restartTimer()
                        
                        if self.previouslyTracked == True: #If previously tracked, try to go to last place buoy was seen
                            self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (2*self.previousObjectIsDown) + (-2*self.previousObjectIsUp)] #True, yaw, pitch, roll, depth
                            self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 100*(1*self.previousObjectIsRight) + 100*(-1*self.previousObjectIsLeft), self.desiredAdjustmentsPoseForGui[4], -50, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            
                        else:
                            netNoBuoySeenTimer = self.noBuoySeenTimer.netTimer(self.noBuoySeenTimer.cpuClockTimeInSeconds())
                            self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                            if netNoBuoySeenTimer <= 5:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoBuoySeenTimer > 5 and netNoBuoySeenTimer <= 15:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, -60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoBuoySeenTimer > 15 and netNoBuoySeenTimer <= 20:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoBuoySeenTimer > 20 and netNoBuoySeenTimer <= 25:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], -60, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoBuoySeenTimer > 25:
                                self.noBuoySeenTimer.restartTimer()
                                
                elif self.goStraightFlag == True:
                    print "TARGET SEEN!!!!!!!"
                    netBuoyInCenterTimer = self.buoyInCenterTimer.netTimer(self.buoyInCenterTimer.cpuClockTimeInSeconds())
                    
                    if netBuoyInCenterTimer <= buoyParams["RamTime"]: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (1*self.objectIsDown) + (-1*self.objectIsUp)] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredAdjustmentsPoseForGui[4], 120, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                    
                    elif netBuoyInCenterTimer > buoyParams["RamTime"]:
                        self.missionSuccessful = True
                            
                         
                return self.desiredAdjustmentsPoseForGui
                
            else: #If timeout occurs
                if self.missionIndex > 0:
                    self.missionSuccessful = True #CHANGED FOR FINALS
                    #self.missionIndex -= 1 #Go back a mission to navigation to restart the buoy event if there is a previous navigation mission
                    #self.initialize = True
                else:
                    self.missionSuccessful = True
                
            
        else: #What to do if vehicle can't get proper data to execute the mission
            print "buoy() sensorDataExsists check failed"
            
            return [False, 0, 0, 0, 0]
        
    def path(self, pathParams, joystickMovementController, imageProcValues, dvlData, ahrsData, medianDepth):
        '''
        Orients the sub based on the rectangular orange path.
        
        **Parameters**: \n
        * **pathParams** - Parameters including the acceptable alignment error and timeout.
        * **joystickMovementController** - Object for controlling the sub's movement.
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **waypointList** - List of waypoints and their coordinates.
        
        **Returns**: \n
        * **self.desiredAdjustmentsPoseForGui** - Desired pose data for the GUI to display. \n
        '''
        def initilizeScreenQuadrants(screenWidth, screenHeight, x, y):
            '''
            This function initializes the screen into 9 quadrants.
            
            **Parameters**: \n
            * **screenWidth** - The screen width of the images.
            * **screenHeight** - The screen height of the images.
            * **x** - X position of tracked object.
            * **y** - Y position of tracked object.
            
            **Returns**: \n
            * **objectIsRight** - A boolean value describing if the object is to the right.
            * **objectIsUp** - A boolean value describing if the object is up.
            * **objectIsLeft** - A boolean value describing if the object is to the left.
            * **objectIsDown** - A boolean value describing if the object is down.
            * **objectIsStraight** - A boolean value describing if the object is in the center panel.
            * **objectIsNotInSight** - A boolean value describing if the object is in sight.
            '''
            left = (screenWidth/3)
            right = ((screenWidth*2)/3)
            up = (screenHeight/3)
            down = ((screenHeight*2)/3)
            
            objectIsNotInSight = (x == 0) and (y == 0)
            objectIsInSight = not objectIsNotInSight
            objectIsRight = (x >= right) and objectIsInSight
            objectIsUp = (y <= up) and objectIsInSight
            objectIsLeft = (x <= left) and objectIsInSight
            objectIsDown = (y >= down) and objectIsInSight
            objectIsMiddle = (x >= left) and (x <= right) and objectIsInSight
            objectIsStraight = (x >= left) and (x <= right) and (y <= down) and (y >= up) and objectIsInSight
            
            
            return objectIsRight, objectIsUp, objectIsLeft, objectIsDown, objectIsMiddle, objectIsStraight, objectIsInSight, objectIsNotInSight 
        
        if self.sensorDataExsists:
            netPathTimeout = self.pathTimeout.netTimer(self.pathTimeout.cpuClockTimeInSeconds())
            if netPathTimeout <= pathParams["Timeout"] or self.goStraightFlag == True:
                
                xBottom, yBottom = imageProcValues[1][0][0], imageProcValues[1][0][1]
                ellipseWidthBottom, ellipseHeightBottom = imageProcValues[1][1][0], imageProcValues[1][1][1]
                orientationBottom = imageProcValues[1][2]
                
                screenWidth, screenHeight = imageProcValues[2][0], imageProcValues[2][1]
                
                currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                currentY = medianDepth #Comment out this line if wanting to use DVL Depth
                
                currentPose = [currentYaw, currentPitch, currentRoll, currentY]
                
                if self.initializePathPose == True:
                    self.desiredPose = [currentY, currentPitch, currentYaw, currentRoll]
                    self.initializePathPose = False
                
                if self.goStraightFlag == False:
                    self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xBottom, yBottom)
                    if self.objectIsInSight:
                        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight
                        halfAcceptableAlignmentError = pathParams["AcceptableAlignmentError"]/2 #degrees
                        
                        aligned = (orientationBottom >= 0 and orientationBottom < halfAcceptableAlignmentError) or (orientationBottom > (180-halfAcceptableAlignmentError) and orientationBottom <= 180)
                        goClockwise = orientationBottom >= halfAcceptableAlignmentError and orientationBottom < 90
                        goCounterClockwise = orientationBottom >= 90 and orientationBottom <= 180-halfAcceptableAlignmentError

                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2] + 9*(1*goClockwise) + 9*(-1*goCounterClockwise), self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                        #                                                                                X PWM                                                 Y Desired                            Z PWM                                                     PITCH DESIRED                            YAW DESIRED                        ROLL DESIRED
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredAdjustmentsPoseForGui[4], 50*(1*self.objectIsUp) + 50*(-1*self.objectIsDown), self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        if aligned:
                            netPathInCenterTimer = self.pathInCenterTimer.netTimer(self.pathInCenterTimer.cpuClockTimeInSeconds())
                            
                            if netPathInCenterTimer > 1:
                                self.goStraightFlag = True
                                self.pathInCenterTimer.restartTimer() #Re-using timer for how long I go straight after aligning with path
                                
                        else:
                            self.pathInCenterTimer.restartTimer()
                            
                        self.desiredPose = [self.desiredPose[0], currentPitch, currentYaw, currentRoll]
                          
                        netPreviousTrackTimer = self.previousTrackTimer.netTimer(self.previousTrackTimer.cpuClockTimeInSeconds()) #Because the previous mission carries over to the next mission, you need to give the main process thread some time to update its image processing values
                        if netPreviousTrackTimer >= 0.3:
                            self.previouslyTracked = True
                        
                    elif self.objectIsNotInSight:
                        print "previously tracked", self.previouslyTracked
                        self.pathInCenterTimer.restartTimer()
                        if self.previouslyTracked == True: #If previously tracked, try to go to last place path was seen
                            self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                            self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 100*(1*self.previousObjectIsRight) + 100*(-1*self.previousObjectIsLeft), self.desiredAdjustmentsPoseForGui[4],  100*(1*self.previousObjectIsUp) + 100*(-1*self.previousObjectIsDown), self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            
                        else:
                            self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                            netNoPathSeenTimer = self.noPathSeenTimer.netTimer(self.noPathSeenTimer.cpuClockTimeInSeconds())
                            if netNoPathSeenTimer <= 5:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose,85, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoPathSeenTimer > 5 and netNoPathSeenTimer <= 15:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, -90, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoPathSeenTimer > 15 and netNoPathSeenTimer <= 20:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 85, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoPathSeenTimer > 20 and netNoPathSeenTimer <= 25:
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], 80, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                            elif netNoPathSeenTimer > 25:
                                self.noPathSeenTimer.restartTimer()
                                
                elif self.goStraightFlag == True:
                    print "PATH ALIGNED!!!!!!!"
                    netPathInCenterTimer = self.pathInCenterTimer.netTimer(self.pathInCenterTimer.cpuClockTimeInSeconds())
                    
                    if netPathInCenterTimer <= 5: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]]
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], 120, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                    
                    elif netPathInCenterTimer > 5:
                        self.missionSuccessful = True
                            
                          
                return self.desiredAdjustmentsPoseForGui
                
            else: #If timeout occurs
                self.missionSuccessful = True #Go to next mission
                
            
        else: #What to do if vehicle can't get proper data to execute the mission
            print "path() sensorDataExsists check failed"
            
            return [False, 0, 0, 0, 0]
        

    def torpedo(self, torpedoParams, movementController, joystickMovementController, imageProcValues, dvlData, ahrsData, medianDepth):
        '''
        Orients the sub and selects the appropriate squares to shot the torpedo through to complete the torpedo task.
        
        **Parameters**: \n
        * **torpedoParams** - Parameters including whether to remove the covers, which torpedo hole is covered, and timeout
        * **joystickMovementController** - Object for controlling the sub's movement.
        * **imageProcValues** - Image processing values that contains the coordinates of targets and target sizes
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **waypointList** - List of waypoints and their coordinates.
        
        **Returns**: \n
        * **self.desiredAdjustmentsPoseForGui** - Desired pose data for the GUI to display. \n
        '''
        
        def initilizeScreenQuadrants(screenWidth, screenHeight, x, y):
            '''  
            This function initializes the screen into 9 quadrants.
            
            **Parameters**: \n
            * **screenWidth** - The screen width of the images.
            * **screenHeight** - The screen height of the images.
            * **x** - X position of tracked object.
            * **y** - Y position of tracked object.
            
            **Returns**: \n
            * **objectIsRight** - A boolean value describing if the object is to the right.
            * **objectIsUp** - A boolean value describing if the object is up.
            * **objectIsLeft** - A boolean value describing if the object is to the left.
            * **objectIsDown** - A boolean value describing if the object is down.
            * **objectIsStraight** - A boolean value describing if the object is in the center panel.
            * **objectIsNotInSight** - A boolean value describing if the object is in sight.
            '''
            left = (screenWidth/3)
            right = ((screenWidth*2)/3)
            up = (screenHeight/3)
            down = ((screenHeight*2)/3)
            
            objectIsNotInSight = (x == 0) and (y == 0)
            objectIsInSight = not objectIsNotInSight
            objectIsRight = (x >= right) and objectIsInSight
            objectIsUp = (y <= up) and objectIsInSight
            objectIsLeft = (x <= left) and objectIsInSight
            objectIsDown = (y >= down) and objectIsInSight
            objectIsMiddle = (x >= left) and (x <= right) and objectIsInSight
            objectIsStraight = (x >= left) and (x <= right) and (y <= down) and (y >= up) and objectIsInSight
            
            return objectIsRight, objectIsUp, objectIsLeft, objectIsDown, objectIsMiddle, objectIsStraight, objectIsInSight, objectIsNotInSight 
        
        def empty(seq):
            if self.foundAllFour == False:
                for n in range(0, len(seq)):
                    if seq[n]:
                        continue
                    else:
                        return True
                return False
                    
            else:
                for n in range(0, len(seq)):
                    if seq[n]:
                        print "At least one square is still seen"
                        return False
                        break
                return True
    
        if self.sensorDataExsists == True:
            netTorpedoTimeout = self.torpedoTimeout.netTimer(self.torpedoTimeout.cpuClockTimeInSeconds())
            if netTorpedoTimeout <= torpedoParams["Timeout"]:
                
                targets = [0,0,0,0]
                # Upper left small target, upper right big target, bottom left small target, bottom right small target, track box of front image when there is no parent contour and only one target
                try:
                    targets[0], targets[1], targets[2], targets[3] = imageProcValues[7], imageProcValues[8], imageProcValues[9], imageProcValues[10]
                except:
                    return [False, 0, 0, 0, 0]
                    pass
                
                
                if empty(targets) == True:
                    return [False, 0, 0, 0, 0]
                else:
                    print "Getting target data and doing the mission"
                    screenWidth, screenHeight = imageProcValues[2][0], imageProcValues[2][1] 
                    
                    currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                    currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                    currentY = medianDepth # Comment out this line if wanting to use DVL depth
                    desiredY = None # Will be used when moving up and down to find big squares
                    
                    currentPose = [currentYaw, currentPitch, currentRoll, currentY] # Used for joystick movement controller
                    advancedPose = [currentYaw, currentPitch, currentRoll, currentX, currentY, currentZ] # Used for movement controller
                    
                    coveredSquare = torpedoParams["CoveredSquare"]
                    if coveredSquare == 1:
                        targets[0] = 0
                    elif coveredSquare == 4:
                        targets[3] = 0
                                
                    
                    if targets[0] != 0 or targets != 0: # One of these targets should be zero if image processing found the correct covered target
                        if targets[0] == 0 and targets[3] != 0: # target = (x, y), (width, height), distance in mm, orientation
                            print "Going for target: 4"
                            target = targets[3] # Setting bottom right small target to target
                            findBottomRightTarget = True # Calling the flag for this target
                        elif targets[3] == 0 and targets[0] != 0:
                            print "Going for target: 1"
                            target = targets[0] # Setting upper left small target to target
                            findUpperLeftTarget = True # Calling the flag for this target
                        else:
                            target = targets[0] # Going to guess and go for the upper left small target to be uncovered
                            print "Can't decide which small target is covered."
                    else:
                        pass
                    
            
                                                   
                    if self.initializeTorpedoPose == True:
                        self.desiredPose = [currentY, currentPitch, currentYaw, currentRoll]
                        self.initializeTorpedoPose = False
                        
                    if self.completedUpperLeftSmallSquare == False and self.completedBottomRightSmallSquare == False: 
                        print target
                        xFront, yFront = target[0][0], target[0][1] 
                        #if self.completedUpperLeftSmallSquare == True:
                                
                        if self.goStraightFlag == False:
                            self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                            
                            if self.objectIsInSight: # Aligning with the target we want to go to
                                self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight            
                                self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (1*self.objectIsDown) + (-1*self.objectIsUp)] #True, yaw, pitch, roll, depth
                                #                                                                                X PWM                                                          Y Desired           Z PWM             PITCH DESIRED                        YAW DESIRED                     ROLL DESIRED
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredAdjustmentsPoseForGui[4], 50, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])        
                                if self.objectIsMiddle: # If target is in the center for a designated time then go straight
                                    print "object is in middle"
                                    netTorpedoInCenterTimer = self.torpedoTargetsInCenterTimer.netTimer(self.torpedoTargetsInCenterTimer.cpuClockTimeInSeconds())
                                            
                                    if netTorpedoInCenterTimer > torpedoParams["CenteringTime"]:
                                        self.axis1 = 0.70
                                        self.goStraightFlag = True
                                        self.torpedoTargetsInCenterTimer.restartTimer()
                                        self.startDistanceAway = target[2] # Find the starting distance away from the small target

                                else:
                                    self.torpedoTargetsInCenterTimer.restartTimer()
            
                                self.desiredPose = [self.desiredPose[0], currentPitch, currentYaw, currentRoll]
                                  
                                netPreviousTrackTimer = self.previousTrackTimer.netTimer(self.previousTrackTimer.cpuClockTimeInSeconds()) #Because the previous mission carries over to the next mission, you need to give the main process thread some time to update its image processing values 
                                if netPreviousTrackTimer >= 0.3: 
                                    self.previouslyTracked = True
                                        
                            elif self.objectIsNotInSight:
                                self.torpedoTargetsInCenterTimer.restartTimer()
                                
                                if self.previouslyTracked == True: #If previously tracked, try to go to last place a torpedo target was seen
                                    self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (2*self.previousObjectIsDown) + (-2*self.previousObjectIsUp)] #True, yaw, pitch, roll, depth
                                    self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 100*(1*self.previousObjectIsRight) + 100*(-1*self.previousObjectIsLeft), self.desiredAdjustmentsPoseForGui[4], -50, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                                
                                '''
                                else:
                                    netNoTorpedoTargetSeenTimer = self.noTorpedoTargetSeenTimer.netTimer(self.noTorpedoTargetSeenTimer.cpuClockTimeInSeconds())
                                    self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                                    if netNoTorpedoTargetSeenTimer  <= 5:
                                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                                    elif netNoTorpedoTargetSeenTimer  > 5 and netNoTorpedoTargetSeenTimer  <= 15:
                                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, -60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                                    elif netNoTorpedoTargetSeenTimer  > 15 and netNoTorpedoTargetSeenTimer  <= 20:
                                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 60, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                                    elif netNoTorpedoTargetSeenTimer  > 20 and netNoTorpedoTargetSeenTimer  <= 25:
                                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], -60, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                                    elif netNoTorpedoTargetSeenTimer  > 25:
                                        self.noBuoySeenTimer.restartTimer()
                                '''
                                        
                        elif self.goStraightFlag == True:
                            
                            print "Going straight"
                            # Continually check where the object is so the sub doesn't get misaligned                        
                            self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                           
                            '''
                            if target == 0: # If the sub loses track because the contours are no longer child contours, then use parent contour 
                                target = targets[4]
                            '''
                            
                            if self.startDistanceAway < 3: # Every 3 feet the speed will be reduced
                                self.axis1 = 0.30 # change how fast the sub moves forward by the distance it is away from the target
                            
                            print target[2]
                            
                            if target[2] > 3: # Distance from the small target
                                if self.objectIsInSight:
                                    self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0] + (1*self.objectIsDown) + (-1*self.objectIsUp)] #True, yaw, pitch, roll, depth
                                    #Orientation lock and move the sub forward while adjusting
                                    self.thrusterPWMs = self.joystickMoveController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredMoveDepth, -self.axis1, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                                
                            elif target[2] <= 3 and target[2] > 1: # Time to use moveController for fine tuned movements
                                self.thrusterPWMs, error, yawDesired = self.moveController.advancedMove(advancedPose, 30*(1*self.objectIsRight) + 30*(-1*self.objectIsLeft), self.desiredMoveDepth, -self.axis1, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll, 0)
                            
                            elif target[2] <= 1: # If target is less than one foot away orientation and position lock
                                print "Time to fire"
                                if self.objectIsInMiddle: # If target is in middle, lock orientation and position, wait for timer then shoot
                                    netTorpedoInCenterTimer = self.torpedoTargetsInCenterTimer.netTimer(self.torpedoTargetsInCenterTimer.cpuClockTimeInSeconds())
                                    if netTorpedoInCenterTimer > torpedoParams["CenteringTime"]:
                                        self.thrusterPWMs, error, yawDesired = self.moveController.advancedMove(advancedPose, currentX, self.desiredMoveDepth, currentZ, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll, 0)
                                        self.initialServoSend == True 
                                        self.completedUpperLeftSmallSquare = True
                                        endingDepth = currentY
                                        firstLoop = False
                                        if findBottomRightTarget == True:
                                            self.completedBottomRightSmallSquare = True
                                        elif findUpperLeftTarget == True:
                                            self.completedUpperLeftSmallSquare = True
                                    else:
                                        self.torpedoTargetsInCenterTimer.restartTimer()

                                        
                    if self.completedUpperLeftSmallSquare == True:
                                                                                       
                        self.initialServoSend = False # Setting to False to 'restart' servo from setting it to true when completing small square
                        
                        if self.completedUpperLeftSmallSquare == True: #Means the sub needs to move down
                            print "Looking for bottom left big square!"
                            
                            if firstLoop == False: # First time looping through set the desired to half a foot deeper or higher than the currentY
                                desiredY = currentY+0.5
                                self.thrusterPWMs = self.joystickMoveController.advancedMove(currentPose, currentX, desiredY, currentZ, currentPitch, currentYaw, currentRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                                firstLoop = True 
                            else:
                                self.thrusterPWMs = self.joystickMoveController.advancedMove(currentPose, currentX, desiredY, currentZ, currentPitch, currentYaw, currentRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                                    
                            if (currentY - endingDepth) > 0.5: #If the sub has moved at least 0.5 feet then start looking for targets
                                for n in targets: # Since we cannot control which targets index the big square will be in.  We need to loop through the list and first which index isn't
                                    if targets[n] == 0:
                                        continue
                                    else:
                                        target = targets[n]
                                        break
                                if target != 0: # If a target does exist then move towards it
                                    xFront, yFront = target[0], target[1]
                                    self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                                    if self.objectIsInSight: # If object is in sight move towards it
                                        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight            
                                        # Need to make fine tuned movements when aligning with target super close
                                        self.thrusterPWMs, error, yawDesired = self.moveController.advancedMove(advancedPose, 30*(1*self.objectIsRight) + 30*(-1*self.objectIsLeft), currentY + (1*self.objectIsDown) + (-1*self.objectIsUp), currentZ, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll, 0)
                                        if self.objectIsMiddle: # If object is in the middle for a certain amount of time then shoot torpedoe
                                            netTorpedoInCenterTimer = self.torpedoTargetsInCenterTimer.netTimer(self.torpedoTargetsInCenterTimer.cpuClockTimeInSeconds())
                                                
                                            if netTorpedoInCenterTimer > torpedoParams["CenteringTime"]:
                                                self.torpedoTargetsInCenterTimer.restartTimer()
                                                self.completedBottomLeftBigSquare = True
                                                self.initialServoSend = True
                                        else:
                                            self.torpedoTargetsInCenterTimer.restartTimer()
                                
                            if (currentY - desiredY) <= 0 and self.objectIsNotInSight: # if the sub has moved half a foot down and hasn't seen the object then increment another half a foot down
                                desiredY += 0.5
                                    
                                    
                            if (currentY - endingDepth) > 4: # If the sub moves this far down then we should have definitely seen the target so end mission
                                print "Bottom Left Big Square not found!"
                                self.completedBottomLeftBigSquare = True
                                self.missionSuccessful = True
                                    
                    elif self.completedBottomRightSmallSquare == True:
                        
                        print "Looking for upper right big square!"
                                                    
                        if endingDepth == currentY or ((desiredY - currentY) == 0 and targets[4] == 0): # First time looping through
                            desiredY = currentY-0.5
                            self.thrusterPWMs = self.joystickMoveController.advancedMove(currentPose, currentX, desiredY, currentZ, currentPitch, currentYaw, currentRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                                    
                        else:
                            self.thrusterPWMs = self.joystickMoveController.advancedMove(currentPose, currentX, desiredY, currentZ, currentPitch, currentYaw, currentRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                                
                        if (endingDepth - currentY) > 0.5: #If the sub has moved at least 0.5 feet then start looking for targets
                            for n in targets: # Since we cannot control which targets index the big square will be in.  We need to loop through the list and first which index isn't
                                if targets[n] == 0:
                                    continue
                                else:
                                    target = targets[n]
                                    break
                            if target != 0: # If a target does exist then move towards it
                                xFront, yFront = target[0], target[1] #
                                self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                                if self.objectIsInSight:
                                    self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight            
                                    self.thrusterPWMs, error, yawDesired = self.moveController.advancedMove(advancedPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), currentY + (1*self.objectIsDown) + (-1*self.objectIsUp), currentZ, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll, 0)
                                    if self.objectIsMiddle and (target[1][0] >= 30 or target[1][1] >= 30):
                                        netTorpedoInCenterTimer = self.torpedoTargetsInCenterTimer.netTimer(self.torpedoTargetsInCenterTimer.cpuClockTimeInSeconds())
                                                
                                        if netTorpedoInCenterTimer > torpedoParams["CenteringTime"]:
                                            self.torpedoTargetsInCenterTimer.restartTimer()
                                            self.completedBottomLeftBigSquare = True
                                            self.initialServoSend = True
                                    else:
                                        self.torpedoTargetsInCenterTimer.restartTimer()
                                
                        if (desiredY - currentY) <= 0 and self.objectIsNotInSight: # if the sub has moved half a foot down and hasn't seen the object then increment another half a foot down
                            desiredY += 0.5
                            
                        if (endingDepth - currentY) > 4: # If the sub moves this far down then we should have definitely seen the target so end mission
                            print "Bottom Left Big Square not found!"
                            self.completedBottomLeftBigSquare = True
                            self.missionSuccessful = True

                            
            else: #If timeout occurs
                self.missionSuccessful = True #Go to next mission
                        
        else: #What to do if vehicle can't get proper data to execute the mission
            print self.sensorDataExsists
            print "torpedo() sensorDataExists check failed"
            return [False, 0, 0, 0, 0]       
                    
                       
                
                        

    def dropper(self, dropperParams, joystickMovementController, movementController, imageProcValues, dvlData, ahrsData, medianDepth):
        '''
        Orients the sub based on the rectangular orange path.
        
        **Parameters**: \n
        * **dropperParams** - Parameters including whether to lift lid, depth to dive for lid, which ball to drop, and timeout.
        * **joystickMovementController** - Object for controlling the sub's movement.
        * **movementController** - Object for controlling sub movement based on DVL + AHRS measurements.
        * **dvlData** - Coordinate data from DVL.
        * **ahrsData** - Orientation data from AHRS.
        * **medianDepth** - Depth data from pressure transducers.
        * **waypointList** - List of waypoints and their coordinates.
        
        **Returns**: \n
        * **self.desiredAdjustmentsPoseForGui** - Desired pose data for the GUI to display. \n
        '''
        

        def initilizeScreenQuadrants(screenWidth, screenHeight, x, y):
            '''
            This function initializes the screen into 9 quadrants.
            
            **Parameters**: \n
            * **screenWidth** - The screen width of the images.
            * **screenHeight** - The screen height of the images.
            * **x** - X position of tracked object.
            * **y** - Y position of tracked object.
            
            **Returns**: \n
            * **objectIsRight** - A boolean value describing if the object is to the right.
            * **objectIsUp** - A boolean value describing if the object is up.
            * **objectIsLeft** - A boolean value describing if the object is to the left.
            * **objectIsDown** - A boolean value describing if the object is down.
            * **objectIsStraight** - A boolean value describing if the object is in the center panel.
            * **objectIsNotInSight** - A boolean value describing if the object is in sight.
            '''
            left = (screenWidth/3)
            right = ((screenWidth*2)/3)
            up = (screenHeight/3)
            down = ((screenHeight*2)/3)
            
            objectIsNotInSight = (x == 0) and (y == 0)
            objectIsInSight = not objectIsNotInSight
            objectIsRight = (x >= right) and objectIsInSight
            objectIsUp = (y <= up) and objectIsInSight
            objectIsLeft = (x <= left) and objectIsInSight
            objectIsDown = (y >= down) and objectIsInSight
            objectIsMiddle = (x >= left) and (x <= right) and objectIsInSight
            objectIsStraight = (x >= left) and (x <= right) and (y <= down) and (y >= up) and objectIsInSight
            
            
            return objectIsRight, objectIsUp, objectIsLeft, objectIsDown, objectIsMiddle, objectIsStraight, objectIsInSight, objectIsNotInSight 
        
        if self.sensorDataExsists:
            netDropperTimeout = self.dropperTimeout.netTimer(self.dropperTimeout.cpuClockTimeInSeconds())
            if netDropperTimeout <= dropperParams["Timeout"] or self.hookLidFlag == True:
                
                xBottom, yBottom = imageProcValues[1][0][0], imageProcValues[1][0][1]
                ellipseWidthBottom, ellipseHeightBottom = imageProcValues[1][1][0], imageProcValues[1][1][1]
                orientationBottom = imageProcValues[1][2]
                
                screenWidth, screenHeight = imageProcValues[2][0], imageProcValues[2][1]
                
                currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                currentY = medianDepth #Comment out this line if wanting to use DVL Depth
                
                currentPose = [currentYaw, currentPitch, currentRoll, currentY]
                
                if self.initializeDropperPose == True:
                    self.desiredPose = [currentY, currentPitch, currentYaw, currentRoll]
                    self.initializeDropperPose = False
                
                if self.hookLidFlag == False:
                    self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xBottom, yBottom)
                    if self.objectIsInSight and dropperParams["LiftLidIfExists"] == 1:
                        self.noDropperSeenTimer.restartTimer()
                        self.previousObjectIsRight, self.previousObjectIsUp, self.previousObjectIsLeft, self.previousObjectIsDown, self.previousObjectIsMiddle, self.previousObjectIsStraight, self.previousObjectIsInSight, self.previousObjectIsNotInSight = self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight
                        #halfAcceptableAlignmentError = dropperParams["AcceptableAlignmentError"]/2 #degrees
                        
                        #aligned = (orientationBottom >= 0 and orientationBottom < halfAcceptableAlignmentError) or (orientationBottom > (180-halfAcceptableAlignmentError) and orientationBottom <= 180)
                        #goClockwise = orientationBottom >= halfAcceptableAlignmentError and orientationBottom < 90
                        #goCounterClockwise = orientationBottom >= 90 and orientationBottom <= 180-halfAcceptableAlignmentError

                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                        #                                                                                X PWM                                                 Y Desired                            Z PWM                                                     PITCH DESIRED                            YAW DESIRED                        ROLL DESIRED
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 60*(1*self.objectIsRight) + 60*(-1*self.objectIsLeft), self.desiredAdjustmentsPoseForGui[4], 60*(1*self.objectIsUp) + 60*(-1*self.objectIsDown), self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        if self.objectIsStraight and (ellipseWidthBottom >= 30 or ellipseHeightBottom >= 30):
                            netDropperInCenterTimer = self.dropperInCenterTimer.netTimer(self.dropperInCenterTimer.cpuClockTimeInSeconds())
                                                        
                            if netDropperInCenterTimer > 1:
                                self.hookLidFlag = True   
                                self.dropperInCenterTimer.restartTimer() #Re-using timer for how long I go straight after aligning with dropper
                                
                        else:
                            self.dropperInCenterTimer.restartTimer()
                            
                        #self.desiredPose = [self.desiredPose[0], currentPitch, currentYaw, currentRoll]
                        
                    elif self.objectIsNotInSight or dropperParams["LiftLidIfExists"] == 0:
                        self.dropperInCenterTimer.restartTimer()
                        
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4],  0,  self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        
                        netNoDropperSeenTimer = self.noDropperSeenTimer.netTimer(self.noDropperSeenTimer.cpuClockTimeInSeconds())
                        if dropperParams["DropBallMode"] != 0 and self.initialServoSend == True:
                            self.arduinoCom.write(str(dropperParams["DropBallMode"]))
                            self.initialServoSend = False
                        if netNoDropperSeenTimer >= 5: #No dropper lid seen, go to next one
                            self.dropperCounter += 1
                            self.missionSuccessful = True
                                
                elif self.hookLidFlag == True:
                    print "DROPPER ALIGNED!!!!!!!"
                    netDropperInCenterTimer = self.dropperInCenterTimer.netTimer(self.dropperInCenterTimer.cpuClockTimeInSeconds())
                    
                    if netDropperInCenterTimer <= 5: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], dropperParams["DepthToLiftLid"]] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 120, self.desiredAdjustmentsPoseForGui[4], 90, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                    
                    elif netDropperInCenterTimer > 5 and netDropperInCenterTimer <= 10: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], dropperParams["DepthToLiftLid"]] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, -150, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        
                    elif netDropperInCenterTimer > 10 and netDropperInCenterTimer <= 15: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1]+30, self.desiredPose[3], dropperParams["DepthToLiftLid"]-20] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], -100, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        
                    elif netDropperInCenterTimer > 15 and netDropperInCenterTimer <= 20: 
                        self.desiredAdjustmentsPoseForGui = [True, self.desiredPose[2], self.desiredPose[1]+30, self.desiredPose[3], dropperParams["DepthToLiftLid"]-20] #True, yaw, pitch, roll, depth
                        self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        
                    elif netDropperInCenterTimer > 20 and netDropperInCenterTimer <= 25: 
                        #self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredAdjustmentsPoseForGui[4], 0, self.desiredAdjustmentsPoseForGui[2], self.desiredAdjustmentsPoseForGui[1], self.desiredAdjustmentsPoseForGui[3])
                        self.thrusterPWMs = joystickMovementController.move(currentPose[3], 0, dropperParams["DepthToLiftLid"]-20, 0, 50, 0, -204)
                            
                    elif netDropperInCenterTimer > 25:
                        print "Before:", self.missionIndex
                        self.missionIndex += 2*(3-self.dropperCounter) #Mission successful (picked up lid), skip the rest of the dropper tasks. Max num self.dropperCounter can be is 3
                        print "After:", self.missionIndex
                        print "Missions:", self.missionSelectorMissions
                        self.missionSuccessful = True
                        
                        
                return self.desiredAdjustmentsPoseForGui
                
            else: #If timeout occurs
                self.missionSuccessful = True #Go to next mission
                
            
        else: #What to do if vehicle can't get proper data to execute the mission
            print "dropper() sensorDataExsists check failed"
            
            return [False, 0, 0, 0, 0]
    
    '''
    def dropper(self, dropperParams, joystickMovementController, imageProcValues, dvlData, ahrsData, medianDepth):
        def initilizeScreenQuadrants(screenWidth, screenHeight, x, y):

            This function initializes the screen into 9 quadrants.
            
            **Parameters**: \n
            * **screenWidth** - The screen width of the images.
            * **screenHeight** - The screen height of the images.
            * **x** - X position of tracked object.
            * **y** - Y position of tracked object.
            
            **Returns**: \n
            * **objectIsRight** - A boolean value describing if the object is to the right.
            * **objectIsUp** - A boolean value describing if the object is up.
            * **objectIsLeft** - A boolean value describing if the object is to the left.
            * **objectIsDown** - A boolean value describing if the object is down.
            * **objectIsStraight** - A boolean value describing if the object is in the center panel.
            * **objectIsNotInSight** - A boolean value describing if the object is in sight.

            left = (screenWidth/3)
            right = ((screenWidth*2)/3)
            up = (screenHeight/3)
            down = ((screenHeight*2)/3)
            
            objectIsNotInSight = (x == 0) and (y == 0)
            objectIsInSight = not objectIsNotInSight
            objectIsRight = (x >= right) and objectIsInSight
            objectIsUp = (y <= up) and objectIsInSight
            objectIsLeft = (x <= left) and objectIsInSight
            objectIsDown = (y >= down) and objectIsInSight
            objectIsMiddle = (x >= left) and (x <= right) and objectIsInSight
            objectIsStraight = (x >= left) and (x <= right) and (y <= down) and (y >= up) and objectIsInSight
            
            
            return objectIsRight, objectIsUp, objectIsLeft, objectIsDown, objectIsMiddle, objectIsStraight, objectIsInSight, objectIsNotInSight 
        
        if dropperParams["Priority"] == "secondary" and (not self.secondaryObjectiveFound):# or dropperParams["Priority"] == "secondary" and (not self.primaryObjectiveFound):
            
            if self.sensorDataExsists:
                netDropperTimeout = self.dropperTimeout.netTimer(self.dropperTimeout.cpuClockTimeInSeconds())
                if netDropperTimeout <= dropperParams["Timeout"] or self.goStraightFlag == True:
    
                    xFront, yFront = imageProcValues[1][0][0], imageProcValues[1][0][1]
                    ellipseWidthFront, ellipseHeightFront = imageProcValues[0][1][0], imageProcValues[0][1][1]
                    orientationFront = imageProcValues[0][2]
                    
                    screenWidth, screenHeight = imageProcValues[2][0], imageProcValues[2][1]
                    
                    currentYaw, currentPitch, currentRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                    currentX, currentY, currentZ = dvlData[0][1], dvlData[0][2], dvlData[0][0]
                    currentY = medianDepth #Comment out this line if wanting to use DVL Depth
                    
                    currentPose = [currentYaw, currentPitch, currentRoll, currentY]
                    
                    if self.initializeDropperPose == True:
                        self.desiredPose = [currentY, currentPitch, currentYaw, currentRoll]
                        self.initializeDropperPose = False
                    
                    if self.goStraightFlag == False:
                        self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xFront, yFront)
                        if self.objectIsInSight:
                            print "Right:", self.objectIsRight, " Up:", self.objectIsUp, " Left:", self.objectIsLeft, " Down:", self.objectIsDown, " Middle:", self.objectIsMiddle, " Straight:",  self.objectIsStraight, " In Sight:",  self.objectIsInSight, " Not in sight:",  self.objectIsNotInSight  
                            #                                                                                X PWM                                                          Y Desired                                          Z PWM     PITCH DESIRED        YAW DESIRED         ROLL DESIRED
                            self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredPose[0] + (1*self.objectIsDown) + (-1*self.objectIsUp), 50, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                            
                            if self.objectIsMiddle and (ellipseWidthFront >= 30 or ellipseHeightFront >= 30):
                                netDropperInCenterTimer = self.dropperInCenterTimer.netTimer(self.dropperInCenterTimer.cpuClockTimeInSeconds())
                                
                                if netDropperInCenterTimer > 2:
                                    self.goStraightFlag = True
                                    self.dropperInCenterTimer.restartTimer() #Re-using timer for how long I go straight to run into buoy
                                    
                            else:
                                self.dropperInCenterTimer.restartTimer()
                                
                            self.desiredPose = currentPose
                                
                            self.previouslyTracked = True
                            
                        elif self.objectIsNotInSight:
                            self.dropperInCenterTimer.restartTimer()
                            
                            if self.previouslyTracked == True: #If previously tracked, try to go to last place buoy was seen
                                self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 100*(1*self.objectIsRight) + 100*(-1*self.objectIsLeft), self.desiredPose[0] + (2*self.objectIsDown) + (-2*self.objectIsUp), -50, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                                
                            else:
                                netNoDropperSeenTimer = self.noDropperSeenTimer.netTimer(self.noBuoySeenTimer.cpuClockTimeInSeconds())
                                if netNoDropperSeenTimer <= 5:
                                    self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 20, self.desiredPose[0], 0, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                                elif netNoDropperSeenTimer > 5 and netNoDropperSeenTimer <= 15:
                                    self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, -20, self.desiredPose[0], 0, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                                elif netNoDropperSeenTimer > 15 and netNoDropperSeenTimer <= 20:
                                    self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 20, self.desiredPose[0], 0, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                                elif netNoDropperSeenTimer > 20 and netNoDropperSeenTimer <= 25:
                                    self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 0, self.desiredPose[0], -20, self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                                elif netNoDropperSeenTimer > 25:
                                    self.noDropperSeenTimer.restartTimer()
                                    
                    elif self.goStraightFlag == True:
                        print "TARGET SEEN!!!!!!!"
                        netDropperInCenterTimer = self.dropperInCenterTimer.netTimer(self.dropperInCenterTimer.cpuClockTimeInSeconds())                        
                        
                        if (not self.objectIsMiddle) or self.objectIsUp or self.objectIsDown: 
                            self.thrusterPWMs = joystickMovementController.advancedMove(currentPose, 50*(1*self.objectIsRight) + 50*(-1*self.objectIsLeft), self.desiredPose[0], 50*(1*self.objectIsUp) + 50*(-1*self.objectIsDown), self.desiredPose[1], self.desiredPose[2], self.desiredPose[3])
                        elif self.objectIsMiddle and (not self.objectIsUp) and (not self.objectIsDown):
                            if netDropperInCenterTimer > 3:
                                if self.dropperMissionCounter < 3:
                                    if imageProcValues[4] != None:
                                            print "Coordinates: ", imageProcValues[4][0]
                                            #xObj, yObj = imageProcValues[4][0][0], imageProcValues[4][0][1]
                                            #self.objectIsRight, self.objectIsUp, self.objectIsLeft, self.objectIsDown, self.objectIsMiddle, self.objectIsStraight, self.objectIsInSight, self.objectIsNotInSight = initilizeScreenQuadrants(screenWidth, screenHeight, xObj, yObj)
                                            #Code to activate dropper
                                            print "DROPPER SUCCESS!!!!!!!!!!!!!!!!!!!!!"  
                                            self.secondaryObjectiveFound = True        
                                    else:
                                        print "TARGET NOT HERE!!!!!!!!!!!!"
                                elif self.dropperMissionCounter == 3 and (not self.secondaryObjectiveFound):
                                    #code to activate dropper
                                    pass
                                self.missionSuccessful = True
                                self.dropperMissionCounter += 1    
                            
                    if self.previouslyTracked:   
                        return [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]]
                    else:
                        return [True, self.desiredPose[2], self.desiredPose[1], self.desiredPose[3], self.desiredPose[0]]
                    
                else: #If timeout occurs
                    self.missionIndex -= 1 #Go back a mission to navigation to restart the buoy event
                    self.initialize = True
                
            
            else: #What to do if vehicle can't get proper data to execute the mission
                print "dropper() sensorDataExsists check failed"
                
                return [False, 0, 0, 0, 0]
        else:
            self.missionSuccessful = True
            self.dropperMissionCounter +=1
    '''