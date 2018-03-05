'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: graphic_overlay
   :synopsis: Draws the gauges on top of the raw camera feeds.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 5, 2014
:Description: Draws the GUI gauges based on the user's settings.
'''
import cv2
import math
import main.utility_package.utilities as utilities
import time, datetime
import numpy

advM = utilities.AdvancedMath()
e1 = advM.e1 #Unit vector for x
e2 = advM.e2 #Unit vector for y
e3 = advM.e3 #Unit vector for z

#Heading
stringAddHeading, counterHeading = 0, 0

#Pitch
counterPitch, stringAddPitch = 0, 0

#Roll
counterRoll, stringAddRoll = 0, 0

#Depth
stringAddDepth, counterDepth = 0, 0

class GraphicOverlay:
    '''
    Creates the gauges and graphics that go on the GUI camera feeds. 
    '''
    def __init__(self, window, screenWidth, screenHeight):
        '''
        Initializes the window, screen, and graphics variables.
        
        **Parameters**: \n
        * **window** - The main TKinter program window.
        * **screenWidth** - The pixel width of the screen.
        * *screenHeight** - The pixel height of the screen.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.window = window
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        
        self.setInitialTickPosition = [True, True, True]
        self.compassNames = ["N", "E", "S", "W"]
        
        self.desiredDepthTriangleScale = 0
        self.desiredYawTriangleScale = 0
        self.desiredPitchTriangleScale = 0
        
    def drawHeadingGauge(self, scaledMainImg, numOfTicks, increments, position, gaugeWidth, rgbValues, sensorInput): #(img, number of tick marks, increments of the scale, gauge width, sensor input)
        '''
        Draws the Heading gauge which changes according to AHRS data.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **numOfTicks** - Number of ticks chosen in settings slider.
        * **increments** - How many degrees each tick represents.
        * **position** -  Boolean indicating whether to place the gauge on top or bottom, 1 being top.
        * **gaugeWidth** - How many pixels wide the gauge is.
        * **rgbValues** - The color values for the gauge.
        * ** sensorInput** - The median heading detected by the AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global counterHeading, stringAddHeading
        if sensorInput[2] == None:
            desiredYaw = 0
        else:
            desiredYaw = sensorInput[2]
            
        if sensorInput[3] == True:
            desiredYaw = sensorInput[4]
        
        #Creating points for the line
        lineLength = gaugeWidth #Originally 381
        x1 = self.screenWidth/2 - lineLength/2
        x2 = self.screenWidth/2 + lineLength/2
        
        if position == 0:
            y1 = self.screenHeight-24
            y2 = self.screenHeight-24
            graphicNumberCorrection = -13
            compassCorrectionValue = -28
            cv2.line(scaledMainImg, (self.screenWidth/2, y1+10), ((self.screenWidth/2)-10, y1+20), rgbValues)#Creating top line for arrow
            cv2.line(scaledMainImg, (self.screenWidth/2, y1+10), ((self.screenWidth/2)+10, y1+20), rgbValues)#Creating bottom line for arrow
            cv2.line(scaledMainImg, ((self.screenWidth/2)-10, y1+20), ((self.screenWidth/2)+10, y1+20), rgbValues)#Creating closing line for triangle
            
        elif position == 1:
            y1 = 20
            y2 = 20
            graphicNumberCorrection = 25
            compassCorrectionValue = 40
            cv2.line(scaledMainImg, (self.screenWidth/2, y1-10), ((self.screenWidth/2)-10, y1-20), rgbValues)#Creating top line for arrow
            cv2.line(scaledMainImg, (self.screenWidth/2, y1-10), ((self.screenWidth/2)+10, y1-20), rgbValues)#Creating bottom line for arrow
            cv2.line(scaledMainImg, ((self.screenWidth/2)-10, y1-20), ((self.screenWidth/2)+10, y1-20), rgbValues)#Creating closing line for triangle
            
        tickMarkGapDistance = lineLength/numOfTicks #Distance between tick marks
        heading = sensorInput[0]
        
        if self.setInitialTickPosition[0]:
            stringAddHeading = (numOfTicks*increments)/2.0 #The amount of tick marks above the middle tick mark
            self.setInitialTickPosition[0] = False
            counterHeading = 0
            
        cv2.line(scaledMainImg, (x1, y1), (x2, y2), rgbValues) #Creating line
        for x in range(numOfTicks+1):
            tickMarkHeight = x1 + (lineLength*x)/numOfTicks #The INITIAL height of each tick mark
            tickMarkMoving = int(round(tickMarkHeight - ((heading-counterHeading)*tickMarkGapDistance)/increments, 0)) #The height of each tick mark after moving them based on sensor input
    
            if x == 0 and tickMarkMoving <= x1 - tickMarkGapDistance: #As the tick marks are moving up; once the tick mark's distance away from the top of the line is the difference between the tick mark gaps...
                counterHeading += increments*((x1 - tickMarkMoving)/tickMarkGapDistance) #Increment a counter that will move the ticks marks back down to their initial position and adjust the tick mark numbers. If the user doesnt enter a high enough increment, the tick marks will run behind. To catch them up, we find out how many tickMarkGaps ahead it is and multiply that to increment
                
            elif x == numOfTicks and tickMarkMoving >= x2 + tickMarkGapDistance: #As the tick marks are moving down; once the tick mark's distance away from the bottom of the line is the difference between the tick mark gaps...
                counterHeading -= increments*((x2 + tickMarkMoving)/tickMarkGapDistance) #Decrement a counter that will move the ticks marks back up to their initial position and adjust the tick mark numbers
                    
            elif tickMarkMoving >= x1 and tickMarkMoving <= x2: #As long as the tick marks don't go past the line upper or lower bounds of the line...
                graphicNumbers = round((360-stringAddHeading+counterHeading+(x*increments))%360, 5)
                graphicNumbersBelow = round((360-stringAddHeading+counterHeading+((x-1)*increments))%360, 5)
                
                cv2.line(scaledMainImg, (tickMarkMoving, y1-10), (tickMarkMoving, y1+10), rgbValues) #Draw the tick mark
                if graphicNumbers - int(graphicNumbers) == 0: #Get rid of decimals when not using them
                    graphicNumbers = int(round(graphicNumbers, 0))
                if graphicNumbers == 0: #This centers the zero
                    cv2.putText(scaledMainImg, str(graphicNumbers), (tickMarkMoving-4, y1+graphicNumberCorrection), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                if graphicNumbers != 0:
                    cv2.putText(scaledMainImg, str(graphicNumbers), (tickMarkMoving-11, y1+graphicNumberCorrection), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                for x in range(4):
                    if graphicNumbers == x*90: #Put north south east west
                        cv2.putText(scaledMainImg, self.compassNames[x], (tickMarkMoving-4, y1+compassCorrectionValue), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues)
    
                #MOVING RED TRIANGLE
                
                if desiredYaw == graphicNumbers:
                    self.desiredYawTriangleScale = tickMarkMoving
                    
                elif desiredYaw > graphicNumbersBelow and desiredYaw <= graphicNumbersBelow+increments:
                    if graphicNumbersBelow+increments == 360:
                        self.desiredYawTriangleScale = int(tickMarkMoving - tickMarkGapDistance*((360-desiredYaw)/increments))
                    else:
                        self.desiredYawTriangleScale = int(tickMarkMoving - tickMarkGapDistance*((graphicNumbers-desiredYaw)/increments))
                        
        if sensorInput[1] == True or sensorInput[3] == True or self.window.DEBUG == True:
            if position == 0:  
                cv2.line(scaledMainImg, (self.desiredYawTriangleScale, y1+10), (-10+self.desiredYawTriangleScale, y1+20), (0, 0, 255))#Creating top line for arrow
                cv2.line(scaledMainImg, (self.desiredYawTriangleScale, y1+10), (10+self.desiredYawTriangleScale, y1+20), (0, 0, 255))#Creating bottom line for arrow
                cv2.line(scaledMainImg, (-10+self.desiredYawTriangleScale, y1+20), (10+self.desiredYawTriangleScale, y1+20), (0, 0, 255))#Creating closing line for triangle
                        
            elif position == 1:
                cv2.line(scaledMainImg, (self.desiredYawTriangleScale, y1-10), (-10+self.desiredYawTriangleScale, y1-20), (0, 0, 255))#Creating top line for arrow
                cv2.line(scaledMainImg, (self.desiredYawTriangleScale, y1-10), (10+self.desiredYawTriangleScale, y1-20), (0, 0, 255))#Creating bottom line for arrow
                cv2.line(scaledMainImg, (10+self.desiredYawTriangleScale, y1-20), (10+self.desiredYawTriangleScale, y1-20), (0, 0, 255))#Creating closing line for triangle

    
    def drawPitchGauge(self, scaledMainImg, numOfTicks, increments, gaugeLength, rgbValues, sensorInput): #(img, number of tick marks, increments of the scale, gauge length, sensor input)
        '''
        Draws the Pitch gauge which changes according to AHRS data.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **numOfTicks** - Number of ticks chosen in settings slider.
        * **increments** - How many feet each tick represents.
        * **gaugeLength** - How many pixels tall the gauge is.
        * **rgbValues** - The color values for the gauge.
        * ** sensorInput** - The median pitch detected by the AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global counterPitch, stringAddPitch
        
        if sensorInput[2] == None:
            desiredPitch = 0
        else:
            desiredPitch = sensorInput[2]
            
        if sensorInput[3] == True:
            desiredPitch = sensorInput[4]    
        
        
        #Creating points for the line
        lineLength = gaugeLength #Originally 361
        x1 = self.screenWidth/2
        y1 = self.screenHeight/2 - lineLength/2
        y2 = self.screenHeight/2 + lineLength/2
            
        tickMarkGapDistance = lineLength/numOfTicks #Distance between tick marks
        pitch = sensorInput[0]
        
        
        cv2.line(scaledMainImg, (x1-7, self.screenHeight/2), (x1+7, self.screenHeight/2), rgbValues) #Creating Plus Sign
        cv2.line(scaledMainImg, (x1, self.screenHeight/2 + 7), (x1, self.screenHeight/2 - 7), rgbValues) #Creating Plus Sign
        if self.setInitialTickPosition[1]:
            stringAddPitch = -(numOfTicks*increments)/2.0 #The amount of tick marks above the middle tick mark
            self.setInitialTickPosition[1] = False
            counterPitch = 0
        
        for x in range(numOfTicks+1):
            tickMarkHeight = y1 + (lineLength*x)/numOfTicks #The INITIAL height of each tick mark
            tickMarkMoving = int(tickMarkHeight + ((pitch+counterPitch)*tickMarkGapDistance)/increments) #The height of each tick mark after moving them based on sensor input

            if x == 0 and tickMarkMoving <= y1 - tickMarkGapDistance: #As the tick marks are moving up; once the tick mark's distance away from the top of the line is the difference between the tick mark gaps...
                counterPitch += increments*((y1 - tickMarkMoving)/tickMarkGapDistance) #Increment a counter that will move the ticks marks back down to their initial position and adjust the tick mark numbers. If the user doesnt enter a high enough increment, the tick marks will run behind. To catch them up, we find out how many tickMarkGaps ahead it is and multiply that to increment

            elif x == numOfTicks and tickMarkMoving >= y2 + tickMarkGapDistance: #As the tick marks are moving down; once the tick mark's distance away from the bottom of the line is the difference between the tick mark gaps...
                counterPitch -= increments*((y2 + tickMarkMoving)/tickMarkGapDistance) #Decrement a counter that will move the ticks marks back up to their initial position and adjust the tick mark numbers
                    
            elif tickMarkMoving >= y1 and tickMarkMoving <= y2: #As long as the tick marks don't go past the line upper or lower bounds of the line...
                graphicNumbers = -round(stringAddPitch+counterPitch+(x*increments), 5) 
                
                if graphicNumbers -  int(graphicNumbers) == 0: #Get rid of decimals when not using them
                    graphicNumbers = int(graphicNumbers) 
                if graphicNumbers >= -90 and graphicNumbers <= 90:
                    if graphicNumbers == 0: #Draw the big tick mark if graphicNumbers = 0
                        cv2.line(scaledMainImg, (x1-50, tickMarkMoving), (x1+50, tickMarkMoving), rgbValues) #Draw the tick mark
                    else:
                        if graphicNumbers > 0:
                            cv2.line(scaledMainImg, (x1-25, tickMarkMoving), (x1-5, tickMarkMoving), rgbValues) #Draw the tick mark
                            cv2.line(scaledMainImg, (x1-5, tickMarkMoving), (x1-5, tickMarkMoving-5), rgbValues) #Draw the tick mark
                            cv2.line(scaledMainImg, (x1+5, tickMarkMoving), (x1+25, tickMarkMoving), rgbValues) #Draw the tick mark 
                            cv2.line(scaledMainImg, (x1+5, tickMarkMoving), (x1+5, tickMarkMoving-5), rgbValues) #Draw the tick mark
                        elif graphicNumbers < 0:
                            cv2.line(scaledMainImg, (x1-25, tickMarkMoving), (x1-5, tickMarkMoving), rgbValues) #Draw the tick mark
                            cv2.line(scaledMainImg, (x1-5, tickMarkMoving), (x1-5, tickMarkMoving+5), rgbValues) #Draw the tick mark
                            cv2.line(scaledMainImg, (x1+5, tickMarkMoving), (x1+25, tickMarkMoving), rgbValues) #Draw the tick mark 
                            cv2.line(scaledMainImg, (x1+5, tickMarkMoving), (x1+5, tickMarkMoving+5), rgbValues) #Draw the tick mark 
                    cv2.putText(scaledMainImg, str(graphicNumbers), (x1+55, tickMarkMoving+5), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                
                #MOVING RED TRIANGLE
                if desiredPitch > (graphicNumbers-increments) and desiredPitch <= graphicNumbers:
                    self.desiredPitchTriangleScale = int(tickMarkMoving + tickMarkGapDistance*((graphicNumbers-desiredPitch)/increments))
                
        
        if sensorInput[1] == True or sensorInput[3] == True or self.window.DEBUG == True:
            cv2.line(scaledMainImg, (x1-7, self.desiredPitchTriangleScale), (x1+7, self.desiredPitchTriangleScale), (0, 0, 255)) #Creating Plus Sign
            cv2.line(scaledMainImg, (x1, 7+self.desiredPitchTriangleScale), (x1, -7+self.desiredPitchTriangleScale), (0, 0, 255)) #Creating Plus Sign
                
    def drawRollGauge(self, scaledMainImg, numOfTicks, incrementRange, position, gaugeWidth, rgbValues, sensorInput): #(img, number of tick marks, increments of the scale, gauge width, sensor input)
        '''
        Draws the Roll gauge which changes according to AHRS data.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **numOfTicks** - Number of ticks chosen in settings slider.
        * **incrementRange** - How many degrees each tick represents.
        * **position** -  Boolean indicating whether to place the gauge on top or bottom, 1 being top.
        * **gaugeWidth** - How many pixels wide the gauge is.
        * **rgbValues** - The color values for the gauge.
        * ** sensorInput** - The median roll detected by the AHRS.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        if sensorInput[2] == None:
            desiredRoll = 0
        else:
            desiredRoll = sensorInput[2]
            
        if sensorInput[3] == True:
            desiredRoll = sensorInput[4] 
        
        roll = sensorInput[0]
        
        #Creating points for the line
        ellipseWidth = gaugeWidth #Originally 90
        ellipseHeight = 50
           
        if position == 0:#BOTTOM
            x1 = self.screenWidth/2 #Center of ellipse in the x direction
            y1 = self.screenHeight-75 #Center of ellipse in the y direction
            changingMiddleNumberCorrection = 20
            graphicCorrectionsX = -5, -20, -10
            graphicCorrectionsY = 11, 11, 11
        elif position == 1: #TOP
            x1 = self.screenWidth/2 #Center of ellipse in the x direction
            y1 = 75 #Center of ellipse in the y direction
            changingMiddleNumberCorrection = -20
            graphicCorrectionsX = -5, 0, -40
            graphicCorrectionsY = -2, -3, -3
        
        a = ellipseWidth/2
        b = ellipseHeight/2
        
        #MOVING GREEN TRIANGLE
        if incrementRange == 1:
            roll = (roll*90)/180.0
        else:
            if roll <= -90:
                roll = -90
            if roll >= 90:
                roll = 90
                
        if position == 0:
            ellipseXEquRoll = -((roll*ellipseWidth)/90.0)+x1
            ellipseYEquRoll = math.sqrt((ellipseHeight**2)*(1-((((roll*a)/90.0)**2)/(a**2))))+(y1-self.screenHeight+15)+self.screenHeight
            startAngle, endAngle = 0, 180
            correctingAngle = 0
        elif position == 1:
            ellipseXEquRoll = ((roll*ellipseWidth)/90.0)+x1
            ellipseYEquRoll = -math.sqrt((ellipseHeight**2)*(1-((((roll*a)/90.0)**2)/(a**2))))+(y1-self.screenHeight+15)+self.screenHeight
            startAngle, endAngle = 180, 360
            correctingAngle = 180
            
        xRoll = a*math.cos(math.radians(roll))
        yRoll = b*math.sin(math.radians(roll))
        angle = math.degrees(math.acos(-yRoll/(math.sqrt((xRoll**2)+(yRoll**2)))))-90
        x1Triangle = int(round(-10*math.cos(math.radians(angle))-10*math.sin(math.radians(angle))+ellipseXEquRoll))
        y1Triangle = int(round(10*math.cos(math.radians(angle))-10*math.sin(math.radians(angle))+(ellipseYEquRoll-15)))
        x2Triangle = int(round(10*math.cos(math.radians(angle))-10*math.sin(math.radians(angle))+(ellipseXEquRoll)))
        y2Triangle = int(round(10*math.cos(math.radians(angle))+10*math.sin(math.radians(angle))+(ellipseYEquRoll-15)))
        cv2.ellipse(scaledMainImg, (x1, y1), (ellipseWidth, ellipseHeight), 0, startAngle, endAngle, rgbValues) #(image, center, axes, angle, startAngle, endAngle, color)
        
        #Triangle
        cv2.line(scaledMainImg, (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), (x1Triangle, y1Triangle), rgbValues)
        cv2.line(scaledMainImg, (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), (x2Triangle, y2Triangle), rgbValues)
        cv2.line(scaledMainImg, (x1Triangle, y1Triangle), (x2Triangle, y2Triangle), rgbValues)
        #cv2.line(scaledMainImg, (x1, y1), (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), rgbValues)
        
        #MOVING RED TRIANGLE
        if sensorInput[1] == True or sensorInput[3] == True or self.window.DEBUG == True:
            if incrementRange == 1:
                desiredRoll = (desiredRoll*90)/180.0
            else:
                if desiredRoll <= -90:
                    desiredRoll = -90
                if desiredRoll >= 90:
                    desiredRoll = 90
                    
            if position == 0:
                ellipseXEquRoll = -((desiredRoll*ellipseWidth)/90.0)+x1
                ellipseYEquRoll = math.sqrt((ellipseHeight**2)*(1-((((desiredRoll*a)/90.0)**2)/(a**2))))+(y1-self.screenHeight+15)+self.screenHeight
                startAngle, endAngle = 0, 180
            elif position == 1:
                ellipseXEquRoll = ((desiredRoll*ellipseWidth)/90.0)+x1
                ellipseYEquRoll = -math.sqrt((ellipseHeight**2)*(1-((((desiredRoll*a)/90.0)**2)/(a**2))))+(y1-self.screenHeight+15)+self.screenHeight
                startAngle, endAngle = 180, 360
                
            xDesiredRoll = a*math.cos(math.radians(desiredRoll))
            yDesiredRoll = b*math.sin(math.radians(desiredRoll))
            desiredAngle = math.degrees(math.acos(-yDesiredRoll/(math.sqrt((xDesiredRoll**2)+(yDesiredRoll**2)))))-90
            x1RedTriangle = int(round(-10*math.cos(math.radians(desiredAngle))-10*math.sin(math.radians(desiredAngle))+ellipseXEquRoll))
            y1RedTriangle = int(round(10*math.cos(math.radians(desiredAngle))-10*math.sin(math.radians(desiredAngle))+(ellipseYEquRoll-15)))
            x2RedTriangle = int(round(10*math.cos(math.radians(desiredAngle))-10*math.sin(math.radians(desiredAngle))+(ellipseXEquRoll)))
            y2RedTriangle = int(round(10*math.cos(math.radians(desiredAngle))+10*math.sin(math.radians(desiredAngle))+(ellipseYEquRoll-15)))
            
            #Triangle
            cv2.line(scaledMainImg, (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), (x1RedTriangle, y1RedTriangle), (0, 0, 255))
            cv2.line(scaledMainImg, (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), (x2RedTriangle, y2RedTriangle), (0, 0, 255))
            cv2.line(scaledMainImg, (x1RedTriangle, y1RedTriangle), (x2RedTriangle, y2RedTriangle), (0, 0, 255))
            #cv2.line(scaledMainImg, (x1, y1), (int(round(ellipseXEquRoll)), int(round(ellipseYEquRoll-15))), (0, 0, 255))

        #Tick Marks
        tickMarkNum = numOfTicks-1
        for x in range(tickMarkNum+1):
            tickAngle = 90.0 - (180.0/tickMarkNum)*x #DONT WANT TO GO IN EVEN INTERVALS WITH THE ELLIPSE, INSTEAD, NEED TO GO WITH EVEN INTERVALS WITH CIRCLE AND TRANSCRIBE THAT ON ELLIPSE
            if position == 0:
                xTick = -ellipseWidth*math.sin(math.radians(tickAngle))
                yTick = ellipseHeight*math.cos(math.radians(tickAngle))
            elif position == 1:
                xTick = ellipseWidth*math.sin(math.radians(tickAngle))
                yTick = -ellipseHeight*math.cos(math.radians(tickAngle))
                
            angle = math.degrees(math.atan2(yTick,xTick))-90
            x1Tick = 10*math.sin(math.radians(angle))+x1+xTick
            y1Tick = -10*math.cos(math.radians(angle))+y1+yTick
            x2Tick = -10*math.sin(math.radians(angle))+x1+xTick
            y2Tick = 10*math.cos(math.radians(angle))+y1+yTick
            cv2.line(scaledMainImg, (int(round(x1Tick)), int(round(y1Tick))), (int(round(x2Tick)), int(round(y2Tick))), rgbValues)
            graphicNumbers = int(round(angle)) + correctingAngle
            
            if incrementRange == 1: # Means user picked 180
                
                cv2.putText(scaledMainImg, str(int(round(sensorInput[0]))), (x1-10, y1+changingMiddleNumberCorrection), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #writes the AHRS roll unrestricted by 90 deg
                if graphicNumbers == 0:
                    cv2.putText(scaledMainImg, str(graphicNumbers*2), (int(round(x2Tick+graphicCorrectionsX[0])), int(round(y2Tick+graphicCorrectionsY[0]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                elif graphicNumbers == 90: #Just 90, not 180, since I scale it to 90. 90 is to 180 as 0 is to 0.
                    cv2.putText(scaledMainImg, str(graphicNumbers*2), (int(round(x2Tick+graphicCorrectionsX[1])), int(round(y2Tick+graphicCorrectionsY[1]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                elif graphicNumbers == -90: #Just 90, not 180, since I scale it to 90. 90 is to 180 as 0 is to 0.
                    cv2.putText(scaledMainImg, str(graphicNumbers*2), (int(round(x2Tick+graphicCorrectionsX[2])), int(round(y2Tick+graphicCorrectionsY[2]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
            else:
                cv2.putText(scaledMainImg, str(int(round(roll))), (x1-10, y1+changingMiddleNumberCorrection), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the AHRS roll restricted by 90 deg
                if graphicNumbers == 0:
                    cv2.putText(scaledMainImg, str(graphicNumbers), (int(round(x2Tick+graphicCorrectionsX[0])), int(round(y2Tick+graphicCorrectionsY[0]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                elif graphicNumbers == 90:
                    cv2.putText(scaledMainImg, str(graphicNumbers), (int(round(x2Tick+graphicCorrectionsX[1])), int(round(y2Tick+graphicCorrectionsY[1]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                elif graphicNumbers == -90:
                    cv2.putText(scaledMainImg, str(graphicNumbers), (int(round(x2Tick+graphicCorrectionsX[2])), int(round(y2Tick+graphicCorrectionsY[2]))), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                
    def drawDepthGauge(self, scaledMainImg, numOfTicks, increments, position, gaugeLength, rgbValues, sensorInput):
        '''
        Draws the Depth gauge which changes according to pressure transducer data.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **numOfTicks** - Number of ticks chosen in settings slider.
        * **increments** - How many degrees each tick represents.
        * **position** -  Boolean indicating whether to place the gauge is right or left, 1 being right.
        * **gaugeLength** - How tall the gauge is.
        * **rgbValues** - The color values for the gauge.
        * ** sensorInput** - The median roll detected by the pressure transducers.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global counterDepth, stringAddDepth
        
        if sensorInput[1] == None:
            desiredDepth = 0
        else:
            desiredDepth = sensorInput[1]
            
        if sensorInput[2][0] == True: #If missions is setting a depth, display depth
            desiredDepth = sensorInput[2][1]
        
        lineLength = gaugeLength #Originally 261
        
        if position == 0:
            x1 = 19
            x2 = 19
            correctedTickMarkPosition = 15
            cv2.line(scaledMainImg, (x1-10, (self.screenHeight)/2), (x1-19, (self.screenHeight/2)+9), rgbValues)#Creating top line for arrow
            cv2.line(scaledMainImg, (x1-10, (self.screenHeight)/2), (x1-19, (self.screenHeight/2)-9), rgbValues)#Creating bottom line for arrow
            cv2.line(scaledMainImg, (x1-19, (self.screenHeight/2)+9), (x1-19, ((self.screenHeight)/2)-9), rgbValues)#Creating closing line for triangle
        elif position == 1:
            
            x1 = self.screenWidth-20
            x2 = self.screenWidth-20
            correctedTickMarkPosition = -40
            cv2.line(scaledMainImg, (x1+10, (self.screenHeight)/2), (x1+19, (self.screenHeight/2)+9), rgbValues)#Creating top line for arrow
            cv2.line(scaledMainImg, (x1+10, (self.screenHeight)/2), (x1+19, (self.screenHeight/2)-9), rgbValues)#Creating bottom line for arrow
            cv2.line(scaledMainImg, (x1+19, (self.screenHeight/2)+9), (x1+19, ((self.screenHeight)/2)-9), rgbValues)#Creating closing line for triangle
            
            
        y1 = self.screenHeight/2 - lineLength/2
        y2 = self.screenHeight/2 + lineLength/2
            
        tickMarkGapDistance = lineLength/numOfTicks #Distance between tick marks
        depth = sensorInput[0] #Actual Depth
        
        if self.setInitialTickPosition[2]:
            stringAddDepth = -(numOfTicks*increments)/2.0 #The amount of tick marks above the middle tick mark
            self.setInitialTickPosition[2] = False
            counterDepth = 0
            
        cv2.line(scaledMainImg, (x1, y1), (x2, y2), rgbValues) #Creating line
        
        for x in range(numOfTicks+1):
            tickMarkHeight = y1 + (lineLength*x)/numOfTicks #The INITIAL height of each tick mark
            tickMarkMoving = int(tickMarkHeight - ((depth-counterDepth)*tickMarkGapDistance)/increments) #The height of each tick mark after moving them based on sensor input

            if x == 0 and tickMarkMoving <= y1 - tickMarkGapDistance: #As the tick marks are moving up; once the tick mark's distance away from the top of the line is the difference between the tick mark gaps...
                counterDepth += increments*((y1 - tickMarkMoving)/tickMarkGapDistance) #Increment a counter that will move the ticks marks back down to their initial position and adjust the tick mark numbers. If the user doesnt enter a high enough increment, the tick marks will run behind. To catch them up, we find out how many tickMarkGaps ahead it is and multiply that to increment

            elif x == numOfTicks and tickMarkMoving >= y2 + tickMarkGapDistance: #As the tick marks are moving down; once the tick mark's distance away from the bottom of the line is the difference between the tick mark gaps...
                counterDepth -= increments*((y2 + tickMarkMoving)/tickMarkGapDistance) #Decrement a counter that will move the ticks marks back up to their initial position and adjust the tick mark numbers
                    
            elif tickMarkMoving >= y1 and tickMarkMoving <= y2: #As long as the tick marks don't go past the line upper or lower bounds of the line...
                graphicNumbers = round(stringAddDepth+counterDepth+(x*increments), 5)
                
                cv2.line(scaledMainImg, (x1-10, tickMarkMoving), (x1+10, tickMarkMoving), rgbValues) #Draw the tick mark
                if graphicNumbers - int(graphicNumbers) == 0: #Get rid of decimals when not using them
                    graphicNumbers = int(graphicNumbers)
                cv2.putText(scaledMainImg, str(graphicNumbers), (x1+correctedTickMarkPosition, tickMarkMoving+5), cv2.FONT_HERSHEY_PLAIN, 0.9, rgbValues) #Write the number
                
                #MOVING RED TRIANGLE
                if desiredDepth > (graphicNumbers-increments) and desiredDepth <= graphicNumbers:
                    self.desiredDepthTriangleScale = int(tickMarkMoving - tickMarkGapDistance*((graphicNumbers-desiredDepth)/increments))
                
        
        if position == 0:    
            cv2.line(scaledMainImg, (x1-10, self.desiredDepthTriangleScale), (x1-19, 9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating top line for arrow
            cv2.line(scaledMainImg, (x1-10, self.desiredDepthTriangleScale), (x1-19, -9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating bottom line for arrow
            cv2.line(scaledMainImg, (x1-19, 9+self.desiredDepthTriangleScale), (x1-19, -9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating closing line for triangle
                    
        elif position == 1:
            cv2.line(scaledMainImg, (x1+10, self.desiredDepthTriangleScale), (x1+19, 9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating top line for arrow
            cv2.line(scaledMainImg, (x1+10, self.desiredDepthTriangleScale), (x1+19, -9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating bottom line for arrow
            cv2.line(scaledMainImg, (x1+19, 9+self.desiredDepthTriangleScale), (x1+19, -9+self.desiredDepthTriangleScale), (0, 0, 255))#Creating closing line for triangle

    def drawAttitude(self, scaledMainImg, length, displayPosVel, position, letterSize, letterScale, rgbValues, orientationData, orientationMissionData, positionData, velocityData, desiredPosition):
        '''
        Draws a 3D representation of the Sub's orientation using XYZ coordinates, with positive Z being the sub's front.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **length** - How long each line is for the attitude gauge.
        * **displayPosVel** - Boolean indicating whether or not to display the Sub's position and velocity.
        * **position** -  Integer from 0-3 for position, with 0 being the bottom left corner and going counter-clockwise up for each number.
        * **letterSize** - The font size for the X, Y, and Z indicators.
        * **letterScale** - The scale for how much the letters shrink to indicate depth for the 3D representation.
        * **rgbValues** - The color values for the gauge.
        * ** orientationData** - Heading, Pitch, and Roll data from the AHRS.
        * **orientationMissionData** - Desired orientation for the current mission.
        * ** positionData** - Coordinate data from the DVL.
        * **velocityData** - Velocity data from the DVL.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        T = advM.matrixMultiply(advM.Rot(e2, orientationData[0][0]), advM.Rot(e1, orientationData[0][1]), advM.Rot(e3, orientationData[0][2]))
        xxAngle = math.degrees(math.acos(T[0, 0]))
        yyAngle = math.degrees(math.acos(T[1, 1]))
        zzAngle = math.degrees(math.acos(T[2, 2]))
        
        if self.window.printOptionCheckboxValues[6].get() == 1:
            R, P = advM.extractData(T)
            numpy.set_printoptions(precision=4, suppress=True)
            print "Time:", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S:%f')
            print "Current Rotation Matrix:"
            print R
            print "x to x Angle:", round(xxAngle, 4)
            print "y to y Angle:", round(yyAngle, 4)
            print "z to z Angle:", round(zzAngle, 4), "\n"
        
        if displayPosVel:
            attitudeCorrection = 20
        else:
            attitudeCorrection = 0
            
        if position == 0:
            x = length+10
            y = self.screenHeight-(length+10+attitudeCorrection)
            
            xPosVelText = 0
            yPosVelText = self.screenHeight-15
            
            textCorrection = 0
            
        if position == 1:
            x = self.screenWidth-(length+30)
            y = self.screenHeight-(length+10+attitudeCorrection)
            
            xPosVelText = self.screenWidth-128
            yPosVelText = self.screenHeight-15
            
            posString = "Pos: {} N, {} E, {} Dwn (ft)".format(round(positionData[2], 2), round(positionData[0], 2), round(positionData[1], 2))
            desString = "Des: {} N, {} E, {} Dwn (ft)".format(round(desiredPosition[0], 2), round(desiredPosition[2], 2), round(desiredPosition[1], 2))
            velString = "Vel: {} N, {} E, {} Dwn (ft/s)".format(round(velocityData[1], 2), round(velocityData[0], 2), round(velocityData[2], 2))
            
            if len(posString) > len(velString):
                greaterString = len(posString)
                
            elif len(velString) >= len(posString):
                greaterString = len(velString)
            
            textCorrection = (greaterString-22)*6-5
            
        if position == 2:
            x = self.screenWidth-(length+30)
            y = length+20+attitudeCorrection
            
            xPosVelText = self.screenWidth-128
            yPosVelText = 15
            
            posString = "Pos: {} N, {} E, {} Dwn (ft)".format(round(positionData[2], 2), round(positionData[0], 2), round(positionData[1], 2))
            desString = "Des: {} N, {} E, {} Dwn (ft)".format(round(desiredPosition[0], 2), round(desiredPosition[1], 2), round(desiredPosition[2], 2))
            velString = "Vel: {} N, {} E, {} Dwn (ft/s)".format(round(velocityData[1], 2), round(velocityData[0], 2), round(velocityData[2], 2))
            
            if len(posString) > len(velString):
                greaterString = len(posString)
                
            elif len(velString) >= len(posString):
                greaterString = len(velString)
            
            textCorrection = (greaterString-22)*6-5
            
        if position == 3:
            x = length+10
            y = length+20+attitudeCorrection
            
            xPosVelText = 0
            yPosVelText = 15

            textCorrection = 0
           
        if displayPosVel:
            posString = "Pos: {} N, {} E, {} Dwn (ft)".format(round(positionData[2], 2), round(positionData[0], 2), round(positionData[1], 2))
            desString = "Des: {} N, {} E, {} Dwn (ft)".format(round(desiredPosition[0], 2), round(desiredPosition[1], 2), round(desiredPosition[2], 2))
            velString = "Vel: {} N, {} E, {} Dwn (ft/s)".format(round(velocityData[1], 2), round(velocityData[0], 2), round(velocityData[2], 2))
            
            if len(posString) > len(velString):
                greaterString = len(posString)
                
            elif len(velString) >= len(posString):
                greaterString = len(velString)

            cv2.putText(scaledMainImg, posString, (xPosVelText-textCorrection, yPosVelText-10), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
            cv2.putText(scaledMainImg, desString, (xPosVelText-textCorrection, yPosVelText+0), cv2.FONT_HERSHEY_PLAIN, 0.7, [0,0,255])
            cv2.putText(scaledMainImg, velString, (xPosVelText-textCorrection, yPosVelText+10), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
            
        x1 = int(x + T[0, 0]*length)
        x2 = int(y + T[1, 0]*length)
        y1 = int(x + T[0, 1]*length)
        y2 = int(y + T[1, 1]*length)
        z1 = int(x + T[0, 2]*length)
        z2 = int(y + T[1, 2]*length)
        
        x3 = int(x + -T[0, 0]*length)
        x4 = int(y + -T[1, 0]*length)
        y3 = int(x + -T[0, 1]*length)
        y4 = int(y + -T[1, 1]*length)
        z3 = int(x + -T[0, 2]*length)
        z4 = int(y + -T[1, 2]*length)
        
        tmp = ((-0.8 * length) + 40) / 45
        attitudeLetterSizeAdjust = (letterSize/10.0) # Multiply Factor, 1 for default
        
        cv2.line(scaledMainImg, (x, y), (x1, x2), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "X", (x1, x2), cv2.FONT_HERSHEY_PLAIN, (1.1 - T[2, 0]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        cv2.line(scaledMainImg, (x, y), (y1, y2), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "Y", (y1, y2), cv2.FONT_HERSHEY_PLAIN, (1.1 - T[2, 1]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        cv2.line(scaledMainImg, (x, y), (z1, z2), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "Z", (z1, z2), cv2.FONT_HERSHEY_PLAIN, (1.1 - T[2, 2]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        cv2.line(scaledMainImg, (x, y), (x3, x4), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "-X", (x3, x4), cv2.FONT_HERSHEY_PLAIN, (1.1 + T[2, 0]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        cv2.line(scaledMainImg, (x, y), (y3, y4), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "-Y", (y3, y4), cv2.FONT_HERSHEY_PLAIN, (1.1 + T[2, 1]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        cv2.line(scaledMainImg, (x, y), (z3, z4), rgbValues) #Draw the tick mark
        cv2.putText(scaledMainImg, "-Z", (z3, z4), cv2.FONT_HERSHEY_PLAIN, (1.1 + T[2, 2]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, rgbValues) #Write the number
        
        
        #RED ATTITUDE GAUGE
        if orientationData[1] == True or orientationMissionData[0] == True or self.window.DEBUG == True:
            if orientationData[2] == None or orientationData[3] == None or orientationData[4] == None:
                desiredYaw, desiredPitch, desiredRoll = 0, 0, 0
            else:
                desiredYaw, desiredPitch, desiredRoll = orientationData[2], orientationData[3], orientationData[4]
                
            if orientationMissionData[0] == True:
                desiredYaw, desiredPitch, desiredRoll = orientationMissionData[1], orientationMissionData[2], orientationMissionData[3]
                
            desiredT = advM.matrixMultiply(advM.Rot(e2, desiredYaw), advM.Rot(e1, desiredPitch), advM.Rot(e3, desiredRoll))
            
            x1 = int(x + desiredT[0, 0]*length)
            x2 = int(y + desiredT[1, 0]*length)
            y1 = int(x + desiredT[0, 1]*length)
            y2 = int(y + desiredT[1, 1]*length)
            z1 = int(x + desiredT[0, 2]*length)
            z2 = int(y + desiredT[1, 2]*length)
            
            x3 = int(x + -desiredT[0, 0]*length)
            x4 = int(y + -desiredT[1, 0]*length)
            y3 = int(x + -desiredT[0, 1]*length)
            y4 = int(y + -desiredT[1, 1]*length)
            z3 = int(x + -desiredT[0, 2]*length)
            z4 = int(y + -desiredT[1, 2]*length)
            
            tmp = ((-0.8 * length) + 40) / 45
            attitudeLetterSizeAdjust = (letterSize/10.0) # Multiply Factor, 1 for default
            
            cv2.line(scaledMainImg, (x, y), (x1, x2), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "X", (x1, x2), cv2.FONT_HERSHEY_PLAIN, (1.1 - desiredT[2, 0]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
            cv2.line(scaledMainImg, (x, y), (y1, y2), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "Y", (y1, y2), cv2.FONT_HERSHEY_PLAIN, (1.1 - desiredT[2, 1]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
            cv2.line(scaledMainImg, (x, y), (z1, z2), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "Z", (z1, z2), cv2.FONT_HERSHEY_PLAIN, (1.1 - desiredT[2, 2]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
            cv2.line(scaledMainImg, (x, y), (x3, x4), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "-X", (x3, x4), cv2.FONT_HERSHEY_PLAIN, (1.1 + desiredT[2, 0]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
            cv2.line(scaledMainImg, (x, y), (y3, y4), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "-Y", (y3, y4), cv2.FONT_HERSHEY_PLAIN, (1.1 + desiredT[2, 1]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
            cv2.line(scaledMainImg, (x, y), (z3, z4), (0, 0, 255)) #Draw the tick mark
            cv2.putText(scaledMainImg, "-Z", (z3, z4), cv2.FONT_HERSHEY_PLAIN, (1.1 + desiredT[2, 2]*(letterScale/10.0) - tmp)*attitudeLetterSizeAdjust, (0, 0, 255)) #Write the number
        
    def drawBatteryGauge(self, scaledMainImg, batteryLength, batteryCurrent, batteryPosition, rgbValues, batteryData):
        '''
        Draws the Battery gauge which changes according to battery data from the PMUD.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **batteryLength** - How wide the gauge is.
        * **batteryCurrent** - Boolean indicating whether or not to show Battery current.
        * **batteryPosition** -  Integer from 0-3 for position, with 0 being the bottom left corner and going counter-clockwise up for each number.
        * **rgbValues** - The color values for the gauge.
        * ** batteryData** - Voltage and current data for both batteries.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        if self.window.DEBUG == True:
            batery1VoltageCapacity, batery1CurrentCapacity, batery2VoltageCapacity, batery2CurrentCapacity = batteryData[0], batteryData[1], batteryData[2], batteryData[3]
        else:
            batery1VoltageCapacity, batery1CurrentCapacity, batery2VoltageCapacity, batery2CurrentCapacity = round(((batteryData[0]-21)/7.5)*100.0, 1), round((batteryData[1]/15.0)*100.0, 1), round(((batteryData[2]-21)/7.5)*100.0, 1), round((batteryData[3]/15.0)*100.0, 1)
        
        if batteryCurrent == 0:
            if batteryPosition == 0:
                x1 = 97
                y1 = self.screenHeight-30
                
            elif batteryPosition == 1:
                x1 = self.screenWidth-batteryLength-40
                y1 = self.screenHeight-30
                
            elif batteryPosition == 2:
                x1 = self.screenWidth-batteryLength-40
                y1 = 5
                
            elif batteryPosition == 3:
                x1 = 97
                y1 = 5
                
            x2 = x1
            y2 = y1+15
            
        elif batteryCurrent == 1:
            if batteryPosition == 0:
                x1 = 97
                y1 = self.screenHeight-50
                
            elif batteryPosition == 1:
                x1 = self.screenWidth-batteryLength-40
                y1 = self.screenHeight-50
                
            elif batteryPosition == 2:
                x1 = self.screenWidth-batteryLength-40
                y1 = 5
                
            elif batteryPosition == 3:
                x1 = 97
                y1 = 5
                
            x2 = x1
            y2 = y1+25
        
        #Battery 1
        cv2.putText(scaledMainImg, "Batt 1 ({} V)".format(batteryData[0]), (x1-97, y1+8), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
        cv2.rectangle(scaledMainImg, (x1, y1), (int(x1+batteryLength*(batery1VoltageCapacity/100.0)), y1+10), rgbValues, thickness=-1)
        cv2.rectangle(scaledMainImg, (x1, y1), (x1+batteryLength, y1+10), (255, 255, 255))
        cv2.putText(scaledMainImg, str(batery1VoltageCapacity)+"%", (x1+batteryLength+2, y1+9), cv2.FONT_HERSHEY_PLAIN, 0.8, rgbValues)
        #cv2.putText(scaledMainImg, "{} V".format(batteryData[0]), (x1+5, y1+9), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255))
        
        if batteryCurrent == 1:
            cv2.putText(scaledMainImg, "Batt 1 ({} A)".format(batteryData[1]), (x1-97, y1+20), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
            cv2.rectangle(scaledMainImg, (x1, y1+10), (int(x1+batteryLength*(batery1CurrentCapacity/100.0)), y1+20), rgbValues, thickness=-1)
            cv2.rectangle(scaledMainImg, (x1, y1+10), (x1+batteryLength, y1+20), (255, 255, 255))
            cv2.putText(scaledMainImg, str(batery1CurrentCapacity)+"%", (x1+batteryLength+2, y1+20), cv2.FONT_HERSHEY_PLAIN, 0.8, rgbValues)
        
        #Battery 2
        cv2.putText(scaledMainImg, "Batt 2 ({} V)".format(batteryData[2]), (x2-97, y2+8), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
        cv2.rectangle(scaledMainImg, (x2, y2), (int(x2+batteryLength*(batery2VoltageCapacity/100.0)), y2+10), rgbValues, thickness=-1)
        cv2.rectangle(scaledMainImg, (x2, y2), (x2+batteryLength, y2+10), (255, 255, 255))
        cv2.putText(scaledMainImg, str(batery2VoltageCapacity)+"%", (x2+batteryLength+2, y2+9), cv2.FONT_HERSHEY_PLAIN, 0.8, rgbValues)
        
        if batteryCurrent == 1:
            cv2.putText(scaledMainImg, "Batt 2 ({} A)".format(batteryData[3]), (x2-97, y2+20), cv2.FONT_HERSHEY_PLAIN, 0.7, rgbValues)
            cv2.rectangle(scaledMainImg, (x2, y2+10), (int(x2+batteryLength*(batery2CurrentCapacity/100.0)), y2+20), rgbValues, thickness=-1)
            cv2.rectangle(scaledMainImg, (x2, y2+10), (x2+batteryLength, y2+20), (255, 255, 255))
            cv2.putText(scaledMainImg, str(batery2CurrentCapacity)+"%", (x2+batteryLength+2, y2+20), cv2.FONT_HERSHEY_PLAIN, 0.8, rgbValues)
            
    def drawTemperature(self, scaledMainImg, size, position, rgbValues, temperatureData):
        '''
        Draws the Temperature gauge which changes according to data from the SIB.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **size** - Size chosen in settings slider.
        * **position** -  Integer from 0-3 for position, with 0 being the bottom left corner and going counter-clockwise up for each number.
        * **rgbValues** - The color values for the gauge.
        * ** temperatureData** - Internal and external temperature data from the SIB.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        scaledSize = 4.0*(size/50.0)
        
        #3 is to 138 as 1 is to 48
        if position == 0:
            x1 = 0
            y1 = int(self.screenHeight - scaledSize/0.07 - (5*scaledSize)/3 - 1)
            
        elif position == 1:
            x1 = int(self.screenWidth-(scaledSize/0.022))
            y1 = int(self.screenHeight - scaledSize/0.07 - (5*scaledSize)/3 - 1)
            
        elif position == 2:
            x1 = int(self.screenWidth-(scaledSize/0.022))
            y1 = int(scaledSize/0.07 - (5*scaledSize)/3 + 2)
            
        elif position == 3:
            x1 = 0
            y1 = int(scaledSize/0.07 - (5*scaledSize)/3 + 2)
        
        
        x2 = x1
        y2 = y1+int(scaledSize/0.076)
        
        #3 is to 40 as 1 is to 13
        cv2.putText(scaledMainImg, str(temperatureData)+"C", (x1, y1), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
        cv2.putText(scaledMainImg, str(round(temperatureData*(9.0/5.0)+32.0, 2))+"F", (x2, y2), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
        
    def drawMotorGauges(self, scaledMainImg, size, position, rgbValues, motorDutyCycleData, motorDirectionData):
        '''
        Draws the Motor Duty Cycle gauges which change according to data from the TCB.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **size** - Size chosen in settings slider.
        * **position** -  Integer from 0-3 for position, with 0 being the bottom left corner and going counter-clockwise up for each number.
        * **rgbValues** - The color values for the gauge.
        * **motorDutyCycleData** - The PWM signal given to the motors.
        * **motorDirectionData** - Booleans indicating motor direction for each motor.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        scaledSize = 2.0*(size/50.0)
        
        y = self.screenHeight/2 + 6
        
        if position == 0:
            x = 0
            cv2.putText(scaledMainImg, "M1: "+str(motorDutyCycleData[0])+"%", (x, int(y-(scaledSize/0.15)*7)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M2: "+str(motorDutyCycleData[1])+"%", (x, int(y-(scaledSize/0.15)*5)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M3: "+str(motorDutyCycleData[2])+"%", (x, int(y-(scaledSize/0.15)*3)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M4: "+str(motorDutyCycleData[3])+"%", (x, int(y-(scaledSize/0.15))), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M5: "+str(motorDutyCycleData[4])+"%", (x, int(y+(scaledSize/0.15))), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M6: "+str(motorDutyCycleData[5])+"%", (x, int(y+(scaledSize/0.15)*3)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M7: "+str(motorDutyCycleData[6])+"%", (x, int(y+(scaledSize/0.15)*5)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M8: "+str(motorDutyCycleData[7])+"%", (x, int(y+(scaledSize/0.15)*7)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
        
        elif position == 1:
            x = int(self.screenWidth-(scaledSize/0.0112)+10)
            cv2.putText(scaledMainImg, "M1: "+str(motorDutyCycleData[0])+"%", (x+(4-len(str(motorDutyCycleData[0])+"%"))*9, int(y-(scaledSize/0.15)*7)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M2: "+str(motorDutyCycleData[1])+"%", (x+(4-len(str(motorDutyCycleData[1])+"%"))*9, int(y-(scaledSize/0.15)*5)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M3: "+str(motorDutyCycleData[2])+"%", (x+(4-len(str(motorDutyCycleData[2])+"%"))*9, int(y-(scaledSize/0.15)*3)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M4: "+str(motorDutyCycleData[3])+"%", (x+(4-len(str(motorDutyCycleData[3])+"%"))*9, int(y-(scaledSize/0.15))), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M5: "+str(motorDutyCycleData[4])+"%", (x+(4-len(str(motorDutyCycleData[4])+"%"))*9, int(y+(scaledSize/0.15))), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M6: "+str(motorDutyCycleData[5])+"%", (x+(4-len(str(motorDutyCycleData[5])+"%"))*9, int(y+(scaledSize/0.15)*3)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M7: "+str(motorDutyCycleData[6])+"%", (x+(4-len(str(motorDutyCycleData[6])+"%"))*9, int(y+(scaledSize/0.15)*5)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
            cv2.putText(scaledMainImg, "M8: "+str(motorDutyCycleData[7])+"%", (x+(4-len(str(motorDutyCycleData[7])+"%"))*9, int(y+(scaledSize/0.15)*7)), cv2.FONT_HERSHEY_PLAIN, scaledSize, rgbValues)
        
        
    def drawStatus(self, scaledMainImg, position, rgbValues, name, onOffAlert, alertNum):
        '''
        Draws the Temperature gauge which changes according to data from the SIB.
        
        **Parameters**: \n
        * **scaledMainImg** - A scaled down image of the camera feed.
        * **position** -  Integer from 0-3 for position, with 0 being the bottom left corner and going counter-clockwise up for each number.
        * **rgbValues** - The color values for the gauge.
        * **name** - String containing the current mission name.
        * **onOffAlert** - Boolean which indicates whether the mission is peing performed or not.
        * **alertNum** - A double used for switching the indicator color in Debug mode.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        name = "Mission: "+name
        if position == 0:
            x1 = 39
            y1 = self.screenHeight-45
            xMissionName = 5
            yMissionName = self.screenHeight-10
        #3 is to 30, 4 is to 36, 1 is to 15, 2 is to 21
        elif position == 1:
            x1 = self.screenWidth-30
            y1 = self.screenHeight-45
            xMissionName = self.screenWidth-(15+len(name)*6)
            yMissionName = self.screenHeight-10

        elif position == 2:
            x1 = self.screenWidth-30
            y1 = 25
            xMissionName = self.screenWidth-(15+len(name)*6)
            yMissionName = 15
            
        elif position == 3:
            x1 = 39
            y1 = 25
            xMissionName = 5
            yMissionName = 15
            
        x2 = x1+20
        y2 = y1+20
        
        
        #12 to 90 as 6 to 55
        cv2.putText(scaledMainImg, name, (xMissionName, yMissionName), cv2.FONT_HERSHEY_SIMPLEX, 0.4, rgbValues)
        
        cv2.rectangle(scaledMainImg, (x1, y1), (x2, y2), rgbValues, thickness = 1)
        cv2.rectangle(scaledMainImg, (x1-30, y1), (x2-30, y2), rgbValues, thickness = 1)

        if onOffAlert == 0:
            cv2.rectangle(scaledMainImg, (x1-29, y1+1), (x2-31, y2-1), (0, 0, 255), thickness = -1)
        elif onOffAlert == 1:
            cv2.rectangle(scaledMainImg, (x1-29, y1+1), (x2-31, y2-1), (0, 255, 0), thickness = -1)
        
        if self.window.DEBUG == True:
            alertNum = alertNum/25.0
            
            if alertNum <= 1: #High Current
                cv2.rectangle(scaledMainImg, (x1+1, y1+1), (x2-1, y2-1), (0, 255, 255), thickness = -1) #Yellow
                cv2.rectangle(scaledMainImg, (x1-29, y1+1), (x2-31, y2-1), (0, 0, 255), thickness = -1)
                
            elif alertNum <= 2: #Over heating
                cv2.rectangle(scaledMainImg, (x1+1, y1+1), (x2-1, y2-1), (0, 150, 255), thickness = -1) #Orange
                cv2.rectangle(scaledMainImg, (x1-29, y1+1), (x2-31, y2-1), (0, 255, 0), thickness = -1)
                
            elif alertNum <= 3: #Low Battery
                cv2.rectangle(scaledMainImg, (x1+1, y1+1), (x2-1, y2-1), (0, 0, 255), thickness = -1) #Red
                cv2.rectangle(scaledMainImg, (x1-29, y1+1), (x2-31, y2-1), (0, 0, 255), thickness = -1)
        
            
        
            
        #cv2.rectangle(scaledMainImg, (x1+1, y1+1), (x2-1, y2-1), (0, 0, 255), thickness = -1)
        
        
        
        
        