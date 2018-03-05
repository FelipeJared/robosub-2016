'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: previous_state_logging_system
   :synopsis: Creates an object for logging or reading saved parameters.
   
:Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Feb 27, 2015
:Description: Sets up Log class to create instances for reading and writing parameters from a text file.
'''

import imp, os
from random import randint

class Log():
    '''
    This class saves and reads in parameter values from a text file. If the text file is blank upon reading in values, 
    this class will create those values and fill them in with ones.
    '''
    def __init__(self, fileName):
        self.fileName = fileName 
        '''
        Sets the filename
        **Parameters**: \n
        * **fileName** - The location name of the file to read the saved parameters from.
        
        **Returns**: \n
        * **No Return.**\n
        '''
    def __passParameter__(self, line, key, orig_val , **kwargs):
        '''
        Checks if a new value exists for the each parameter. If a new value exists, the old one is overwritten
        If the parameter does not have a new value, the old one is kept
        **Parameters**: \n
        * **line** - single line from the text file
        * **key** - parameter name in current line
        * **orig_val** - parameter value in current line
        * **kwargs** - new parameters to be input
        
        **Returns**: \n
        * **param** - writes new/old parameter
        '''
        Present = False
        for name, val in (kwargs.items()):
            if name == key:
                param = '%s=%s\n' % (key, val)
                Present = True
        if Present == False:                    
            param = '%s=%s\n' % (key, orig_val)
        return param
    
    def __appendNewParameter__(self, name, val, param_name, values):
        '''
        Checks if the parameter is missing from the text file. If missing, the new parameter is written in 
        **Parameters**: \n
        * **name** - parameter being searched
        * **val** - value of the parameter
        * **param_name** - parameter name in string format
        * **values** - lines from the text file
        
        **Returns**: \n
        * **missing_param** - writes only missing parameter
        '''
        Present = False
        for line in values:
            if line.strip() != '':
                key, value = line.split("=")
                if param_name == key:
                    Present = True
        if Present == False:
            missing_param = '%s=%s\n' % (name, val)
            return missing_param
        else:
            return ''
    
    def __searchParameters__(self, line, key, *args):
        '''
        Searches the log for the parameter and returns a string with its name and value if found.
        
        **Parameters**: \n
        * **line** - line being currently searched
        * **key** - name of the parameter in the line
        * **args** - the parameters being searched for
        
        **Returns**: \n
        * **foundParameters** - string containing the parameter and its value
        '''
        foundParameters = ''
        for arg in args:
            if arg == key:
                foundParameters += line
        return foundParameters
    
    def __missingParameters__(self, values, arg):
        '''
        Checks if any parameter is missing. If a parameter is missing, a string setting its value to 0 is returned
        
        **Parameters**: \n
        * **values** - lines from the log
        * **arg** - parameter being searched
        
        **Returns**: \n
        * **new** - string setting the parameter's value to 0
        '''  
        Present = False
        for line in values:
            if line.strip() != '':
                key, value = line.split("=")
                if arg == key:
                    Present = True
        if Present == False:
            new = '%s=0\n' % (arg)
            return new
        else:
            return ''
        
    def writeParameters(self, **kwargs):#writes the last values recorded for the parameters in a text file
        '''
        Writes the values for specified parameters specified in kwargs in a text file 
        **Parameters**: \n
        * ***kwargs** - Parameters with their values, written as parameter=value; to request more than one, separate the component ID's by commas.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        initial_params = ''
        try:
            f = open(self.fileName, 'r')
        except:
            try:
                with open(self.fileName, 'w') as f:
                    f.write('')
                f = open(self.fileName, 'r')
            except:
                return
        p = 1     
        if (p == 1):#if there is something in the file, write to it
            f.seek(0)#puts pointer at beginning of file since f.read made pointer go to the end of the file
            values = f.readlines()
            
            for line in values:#writes new parameter values
                if line.strip() != '':
                    key, value = line.split("=")
                    param = value.strip()
                    initial_params += self.__passParameter__(line, key, param, **kwargs)
            for name, val in (kwargs.items()):#appends new parameters
                param_name = '%s' % (name)
                initial_params += self.__appendNewParameter__(name, val, param_name, values)
            f.close()
            g = open(self.fileName, 'w')
            g.write(initial_params)
            g.close()
                 
    def getParameters(self, *args):#read in parameters in text file and allow them to be called on
        '''
        Reads in the specified parameter values from the log by writing them to the second file, then loading that file. 
        You can call each one using object.parametername  
        **Parameters**: \n
        * **args** - Any number of parameters are read as strings, separated by a comma
        
        **Returns**: \n
        * **mymodule** - module containing values of the specified parameters
        '''
        
        try:
            f = open(self.fileName, 'r')
        except:
            with open(self.fileName, 'w') as f:
                f.write('')
            f = open(self.fileName, 'r')
        savedParameters = ''
        if (len(f.readlines()) > 0):#if there is something in the file, read the params and return them
            f.seek(0)
            values = f.readlines()
            
            for line in values:#writes new value for parameter
                if line.strip() != '':
                    key, value = line.split("=")
                    savedParameters += self.__searchParameters__(line, key, *args)
            for arg in args:#checks if parameter is missing, and set it to 0 if it is
                savedParameters += self.__missingParameters__(values, arg)
                
        else:#if file is blank, set all parameters to 0
            for arg in args:
                line = '%s=0\n' % (arg)
                savedParameters += line
                
        f.close()
        mymodule = imp.new_module('mymodule')
        exec(savedParameters, mymodule.__dict__)
        return mymodule
    
