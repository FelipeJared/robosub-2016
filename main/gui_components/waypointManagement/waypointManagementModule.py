'''
Created on May 1, 2016

@author: Magnus
'''
import Tkinter
import main.gui_components.data_graphing as graphing
from main.gui_components import previous_state_logging_system

class WaypointManagment:
    '''
    classdocs
    '''

    def __init__(self, window):
        '''
        Constructor
        '''
        
        self.window = window
        
        self.notebook = window.notebook
        
        tab8 = Tkinter.Frame(self.notebook, width = 1000, height = 200)
        tab8.place()
        self.notebook.add(tab8, text="Waypoint Managment")
        self.notebook.bind("<<NotebookTabChanged>>", self.onOpen)
        
        graph1 = graphing.GraphingModule(tab8, width = int(self.window.screenRes[0]/2.2), height = int(self.window.screenRes[0]/5), window = window)
        graph2 = graphing.GraphingModule(tab8, width = int(self.window.screenRes[0]/2.2), height = int(self.window.screenRes[0]/5), window = window)
        graph1.grid(column = 0, row = 0, rowspan=2,sticky=Tkinter.W+Tkinter.E)
        graph2.grid(column = 2, row = 0, rowspan=2,sticky=Tkinter.W+Tkinter.E)
        
        graph1.setView("North","East")
        graph2.setView("North","Depth")
        
        panel1 = Tkinter.Frame(tab8)
        panel2 = Tkinter.Frame(tab8)
        
        graph1x = Tkinter.StringVar()
        graph1y = Tkinter.StringVar()
        Tkinter.Button(panel1, text="Zoom Out", command = graph1.zoomOut).grid(column = 0, row = 0)
        Tkinter.Button(panel1, text="Zoom In", command = graph1.zoomIn).grid(column = 1, row = 0)
        Tkinter.OptionMenu(panel1, graph1x, "East","Depth","North", command = lambda event: graph1.setView(graph1x.get(),graph1y.get())).grid(column=1, row=1, sticky=Tkinter.W+Tkinter.E)
        Tkinter.OptionMenu(panel1, graph1y, "East","Depth","North", command = lambda event: graph1.setView(graph1x.get(), graph1y.get())).grid(column = 0, row = 1, sticky=Tkinter.W+Tkinter.E)
        graph1y.set("North")
        graph1x.set("East")
        
        graph2x = Tkinter.StringVar()
        graph2y = Tkinter.StringVar()
        Tkinter.Button(panel2, text="Zoom Out", command = graph2.zoomOut).grid(column = 0, row = 0)
        Tkinter.Button(panel2, text="Zoom In", command = graph2.zoomIn).grid(column = 1, row = 0)
        Tkinter.OptionMenu(panel2, graph2x, "East","Depth","North", command = lambda event: graph2.setView(graph2x.get(),graph2y.get())).grid(column = 1, row = 1, sticky=Tkinter.W+Tkinter.E)
        Tkinter.OptionMenu(panel2, graph2y, "East","Depth","North", command = lambda event: graph2.setView(graph2x.get(), graph2y.get())).grid(column = 0, row = 1, sticky=Tkinter.W+Tkinter.E)
        graph2y.set("North")
        graph2x.set("Depth")
        
        
        panel1.grid(column = 1, row = 0, sticky=Tkinter.W+Tkinter.E)
        panel2.grid(column = 1, row = 1, sticky=Tkinter.W+Tkinter.E)
        
#         graph1.addWaypoint(0, 0,25)
#         graph1.addWaypoint(25,5,40)
#         graph1.addWaypoint(50,10,30)
        
        self.graph1 = graph1
        self.graph2 = graph2
        
        self.graph1.drawWaypoints(False)
        self.graph2.drawWaypoints(False)
        
        tab8.onMouseRelease = self.onMouseRelease
        tab8.bind("<Button-1>", self.onMouseClick)
        
    def onMouseClick(self, event):
        self.graph1.drawWaypoints(True)
        self.graph2.drawWaypoints(True)
        
    def onMouseRelease(self, event):
        self.graph1.recalibrateWaypoints()
        self.graph2.recalibrateWaypoints()
        self.graph1.drawWaypoints(True)
        self.graph2.drawWaypoints(True)   
    
    def update(self):
        pass
    
    def onOpen(self, event):
        #if(self.notebook.index(self.notebook.select())==tab):
            self.graph1.recalibrateWaypoints()
            self.graph2.recalibrateWaypoints()
            self.graph1.drawWaypoints(False)
            self.graph2.drawWaypoints(False)
        
            