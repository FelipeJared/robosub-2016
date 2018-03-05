'''
Copyright 2013, Austin Owens, All rights reserved.

.. module:: utilities
   :synopsis: Contains helpful classes used throughout the API.


:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Oct 21, 2013
:Description: This module is a combination of useful utilities used throughout the API, such as Timer and Advanced Math.

'''
import datetime
import time
import numpy
import math

            
class Timer:
    '''
    Provides useful timer information.
    '''
    def __init__(self):
        '''
        Initializing timer variables.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.netTime = 0
        self.netTimeIteration = 0
        self.initialTime = 0
        self.timeOverLap = False
        self.resetFlag = False
    
    def cpuClockTime(self):
        '''
        The CPU clock time in year-month-day hour:minute:second format.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **cpuClock** - The CPU clock time in year-month-day hour:minute:second format.\n
        '''
        cpuClock = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S:%f')
        return cpuClock
    
    def cpuClockTimeInSeconds(self):
        '''
        The CPU clock time in seconds.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **cpuClockInSeconds** - The CPU clock time in seconds. \n
        '''
        
        cpuClockInSeconds = time.time()
        return cpuClockInSeconds
    
    def netTimer(self, cpuClockInSeconds):
        '''
        Starts a timer on 0 that is based on the system clock.
        
        **Parameters**: \n
        * **cpuClockInSeconds** - The system clock in seconds
        
        **Returns**: \n
        * **self.netTime*ime = cpuClockInSeconds
            self.resetFlag = False
              
        self.netTime = cpu* - The time in seconds from when the *netTimer* function was called. \n
        '''
        
        if self.netTimeIteration == 0 or self.resetFlag == True:
            self.initialTime = cpuClockInSeconds
            self.resetFlag = False
              
        self.netTime = cpuClockInSeconds - self.initialTime
        
        if self.netTime < 0:
            self.netTime = self.netTime + 60
            self.timeOverLap = True
        
        self.netTimeIteration += 1
        
        return self.netTime
    
    def restartTimer(self):
        '''
        Restarts the *netTimer* function to 0.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.resetFlag = True

