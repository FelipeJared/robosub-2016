
from Tkinter import Widget
import Tkinter
import math
import random
import re

from main.gui_components import previous_state_logging_system, \
    mission_selector_system


class GraphingModule(Widget):
    
    waypoints = []
    waypointRadius = 15
    haveSelected = None
    axis = {"x":0, "y":1,"z":2, "North":2, "East":0, "Depth":1}
    
    def __init__(self, master=None, width=0, height=0, window = 0,**kargs):
        
        Tkinter.Widget.__init__(self, master, "canvas", kargs)
        
        self.master = master
        self.window = window
        
        self.selectedView1 = 0
        self.selectedView2 = 1
        
        self.draggedX = None
        self.draggedY = None
        
        self.xInterval = 10
        self.yInterval = 10
        
        self.xMax = 10
        self.xMin = 0
        
        self.yMax = 10
        self.yMin = 0
        
        self.width = width
        self.height = height
        
        self.xList = []
        self.yList=[]
        
        self.xLabels = []
        self.yLabels = []
        
        self.canvas = Tkinter.Canvas(self, relief=Tkinter.SUNKEN, width=self.width, height=self.height,bd = 2)
        
        self.canvas.bind("<B1-Motion>", self.onMouseDrag)
        self.canvas.bind("<ButtonRelease-1>", self.onMouseRelease)
        self.canvas.bind("<Button-1>", self.onMouseLeftClick)
        self.master.bind("<Button-3>", self.onMouseRightClick)
        self.master.bind("<Delete>", self.onDelete)
        
        
        self.label = Tkinter.Label(self, text="Test")
        
        self.changeInterval(10, 10)
        
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
          
        
    def draw(self, xVals, yVals, xr, yr, *dragged):
        
        self.canvas.delete("all")
                
        self.xList = xVals
        self.yList = yVals
        
        self.changeInterval(xr, yr)
        
        if not dragged:
            for index, pos in enumerate(self.xList):
                if index == 0:
                    self.xMax = pos
                    self.xMin = pos
                    
                if pos>self.xMax:
                    self.xMax = pos
                if pos<self.xMin:
                    self.xMin = pos
                    
            for index, pos in enumerate(self.yList):
                if index == 0:
                    self.yMax = pos
                    self.yMin = pos
                    
                if pos>self.yMax:
                    self.yMax = pos
                if pos<self.yMin:
                    self.yMin = pos
                    
        
        
        for pos in range(0, len(self.xList)):
            if pos != 0:
                if self.xMax-self.xMin != 0 and self.yMax-self.yMin != 0:
                    self.canvas.create_line(self.canvas.winfo_width()*(float(self.xList[pos-1]-self.xMin)/(self.xMax-self.xMin)), self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(self.yList[pos-1]-self.yMin)/(self.yMax - self.yMin))),
                                            self.canvas.winfo_width()*(float(self.xList[pos]-self.xMin)/(self.xMax - self.xMin)),self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(self.yList[pos]-self.yMin)/(self.yMax - self.yMin))), 
                                            width=1.3, fill="blue")
    
    def drawWaypoints(self, *dragged):
        if(not len(dragged) > 0):
            dragged = [False]
        self.canvas.delete("all")
        self.changeInterval(3, 3)
        for index, value in enumerate(self.waypoints):
            if index==0 and not dragged[0]:
                self.xMax=value[0]
                self.xMin=value[0]
                self.yMax=value[1]
                self.yMin=value[1]
            if value != None and not dragged[0]:
                if value[self.selectedView1] > self.xMax:
                    self.xMax = value[self.selectedView1]
                elif value[self.selectedView1] < self.xMin:
                    self.xMin = value[self.selectedView1]
                if value[self.selectedView2] > self.yMax:
                    self.yMax = value[self.selectedView2]
                elif value[self.selectedView2] < self.yMin:
                    self.yMin = value[self.selectedView2]
        for index, value in enumerate(self.waypoints):
            color = "red"
            if index == 0:
                color = "blue"
            if value[3] == 1:
                color = "green"
            self.canvas.create_oval(self.canvas.winfo_width() * (float(value[self.selectedView1]-self.xMin)/(self.xMax-self.xMin))-self.waypointRadius, self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(value[self.selectedView2]-self.yMin)/(self.yMax - self.yMin)))+self.waypointRadius,
                                    self.canvas.winfo_width() * (float(value[self.selectedView1]-self.xMin)/(self.xMax-self.xMin))+self.waypointRadius, self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(value[self.selectedView2]-self.yMin)/(self.yMax - self.yMin)))-self.waypointRadius, 
                                    fill = color)
            if index != len(self.waypoints)-1:
                self.canvas.create_line(self.canvas.winfo_width()*(float(value[self.selectedView1]-self.xMin)/(self.xMax - self.xMin)),self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(value[self.selectedView2]-self.yMin)/(self.yMax - self.yMin))),
                                        self.canvas.winfo_width()*(float(self.waypoints[index+1][self.selectedView1]-self.xMin)/(self.xMax - self.xMin)),self.canvas.winfo_height()-(self.canvas.winfo_height()*(float(self.waypoints[index+1][self.selectedView2]-self.yMin)/(self.yMax - self.yMin))))
            
    
    def changeInterval(self, xr, yr):
        
        if xr>0:
            self.xInterval = xr
        else:
            return
        if yr>0:
            self.yInterval = yr
        else:
            return
        
        xDifference = self.width/self.xInterval
        for count in range(1,self.xInterval+1):
            self.canvas.create_line(xDifference*count, 0, xDifference*count, self.height, width=1)
            if count-1 >= len(self.xLabels):
                self.xLabels.append(Tkinter.Label(self, text=int(self.xMin+(count*(self.xMax-self.xMin)/self.xInterval))))
            self.xLabels[count-1].config(text=int(self.xMin+(count*(self.xMax-self.xMin)/self.xInterval)))
            
        yDifference = self.height/self.yInterval
        for count in range(1,self.yInterval+1):
            self.canvas.create_line(0, yDifference*count, self.width, yDifference*count, width=1)
            if count-1>=len(self.yLabels):
                self.yLabels.append(Tkinter.Label(self, text=int(self.yMin+(count*(self.yMax-self.yMin)/self.yInterval))))
            self.yLabels[count-1].config(text=int(self.yMin+(count*(self.yMax-self.yMin)/self.yInterval))) 
            
        for i,v in enumerate(self.xLabels):
            if i > self.xInterval:
                self.xLabels[i].config(text="")
        for i,v in enumerate(self.yLabels):
            if i > self.yInterval:
                self.yLabels[i].config(text="")        
        
        self.canvas.grid(row=0, column=1, columnspan = len(self.xLabels)+1, rowspan=len(self.yLabels)+1)
        
        
        for index,value in enumerate(self.xLabels):
            xAmt = ((index*xDifference)+xDifference)/float(self.canvas.winfo_width())
            if xAmt >= 1:
                xAmt = 0
            if xAmt >.97:
                xAmt = .95
            
            value.place(relx=xAmt, rely=.9)

        for index,value in enumerate(self.yLabels):
            yAmt = ((index*yDifference)+yDifference)/float(self.canvas.winfo_height())
            if yAmt == 1:
                yAmt = .97
            value.place(rely=(1 - yAmt), relx=.01)
            
    def addWaypoint(self, xPos, yPos, zPos, *name):
        if(len(name) >0):
            self.waypoints.append([xPos, yPos,zPos,0, name[0]])
        else:
            self.waypoints.append([xPos, yPos,zPos,0, None])
        self.drawWaypoints(True)
    
    def onMouseDrag(self, event):         
        if self.draggedX != None:
            xDif = self.draggedX - (float(event.x)/10)
            yDif = (float(event.y)/10) - self.draggedY
            
            self.draggedX = (float(event.x)/10)
            self.draggedY = (float(event.y)/10)
            
            if not self.haveSelected!=None:
                self.xMax += xDif
                self.xMin += xDif
                
                self.yMax += yDif
                self.yMin += yDif
            else:
                num = self.haveSelected
                xpos = (event.x*float(self.xMax - self.xMin))/float(self.canvas.winfo_width())+self.xMin
                ypos = ((self.canvas.winfo_height()-event.y)*float(self.yMax - self.yMin))/float(self.canvas.winfo_height())+self.yMin
                
                self.waypoints[num][self.selectedView1] = xpos
                self.waypoints[num][self.selectedView2] = ypos
            
            self.drawWaypoints(True)
            
        else:            
            self.draggedX = (float(event.x)/10)
            self.draggedY = (float(event.y)/10)
    
    def onMouseLeftClick(self, event):
        if self.haveSelected!=None:
            self.waypoints[self.haveSelected][3] = 0
            self.haveSelected = None
        possible = []
        for index,value in enumerate(self.waypoints):
            centerX = ((value[self.selectedView1]-self.xMin)/float(self.xMax - self.xMin))*self.canvas.winfo_width()
            centerY = ((value[self.selectedView2]-self.yMin)/float(self.yMax - self.yMin))*self.canvas.winfo_height()
            centerY = self.canvas.winfo_height() - centerY
            
            if math.pow(event.x-centerX,2) + math.pow(event.y-centerY,2) <= math.pow(self.waypointRadius,2):
                if self.haveSelected != None:
                     self.waypoints[self.haveSelected][3] = 0
                value[3] = 1
                self.haveSelected = index

                
        self.drawWaypoints(1)
        
    def onMouseRightClick(self,event):
        if self.haveSelected != None:
            num = self.haveSelected
            newPoint = [0,0,0,0]       
            newPoint[self.selectedView1] = (event.x*float(self.xMax - self.xMin))/float(self.canvas.winfo_width())+self.xMin
            newPoint[self.selectedView2] = ((self.canvas.winfo_height()-event.y)*float(self.yMax - self.yMin))/float(self.canvas.winfo_height())+self.yMin
            self.waypoints.insert(num+1, newPoint) 
            self.waypoints[self.haveSelected][3] = 0
            self.haveSelected = None
            
        self.drawWaypoints(1)
        print self.haveSelected
    
    def onDelete(self,event):
        if self.haveSelected!=None:
            self.waypoints.remove(self.waypoints[self.haveSelected])
        self.drawWaypoints(1)
            
    
    def onMouseRelease(self, event):
        if(self.haveSelected != None):
            Log = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()))
            waypointsDictionary = Log.getParameters("waypoints").waypoints
            waypoint = waypointsDictionary.get(self.waypoints[self.haveSelected][4])
            waypoint[0][0] = self.waypoints[self.haveSelected][2]
            waypoint[0][1] = self.waypoints[self.haveSelected][0]
            waypoint[2] = self.waypoints[self.haveSelected][1]
            
            
            if waypointsDictionary != 0 and waypointsDictionary !=None: #If "waypoints" is in the list
                waypointsDictionary[self.waypoints[self.haveSelected][4]] = [waypoint[0], waypoint[1], waypoint[2]] #Append on to it
            else: #Otherwise, start a new one
                waypointsDictionary = {"{}".format(self.waypoints[self.haveSelected][4]): [waypoint[0], waypoint[1], waypoint[2]]}
                
            Log.writeParameters(waypoints = waypointsDictionary)
        if(self.haveSelected != None and self.draggedX != None and self.draggedY != None):
            self.master.onMouseRelease(event) 
        self.draggedX = None
        self.draggedY = None
        
    def zoomIn(self):
        self.xMax -= (self.xMax*.10)
        self.xMin += (self.xMax*.10)
        self.yMax -= (self.yMax*.10)
        self.yMin += (self.yMax*.10)
        
        if(self.xMin > self.xMax):
            temp = self.xMax
            self.xMax = self.xMin
            self.xMin = temp
        if(self.yMin > self.yMax):
            temp = self.yMax
            self.yMax = self.yMin
            self.yMin = temp
            
        self.drawWaypoints(True)
        
    def zoomOut(self):
        self.xMax += (self.xMax*.10)
        self.xMin -= (self.xMax*.10)
        self.yMax += (self.yMax*.10)
        self.yMin -= (self.yMax*.10)
        
        if(self.xMin > self.xMax):
            temp = self.xMax
            self.xMax = self.xMin
            self.xMin = temp
        if(self.yMin > self.yMax):
            temp = self.yMax
            self.yMax = self.yMin
            self.yMin = temp
        self.drawWaypoints(True)
        
    def setView(self, i,v):
        self.selectedView1 = self.axis.get(i)
        self.selectedView2 = self.axis.get(v)
        self.drawWaypoints()
        
    def recalibrateWaypoints(self):
        Log = previous_state_logging_system.Log('_Saved_Missions_/_Last_Mission_List_({})'.format(self.window.lastUser.get()))
        self.missionList = Log.getParameters("missionList").missionList
        self.waypointList = Log.getParameters("waypoints").waypoints
        self.parameters = Log.getParameters("paramValueList").paramValueList
        self.waypoints = []
        NavigationNumber = 1
        for index, value in enumerate(self.missionList):
            if(value[:10] == "Navigation"):
                st = value[:10]
                st += "Waypoint"
                num = re.split("\s+",value)
                st += " "+ num[1]
                st = self.parameters.get(st)
                NavigationNumber += 1
                waypoint = self.waypointList.get(st)
                self.addWaypoint(waypoint[0][1], waypoint[2], waypoint[0][0], st)
                
        self.drawWaypoints(True)
        
