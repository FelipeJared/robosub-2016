'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: microcontroller_sib
   :synopsis: Defines the various movement options for the Sub.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Mar 29, 2015
:Description: Contains movement options and PID controllers for moving the based on position, way, pitch, and roll.
'''
import main.utility_package.utilities as utilities
import time
import math

sendTCBDataTimer = utilities.Timer()
noTranslationTimer = utilities.Timer()
initialTime = time.time()

#TCB = microcontroller.MicrocontrollerDataPackets()

advM = utilities.AdvancedMath()
e1 = advM.e1
e2 = advM.e2
e3 = advM.e3

autonomousSliderValues = []
joystickSliderValues = []
lockedSliderValues = []


class BrushedThruster():
    
    def __init__(self, motorID, orientation, location):
        '''
        Orients the sub based on the rectangular orange path.
        
        **Parameters**: \n
        * **motorID** - ID value that we assign to thruster
        * **orientation** - [Unit in x direction, Unit in y direction, Unit in z direction]. X is Sub's right, Y is Sub's bottom, Z is Sub's front. 
        * **location** - [Unit in x direction, Unit in y direction, Unit in z direction]. X is Sub's right, Y is Sub's bottom, Z is Sub's front. 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.motorID = motorID #ID value that we assign to thruster
        self.orientation = orientation #Direction thruster is facing: 3=Positive Z-axis, 2=Positive Y-axis, 1=Positive X-axis, -1=Negative X-axis, -2=Negative Y-axis, -3=Negative Z-axis 
        self.location = location #[Unit in x direction, Unit in y direction, Unit in z direction] Location data currently doesn't do anything.
        
        self.maxPwm = 204 #80% duty cycle
        self.pwm = 0

    def setPWM(self, pwm):
        '''
        This function gets called instead of setting self.speed directly so a 
        check can be done to make sure we don't go over a certain PWM by mistake.
        
        **Parameters**: \n
        * **pwm** - Integer between 0 and 255, typically capped at 204.
        
        **Returns**: \n
        * **No Return.\n
        '''
        if pwm > self.maxPwm:
            self.pwm = self.maxPwm
        elif pwm < -self.maxPwm:
            self.pwm = -self.maxPwm
        else:
            self.pwm = pwm


def autonomousPIDSliderValues(pidValues):
    
    global autonomousSliderValues
    
    autonomousSliderValues = pidValues[24:66:1]


