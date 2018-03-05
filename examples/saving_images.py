'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Oct 2, 2014

@author: Austin
'''

import cv2
import fnmatch, os, shutil
import time

cap1 = cv2.VideoCapture(0) #Find imaging devices

count = 0
flag = 0

def writeImageToFile():
    if count == 0:
        if os.path.exists('Pictures'):
            shutil.rmtree('Pictures')
            os.mkdir('Pictures')
        else:
            os.mkdir('Pictures')
        
    ret1, rawImg = cap1.read() #Read from imaging device
    
    cv2.imshow('rawImg', rawImg) #Show img

    cv2.imwrite('Pictures/MyImage{}.png'.format(count), rawImg) #Write image to file in a .png format

def readImageFromFile():
    if count < len(fnmatch.filter(os.listdir('Pictures/'), '*.png')):
        rawImg = cv2.imread('Pictures/MyImage{}.png'.format(count)) #Read in image from file in a .png format
        cv2.imshow('rawImg', rawImg) #Show img
    
    else:
        return 1
    
    return 0
    

if __name__ == "__main__":
    while True:
        #writeImageToFile() #Uncomment this line to write images to a file
        flag = readImageFromFile() #Uncomment this line to read images from that file
        
        count+=1
        
        ch = cv2.waitKey(1) #Listen for keyboard cmds
        
        if ch == 27 or flag == 1: #If the esc button is pushed or done reading pictures
            break #break out of while loop
    
    cv2.destroyAllWindows() #Destroy all windows