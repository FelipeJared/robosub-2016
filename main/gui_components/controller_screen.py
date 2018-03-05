'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: controller_screen
   :synopsis: Handles the screen in the Manual Control tab.
   
:Author: Felipe Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Jan 17, 2015
:Description: Sets up the joystick feedback screen in the Manual Control tab and updates it.
'''
import pygame, os
from pygame.locals import *

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

class TextPrint:
    '''
    This class prints the joystick and button values to the robosub movement GUI as signed floating-point integers
    Only used for local joystick feedback in a pygame window.
    '''
    
    def __init__(self):
        '''
        Font initialization for *TextPrint* class.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Returns.**\n
        '''
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def my_print(self, screen, textString):
        '''
        Determines position in x/y coordinated of printed output
        
        **Parameters**: \n
        * **screen** - Object for output screen
        * **textString** - Output string
        
        **Returns**: \n
        * **No Return.**\n
        '''
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        '''
        Sets cursor to initial position
        
        **Parameters**: \n
        * **No Input Parameters.** 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        '''
        Indents cursor position (same effect as Tab)
        
        **Parameters**: \n
        * **No Input Parameters.** 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.x += 10

    def unindent(self):
        '''
        Un-indents the cursor position (same effect as Shitf+Tab)
        
        **Parameters**: \n
        * **No Input Parameters.** 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.x -= 10

class controller():
    '''
    This class sets up a joystick for manual control.
    '''
    def __init__(self, embed, window):
        '''
        Sets up the screen in the Manual Control tab where the joystick info will be displayed.
        
        **Parameters**: \n
        * **embed** - A TKinter label where the screen will be placed
        * **window** - The main TKinter program window. 
        
        **Returns**: \n
        * **No Return**\n
        '''
        self.screen = None
        self.window = window
        self.embed = embed
        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        size = [800, 400]
        self.screen = pygame.display.set_mode(size)
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        
    def setup(self):
        '''
        Initializes the joystick, needed font, and updates the screen to reflect it.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return**\n
        '''
        pygame.init()
        self.embed.update()
        pygame.font.init()
        #Loop until the user clicks the close button.
        done = False
        
        pygame.display.set_caption("Sub Controller")
    
                
    def run(self):
        '''
        Displays the joystick info through text on the controller screen.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return**\n
        '''
        # Get ready to print
        #pygame.joystick.init()
        pygame.font.init()
        textPrint = TextPrint()
                    
                    
        # DRAWING STEP
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        self.screen.fill(WHITE)
        textPrint.reset()
        
        
        if self.window.manualModeEnabled == True:
            try:           
                if self.window.externalDevicesData[3][0] == False:
                    #If no Joystick is detected, a message is put on the Manual Control Screen
                    textPrint.my_print(self.screen, "No Joystick detected")
                    
                else:
                    # Get the name from the OS for the controller/joystick
                    name = self.window.externalDevicesData[3][0]
                    textPrint.my_print(self.screen, "Joystick name: {}".format(name))
                    
                    # Usually axis run in pairs, up/down for one, and left/right for the other
                    axes = self.window.externalDevicesData[3][1]
                    #print "Number of axes: {}".format(axes)
                    textPrint.my_print(self.screen, "Number of axes: {}".format(len(axes)) )
                    textPrint.indent()
                        
                    for i, axis in enumerate(axes):
                        #print "Axis {} value: {}".format(i, int(axis*100))
                        if i == 1 or i == 3:
                            textPrint.my_print(self.screen, "Axis {} value: {:>6.3f}".format(i, float((axis*-1))))
                        else:
                            textPrint.my_print(self.screen, "Axis {} value: {:>6.3f}".format(i, float((axis))))
                    textPrint.unindent()
                            
                    buttons = self.window.externalDevicesData[3][2]
                    textPrint.my_print(self.screen, "Number of buttons: {}".format(len(buttons)))
                    textPrint.indent()
                            
                    for i, button in enumerate(buttons):
                            if button == 1:
                                textPrint.my_print(self.screen, "Button {} value: True".format(i) )
                            else:
                                textPrint.my_print(self.screen, "Button {} value: False".format(i) )                
                    textPrint.unindent()
                        
                    hats = self.window.externalDevicesData[3][3]
                    textPrint.my_print(self.screen, "Number of hats: {}".format(len(hats)))
                        
                    for i, hat in enumerate(hats):
                            hat = i
                            #print "Hat {} value: {}".format(i, str(hat))
                            textPrint.my_print(self.screen, "Hat {} value: {}".format(i, str(hat)))
                    textPrint.unindent()
            except:
                #Debug mode activated
                textPrint.my_print(self.screen, "Debug mode")
                
            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
                    
        # Go ahead and update the screen with what we've drawn.
        pygame.display.update()
        #self.clock.tick(30)
        
    def stop(self):
        '''
        Stops the program handling the controller screen.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return**\n
        '''
        pygame.init()
        pygame.quit()
