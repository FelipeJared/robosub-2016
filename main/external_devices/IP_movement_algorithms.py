'''
Copyright 2016, Austin Owens, All rights reserved.

.. module:: IP_movement_algorithms
   :synopsis: Contains movement algorithms that tell how robotic arm should move with image processing input.
   
:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Jan 4, 2016
:Description: When the inverse kinematics are given to the kinematics module, a series of movements can be put together based upon image processing input.
'''

from main.utility_package import utilities

class IP4DOFCamRefModes:
    def __init__(self, window, kinematicDimensions, homeConfigurationOffset):
        self.window = window
        self.a1, self.a2, self.b1, self.b2, self.b3 = kinematicDimensions
        self.homeConfigurationOffset = homeConfigurationOffset
        
        self.fx, self.fy = 635, 400#2.0408163*(window.imgWidth-530)+500, 1.9230769*(window.imgHeight-362)+400#500, 400#400, 300
        self.cx, self.cy = 265, 181#window.imgWidth/2.0, window.imgHeight/2.0 #240.5, 155
        self.c1, self.c2 = 140, 2000#2.65306*(window.imgWidth-530)+500, -0.961538*(window.imgHeight-362)+440#500, 440#8.5714286*(window.imgWidth-530)+790, -0.7692308*(window.imgHeight-362)+450#810, 490#370, 490
        
        
        #XYZTimedTrack
        self.movementList = None
        self.initializePosition = True
        self.nextPositionTimer = utilities.Timer()
        self.positionNumber = 1

        
    def XYActiveTrack(self, imageProcessingData, Z):
        u, v, uWidth, vHeight = imageProcessingData[0][0][0], imageProcessingData[0][0][1], imageProcessingData[0][1][0], imageProcessingData[0][1][1]
        
        if uWidth >= 1 and vHeight >= 1:           
            #Z, fx, fy = 0.82086, 600, 612 #Trial1
            #Z, fx, fy = 0.13145, 450, 375 #Trial2
            #Z, fx, fy = 0.13145, 450, 300 #Trial3
            #Z, fx, fy, cx, cy = 0.13145, 549.65, 475.64, 264.13, 142.74 #Trial4
            
            X = ((Z*0.001)/self.fx)*(u - self.cx)*1000
            Y = ((Z*0.001)/self.fy)*(v - self.cy)*1000
            
        else:
            X = self.window.positionScales[0].get()
            Y = self.window.positionScales[1].get()
            
        self.window.positionScales[0].set(X)
        self.window.positionScales[1].set(Y)
    
    def XYZActiveTrack(self, imageProcessingData, xWidth, yHeight):
        u, v, uWidth, vHeight, orientation = imageProcessingData[0][0][0], imageProcessingData[0][0][1], imageProcessingData[0][1][0], imageProcessingData[0][1][1], imageProcessingData[0][2] 
        
        if uWidth >= 1 and vHeight >= 1:           
            
            Z1 = (((xWidth*0.001)/uWidth)*self.c1)*1000
            Z2 = (((yHeight*0.001)/vHeight)*self.c2)*1000
            
            Z = (Z1+Z2)/2.0
            if Z >= self.a1 + self.a2 - self.b3:
                Z = self.a1 + self.a2 - self.b3
            
            X = ((Z*0.001)/self.fx)*(u - self.cx)*1000
            Y = ((Z*0.001)/self.fy)*(v - self.cy)*1000
            
            '''
            orientationOffset = orientation - 32
            if orientationOffset < 0:
                orientationOffset = 0
            self.window.jointScales[3].set(orientationOffset)
            self.window.servoModel.setGoalPosition(4, orientationOffset)
            '''
            
        else:
            X = self.window.positionScales[0].get()
            Y = self.window.positionScales[1].get()
            Z = self.window.positionScales[2].get()
            
        self.window.positionScales[0].set(X)
        self.window.positionScales[1].set(Y)
        self.window.positionScales[2].set(Z)
        
    def XYZTimedTrack(self, imageProcessingData, xWidth, yHeight):
        if self.initializePosition == True:  
            u, v, uWidth, vHeight, orientation = imageProcessingData[0][0][0], imageProcessingData[0][0][1], imageProcessingData[0][1][0], imageProcessingData[0][1][1], imageProcessingData[0][2]
            Z1 = (((xWidth*0.001)/uWidth)*self.c1)*1000
            Z2 = (((yHeight*0.001)/vHeight)*self.c2)*1000
            ZTimedTrack = (Z1+Z2)/2.0
            
            if ZTimedTrack >= self.a1 + self.a2 - self.b3:
                ZTimedTrack = self.a1 + self.a2 - self.b3
            
            XTimedTrack = ((ZTimedTrack*0.001)/self.fx)*(u - self.cx)*1000
            YTimedTrack = ((ZTimedTrack*0.001)/self.fy)*(v - self.cy)*1000
            
            orientationOffset = 149.06+orientation
            if orientation > 90:
                orientationOffset = orientation - 32
                
            self.movementList = [[XTimedTrack, YTimedTrack, 70, self.homeConfigurationOffset[3], 166, 18], [XTimedTrack, YTimedTrack, ZTimedTrack, orientationOffset, 166, 0], [XTimedTrack, YTimedTrack, ZTimedTrack, orientationOffset, 115, 0], [XTimedTrack, YTimedTrack, 100, self.homeConfigurationOffset[3], 115, 0], [self.b1, self.a1+self.a2+self.b2, -self.b3, self.homeConfigurationOffset[3], 115, 18]] #[XPos, YPos, ZPos, wristJointAngle, EEJointAngle, thirdJointAngleSpeed]

            #Changing third joint speed
            self.window.config1Scales[0][2].set(self.movementList[0][5])
            self.window.servoModel.setMovingSpeed(3, self.movementList[0][5])
            
            #Changing position
            self.window.positionScales[0].set(self.movementList[0][0])
            self.window.positionScales[1].set(self.movementList[0][1])
            self.window.positionScales[2].set(self.movementList[0][2])
            
            #Changing wrist angle
            self.window.jointScales[3].set(self.movementList[0][3])
            self.window.servoModel.setGoalPosition(4, self.movementList[0][3])
            
            ##Changing EE angle
            self.window.jointScales[4].set(self.movementList[0][4])
            self.window.servoModel.setGoalPosition(5, self.movementList[0][4])
            
            self.initializePosition = False
            
        netNextPositionTimer = self.nextPositionTimer.netTimer(self.nextPositionTimer.cpuClockTimeInSeconds()) 
        if netNextPositionTimer > 1.4 and self.positionNumber < len(self.movementList):
            #Changing third joint speed
            self.window.config1Scales[0][2].set(self.movementList[self.positionNumber][5])
            self.window.servoModel.setMovingSpeed(3, self.movementList[self.positionNumber][5])
            
            #Changing position
            self.window.positionScales[0].set(self.movementList[self.positionNumber][0])
            self.window.positionScales[1].set(self.movementList[self.positionNumber][1])
            self.window.positionScales[2].set(self.movementList[self.positionNumber][2])
            
            #Changing wrist angle
            self.window.jointScales[3].set(self.movementList[self.positionNumber][3])
            self.window.servoModel.setGoalPosition(4, self.movementList[self.positionNumber][3])
            
            #Changing EE angle
            self.window.jointScales[4].set(self.movementList[self.positionNumber][4])
            self.window.servoModel.setGoalPosition(5, self.movementList[self.positionNumber][4])
            
            self.nextPositionTimer.restartTimer()
            self.positionNumber += 1
            
        if self.positionNumber >= len(self.movementList):
            self.window.trackObjectButton.config(text="Track Object")
            self.window.trackObject = False
            self.initializePosition = True
            self.positionNumber = 1
            
            