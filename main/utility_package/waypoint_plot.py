'''
Copyright 2015, Austin Owens, All rights reserved.

.. module:: waypoint_plot
   :synopsis: Creates a 2D and 3D scatter plot of recorded waypoints.

:Author: Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Jul 22, 2015
:Description: This module creates a 2D and 3D scatter plot of waypoints that are recorded in the _Saved_Missions_ folder.
'''
import main.gui_components.previous_state_logging_system as previous_state_logging_system
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

missionSelectorData = previous_state_logging_system.Log('../mechatronics(Main_Computer_2015)/main/_Saved_Missions_/_Last_Mission_List_({})'.format("Austin Owens"))  #Sphinx
#missionSelectorData = previous_state_logging_system.Log('../_Saved_Missions_/_Last_Mission_List_({})'.format("Austin Owens"))

waypointsDictionary = missionSelectorData.getParameters("waypoints").waypoints #Returns 0 if "waypoints" not in list
datax = []
datay = []
dataz = []
datae = []
labels = []

for name, waypoint in waypointsDictionary.items():
    print name+":",
    print waypoint
    datax.append(waypoint[0][0])
    datay.append(waypoint[0][1])
    dataz.append(-1*waypoint[2])
    datae.append(waypoint[0][3])
    labels.append(name)
print ""
print labels
print datax
print datay
print dataz

#labels = ['point{0}'.format(i) for i in range(N)]
#plt.scatter(data[:, 0], data[:, 1], s, c, marker, cmap, norm, vmin, vmax, alpha, linewidths, verts, hold)
colors = np.random.rand(len(datax))
plt.scatter(datax, datay, marker = 'o', c = colors, cmap = plt.get_cmap('Spectral'))

for label, x, y in zip(labels, datax, datay):
    plt.annotate(
        label, 
        xy = (x, y), xytext = (-10, 10),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

fig = plt.figure()
ax = Axes3D(fig)
#ax.plot(xs = datax, ys = datay, zs=dataz, zdir='z', label='zs=0, zdir=z')
ax.scatter(xs = datax, ys = datay, zs=dataz, zdir='z', label='zs=0, zdir=z')
''''n = 1024
X = np.random.normal(0,1,n)
Y = np.random.normal(0,1,n)

print X
plt.scatter(X,Y)'''
plt.show()

