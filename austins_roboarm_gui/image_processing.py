'''
Copyright 2016, Austin Owens, All rights reserved.

.. module:: image_processing
   :synopsis: Updates image processing values.
   
:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 8, 2014
:Description: These functions update Image Processing values and images accordingly. 
'''
import cv2, numpy
import PIL.ImageTk, PIL.Image
import object_detection

class ImageProcessing():
    '''
    This class handles the aspects of the GUI which have to be updated.
    '''
    def __init__(self, window):
        '''
        Initializes the image dimensions. 
        
        **Parameters**: \n
        * **window** - Main TKinter program window.
        * **rawImgWidth** - Raw image width.
        * **rawImgHeight** - Raw image height.
        * **processedImgWidth** - Processed image width.
        * **processedImgHeight** - Processed image height.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #GUI Window Object
        self.window = window
        
        #Open Camera
        self.cap1 = cv2.VideoCapture(0)

        #Camshift
        self.camshiftFront = object_detection.Camshift()
        
        #Img Sizes
        self.imgWidth, self.imgHeight = window.imgWidth, window.imgHeight
        
    def updateImageProcessing(self):
        '''
        Main update process which calls methods for image processing, manual control, mission selector data, and keyboard input. Also handles DEBUG settings.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **missionSelectorData** - Mission parameters selected by user to be passed along to external process.
        * **imageProcValues** - Processed image height and width, along with the center coordinates of trackboxes to be passed to external process.\n
        '''
        
        #RAW IMG
        flagFront, frontImg = self.cap1.read()  
        scaledFrontImg = cv2.resize(frontImg, (self.imgWidth, self.imgHeight)) #resize image 
        
        #ROI SAMPLING  
        self.__roiSample__(scaledFrontImg, 3, self.window.frontImgLabel, self.window.filterScales) #(Tolerance, frontImgLabel, filterScales)            
        
        #IMAGE PROCESSING       
        imageProcValues = self.__imageProcessing__(scaledFrontImg, self.window.frontImgLabel, self.window.filterScales)
        
        return imageProcValues
        
    def __roiSample__(self, scaledFrontImg, tolerance, frontImgLabel, filterScales):
        '''
        Main update process which calls methods for image processing, manual control, mission selector data, and keyboard input 
        
        **Parameters**: \n
        * **tolerance** - How much tolerance is added or subtracted to the maximum/minimum HSV values.
        * **frontRawImgLabel** - The frame for the front raw video feed.
        * **bottomRawImgLabel** - The frame for the bottom raw video feed.
        * **filterScales** - The HSV values set on the Image Processing tab.
        
        **Returns**: \n
        * **No Return**\n
        '''
        global previousDropBoxImageProcessingValue
            
          
        if frontImgLabel.buttonReleased == True:
            x1, y1 = frontImgLabel.boxPoint1
            x2, y2 = frontImgLabel.boxPoint2
            tolerance = 3
            
            roiBGR = scaledFrontImg[y1:y2, x1:x2] #position (x, y) in matrix
            
            roiHSV = cv2.cvtColor(roiBGR, cv2.COLOR_BGR2HSV)
            
            minHSV = numpy.amin((numpy.amin(roiHSV, 1)), 0)
            maxHSV = numpy.amax((numpy.amax(roiHSV, 1)), 0)
            
            filterScales[0].set(minHSV[0] - tolerance)
            filterScales[1].set(minHSV[1] - tolerance) 
            filterScales[2].set(minHSV[2] - tolerance) 
            filterScales[4].set(maxHSV[0] + tolerance) 
            filterScales[5].set(maxHSV[1] + tolerance) 
            filterScales[6].set(maxHSV[2] + tolerance)

            frontImgLabel.mouseDragLocation = [0, 0] #Reset so box doesn't start in a weird location when I start to draw again
            frontImgLabel.buttonReleased = False
    
    def __imageProcessing__(self, scaledFrontImg, frontImgLabel, filterScales):
        '''
        Analyzes image based on desired HSV values and number of contours. 
        
        **Parameters**: \n
        * **frontImg** - The front image feed.
        * **bottomImg** - The bottom image feed.
        * **frontRawImgLabel** - Frame for the front raw image feed.
        * **bottomRawImgLabel** - Frame for the bottom raw image feed.
        * **frontProcessedImgLabel** - Frame for the processed front image.
        * **bottomProcessedImgLabel** - Frame for the processed bottom image.
        * **filterScales** - Scale values for the maximum/minimum HSV values or contour amount.

        **Returns**: \n
        * **trackBoxFrontImg** - The center coordinates of what's tracked on the front image.
        * **trackBoxBottomImg** - The center coordinates of what's tracked on the bottom image.
        * **[self.processedImgWidth, self.processedImgHeight]** - Width and height of the processed image.
        * **shape_centerFrontImg** - The center coordinates of the desired shape in the front image.
        * **shape_centerBottomImg** - The center coordinates of the desired shape in the bottom image.
        * **targetsFrontImg** - The center coordinates of the desired inner shape in the front image.
        * **targetsBottomImg** - The center coordinates of the desired inner shape in the front image.\n
        '''
        
        
        #PROCESSED IMG 1
        #hsv filter
        HSVFrontImg = cv2.cvtColor(scaledFrontImg, cv2.COLOR_BGR2HSV)
        lowerBound = (filterScales[0].get(), filterScales[1].get(), filterScales[2].get())
        upperBound = (filterScales[4].get(), filterScales[5].get(), filterScales[6].get())
        maskFrontImg = cv2.inRange(HSVFrontImg, lowerBound , upperBound) #Black and white image
        maskHSV3rdAxisFrontImg = maskFrontImg[:, :, numpy.newaxis] #Adding 3rd axis to make RGB compatible
        HSVBitwiseAndFrontImg = numpy.bitwise_and(scaledFrontImg, maskHSV3rdAxisFrontImg)
        
        #morphology filter
        morphologyFrontImg = cv2.morphologyEx(HSVBitwiseAndFrontImg, filterScales[3].get(), numpy.ones((5,5), numpy.uint8), iterations = filterScales[7].get())
        HSVFrontImg = cv2.cvtColor(morphologyFrontImg, cv2.COLOR_BGR2HSV)
        
        maskFrontImg = cv2.inRange(HSVFrontImg, lowerBound , upperBound) #Black and white image
        
        trackBoxFrontImg = self.camshiftFront.camshift(morphologyFrontImg, HSVFrontImg, maskFrontImg, self.imgWidth, self.imgHeight)
        if trackBoxFrontImg[0][0] != 0 and trackBoxFrontImg[0][1] != 0: #If their is something to track onto 
            cv2.putText(morphologyFrontImg, "(" + str(trackBoxFrontImg[0][0]) + ", " + str(trackBoxFrontImg[0][1]) + ")", (int(trackBoxFrontImg[0][0]), int(trackBoxFrontImg[0][1])), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            cv2.putText(morphologyFrontImg, "(" + str(round(trackBoxFrontImg[1][0], 1)) + ", " + str(round(trackBoxFrontImg[1][1], 1)) + ")", (int(trackBoxFrontImg[0][0]), int(trackBoxFrontImg[0][1]+15)), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            cv2.putText(morphologyFrontImg, "(" + str(round(trackBoxFrontImg[2], 1)) + ")", (int(trackBoxFrontImg[0][0]), int(trackBoxFrontImg[0][1]+30)), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))   
        
            
        bgrToRgbFrontImg = cv2.cvtColor(morphologyFrontImg, cv2.COLOR_BGR2RGB)
        
        if frontImgLabel.buttonPressed == True: #Draws the box on the img
            point1 = frontImgLabel.boxPoint1
            point2 = frontImgLabel.mouseDragLocation
            cv2.rectangle(bgrToRgbFrontImg, (point1[0], point1[1]), (point2[0], point2[1]), (255, 0, 0))
        
        #Converts OpenCV Image to TKinter
        tkHSVFrontImg = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(bgrToRgbFrontImg))
        
        #SHOW ALL IMGS
        frontImgLabel.config(image = tkHSVFrontImg)
        
        self.window.update()
        
        return trackBoxFrontImg, [self.imgWidth, self.imgHeight]
    