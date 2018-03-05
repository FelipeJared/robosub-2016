'''
Created on Oct 2, 2014

@author: Austin
'''

import cv2
import fnmatch, os
import time


#User modifies these variables
waitTimeBetweenEachImage = 0.1 #Starting time
fileName = 'Front'
#fileName = 'Bottom'


files = fnmatch.filter(os.listdir('{}/'.format(fileName)), '*.png')
smallestImageNumber = 999999999
largestImageNumber = 0
for x in range(len(files)):
    number = int(filter(str.isdigit, files[x]))
    if number < smallestImageNumber:
        smallestImageNumber = number
    if number > largestImageNumber:
        largestImageNumber = number

if largestImageNumber == 0:
    flag = 1 #Shutdown, no images to read  
else:
    flag = 0

count = smallestImageNumber
direction = 1 #Forward
initialTime = time.time()

pauseToggle = False

def readImageFromFile():
    global count
    if count >= smallestImageNumber and count <= largestImageNumber:
        rawImg = cv2.imread('{}/Image{}.png'.format(fileName, count)) #Read in image from file in a .png format
        cv2.imshow('rawImg', rawImg) #Show img
    elif count < smallestImageNumber:
        count = smallestImageNumber
    
    elif count > largestImageNumber:
        count = largestImageNumber
    
    else:
        print "ERROR, SHUTTING DOWN"
        return 1
    
    return 0
    

if __name__ == "__main__":
    while True:
        
        currentTime = time.time() - initialTime
        #print currentTime
        
        if currentTime >= waitTimeBetweenEachImage and pauseToggle == False:
            flag = readImageFromFile()
            count+=direction
            initialTime = time.time()
        
        ch = cv2.waitKey(1) #Listen for keyboard cmds
        
        if ch == 32: #Spacebar
            pauseToggle = not pauseToggle
            
        elif ch == ord('d'): 
            direction = -direction
            
             
        elif ch == 2424832: #Left arrow key
            if waitTimeBetweenEachImage >= 0.1:
                waitTimeBetweenEachImage += 0.1
            if waitTimeBetweenEachImage < 0.1:
                waitTimeBetweenEachImage += 0.01
        elif ch == 2555904: #Right arrow key
            if waitTimeBetweenEachImage > 0.1:
                waitTimeBetweenEachImage -= 0.1
            elif waitTimeBetweenEachImage <= 0.1:
                waitTimeBetweenEachImage -= 0.01
        
        if waitTimeBetweenEachImage <= 0.01:
            waitTimeBetweenEachImage = 0.01
            
        print "Action keys: Spacebar, Left/Right Arrow Keys, 'd' Key. FPS: ", 1.0/waitTimeBetweenEachImage
            
        if ch == 27 or flag == 1: #If the esc button is pushed or done reading pictures
            break #break out of while loop
    
    cv2.destroyAllWindows() #Destroy all windows