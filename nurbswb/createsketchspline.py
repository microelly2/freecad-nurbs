import random
import Draft,Part

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt




import Sketcher 

def createSketchSpline(pts=None,label="BSpline Sketch"):

	try: body=App.activeDocument().Body
	except:	body=App.activeDocument().addObject('PartDesign::Body','Body')

	sk=App.activeDocument().addObject('Sketcher::SketchObject','Sketch')
	sk.Label=label

#	sk.Support = (App.activeDocument().XY_Plane, [''])

	sk.MapMode = 'FlatFace'

	App.activeDocument().recompute()

	if pts==None:
		pass
		pts=[FreeCAD.Vector(a) for a in [(10,20,30), (30,60,30), (20,50,40),(50,80,90)]]

	for i,p in enumerate(pts):
		sk.addGeometry(Part.Circle(App.Vector(int(round(p.x)),int(round(p.y)),0),App.Vector(0,0,1),10),True)
		if i == 1: sk.addConstraint(Sketcher.Constraint('Radius',0,10.000000)) 
		if i>0: sk.addConstraint(Sketcher.Constraint('Equal',0,i)) 

	k=i+1

	l=[App.Vector(int(round(p.x)),int(round(p.y))) for p in pts]

	# sk.addGeometry(Part.BSplineCurve(l,False),False)
	sk.addGeometry(Part.BSplineCurve(l,True),False)

	conList = []

	for i,p in enumerate(pts):
		conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',i,3,k,i))

	sk.addConstraint(conList)

	App.activeDocument().recompute()

 	sk.Placement = App.Placement(App.Vector(0,0,p.z),App.Rotation(App.Vector(1,0,0),0))

	App.activeDocument().recompute()
	print "ZZZZZZZZZZZZZZZZZZZ",p.z

	return sk


def run():
	for obj in Gui.Selection.getSelection():
		bc=obj.Shape.Edge1.Curve
		pts=bc.getPoles()
		l=obj.Label
		createSketchSpline(pts,"Sketch for " + str(l))
