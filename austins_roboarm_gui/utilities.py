'''
Copyright 2016, Austin Owens, All rights reserved.

.. module:: utilities
   :synopsis: Contains helpful classes used throughout the API.


:Author: Austin Owens <austin.timothy.owens@gmail.com>
:Date: Created on Oct 21, 2013
:Description: This module is a combination of useful utilities used throughout the API, such as Timer.

'''
import datetime
import time

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
         
        