class MovementController():
    '''
    Contains various types of movement for the Sub in autonomous mode, including an advanced move for Navigation missions using NESW coordinates.
    '''
    def __init__(self, TCB1DataPacketsObject, TCB2DataPacketsObject, *thrusters):
        '''
        Initializes the thrusters and PID controllers. 
        
        **Parameters**: \n
        * **TCB1DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **TCB2DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **thrusters** -  BrushedThruster objects containing orientation and location data for the thrusters.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        
        
        self.tcb1DataPackets = TCB1DataPacketsObject
        self.tcb2DataPackets = TCB2DataPacketsObject
        self.thrusters = thrusters
        self.previousPwm = [0]*len(self.thrusters) #Allows me to keep track of previous PWM values so I don't spam TCB
        
        advM = utilities.AdvancedMath()
        e1 = advM.e1 #Unit vector for x
        e2 = advM.e2 #Unit vector for y
        e3 = advM.e3 #Unit vector for z
        
        self.maxPwm = 204
        self.rotateFirstToggle = False

        '''
        #PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(1.5, 2.0, 12, 0.25, -20, 20)
        self.yawPIDControllerBackwardsMode = PIDController(4, 1.8, 4.5, 0.7, -30, 30)
        self.pitchPIDController = PIDController(1, 1, 15, 0.1, -5, 5)
        self.rollPIDController = PIDController(0.3, 0.2, 9, 0.06, -1, 1)
        self.depthPIDController = PIDController(0.7, 4, 6, 0.1, -2, 2)
        self.xPIDController = PIDController(0.7, 0.2, 10, 0.5, -1, 1)
        self.zPIDController = PIDController(0.7, 0.2, 10, 0.5, -1, 1)
        '''
        
        #PID CONTROLLERS
        '''
        if autonomousSliderValues =
        
        self.yawPIDControllerForwardMode = PIDController(autonomousSliderValues[0], autonomousSliderValues[1], autonomousSliderValues[2], autonomousSliderValues[3], -autonomousSliderValues[4], autonomousSliderValues[5])
        self.yawPIDControllerBackwardsMode = PIDController(autonomousSliderValues[6], autonomousSliderValues[7], autonomousSliderValues[8], autonomousSliderValues[9], -autonomousSliderValues[10], autonomousSliderValues[11])
        self.pitchPIDController = PIDController(autonomousSliderValues[12], autonomousSliderValues[13], autonomousSliderValues[14], autonomousSliderValues[15], -autonomousSliderValues[16], autonomousSliderValues[17])
        self.rollPIDController = PIDController(autonomousSliderValues[18], autonomousSliderValues[19], autonomousSliderValues[20], autonomousSliderValues[21], -autonomousSliderValues[22], autonomousSliderValues[23])
        self.depthPIDController = PIDController(autonomousSliderValues[24], autonomousSliderValues[25], autonomousSliderValues[26], autonomousSliderValues[27], -autonomousSliderValues[28], autonomousSliderValues[29])
        self.xPIDController = PIDController(autonomousSliderValues[30], autonomousSliderValues[31], autonomousSliderValues[32], autonomousSliderValues[33], -autonomousSliderValues[34], autonomousSliderValues[35])
        self.zPIDController = PIDController(autonomousSliderValues[36], autonomousSliderValues[37], autonomousSliderValues[38], autonomousSliderValues[39], -autonomousSliderValues[40], autonomousSliderValues[40])
        
        print "Autonomous: ", self.yawPIDControllerForwardMode, self.yawPIDControllerBackwardsMode, self.pitchPIDController, self.rollPIDController, self.depthPIDController, self.xPIDController, self.zPIDController
        '''
        
    def setPID(self):
        
        #print "autonomous: ", autonomousSliderValues

        self.yawPIDControllerForwardMode = PIDController(autonomousSliderValues[0], autonomousSliderValues[1],
                                                         autonomousSliderValues[2], autonomousSliderValues[3],
                                                         -autonomousSliderValues[4], autonomousSliderValues[5])
        self.yawPIDControllerBackwardsMode = PIDController(autonomousSliderValues[6], autonomousSliderValues[7],
                                                           autonomousSliderValues[8], autonomousSliderValues[9],
                                                           -autonomousSliderValues[10], autonomousSliderValues[11])
        self.pitchPIDController = PIDController(autonomousSliderValues[12], autonomousSliderValues[13],
                                                autonomousSliderValues[14], autonomousSliderValues[15],
                                                -autonomousSliderValues[16], autonomousSliderValues[17])
        self.rollPIDController = PIDController(autonomousSliderValues[18], autonomousSliderValues[19],
                                               autonomousSliderValues[20], autonomousSliderValues[21],
                                               -autonomousSliderValues[22], autonomousSliderValues[23])
        self.depthPIDController = PIDController(autonomousSliderValues[24], autonomousSliderValues[25],
                                                autonomousSliderValues[26], autonomousSliderValues[27],
                                                -autonomousSliderValues[28], autonomousSliderValues[29])
        self.xPIDController = PIDController(autonomousSliderValues[30], autonomousSliderValues[31],
                                            autonomousSliderValues[32], autonomousSliderValues[33],
                                            -autonomousSliderValues[34], autonomousSliderValues[35])
        self.zPIDController = PIDController(autonomousSliderValues[36], autonomousSliderValues[37],
                                            autonomousSliderValues[38], autonomousSliderValues[39],
                                            -autonomousSliderValues[40], autonomousSliderValues[41])
        
        #print "Autonomous: ", self.yawPIDControllerForwardMode, self.yawPIDControllerBackwardsMode, self.pitchPIDController, self.rollPIDController, self.depthPIDController, self.xPIDController, self.zPIDController


        
    def simpleMove(self, *motorPwms): #Assign thruster pwm by thruster pwm
        '''
        Directly sets each indiviudal PWM for each thruster. 
        
        **Parameters**: \n
        * **motorPwms** - Integers to directly set PWM on each thruster, must be between 0 and 204.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        for index, motorPwm in enumerate(motorPwms):
            self.thrusters[index].setPWM(motorPwm) #Assign motor PWMs to objects speed variable
            
    def move(self, xPwmSignal, yPwmSignal, zPwmSignal, xPwmRotateSignal, yPwmRotateSignal, zPwmRotateSignal):
        '''
        Moves Sub based on XYZ coordinates and about each axis, combining the signals to get the final PWM for each thruster.
        
        **Parameters**: \n
        * **xPwmSignal** - Signal to move Sub to its left or right.
        * **yPwmSignal** - Signal to move Sub up or down.
        * **zPwmSignal** - Signal to move Sub forward or backward.
        * **xPwmRotateSignal** - Signal to pitch Sub up or down.
        * **yPwmRotateSignal** - Signal to rotate Sub clock- or counter-clockwise.
        * **zPwmRotateSignal** - Signal to roll Sub towards its right or left.
        
        **Returns**: \n
        * **thrusterPWMs** - List containing the final PWMs assigned to each thruster.\n
        '''
        thrusterPWMs = []
        for index, thruster in enumerate(self.thrusters): #For each thruster object..
            
            #This line of code is able to account for any orientation and location of thruster specified. This means that we can have various thruster mounting configurations and the code wont need to change.
            self.thrusters[index].setPWM(xPwmSignal*-thruster.orientation[0] + yPwmSignal*-thruster.orientation[1] + zPwmSignal*-thruster.orientation[2] + xPwmRotateSignal*thruster.orientation[1]*thruster.location[2] + (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]) + zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0])
            
            #Need this list to send over to the GUI to display motor duty cycles
            thrusterPWMs.append(int(self.thrusters[index].pwm))
            
            #print index, xPwmSignal*-thruster.orientation[0], yPwmSignal*-thruster.orientation[1], zPwmSignal*-thruster.orientation[2], xPwmRotateSignal*thruster.orientation[1]*thruster.location[2], (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]), zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0]
            
        netSendTCBDataTimer = sendTCBDataTimer.netTimer(sendTCBDataTimer.cpuClockTimeInSeconds())
        if netSendTCBDataTimer >= 0.05: #Because I send data to fast for TCB to process, I need to send less data to the TCB. This timer slows down data being sent to the TCB so its circular buffer wont overwrite data
            #If statements are so I don't spam TCB
            if thrusterPWMs[0] != self.previousPwm[0]:
                self.tcb1DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[0] < 0, abs(thrusterPWMs[0]))
            if thrusterPWMs[1] != self.previousPwm[1]:
                self.tcb1DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[1] < 0, abs(thrusterPWMs[1]))
            if thrusterPWMs[2] != self.previousPwm[2]:
                self.tcb1DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[2] < 0, abs(thrusterPWMs[2]))
            if thrusterPWMs[3] != self.previousPwm[3]:
                self.tcb1DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[3] < 0, abs(thrusterPWMs[3]))
            if thrusterPWMs[4] != self.previousPwm[4]:
                self.tcb2DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[4] < 0, abs(thrusterPWMs[4]))
            if thrusterPWMs[5] != self.previousPwm[5]:
                self.tcb2DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[5] < 0, abs(thrusterPWMs[5]))
            if thrusterPWMs[6] != self.previousPwm[6]:
                self.tcb2DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[6] < 0, abs(thrusterPWMs[6]))
            if thrusterPWMs[7] != self.previousPwm[7]:
                self.tcb2DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[7] < 0, abs(thrusterPWMs[7]))
                
            sendTCBDataTimer.restartTimer()
            self.previousPwm = thrusterPWMs 
           
        return thrusterPWMs
            
    def advancedMove(self, poseData, eastTranslateDesired, upTranslateDesired, northTranslateDesired, xRotateDesired, yRotateDesired, zRotateDesired, *userVariables): #Translation in feet with respect to NSEW, rotation in degrees with respect to NSEW
        '''
        Moves the Sub based on desired NESW coordinates and desired yaw, pitch, and roll.
        
        **Parameters**: \n
        * **poseData** - Current yaw, pitch, roll, and position data.
        * **eastTranslateDesired** - Desired position in East/West direction.
        * **upTranslateDesired** - Desired position in Up/Down direction.
        * **northTranslateDesired** - Desired position in North/South direction.
        * **xRotateDesired** - Desired pitch.
        * **yRotateDesired** - Desired yaw.
        * **zRotateDesired** - Desired roll.
        * **userVariables** - Driving mode. 0 is forwards, 1 is backwards.
        
        **Returns**: \n
        * **thrusterPWMs** - List of final PWMs assigned to each thruster.
        * **[pos[0][0], pos[1][0], pos[2][0], pitchError, yawError, rollError]** - Remaining error in position, pitch, yaw, and roll.
        * **yRotateDesired** - Desired yaw.\n
        '''
        yaw, pitch, roll = poseData[0], poseData[1], poseData[2]
        eastPosition, upPosition, northPosition = poseData[3], poseData[4], poseData[5]
        
        if len(userVariables) > 0:
            drivingMode = userVariables[0]
        
        #X TRANSLATE CONTROLLER
        eastScale = self.maxPwm/2
        eastError = eastTranslateDesired-eastPosition
        
        #Y TRANSLATE CONTROLLER
        upScale = self.maxPwm/2
        upError = upTranslateDesired-upPosition
        
        #Z TRANSLATE CONTROLLER
        northScale = self.maxPwm/2
        northError = northTranslateDesired-northPosition
        
        
        #TRANSFORMATION MATRICIE
        T = advM.matrixMultiply(advM.inv(advM.Rot(e2, yaw)), advM.Trans(e1, eastError), advM.Trans(e2, upError), advM.Trans(e3, northError), advM.Rot(e2, yaw))       
        rot, pos = advM.extractData(T)
        
        #X TRANSLATE CONTROLLER
        xPIDValue = self.xPIDController.PIDControl(pos[0][0], eastScale) 
        
        xPwmSignal = int(round(xPIDValue))
        if xPwmSignal < -self.maxPwm:
            xPwmSignal = -self.maxPwm
        elif xPwmSignal > self.maxPwm:
            xPwmSignal = self.maxPwm
        
        #Y TRANSLATE CONTROLLER
        depthPIDValue = self.depthPIDController.PIDControl(pos[1][0], upScale) 
        
        yPwmSignal = int(round(depthPIDValue))
        if yPwmSignal < -self.maxPwm:
            yPwmSignal = -self.maxPwm
        elif yPwmSignal > self.maxPwm:
            yPwmSignal = self.maxPwm
        
        #Z TRANSLATE CONTROLLER
        zPIDValue = self.zPIDController.PIDControl(pos[2][0], northScale) 
        
        zPwmSignal = int(round(zPIDValue))
        if zPwmSignal < -self.maxPwm:
            zPwmSignal = -self.maxPwm
        elif zPwmSignal > self.maxPwm:
            zPwmSignal = self.maxPwm
            
            
        #print "North error:", pos[2][0], " East error:", pos[0][0]
        
        #PITCH CONTROLLER
        pitchScale = 255.0/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        pitchError = xRotateDesired-pitch
        
        pitchPIDValue = self.pitchPIDController.PIDControl(pitchError, pitchScale)
        
        pitchPwmSignal = int(round((pitchPIDValue))) 
        if pitchPwmSignal < -self.maxPwm:
            pitchPwmSignal = -self.maxPwm
        elif pitchPwmSignal > self.maxPwm:
            pitchPwmSignal = self.maxPwm
        
        #YAW CONTROLLER 
        yawScale = self.maxPwm/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        print yRotateDesired
        #FACE IN WAYPOINT DIRECTION
        corectOrientationBubble = 3.5 #feet
        if abs(northError) > corectOrientationBubble or abs(eastError) > corectOrientationBubble:
            yRotateDesired = (math.atan2(eastError, northError)*(180/3.14159265))%360 #Yaw to facing at waypoint

        #USER VARIABLE 
        if drivingMode == 1:
            yRotateDesired = (yRotateDesired + 180)%360
            
        
        yawError = yRotateDesired - yaw
        if yaw > yRotateDesired and yawError < -180: 
            yawError = yawError + 360
        
        elif yaw <= yRotateDesired and yawError >= 180: 
            yawError = yawError - 360
            
        #USER VARIABLE
        if abs(pos[0][0]) > 5 or abs(pos[2][0]) > 5:
            if drivingMode == 2:
                yawError = -150 #clockwise
            elif drivingMode == 3:
                yawError = 150 #Counter clockwise
                
        
        if drivingMode == 0:
            yawPIDValue = self.yawPIDControllerForwardMode.PIDControl(yawError, yawScale)       
        if drivingMode == 1:
            yawPIDValue = self.yawPIDControllerBackwardsMode.PIDControl(yawError, yawScale)    
        
        yawPwmSignal = int(round(yawPIDValue)) 
        if yawPwmSignal < -self.maxPwm:
            yawPwmSignal = -self.maxPwm
        elif yawPwmSignal > self.maxPwm:
            yawPwmSignal = self.maxPwm
            
        
        #FACE IN WAYPOINT DIRECTION  
        
        if drivingMode == 0 or drivingMode == 1: #USER VARIABLE
            if abs(northError) > corectOrientationBubble or abs(eastError) > corectOrientationBubble:
                if abs(yawError) >= 5:
                    xPwmSignal = xPwmSignal*0.85
                    zPwmSignal = zPwmSignal*0.85
        
        
        #ROLL CONTROLLER
        Kp = 1.5 #Just using a P controller of PID
        rollScale = 255.0/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.

        if zRotateDesired-roll > 180:
            rollError = zRotateDesired-roll - 360
        elif zRotateDesired-roll < -180:
            rollError = zRotateDesired-roll + 360
        else:
            rollError = zRotateDesired-roll 
        
        rollPIDValue = self.rollPIDController.PIDControl(rollError, rollScale)
        
        rollPwmSignal = int(round(rollPIDValue)) 
        if rollPwmSignal < -self.maxPwm:
            rollPwmSignal = -self.maxPwm
        elif rollPwmSignal > self.maxPwm:
            rollPwmSignal = self.maxPwm
        
        #MOVE
        thrusterPWMs = self.move(xPwmSignal, yPwmSignal, zPwmSignal, pitchPwmSignal, yawPwmSignal, rollPwmSignal)
        
        if yRotateDesired == None:
            print yRotateDesired
        
        return thrusterPWMs, [pos[0][0], pos[1][0], pos[2][0], pitchError, yawError, rollError], yRotateDesired
        
    def trajectoryPlanningAndGeneration(self, desiredPosX, desiredPosY, desiredPosZ, desiredAngleX, desiredAngleY, desiredAngleZ, finalTime, ahrsData):
        '''
        Controls the time it takes for thrusters to ramp up.
        
        **Parameters**: \n
        * **desiredPosX** - Desired X position, left or right.
        * **desiredPosY** - Desired Y position, up or down.
        * **desiredPosZ** - Desired Z position, front or back.
        * **desiredAngleX** - Desired yaw.
        * **desiredAngleY** - Desired pitch.
        * **desiredAngleZ** - Desired roll.
        * **finalTime** - Time it takes to ramp up.
        * **ahrsData** - Orientation data from AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #This is being tested for now but what i have so far is correct for a cycloid, except probably want to change the while statement
        yaw, pitch, roll = ahrsData[0], ahrsData[1], ahrsData[2]
        k = 1
        incrementalPitchAngle = 0
        
        while(incrementalPitchAngle < desiredAngleX):
            currentTime = time.time()-initialTime
            incrementalPitchAngle = pitch + (desiredAngleX-pitch)*((currentTime/finalTime)-math.sin((2*k*3.1416*currentTime)/finalTime)/(2*k*3.1416))
            moveController.advancedMove(0, 0, 0, incrementalPitchAngle, 0, 0, ahrsData)
            

def joystickPIDSliderValues(pidValues):
    
    global joystickSliderValues
 
    joystickSliderValues = pidValues[0:24:1]

            
class JoystickMovementController():
    '''
    Contains various types of movement for the Sub in manual control.
    '''
    def __init__(self, TCB1DataPacketsObject, TCB2DataPacketsObject, *thrusters):
        '''
        Initializes the thrusters and PID controllers. 
        
        **Parameters**: \n
        * **TCB1DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **TCB2DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **thrusters** -  BrushedThruster objects containing orientation and location data for the thrusters.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.tcb1DataPackets = TCB1DataPacketsObject
        self.tcb2DataPackets = TCB2DataPacketsObject
        self.thrusters = thrusters
        self.previousPwm = [0]*len(self.thrusters) #Allows me to keep track of previous PWM values so I don't spam TCB
        
        '''
        #PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(2.2, 2.0, 21, 0.02, -25, 25)
        self.pitchPIDController = PIDController(1.75, 0.2, 18, 0.01, -5, 5)
        self.rollPIDController = PIDController(0.6, 0.2, 9, 0.06, -1, 1)
        self.depthPIDController = PIDController(0.7, 4, 6, 0.1, -2, 2)
        '''
        
        '''
        #PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(joystickSliderValues[0], joystickSliderValues[1], joystickSliderValues[2], joystickSliderValues[3], -joystickSliderValues[4], joystickSliderValues[5])
        self.pitchPIDController = PIDController(joystickSliderValues[6], joystickSliderValues[7], joystickSliderValues[8], joystickSliderValues[9], -joystickSliderValues[10], joystickSliderValues[11])
        self.rollPIDController = PIDController(joystickSliderValues[12], joystickSliderValues[13], joystickSliderValues[14], joystickSliderValues[15], -joystickSliderValues[16], joystickSliderValues[17])
        self.depthPIDController = PIDController(joystickSliderValues[18], joystickSliderValues[19], joystickSliderValues[20], joystickSliderValues[21], -joystickSliderValues[22], joystickSliderValues[23])
        
        print "Joystick: ", self.yawPIDControllerForwardMode, self.pitchPIDController, self.rollPIDController, self.depthPIDController
        '''
        self.maxPwm = 204 #80% duty cycle
     
      
    def setPID(self):
        
        #print "Joystick: ", joystickSliderValues
        
        #PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(joystickSliderValues[0], joystickSliderValues[1], joystickSliderValues[2], joystickSliderValues[3], -joystickSliderValues[4], joystickSliderValues[5])
        self.pitchPIDController = PIDController(joystickSliderValues[6], joystickSliderValues[7], joystickSliderValues[8], joystickSliderValues[9], -joystickSliderValues[10], joystickSliderValues[11])
        self.rollPIDController = PIDController(joystickSliderValues[12], joystickSliderValues[13], joystickSliderValues[14], joystickSliderValues[15], -joystickSliderValues[16], joystickSliderValues[17])
        self.depthPIDController = PIDController(joystickSliderValues[18], joystickSliderValues[19], joystickSliderValues[20], joystickSliderValues[21], -joystickSliderValues[22], joystickSliderValues[23])
        

       
        
    def move(self, depth, xPwmSignal, yTranslateDesired, zPwmSignal, xPwmRotateSignal, yPwmRotateSignal, zPwmRotateSignal):
        '''
        Moves Sub based on XYZ coordinates and about each axis, combining the signals to get the final PWM for each thruster.
        
        **Parameters**: \n
        * **xPwmSignal** - Signal to move Sub to its left or right.
        * **yPwmSignal** - Signal to move Sub up or down.
        * **zPwmSignal** - Signal to move Sub forward or backward.
        * **xPwmRotateSignal** - Signal to pitch Sub up or down.
        * **yPwmRotateSignal** - Signal to rotate Sub clock- or counter-clockwise.
        * **zPwmRotateSignal** - Signal to roll Sub towards its right or left.
        
        **Returns**: \n
        * **thrusterPWMs** - List containing the final PWMs assigned to each thruster.\n
        '''
        #Y TRANSLATE CONTROLLER
        yScale = self.maxPwm/2.5
        yError = yTranslateDesired-depth
        
        depthPIDValue = self.depthPIDController.PIDControl(yError, yScale)  
        yPwmSignal = int(round(depthPIDValue))
        
        thrusterPWMs = []
        for index, thruster in enumerate(self.thrusters): #For each thruster object..
            
            #This line of code is able to account for any orientation and location of thruster specified. This means that we can have various thruster mounting configurations and the code wont need to change.
            self.thrusters[index].setPWM(xPwmSignal*-thruster.orientation[0] + yPwmSignal*-thruster.orientation[1] + zPwmSignal*-thruster.orientation[2] + xPwmRotateSignal*thruster.orientation[1]*thruster.location[2] + (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]) + zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0])
            
            #Need this list to send over to the GUI to display motor duty cycles
            thrusterPWMs.append(int(self.thrusters[index].pwm))
            
            #print index, xPwmSignal*-thruster.orientation[0], yPwmSignal*-thruster.orientation[1], zPwmSignal*-thruster.orientation[2], xPwmRotateSignal*thruster.orientation[1]*thruster.location[2], (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]), zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0]
            
        netSendTCBDataTimer = sendTCBDataTimer.netTimer(sendTCBDataTimer.cpuClockTimeInSeconds())
        if netSendTCBDataTimer >= 0.05: #Because I send data to fast for TCB to process, I need to send less data to the TCB. This timer slows down data being sent to the TCB so its circular buffer wont overwrite data
            #If statements are so I don't spam TCB
            if thrusterPWMs[0] != self.previousPwm[0]:
                self.tcb1DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[0] < 0, abs(thrusterPWMs[0]))
            if thrusterPWMs[1] != self.previousPwm[1]:
                self.tcb1DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[1] < 0, abs(thrusterPWMs[1]))
            if thrusterPWMs[2] != self.previousPwm[2]:
                self.tcb1DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[2] < 0, abs(thrusterPWMs[2]))
            if thrusterPWMs[3] != self.previousPwm[3]:
                self.tcb1DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[3] < 0, abs(thrusterPWMs[3]))
            if thrusterPWMs[4] != self.previousPwm[4]:
                self.tcb2DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[4] < 0, abs(thrusterPWMs[4]))
            if thrusterPWMs[5] != self.previousPwm[5]:
                self.tcb2DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[5] < 0, abs(thrusterPWMs[5]))
            if thrusterPWMs[6] != self.previousPwm[6]:
                self.tcb2DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[6] < 0, abs(thrusterPWMs[6]))
            if thrusterPWMs[7] != self.previousPwm[7]:
                self.tcb2DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[7] < 0, abs(thrusterPWMs[7]))
                
            sendTCBDataTimer.restartTimer()
            self.previousPwm = thrusterPWMs 
           
        return thrusterPWMs
            
    def advancedMove(self, poseData, xPwmSignal, yTranslateDesired, zPwmSignal, xRotateDesired, yRotateDesired, zRotateDesired): #Translation in feet with respect to NSEW, rotation in degrees with respect to NSEW
        '''
        Moves the Sub based on XYZ coordinates and desired yaw, pitch, and roll.
        
        **Parameters**: \n
        * **poseData** - Current yaw, pitch, roll, and position data.
        * **xPwmSignal** - Signal for movement to Sub's left or right.
        * **yTranslateDesired** - Desired position in Up/Down direction.
        * **zPwmSignal** - Signal for movement to Sub's front or back.
        * **xRotateDesired** - Desired pitch.
        * **yRotateDesired** - Desired yaw.
        * **zRotateDesired** - Desired roll.
        
        **Returns**: \n
        * **thrusterPWMs** - List of final PWMs assigned to each thruster.\n
        '''
        yaw, pitch, roll, depth = poseData[0], poseData[1], poseData[2], poseData[3]
        
        #PITCH CONTROLLER
        pitchScale = self.maxPwm/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        pitchError = xRotateDesired-pitch

        pitchPIDValue = self.pitchPIDController.PIDControl(pitchError, pitchScale)   
        pitchPwmSignal = int(round((pitchPIDValue))) 
        
        #YAW CONTROLLER
        yawScale = self.maxPwm/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        
        if yRotateDesired < 90 and yaw >= 270: #Because yaw is 0 to 360 deg, it is difficult to work with. This algorithm is tackling pieces of the circle one at a time
            yawError = ((yRotateDesired-yaw)+360)
        elif yRotateDesired > 270 and yaw <= 90:
            yawError = -((yaw-yRotateDesired)+360)
        else:
            yawError = yRotateDesired-yaw
          
        yawPIDValue = self.yawPIDControllerForwardMode.PIDControl(yawError, yawScale)     
        yawPwmSignal = int(round((yawPIDValue))) 
        
        #ROLL CONTROLLER
        rollScale = self.maxPwm/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.

        if zRotateDesired-roll > 180:
            rollError = zRotateDesired-roll - 360
        elif zRotateDesired-roll < -180:
            rollError = zRotateDesired-roll + 360
        else:
            rollError = zRotateDesired-roll 
           
        rollPIDValue = self.rollPIDController.PIDControl(rollError, rollScale)
        rollPwmSignal = int(round((rollPIDValue))) 
        
        #MOVE
        thrusterPWMs = self.move(depth, xPwmSignal, yTranslateDesired, zPwmSignal, pitchPwmSignal, yawPwmSignal, rollPwmSignal)
        
        return thrusterPWMs


