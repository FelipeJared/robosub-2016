'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Oct 18, 2014

@author: Austin Owens
'''

import multiprocessing
import cv2
import numpy

colorImgSharing = 0; grayImgSharing = 1; #color codes

grayScalingSize = 2 #2:1 scaling
colorScalingSize = 3 #3:1 scaling

imgSharing = colorImgSharing #uncomment this line to share colored images from one process to another
#imgSharing = grayImgSharing #uncomment this line to share gray images from one process to another

grayImgSize = [640/grayScalingSize, 480/grayScalingSize]  #width, height
colorImgSize = [640/colorScalingSize, 480/colorScalingSize] #width, height
    
def grabImages(a):
    
    cap = cv2.VideoCapture(0)
    
    if imgSharing == colorImgSharing:
        while True:
            flag, img = cap.read()
            scaledImg = cv2.resize(img, (colorImgSize[0], colorImgSize[1]))
            cv2.imshow('SRC PROCESS', scaledImg)
            
            ImgArray = numpy.asarray(scaledImg).reshape(-1)
            
            a[:] = ImgArray
    
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()
        
    elif imgSharing == grayImgSharing:
        while True:
            flag, img = cap.read()
            scaledImg = cv2.resize(img, (grayImgSize[0], grayImgSize[1]))
            scaledGrayImg = cv2.cvtColor(scaledImg, cv2.COLOR_BGR2GRAY)
            cv2.imshow('SRC PROCESS', scaledGrayImg)
            
            grayImgArray = numpy.asarray(scaledGrayImg).reshape(-1) #Turns the scaled gray image from a matrix into an array
            
            a[:] = grayImgArray
    
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()  

if __name__ == '__main__':

    if imgSharing == colorImgSharing:
        arr = multiprocessing.Array('h', colorImgSize[0]*colorImgSize[1]*3) #width*height*3 for red, green, and blue

        p = multiprocessing.Process(target=grabImages, args=(arr,))
        p.start()
        
        while True:
            sharedImgArray = numpy.asarray(arr[:])
            sharedImg = sharedImgArray.reshape(colorImgSize[1], colorImgSize[0], 3)/255.0 #reshape needs height THEN width since OpenCV is row dominant
            
            sharedScaledUpImg = cv2.resize(sharedImg, (colorImgSize[0]*colorScalingSize, colorImgSize[1]*colorScalingSize)) #Scaling up image by a factor of colorScalingSize
    
            cv2.imshow('DEST MAIN', sharedScaledUpImg)
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()
    
    elif imgSharing == grayImgSharing:
        arr = multiprocessing.Array('h', grayImgSize[0]*grayImgSize[1]) #width*height for gray

        p = multiprocessing.Process(target=grabImages, args=(arr,))
        p.start()
        
        while True:
            sharedImgArray = numpy.asarray(arr[:])
            sharedImg = sharedImgArray.reshape(grayImgSize[1], grayImgSize[0])/255.0 #reshape needs height THEN width since OpenCV is row dominant
            
            sharedScaledUpImg = cv2.resize(sharedImg, (grayImgSize[0]*grayScalingSize, grayImgSize[1]*grayScalingSize)) #Scaling up image by a factor of grayScalingSize
    
            cv2.imshow('DEST MAIN', sharedScaledUpImg)
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()
        