class AdvancedMath:
    def __init__(self):
        '''
        Initializes the unit vector arrays and angle variables as attributes. e1 is X, e2 is Y, and e3 is Z.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.e1 = numpy.array([[1], [0], [0]])#
        self.e2 = numpy.array([[0], [1], [0]])
        self.e3 = numpy.array([[0], [0], [1]])
        
        self.k = numpy.array([[0], [0], [0]])
        self.angle = 0
        
    def matrixMultiply(self, *matricies):
        '''
        Dot multiplies the given matrices.
        
        **Parameters**: \n
        * **matricies** - The matrices containing yaw, pitch, heading, and position data.
        
        **Returns**: \n
        * **numpy.round(T, 8)** - Matrix which contains the transformed XYZ coordinate data.\n
        '''
        if matricies[0].size == 16:
            T = numpy.eye(4, dtype=int) #Initialize transformation matrix to 1
        elif matricies[0].size == 9:
            T = numpy.eye(3, dtype=int) #Initialize transformation matrix to 1
        
        for x in range(len(matricies)):
            T = T.dot(matricies[x])
            
        return numpy.round(T, 8)
        
    def Trans(self, k, displacement): #k must be unit vector with 3 elements
        '''
        Turns the current or desired displacement value into a matrix for transformation.
        
        **Parameters**: \n
        * **k** - The unit vector indicating the displacemet's direction..
        * **displacement** - The current or desired translation in the given direction.
        
        **Returns**: \n
        * **numpy.round(T, 8)** - Matrix with the displacement data.\n
        '''
        T = numpy.array([[1, 0, 0, displacement*k[0, 0]],
                         [0, 1, 0, displacement*k[1, 0]],
                         [0, 0, 1, displacement*k[2, 0]],
                         [0, 0, 0, 1]])
        
        return numpy.round(T, 8)
    
    def Rot(self, k, angle): #k must be unit vector with 3 elements
        '''
        Turns the current or desired yaw value into a matrix for transformation.
        
        **Parameters**: \n
        * **k** - The unit vector for yaw.
        * **angle** - The current or desired angle.
        
        **Returns**: \n
        * **numpy.round(T, 8)** - Matrix indicating the angle.\n
        '''
        I = numpy.eye(3, dtype=int)
        R = I + numpy.dot(math.sin(math.radians(angle)), self.skew(k)) + (1-math.cos(math.radians(angle))) * numpy.dot(self.skew(k), self.skew(k))
        R = numpy.append(R, [[0, 0, 0]], axis = 0)
        R = numpy.append(R, [[0], [0], [0], [1]], axis = 1)
        
        return numpy.round(R, 8)
    
    def rot(self, k, angle):
        '''
        Turns the current or desired yaw value into a matrix for transformation.
        
        **Parameters**: \n
        * **k** - The unit vector for yaw.
        * **angle** - The current or desired angle.
        
        **Returns**: \n
        * **numpy.round(T, 8)** - Matrix indicating the angle.\n
        '''
        I = numpy.eye(3, dtype=int)
        R = I + numpy.dot(math.sin(math.radians(angle)), self.skew(k)) + (1-math.cos(math.radians(angle))) * numpy.dot(self.skew(k), self.skew(k))
        
        return numpy.round(R, 8)
    
    def aRot(self, R):
        '''
        Checks if the angle is 0 or 180 and modifies the matrix so it is not undefined.
        
        **Parameters**: \n
        * **k** - The unit vector for yaw.
        * **angle** - The current or desired angle.
        
        **Returns**: \n
        * **self.k** - Matrix for the unit vector.
        * **self.angle** - Matrix indicating the angle.\n
        '''
        if R.size == 16: #Determine if matrix is 4x4. If so, convert to 3x3.
            R, P = self.extractData(R)
            
        if numpy.all(numpy.equal(self.inv(R), numpy.transpose(R), dtype=bool)) == True: #Check if orthogonal
            
            self.angle = round(math.degrees(math.acos(0.5*(numpy.trace(R)-1))), 8)
            
            #Checking angle since rodrigues formula does not work when angles are at 0 or 180 degrees
            if self.angle == 0.0 or self.angle == 180.0:
                k1 = math.sqrt((R[0, 0] + 1)/2)
                k2 = math.sqrt((R[1, 1] + 1)/2)
                k3 = math.sqrt((R[2, 2] + 1)/2)
                
                #If a component of the unit vector is 0, I try another formula until the unit vector is not undefined
                if k1 != 0:
                    self.k = numpy.array([[k1], 
                                     [R[0, 1]/(2*k1)], 
                                     [R[0, 2]/(2*k1)]])
                    
                elif k2 != 0:
                    self.k = numpy.array([[R[1, 0]/(2*k2)], 
                                     [k2], 
                                     [R[1, 2]/(2*k2)]])
                   
                elif k3 != 0:
                    self.k = numpy.array([[R[2, 0]/(2*k3)], 
                                     [R[2, 1]/(2*k3)], 
                                     [k3]])
                    
            else:
                self.k = numpy.array([[(R[2, 1]-R[1, 2])/(2*math.sin(math.radians(self.angle)))], 
                                 [(R[0, 2]-R[2, 0])/(2*math.sin(math.radians(self.angle)))], 
                                 [(R[1, 0]-R[0, 1])/(2*math.sin(math.radians(self.angle)))]])
        
        return self.k, self.angle
    
    def skew(self, a): #must be 3 element vector
        '''
        Alters the matrix for use in rotation from NESW to XYZ and back.
        
        **Parameters**: \n
        * **a** - The input matrix.
        
        **Returns**: \n
        * **k** - Skewed matrix.\n
        '''
        k = numpy.array([[0, -a[2, 0], a[1, 0]], 
                         [a[2, 0], 0, -a[0, 0]], 
                         [-a[1, 0], a[0, 0], 0]])
        
        return k
    
    def extractData(self, T):
        '''
        Separates and takes out the yaw, pitch, roll, and position data from the transformed matrix..
        
        **Parameters**: \n
        * **T** - The transformed matrix.
        
        **Returns**: \n
        * **R** - Matrix with the unit vectors.
        * **P** - Matrix containing the yaw, pitch, and roll.\n
        '''
        R = numpy.array([[T[0, 0], T[0, 1], T[0, 2]],
                         [T[1, 0], T[1, 1], T[1, 2]],
                         [T[2, 0], T[2, 1], T[2, 2]]])
        
        P = numpy.array([[T[0, 3]], [T[1, 3]], [T[2, 3]]])
        
        return R, P
    
    def inv(self, a):
        '''
        Inverts the given matrix.
        
        **Parameters**: \n
        * **a** - Matrix which will be inverted.
        
        **Returns**: \n
        * **m** - The inverted matrix.\n
        '''
        m = numpy.linalg.inv(a)
        
        return m