def lockedPIDSliderValues(pidValues):
    global lockedSliderValues

    lockedSliderValues = pidValues[65:108:1]
        
class LockedController():
    '''
    Contains various types of movement for the Sub in autonomous mode, including an advanced move for  using NESW coordinates.
    '''
    def __init__(self, TCB1DataPacketsObject, TCB2DataPacketsObject, *thrusters):
        '''
        Initializes the thrusters and PID controllers. 
        
        **Parameters**: \n
        * **TCB1DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **TCB2DataPacketsObject** - Object containing thruster feedback and control for 4 thrusters.
        * **thrusters** -  BrushedThruster objects containing orientation and location data for the thrusters.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        
        
        self.tcb1DataPackets = TCB1DataPacketsObject
        self.tcb2DataPackets = TCB2DataPacketsObject
        self.thrusters = thrusters
        self.previousPwm = [0]*len(self.thrusters) #Allows me to keep track of previous PWM values so I don't spam TCB
        
        advM = utilities.AdvancedMath()
        e1 = advM.e1 #Unit vector for x
        e2 = advM.e2 #Unit vector for y
        e3 = advM.e3 #Unit vector for z
        
        self.maxPwm = 204
        self.rotateFirstToggle = False

        '''
        #PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(1.5, 1.5, 12, 0.25, -20, 20)
        self.yawPIDControllerBackwardsMode = PIDController(4, 1.8, 4.5, 0.7, -30, 30)
        self.pitchPIDController = PIDController(1, 1, 15, 0.1, -5, 5)
        self.rollPIDController = PIDController(0.3, 0.2, 9, 0.06, -1, 1)
        self.depthPIDController = PIDController(0.7, 4, 6, 0.1, -2, 2)
        self.xPIDController = PIDController(0.7, 0.2, 10, 0.5, -1, 1)
        self.zPIDController = PIDController(0.7, 0.2, 10, 0.5, -1, 1)
        '''
        
        
    def setPID(self):

        # PID CONTROLLERS
        self.yawPIDControllerForwardMode = PIDController(lockedSliderValues[0], lockedSliderValues[1],
                                                         lockedSliderValues[2], lockedSliderValues[3],
                                                         -lockedSliderValues[4], lockedSliderValues[5])
        self.yawPIDControllerBackwardsMode = PIDController(lockedSliderValues[6], lockedSliderValues[7],
                                                           lockedSliderValues[8], lockedSliderValues[9],
                                                           -lockedSliderValues[10], lockedSliderValues[11])
        self.pitchPIDController = PIDController(lockedSliderValues[12], lockedSliderValues[13],
                                                lockedSliderValues[14], lockedSliderValues[15],
                                                -lockedSliderValues[16], lockedSliderValues[17])
        self.rollPIDController = PIDController(lockedSliderValues[18], lockedSliderValues[19],
                                               lockedSliderValues[20], lockedSliderValues[21],
                                               -lockedSliderValues[22], lockedSliderValues[23])
        self.depthPIDController = PIDController(lockedSliderValues[24], lockedSliderValues[25],
                                                lockedSliderValues[26], lockedSliderValues[27],
                                                -lockedSliderValues[28], lockedSliderValues[29])
        self.xPIDController = PIDController(lockedSliderValues[30], lockedSliderValues[31],
                                            lockedSliderValues[32], lockedSliderValues[33],
                                            -lockedSliderValues[34], lockedSliderValues[35])
        self.zPIDController = PIDController(lockedSliderValues[36], lockedSliderValues[37],
                                            lockedSliderValues[38], lockedSliderValues[39],
                                            -lockedSliderValues[40], lockedSliderValues[41])

        #print "Locked: ", lockedSliderValues[35], lockedSliderValues[36], lockedPIDSliderValues[37]
        
        
    def simpleMove(self, *motorPwms): #Assign thruster pwm by thruster pwm
        '''
        Directly sets each indiviudal PWM for each thruster. 
        
        **Parameters**: \n
        * **motorPwms** - Integers to directly set PWM on each thruster, must be between 0 and 204.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        for index, motorPwm in enumerate(motorPwms):
            self.thrusters[index].setPWM(motorPwm) #Assign motor PWMs to objects speed variable
            
    def move(self, xPwmSignal, yPwmSignal, zPwmSignal, xPwmRotateSignal, yPwmRotateSignal, zPwmRotateSignal):
        '''
        Moves Sub based on XYZ coordinates and about each axis, combining the signals to get the final PWM for each thruster.
        
        **Parameters**: \n
        * **xPwmSignal** - Signal to move Sub to its left or right.
        * **yPwmSignal** - Signal to move Sub up or down.
        * **zPwmSignal** - Signal to move Sub forward or backward.
        * **xPwmRotateSignal** - Signal to pitch Sub up or down.
        * **yPwmRotateSignal** - Signal to rotate Sub clock- or counter-clockwise.
        * **zPwmRotateSignal** - Signal to roll Sub towards its right or left.
        
        **Returns**: \n
        * **thrusterPWMs** - List containing the final PWMs assigned to each thruster.\n
        '''
        thrusterPWMs = []
        for index, thruster in enumerate(self.thrusters): #For each thruster object..
            
            #This line of code is able to account for any orientation and location of thruster specified. This means that we can have various thruster mounting configurations and the code wont need to change.
            self.thrusters[index].setPWM(xPwmSignal*-thruster.orientation[0] + yPwmSignal*-thruster.orientation[1] + zPwmSignal*-thruster.orientation[2] + xPwmRotateSignal*thruster.orientation[1]*thruster.location[2] + (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]) + zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0])
            
            #Need this list to send over to the GUI to display motor duty cycles
            thrusterPWMs.append(int(self.thrusters[index].pwm))
            
            #print index, xPwmSignal*-thruster.orientation[0], yPwmSignal*-thruster.orientation[1], zPwmSignal*-thruster.orientation[2], xPwmRotateSignal*thruster.orientation[1]*thruster.location[2], (yPwmRotateSignal*-thruster.orientation[0]*thruster.location[2] + yPwmRotateSignal*thruster.orientation[2]*thruster.location[0]), zPwmRotateSignal*-thruster.orientation[1]*thruster.location[0]
            
        netSendTCBDataTimer = sendTCBDataTimer.netTimer(sendTCBDataTimer.cpuClockTimeInSeconds())
        if netSendTCBDataTimer >= 0.05: #Because I send data to fast for TCB to process, I need to send less data to the TCB. This timer slows down data being sent to the TCB so its circular buffer wont overwrite data
            #If statements are so I don't spam TCB
            if thrusterPWMs[0] != self.previousPwm[0]:
                self.tcb1DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[0] < 0, abs(thrusterPWMs[0]))
            if thrusterPWMs[1] != self.previousPwm[1]:
                self.tcb1DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[1] < 0, abs(thrusterPWMs[1]))
            if thrusterPWMs[2] != self.previousPwm[2]:
                self.tcb1DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[2] < 0, abs(thrusterPWMs[2]))
            if thrusterPWMs[3] != self.previousPwm[3]:
                self.tcb1DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[3] < 0, abs(thrusterPWMs[3]))
            if thrusterPWMs[4] != self.previousPwm[4]:
                self.tcb2DataPackets.setMotorDirectionSpeed(1, thrusterPWMs[4] < 0, abs(thrusterPWMs[4]))
            if thrusterPWMs[5] != self.previousPwm[5]:
                self.tcb2DataPackets.setMotorDirectionSpeed(2, thrusterPWMs[5] < 0, abs(thrusterPWMs[5]))
            if thrusterPWMs[6] != self.previousPwm[6]:
                self.tcb2DataPackets.setMotorDirectionSpeed(3, thrusterPWMs[6] < 0, abs(thrusterPWMs[6]))
            if thrusterPWMs[7] != self.previousPwm[7]:
                self.tcb2DataPackets.setMotorDirectionSpeed(4, thrusterPWMs[7] < 0, abs(thrusterPWMs[7]))
                
            sendTCBDataTimer.restartTimer()
            self.previousPwm = thrusterPWMs 
           
        return thrusterPWMs
            
    def advancedMove(self, poseData, eastTranslateDesired, upTranslateDesired, northTranslateDesired, xRotateDesired, yRotateDesired, zRotateDesired, *userVariables): #Translation in feet with respect to NSEW, rotation in degrees with respect to NSEW
        '''
        Moves the Sub based on desired NESW coordinates and desired yaw, pitch, and roll.
        
        **Parameters**: \n
        * **poseData** - Current yaw, pitch, roll, and position data.
        * **eastTranslateDesired** - Desired position in East/West direction.
        * **upTranslateDesired** - Desired position in Up/Down direction.
        * **northTranslateDesired** - Desired position in North/South direction.
        * **xRotateDesired** - Desired pitch.
        * **yRotateDesired** - Desired yaw.
        * **zRotateDesired** - Desired roll.
        * **userVariables** - Driving mode. 0 is forwards, 1 is backwards.
        
        **Returns**: \n
        * **thrusterPWMs** - List of final PWMs assigned to each thruster.
        * **[pos[0][0], pos[1][0], pos[2][0], pitchError, yawError, rollError]** - Remaining error in position, pitch, yaw, and roll.
        * **yRotateDesired** - Desired yaw.\n
        '''
        yaw, pitch, roll = poseData[0], poseData[1], poseData[2]
        eastPosition, upPosition, northPosition = poseData[3], poseData[4], poseData[5]
        
        if len(userVariables) > 0:
            drivingMode = userVariables[0]
        
        #X TRANSLATE CONTROLLER
        eastScale = self.maxPwm/2
        eastError = eastTranslateDesired-eastPosition
        
        #Y TRANSLATE CONTROLLER
        upScale = self.maxPwm/2
        upError = upTranslateDesired-upPosition
        
        #Z TRANSLATE CONTROLLER
        northScale = self.maxPwm/2
        northError = northTranslateDesired-northPosition
        
        
        #TRANSFORMATION MATRICIE
        T = advM.matrixMultiply(advM.inv(advM.Rot(e2, yaw)), advM.Trans(e1, eastError), advM.Trans(e2, upError), advM.Trans(e3, northError), advM.Rot(e2, yaw))       
        rot, pos = advM.extractData(T)
        
        #X TRANSLATE CONTROLLER
        xPIDValue = self.xPIDController.PIDControl(pos[0][0], eastScale) 
        
        xPwmSignal = int(round(xPIDValue))
        if xPwmSignal < -self.maxPwm:
            xPwmSignal = -self.maxPwm
        elif xPwmSignal > self.maxPwm:
            xPwmSignal = self.maxPwm
        
        #Y TRANSLATE CONTROLLER
        depthPIDValue = self.depthPIDController.PIDControl(pos[1][0], upScale) 
        
        yPwmSignal = int(round(depthPIDValue))
        if yPwmSignal < -self.maxPwm:
            yPwmSignal = -self.maxPwm
        elif yPwmSignal > self.maxPwm:
            yPwmSignal = self.maxPwm
        
        #Z TRANSLATE CONTROLLER
        zPIDValue = self.zPIDController.PIDControl(pos[2][0], northScale) 
        
        zPwmSignal = int(round(zPIDValue))
        if zPwmSignal < -self.maxPwm:
            zPwmSignal = -self.maxPwm
        elif zPwmSignal > self.maxPwm:
            zPwmSignal = self.maxPwm
            
            
        #print "North error:", pos[2][0], " East error:", pos[0][0]
        
        #PITCH CONTROLLER
        pitchScale = 255.0/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        pitchError = xRotateDesired-pitch
        
        pitchPIDValue = self.pitchPIDController.PIDControl(pitchError, pitchScale)
        
        pitchPwmSignal = int(round((pitchPIDValue))) 
        if pitchPwmSignal < -self.maxPwm:
            pitchPwmSignal = -self.maxPwm
        elif pitchPwmSignal > self.maxPwm:
            pitchPwmSignal = self.maxPwm
        
        #YAW CONTROLLER 
        yawScale = self.maxPwm/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.
        print yRotateDesired
        #FACE IN WAYPOINT DIRECTION
        corectOrientationBubble = 3.5 #feet
        if abs(northError) > corectOrientationBubble or abs(eastError) > corectOrientationBubble:
            yRotateDesired = (math.atan2(eastError, northError)*(180/3.14159265))%360 #Yaw to facing at waypoint

        #USER VARIABLE 
        if drivingMode == 1:
            yRotateDesired = (yRotateDesired + 180)%360
            
        
        yawError = yRotateDesired - yaw
        if yaw > yRotateDesired and yawError < -180: 
            yawError = yawError + 360
        
        elif yaw <= yRotateDesired and yawError >= 180: 
            yawError = yawError - 360
            
        #USER VARIABLE
        if abs(pos[0][0]) > 5 or abs(pos[2][0]) > 5:
            if drivingMode == 2:
                yawError = -150 #clockwise
            elif drivingMode == 3:
                yawError = 150 #Counter clockwise
                
        
        if drivingMode == 0:
            yawPIDValue = self.yawPIDControllerForwardMode.PIDControl(yawError, yawScale)       
        if drivingMode == 1:
            yawPIDValue = self.yawPIDControllerBackwardsMode.PIDControl(yawError, yawScale)    
        
        yawPwmSignal = int(round(yawPIDValue)) 
        if yawPwmSignal < -self.maxPwm:
            yawPwmSignal = -self.maxPwm
        elif yawPwmSignal > self.maxPwm:
            yawPwmSignal = self.maxPwm
            
        
        #FACE IN WAYPOINT DIRECTION  
        
        if drivingMode == 0 or drivingMode == 1: #USER VARIABLE
            if abs(northError) > corectOrientationBubble or abs(eastError) > corectOrientationBubble:
                if abs(yawError) >= 5:
                    xPwmSignal = xPwmSignal*0.85
                    zPwmSignal = zPwmSignal*0.85
        
        
        #ROLL CONTROLLER
        Kp = 1.5 #Just using a P controller of PID
        rollScale = 255.0/180.0 #180 being the highest value pitchError can be and 255 being the desired range to map to.

        if zRotateDesired-roll > 180:
            rollError = zRotateDesired-roll - 360
        elif zRotateDesired-roll < -180:
            rollError = zRotateDesired-roll + 360
        else:
            rollError = zRotateDesired-roll 
        
        rollPIDValue = self.rollPIDController.PIDControl(rollError, rollScale)
        
        rollPwmSignal = int(round(rollPIDValue)) 
        if rollPwmSignal < -self.maxPwm:
            rollPwmSignal = -self.maxPwm
        elif rollPwmSignal > self.maxPwm:
            rollPwmSignal = self.maxPwm
            
        if len(userVariables) > 1:
            if userVariables[1][0] == True:
                yawPwmSignal = 0
                if userVariables[1][1] > 0.2 or userVariables[1][1] < -0.2:
                    yawPwmSignal = userVariables[1][1]
            if userVariables[1][2] > 0.2 or userVariables[1][2] < -0.2:
                pitchPwmSignal = userVariables[1][2]
            if userVariables[1][3] > 0.2 or userVariables[1][3] < -0.2:
                rollPwmSignal = userVariables[1][3]
        
        #MOVE
        thrusterPWMs = self.move(xPwmSignal, yPwmSignal, zPwmSignal, pitchPwmSignal, yawPwmSignal, rollPwmSignal)
        
        if yRotateDesired == None:
            pass
            #print yRotateDesired
        
        return thrusterPWMs, [pos[0][0], pos[1][0], pos[2][0], pitchError, yawError, rollError], yRotateDesired
        
    def trajectoryPlanningAndGeneration(self, desiredPosX, desiredPosY, desiredPosZ, desiredAngleX, desiredAngleY, desiredAngleZ, finalTime, ahrsData):
        '''
        Controls the time it takes for thrusters to ramp up.
        
        **Parameters**: \n
        * **desiredPosX** - Desired X position, left or right.
        * **desiredPosY** - Desired Y position, up or down.
        * **desiredPosZ** - Desired Z position, front or back.
        * **desiredAngleX** - Desired yaw.
        * **desiredAngleY** - Desired pitch.
        * **desiredAngleZ** - Desired roll.
        * **finalTime** - Time it takes to ramp up.
        * **ahrsData** - Orientation data from AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #This is being tested for now but what i have so far is correct for a cycloid, except probably want to change the while statement
        yaw, pitch, roll = ahrsData[0], ahrsData[1], ahrsData[2]
        k = 1
        incrementalPitchAngle = 0
        
        while(incrementalPitchAngle < desiredAngleX):
            currentTime = time.time()-initialTime
            incrementalPitchAngle = pitch + (desiredAngleX-pitch)*((currentTime/finalTime)-math.sin((2*k*3.1416*currentTime)/finalTime)/(2*k*3.1416))
            moveController.advancedMove(0, 0, 0, incrementalPitchAngle, 0, 0, ahrsData)
            
class PIDController():
    '''
    Creates customizable PID controller for yaw, pitch, or roll.
    '''
    def __init__(self, Kp, Ki, Kd, dControllerTime, integratorMin, integratorMax):
        '''
        Moves the Sub based on XYZ coordinates and desired yaw, pitch, and roll.
        
        **Parameters**: \n
        * **Kp** - Factor for proportional gain.
        * **Ki** - Factor for integral or error over time gain.
        * **Kd** - Factor for dampening
        * **integratorMin** - Minimum integrator factor.
        * **integratorMax** - Maximum integrator factor.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        self.derivator = 0
        self.integrator = 0
        self.integratorMin = integratorMin
        self.integratorMax = integratorMax
        
        
        self.dControllerTimer = utilities.Timer()
        self.dControllerTime = dControllerTime
        
    def PIDControl(self, error, errorScale):
        '''
        Moves the Sub based on XYZ coordinates and desired yaw, pitch, and roll.
        
        **Parameters**: \n
        * **error** - How far away the current value is from the desired value.
        * **errorScale** - The scale for the system being controlled.
        
        **Returns**: \n
        * **PID** - Signal for the yaw, pitch, or roll.\n
        '''
        Kp = self.Kp
        P = Kp*error*errorScale
        
        Ki = self.Ki
        self.integratorMax = 10
        self.integratorMin = -10
        self.integrator = self.integrator + error*errorScale
        if self.integrator > self.integratorMax:
            self.integrator = self.integratorMax
        elif self.integrator < self.integratorMin:
            self.integrator = self.integratorMin

        I = self.integrator * Ki
        
        
        Kd = self.Kd
        D = Kd * (error*errorScale - self.derivator)

        netDControllerTimer = self.dControllerTimer.netTimer(self.dControllerTimer.cpuClockTimeInSeconds())
        if netDControllerTimer >= self.dControllerTime:
            self.derivator = error*errorScale
            self.dControllerTimer.restartTimer()
            
            
        PID = P+I+D
        
        return PID        
    

