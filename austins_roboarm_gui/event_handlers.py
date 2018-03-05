'''
Copyright 2016, Austin Owens, All rights reserved.

.. module:: event_handlers
   :synopsis: Handles commands from keyboard, mouse, and widget events.
   
:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 7, 2014
:Description: Contains all the code specific to event handlers, such as pressing drawing a box on the raw image feed with the mouse to select a region of interest to track with image processing.The majority of these functions are only supposed to be called by the binding functions offered by the Tkinter library.
'''


buttonPressedToggle = False #Used for knowing when the user is pressing or releasing the mouse button
class EventHandlers:
    '''
    This class is where the event-based commands are written.
    '''
    def __init__(self, guiWidth, imgWidth):
        '''
        Initializes window and image widths as instance attributes.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.guiWidth = guiWidth
        self.imgWidth = imgWidth
        
    def initilizeFrontRawImgEvents(self, frontRawImgLabel):
        '''
        Initializes label as instance attribute.
        
        **Parameters**: \n
        * **frontRawImgLabel** - Label on front camera feed.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.frontRawImgLabel = frontRawImgLabel
        
    def frontRawImgDraw(self, event):
        '''
        Draws a square on front image of what you're capturing for color tracking.
        
        **Parameters**: \n
        * **event** - Moving the mouse while clicking on front raw image.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        halfOfGui = self.guiWidth/2
        whiteSpace = halfOfGui - self.imgWidth
        
        x = event.x#-int(whiteSpace/2)+154
        y = event.y
        
        if x < 0:
            x = 0  
              
        elif x > self.imgWidth:
            x = self.imgWidth
            
        self.frontRawImgLabel.mouseDragLocation[0] = x
        self.frontRawImgLabel.mouseDragLocation[1] = y

    def frontRawImgMouseEvent(self, event):
        '''
        Creates a box by dragging the mouse on the image to detect the colors enclosed within. 
        
        **Parameters**: \n
        * **event** - Clicking on the Front raw image feed
        
        **Returns**: \n
        * **No Return.**\n
        '''
        global buttonPressedToggle
        
        buttonPressedToggle = not buttonPressedToggle
        
        halfOfGui = self.guiWidth/2
        whiteSpace = halfOfGui - self.imgWidth
        
        x = event.x#-int(whiteSpace/2)+154
        y = event.y
        
        if x < 0:
            x = 0
        
        if y < 0:
            y = 0
              
        elif x > self.imgWidth:
            x = self.imgWidth
            
        self.frontRawImgLabel.mouseDragLocation = [x, y] #This is so this variable can initially start with these locations so the box wont start at [0, 0]
            
        if buttonPressedToggle == True:
            self.frontRawImgLabel.boxPoint1 = [x, y]
            self.frontRawImgLabel.buttonReleased = False
            self.frontRawImgLabel.buttonPressed = True
        
        elif buttonPressedToggle == False:
            self.frontRawImgLabel.boxPoint2 = [x, y]
            if self.frontRawImgLabel.boxPoint1[0] != self.frontRawImgLabel.boxPoint2[0] and self.frontRawImgLabel.boxPoint1[1] != self.frontRawImgLabel.boxPoint2[1]: #As long as boxPoint1 is not the same as boxPoint2
                if self.frontRawImgLabel.boxPoint2[0] > self.frontRawImgLabel.boxPoint1[0] and self.frontRawImgLabel.boxPoint2[1] > self.frontRawImgLabel.boxPoint1[1]: #As long as going from quadrant 2 to 4
                    self.frontRawImgLabel.boxPoint2 = [x, y]
                elif self.frontRawImgLabel.boxPoint2[0] < self.frontRawImgLabel.boxPoint1[0] and self.frontRawImgLabel.boxPoint2[1] < self.frontRawImgLabel.boxPoint1[1]: #As long as going from quadrant 4 to 2
                    self.frontRawImgLabel.boxPoint2 = self.frontRawImgLabel.boxPoint1 #Switch coordinates with boxPoint1
                    self.frontRawImgLabel.boxPoint1 = [x, y] #Switch x coordinates with boxPoint2
                elif self.frontRawImgLabel.boxPoint2[0] > self.frontRawImgLabel.boxPoint1[0] and self.frontRawImgLabel.boxPoint2[1] < self.frontRawImgLabel.boxPoint1[1]: #As long as going from quadrant 3 to 1
                    self.frontRawImgLabel.boxPoint2[1] = self.frontRawImgLabel.boxPoint1[1] #Switch y coordinates with boxPoint1
                    self.frontRawImgLabel.boxPoint1[1] = y #Switch y coordinates with boxPoint2
                elif self.frontRawImgLabel.boxPoint2[0] < self.frontRawImgLabel.boxPoint1[0] and self.frontRawImgLabel.boxPoint2[1] > self.frontRawImgLabel.boxPoint1[1]: #As long as going from quadrant 1 to 3
                    self.frontRawImgLabel.boxPoint2[0] = self.frontRawImgLabel.boxPoint1[0] #Switch x coordinates with boxPoint1
                    self.frontRawImgLabel.boxPoint1[0] = x  #Switch x coordinates with boxPoint2
                
                self.frontRawImgLabel.buttonReleased = True
                self.frontRawImgLabel.buttonPressed = False   
                     
            else: #If boxPoint1 and boxPoint2 are the same
                self.frontRawImgLabel.buttonReleased = False #Pretend it never happened
                self.frontRawImgLabel.buttonPressed = False #Pretend it never happened
                