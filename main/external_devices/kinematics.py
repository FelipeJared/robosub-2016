'''
Copyright (c) 2016, Austin Owens, All rights reserved.

.. module:: kinematics
   :synopsis: Contains forward and inverse kinematic algorithms for serial linkage robots.

:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Nov 4, 2015
:Description: This module is automatically parse for all functions contained inside the ForwardKinematics and InverseKinematics classes. If functions are found, the names of the functions are placed in a drop down in the the GUI so the user can select which ones they want to use.
'''

from math import *
import cmath

class ForwardKinematics:
    """
    Steps for creating forward kinematics that can be read by the program:
    
    1. The function can be named anything, but the parameters must be self, *thetas
    2. The function must return [X, Y, Z, maximumReachXYZ, kinematicDimensions, homeConfiguration]
            Where:
                *thetas is an array of single numbers representing the joint angle in degrees
                maximumReachXYZ is a 3 element array that contains numbers representing the farthest reach with respect to base
                kinematicDimensions is an array of the dimensions needed for kinematic calculations. Image processing has access to kinematicDimensions so more values can be added to this array if more dimensions are needed for image processing calculations.
                homeConfiguration is an array containing the angles at which the joints take that the user considers a home configuration. Image processing has access to homeConfiguration
    Note: There can more than 1 function. This class is meant to be a library you can pull from if you want to try out different forward kinematics.
        a.Ex.
            def get4DOFBaseRef(self, *thetas):
                '''
                Forward kinematics for a 4 Degree of Freedom (DOF) serial linkage robot.
                '''
                
                #Kinematic Dimensions and Home Configurations
                a1, a2 = 145.47, 187.17
                homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
                
                #Thetas offset and converted to radians
                theta1 = (thetas[0]-homeConfiguration[0])*(pi/180.0) #The homeConfigurationOffset variable offsets theta by a given amount in order to change where the servo's 0 degree point starts. Note: homeConfigurationOffset may not be necessary for every application
                theta2 = (thetas[1]-homeConfiguration[1])*(pi/180.0)
                theta3 = (thetas[2]-homeConfiguration[2])*(pi/180.0)
                
                #Forward Kinematics
                X = round(a1*cos(theta1)*cos(theta2) + a2*cos(theta1)*cos(theta2-theta3), 2)
                Y = round(a1*sin(theta1)*cos(theta2) + a2*sin(theta1)*cos(theta2-theta3), 2)
                Z = round(a2*sin(theta3-theta2) - a1*sin(theta2), 2)
                
                #X, Y, Z positions and max reach for X, Y, Z
                positions = [X, Y, Z]  
                maximumReachXYZ = [a1+a2, a1+a2, a1+a2]
                
                #Loops through and replaces X, Y, and Z with their maximum reach if greater than or less than their maximum reach
                for index, position in enumerate(positions):
                    if position > maximumReachXYZ[index]:
                        positions[index] = maximumReachXYZ[index]
                    elif position < -maximumReachXYZ[index]:
                        positions[index] = -maximumReachXYZ[index]
        
                return [positions[0], positions[1], positions[2], maximumReachXYZ, [a1, a2], homeConfiguration]
    """
    
    def get4DOFBaseRef(self, *thetas):
        '''
        Forward kinematics for a 4 Degree of Freedom (DOF) serial linkage robot.
        '''
        
        #Kinematic Dimensions and Home Configuration
        a1, a2 = 145.47, 187.17
        homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
        
        #Thetas offset and converted to radians
        theta1 = (thetas[0]-homeConfiguration[0])*(pi/180.0) #The homeConfigurationOffset variable offsets theta by a given amount in order to change where the servo's 0 degree point starts. Note: homeConfigurationOffset may not be necessary for every application
        theta2 = (thetas[1]-homeConfiguration[1])*(pi/180.0)
        theta3 = (thetas[2]-homeConfiguration[2])*(pi/180.0)
        
        #Forward Kinematics
        X = round(a1*cos(theta1)*cos(theta2) + a2*cos(theta1)*cos(theta2-theta3), 2)
        Y = round(a1*sin(theta1)*cos(theta2) + a2*sin(theta1)*cos(theta2-theta3), 2)
        Z = round(a2*sin(theta3-theta2) - a1*sin(theta2), 2)
        
        #X, Y, Z positions and max reach for X, Y, Z
        positions = [X, Y, Z]  
        maximumReachXYZ = [a1+a2, a1+a2, a1+a2]
        
        #Loops through and replaces X, Y, and Z with their maximum reach if greater than or less than their maximum reach
        for index, position in enumerate(positions):
            if position > maximumReachXYZ[index]:
                positions[index] = maximumReachXYZ[index]
            elif position < -maximumReachXYZ[index]:
                positions[index] = -maximumReachXYZ[index]

        return [positions[0], positions[1], positions[2], maximumReachXYZ, [a1, a2], homeConfiguration]
    
    def get4DOFCamRef(self, *thetas):
        '''
        Forward kinematics for a 4 Degree of Freedom (DOF) serial linkage robot.
        '''
        
        #Kinematic Dimensions and Home Configuration
        a1, a2, b1, b2, b3 = 145.47, 187.17, 0.0, 231.56, 42.1  # in mm. For test stand: 145.47, 187.17, -10.0, 140.0, 94.55
        homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
        
        #Thetas offset and converted to radians
        theta1 = (thetas[0]-homeConfiguration[0])*(pi/180.0)
        theta2 = (thetas[1]-homeConfiguration[1])*(pi/180.0)
        theta3 = (thetas[2]-homeConfiguration[2])*(pi/180.0)
        
        #Forward Kinematics
        X = round(a1*cos(theta1)*cos(theta2) + a2*cos(theta1)*cos(theta2-theta3), 2)
        Y = round(a1*sin(theta1)*cos(theta2) + a2*sin(theta1)*cos(theta2-theta3), 2)
        Z = round(a2*sin(theta3-theta2) - a1*sin(theta2), 2)
        
        X, Y, Z = Y+b1, Z+b2, X-b3
        
        #X, Y, Z positions and max reach for X, Y, Z
        positions = [X, Y, Z]  
        maximumReachXYZ = [a1+a2+b1, a1+a2+b2, a1+a2-b3]
        
        #Loops through and replaces X, Y, and Z with their maximum reach if greater than or less than their maximum reach
        for index, position in enumerate(positions):
            if position > maximumReachXYZ[index]:
                positions[index] = maximumReachXYZ[index]
            elif position < -maximumReachXYZ[index]:
                positions[index] = -maximumReachXYZ[index]
        
        return [positions[0], positions[1], positions[2], maximumReachXYZ, [a1, a2, b1, b2, b3], homeConfiguration]
    
    def get7DOFBaseRef(self, *thetas):
        '''
        Forward kinematics for a 7 Degree of Freedom (DOF) serial linkage robot.
        '''
        
        #Kinematic Dimensions and Home Configuration
        a1, a2, b1, b2, b3 = 145.47, 187.17, 0.0, 231.56, 9.31  # in mm. For test stand: 145.47, 187.17, -10.0, 140.0, 94.55
        homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
        
        #Thetas offset and converted to radians
        theta1 = (thetas[0]-homeConfiguration[0])*(pi/180.0) #The homeConfiguration variable offsets theta by a given amount in order to change where the servo's 0 degree point starts. Note: homeConfigurationOffset may not be necessary for every application
        theta2 = (thetas[1]-homeConfiguration[1])*(pi/180.0)
        theta3 = (thetas[2]-homeConfiguration[2])*(pi/180.0)
        
        #Forward Kinematics
        X = round(a1*cos(theta1)*cos(theta2) + a2*cos(theta1)*cos(theta2-theta3), 2)
        Y = round(a1*sin(theta1)*cos(theta2) + a2*sin(theta1)*cos(theta2-theta3), 2)
        Z = round(a2*sin(theta3-theta2) - a1*sin(theta2), 2)
        
        #X, Y, Z positions and max reach for X, Y, Z
        positions = [X, Y, Z]  
        maximumReachXYZ = [a1+a2, a1+a2, a1+a2]
        
        #Loops through and replaces X, Y, and Z with their maximum reach if greater than or less than their maximum reach
        for index, position in enumerate(positions):
            if position > maximumReachXYZ[index]:
                positions[index] = maximumReachXYZ[index]
            elif position < -maximumReachXYZ[index]:
                positions[index] = -maximumReachXYZ[index]

        return [positions[0], positions[1], positions[2], maximumReachXYZ, [a1, a2], homeConfiguration]
        