if __name__=="__main__":
    thruster1 = BrushedThruster(1, [0, 1, 0], [1, 0, 1])  #Up/Down thruster
    thruster2 = BrushedThruster(2, [0, 1, 0], [-1, 0, 1])  #Up/Down thruster
    thruster3 = BrushedThruster(3, [0, 1, 0], [1, 0, -1])  #Up/Down thruster
    thruster4 = BrushedThruster(4, [0, 1, 0], [-1, 0, -1])  #Up/Down thruster
    thruster5 = BrushedThruster(5, [-1, 0, 0], [0, 1, 1]) #Left/Right thruster
    thruster6 = BrushedThruster(6, [-1, 0, 0], [0, 1, -1]) #Left/Right thruster
    thruster7 = BrushedThruster(7, [0, 0, -1], [1, 1, 0]) #Fwd/Rev thruster
    thruster8 = BrushedThruster(8, [0, 0, -1], [-1, 1, 0]) #Fwd/Rev thruster

    moveController = MovementController(thruster1, thruster2, thruster3, thruster4, thruster5, thruster6, thruster7, thruster8)
    
    #moveController.simpleMove(255, 255, 255, 255, 0, 0, 0, 0)
    #moveController.move(0, 60, 0, 50, 0, 25)
    moveController.advancedMove(0, 0, 0, 40, 0, 0, [0, 20, 0])
    #moveController.trajectoryPlanningAndGeneration(0, 0, 0, 10, 0, 0, 2, [0, 0, 0])