if __name__ == '__main__':
    
    logger = Log("Parameters.txt") #Making an instance of class 'Log'
    
    Flag = 2
    
    if Flag == 0:
        p = Log("Parameters.txt").getParameters('minHue', 'maxHue', 'minVal')    
        minHue = p.minHue#brings in the parameters to be used
        maxHue = p.maxHue
        minVal = p.minVal
        print 'minHue=' + str(minHue)
        print 'maxHue=' + str(maxHue)
        print 'minVal=' + str(minVal)
        #Flag = 1
        
    if Flag == 1:#write
        maxHue = randint(0,255)#simulating changing the values
        maxSat = randint(0,255)
        maxVal = randint(0,255)
        minSat = randint(0,255)
        minVal = randint(0,255)
        minHue = randint(0,255)
        first_params = Log("Parameters.txt", "SpecParameters.txt").writeParameters(minHue = minHue, maxHue = maxHue, minSat = minSat)
        second_params = Log("Parameters.txt", "SpecParameters.txt").writeParameters(maxSat = maxSat, minVal = minVal, maxVal = maxVal)
        print 'minHue=' + str(minHue)
        print 'maxHue=' + str(maxHue)
        print 'minSat=' + str(minSat)
        print 'maxSat=' + str(maxSat)
        print 'minVal=' + str(minVal)
        print 'maxVal=' + str(maxVal)
        
    if Flag == 2:
        for x in range(0, 2):
            maxHue = randint(0,255)#simulating changing the values
            maxSat = randint(0,255)
            maxVal = randint(0,255)
            minSat = randint(0,255)
            minVal = randint(0,255)
            minHue = randint(0,255)
            
            logger.getParameters('minHue', 'maxHue', 'minVal')
            hsvVals = logger.getParameters('minHue', 'maxHue', 'minVal')  
            print hsvVals.minHue, hsvVals.maxHue, hsvVals.minVal
            logger.writeParameters(minHue = minHue, maxHue = maxHue, minSat = minSat, m=1, n=3, z=4)
            
            newValues = logger.getParameters('newVal')
            print newValues.newVal
            logger.writeParameters(newVal = 20)
            
            moreValues = logger.getParameters('morVal')
            print moreValues.morVal