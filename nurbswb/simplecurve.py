import random
import Draft,Part

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt



def simplecurve(wire,ct=20,plotit=False,offset=0):

	pts=wire.Points
	off=FreeCAD.Vector(0,0,offset)

	bc=Part.BSplineCurve()
	bc.approximate(pts,DegMax=3,Tolerance=1)
	bc.setPeriodic()
	sc=bc.toShape()
	print 

	sp=App.ActiveDocument.addObject("Part::Spline","approx Spline")
	sp.Shape=sc

	x=np.array(range(ct+1))

	vps=np.array([bc.value(1.0/ct*i)+off for i in x])
	y=np.array([sc.curvatureAt(1.0/ct*i) for i in x])

	z=argrelextrema(y, np.greater)
	z2=argrelextrema(y, np.less)
	z=z[0]
	z2=z2[0]

	mm=y[z]
	mm2=y[z2]

	if plotit:
		plt.plot(x,y, 'r-')
		plt.plot(z,mm,'bo')
		plt.plot(z2,mm2,'go')
		plt.show()

	zc=np.concatenate([z,z2,[0,ct]])
	zc.sort()
	exps=vps[zc]

	ps=[tuple(p) for p in exps]

	# Draft.makeWire(ps,closed=True)
	Draft.makeBSpline(ps,closed=True,face=False)

	App.ActiveDocument.ActiveObject.Label="simple " +str(ct) 
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.0,1.0,0.0)
	App.ActiveDocument.ActiveObject.ViewObject.LineWidth=6
	#print App.ActiveDocument.ActiveObject.Shape.Area
	App.activeDocument().recompute()
	App.activeDocument().recompute()

	sh=App.ActiveDocument.ActiveObject.Shape.Edge1.Curve.toShape()
	sp=App.ActiveDocument.addObject("Part::Spline","simple Spline")
	sp.Shape=sh

	Gui.updateGui()


def run():
	for obj in Gui.Selection.getSelection():
		#for s in [0,1,4]:
		for s in [2]:
			simplecurve(obj,(s+1)*10,False,offset=-10*s-1)
		#print obj.Shape.Area
