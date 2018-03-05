'''
Created on Apr 29, 2016

@author: Austin
'''

class Refresh(): #This is to stop the gui from flickering. All drop downs that freezes the gui will have to bind with this. See below for examples.
    '''
    This class is to stop the gui from flickering. All drop downs that freeze the gui will have to bind with this.
    '''
    def __init__(self, event, args):
        '''
        Updates the window to avoid flickering
        
        **Parameters**: \n
        * **event** - The widget action to which the method is binded. 
        * **args** - Main TKinter window 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        args[0].update()