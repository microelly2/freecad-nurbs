# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create test data for curve approximations
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


import random
import Draft,Part,Points

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt



def run():
	count=1000
	ri=100
	rm=400
	kaps=np.random.random(count)*2*np.pi
	mmaa=np.random.random(count)*ri*np.cos(kaps*5)*np.cos(kaps*1.3)
	mmaa += rm

	y= np.cos(kaps)
	x=np.sin(kaps)
	x *= mmaa
	y *= mmaa
	z  =  x*0

	pps=np.array([x,y,z]).swapaxes(0,1)
	goods=[FreeCAD.Vector(tuple(p)) for p in pps]

	Points.show(Points.Points(goods))
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.0,0.0,0.0)
	App.ActiveDocument.ActiveObject.ViewObject.PointSize=10

#	Draft.makeWire(goods,closed=True)