class InverseKinematics:
    """
    Steps for creating inverse kinematics that can be read by the program:
    
    1. The function can be named anything, but the parameters must be self, X, Y, Z.
    2. The function must return [thetas, maximumReachXYZ, kinematicDimensions, homeConfiguration]
            Where:
                theta# is either a single number, or an array of numbers depending on if there are multiple thetas for theta#
                maximumReachXYZ is a 3 element array that contains numbers representing the farthest reach with respect to base
                kinematicDimensions is an array of the dimensions needed for kinematic calculations. Image processing has access to kinematicDimensions so more values can be added to this array if more dimensions are needed for image processing calculations.
                homeConfiguration is an array containing the angles at which the joints take that the user considers a home configuration. Image processing has access to homeConfiguration
    Note: There can more than 1 function. This class is meant to be a library you can pull from if you want to try out different inverse kinematics.
        a.Ex.
            def myInverseKinematicFunc(self, X, Y, Z):
                #Write inverse kinematic mathematics here
                
                thetas = [theta1, [theta2Sol1, theta2Sol2], [theta3Sol1, theta3Sol2]]
                maximumReachXYZ = [maxReachX, maxReachY, maxReachZ]
                return [thetas, maximumReachXYZ, kinematicDimensions, homeConfiguration]
    """
    
    def get4DOFBaseRef(self, X, Y, Z):
        """
        Inverse kinematics for a 4 Degree of Freedom (DOF) serial linkage robot.
        """
        
        #Kinematic Dimensions and Home Configuration
        a1, a2 = 145.47, 187.17
        homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
        
        #Inverse Kinematics
        ZBar = -Z
        theta1 = atan2(Y, X)
        
        if round(cos(theta1), 5) == 0:
            XBar = 0
        else:
            XBar = X/(cos(theta1))
        if round(sin(theta1), 5) == 0:
            YBar = 0;
        else:
            YBar = Y/(sin(theta1))
            
        B1 = (XBar**2 + ZBar**2 + a1**2 - a2**2)/(2*a1)
        sigma1 = cmath.sqrt(ZBar**2 + XBar**2 - B1**2).real
        B2 = (YBar**2 + ZBar**2 + a1**2 - a2**2)/(2*a1)
        sigma2 = cmath.sqrt(ZBar**2 + YBar**2 - B2**2).real
        
        #Two pairs of two solutions under certain conditions. Converting to degrees.
        theta2For0_180 = [round((atan2(ZBar, XBar) - atan2(sigma1, B1))*(180/pi), 5)+homeConfiguration[1], round((atan2(ZBar, XBar) + atan2(sigma1, B1))*(180/pi), 5)+homeConfiguration[1]] #The homeConfigurationOffset variable offsets theta by a given amount in order to change where the servo's 0 degree point starts. Note: homeConfigurationOffset may not be necessary for every application
        theta2For90_270 = [round((atan2(ZBar, YBar) - atan2(sigma2, B2))*(180/pi), 5)+homeConfiguration[1], round((atan2(ZBar, YBar) + atan2(sigma2, B2))*(180/pi), 5)+homeConfiguration[1]]
        
        B3 = (XBar**2 + ZBar**2 + a2**2 - a1**2)/(2*a2)
        sigma3 = cmath.sqrt(ZBar**2 + XBar**2 - B3**2).real
        B4 = (YBar**2 + ZBar**2 + a2**2 - a1**2)/(2*a2)
        sigma4 = cmath.sqrt(ZBar**2 + YBar**2 - B4**2).real
        
        #Two pairs of two solutions under certain conditions. Converting to degrees.
        theta3For0_180 = [round((-atan2(sigma3, B3) - atan2(sigma1, B1))*(180/pi), 5)+homeConfiguration[2], round((atan2(sigma3, B3) + atan2(sigma1, B1))*(180/pi), 5)+homeConfiguration[2]]
        theta3For90_270 = [round((-atan2(sigma4, B4) - atan2(sigma2, B2))*(180/pi), 5)+homeConfiguration[2], round((atan2(sigma4, B4) + atan2(sigma2, B2))*(180/pi), 5)+homeConfiguration[2]]
        
        #Converting to degrees
        theta1 = round(theta1*(180/pi), 5)
        
        #Conditions in which to use one pair of solutions over the other
        if theta1%360 == 0 or theta1%360 == 180:
            theta2 = theta2For0_180
            theta3 = theta3For0_180
        else:
            theta2 = theta2For90_270
            theta3 = theta3For90_270
            
        maximumReachXYZ = [a1+a2, a1+a2, a1+a2] #Max reach for X, Y, and Z
        
        thetas = [theta1+homeConfiguration[0], theta2, theta3]
        
        return [thetas, maximumReachXYZ, [a1, a2], homeConfiguration]

    
    def get4DOFCamRef(self, X, Y, Z):
        """
        Inverse kinematics for a 4 Degree of Freedom (DOF) serial linkage robot. Transforming position found by camera to be with respect to the base joint for the arm.
        """
        
        #Kinematic Dimensions and Home Configuration
        a1, a2, b1, b2, b3 = 145.47, 187.17, 0.0, 231.56, 42.1  # in mm. For test stand: 145.47, 187.17, -10.0, 140.0, 94.55
        homeConfiguration = [147.32, 245.63, 148.48, 149.06, 148.00]
        
        #get4DOFBaseRef function
        thetas = self.get4DOFBaseRef(Z+b3, X-b1, Y-b2)[0]
        
        #Max reach for X, Y, and Z
        maximumReachXYZ = [a1+a2+b1, a1+a2+b2, a1+a2-b3]
        
        return [thetas, maximumReachXYZ, [a1, a2, b1, b2, b3], homeConfiguration]
    