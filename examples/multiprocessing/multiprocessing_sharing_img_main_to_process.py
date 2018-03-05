'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Oct 19, 2014

@author: Austin
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
    
def recieveImages(a):

    if imgSharing == colorImgSharing:
        while True:
            sharedImgArray = numpy.asarray(a[:])
            sharedImg = sharedImgArray.reshape(colorImgSize[1], colorImgSize[0], 3)/255.0 #reshape needs height THEN width since OpenCV is row dominant
            
            sharedScaledUpImg = cv2.resize(sharedImg, (colorImgSize[0]*colorScalingSize, colorImgSize[1]*colorScalingSize)) #Scaling up image by a factor of colorScalingSize
    
            cv2.imshow('DEST PROCESS', sharedScaledUpImg)
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()
        
    elif imgSharing == grayImgSharing:
        while True:
            sharedImgArray = numpy.asarray(a[:])
            sharedImg = sharedImgArray.reshape(grayImgSize[1], grayImgSize[0])/255.0 #reshape needs height THEN width since OpenCV is row dominant
            
            sharedScaledUpImg = cv2.resize(sharedImg, (grayImgSize[0]*grayScalingSize, grayImgSize[1]*grayScalingSize)) #Scaling up image by a factor of grayScalingSize
    
            cv2.imshow('DEST PROCESS', sharedScaledUpImg)
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
            
        cv2.destroyAllWindows()  

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    
    if imgSharing == colorImgSharing:
        arr = multiprocessing.Array('h', colorImgSize[0]*colorImgSize[1]*3) #width*height*3 for red, green, and blue
        p = multiprocessing.Process(target=recieveImages, args=(arr,))
        p.start()
        while True:
            flag, img = cap.read()
            scaledImg = cv2.resize(img, (colorImgSize[0], colorImgSize[1]))
            cv2.imshow('SRC MAIN', scaledImg)
            
            ImgArray = numpy.asarray(scaledImg).reshape(-1)
            
            arr[:] = ImgArray
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
    
        cv2.destroyAllWindows() 
    
    elif imgSharing == grayImgSharing:
        arr = multiprocessing.Array('h', grayImgSize[0]*grayImgSize[1]) #width*height for gray
        p = multiprocessing.Process(target=recieveImages, args=(arr,))
        p.start()
        
        while True:
            flag, img = cap.read()
            scaledImg = cv2.resize(img, (grayImgSize[0], grayImgSize[1]))
            grayScaledImg = cv2.cvtColor(scaledImg, cv2.COLOR_BGR2GRAY)
            cv2.imshow('SRC MAIN', grayScaledImg)
            
            ImgArray = numpy.asarray(grayScaledImg).reshape(-1)
            
            arr[:] = ImgArray
            
            ch = cv2.waitKey(1)    
            if ch == 27:
                break
    
        cv2.destroyAllWindows() 
