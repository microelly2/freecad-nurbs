# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- feedbacksketch
#--
#-- microelly 2017 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


# from say import *
# import nurbswb.pyob
#------------------------------
import FreeCAD,FreeCADGui,Sketcher,Part

App = FreeCAD
Gui = FreeCADGui

import numpy as np
import time



def myShape(obj,shapeBuilder):
	print (shapeBuilder) 
	if shapeBuilder=="xy+xz":
		return methodA(obj)
	else:
		return None


def methodA(obj):
	#v1=App.ActiveDocument.Sketch.Shape.Vertexes
	#v2=App.ActiveDocument.Sketch001.Shape.Vertexes
	try:
		v1=obj.baseClientA.Shape.Vertexes
		v2=obj.baseClientB.Shape.Vertexes
	except:
		print "cannont buid shape"
		return Part.Shape()
	
	pts=[]
	pts2=[]
	for i,v in enumerate(v1):
		p=v.Point
		z=v2[i].Point.z
		pts.append(FreeCAD.Vector(p.x,p.y,z))
		pts2.append(FreeCAD.Vector(p.x,p.y+25,z+10))

	print pts
	
	sh=Part.makeLoft([Part.makePolygon(pts),Part.makePolygon(pts2)])
	print sh
	return Part.Compound([sh])

