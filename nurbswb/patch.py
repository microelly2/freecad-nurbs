#-*- coding: utf-8 -*-
'''
#-------------------------------------------------
#-- methods for drawing on faces 
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
'''

##\cond
from nurbswb.say import *

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtGui
import Part,Mesh,Draft,Points

import numpy as np
import random

def normalizek(bc):

	bx=Part.BSplineCurve()

	poles=bc.getPoles()
	mults=bc.getMultiplicities()

	knots=bc.getKnots()
	knots=np.array(knots)
	knots *=3
	knots -= knots.min()
	knots /= knots.max()

	bx.buildFromPolesMultsKnots(poles,mults,knots)
	return bx


def createSubEdge(ed,p1,p2):
	v1=p1.Point
	v2=p2.Point
	k1=ed.Curve
	rc=createSubcurve(k1,v1,v2)
	return rc

def createSubcurve(k1,v1,v2):
	k1c=k1.copy()
	kka=k1.parameter(v1)
	kkb=k1.parameter(v2)

	k1c.insertKnot(kka,2,0)
	k1c.insertKnot(kkb,2,0)

	if kka>kkb:
		kka,kkb=kkb,kka

	k1c.segment(kka,kkb)
	k1cn=normalizek(k1c)

	b3=App.ActiveDocument.addObject("Part::Spline","subedge")
	b3.ViewObject.LineColor=(10.0,0.0,1.0)
	b3.ViewObject.LineWidth=4
	b3.Shape=k1cn.toShape()

	return k1cn


def machFlaeche(psta,ku,objName="XXd"):
		NbVPoles,NbUPoles,_t1 =psta.shape

		degree=3

		ps=[[FreeCAD.Vector(psta[v,u,0],psta[v,u,1],psta[v,u,2]) for u in range(NbUPoles)] for v in range(NbVPoles)]

		kv=[1.0/(NbVPoles-3)*i for i in range(NbVPoles-2)]
		mv=[4] +[1]*(NbVPoles-4) +[4]
		mu=[4]+[1]*(NbUPoles-4)+[4]

		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(ps, mv, mu, kv, ku, False, False ,degree,degree)

		res=App.ActiveDocument.getObject(objName)

		# if res==None:
		res=App.ActiveDocument.addObject("Part::Spline",objName)
			# res.ViewObject.ControlPoints=True

		res.Shape=bs.toShape()

		return bs









def run():

	#edge and 2 points
	#ed=App.ActiveDocument.Sketch.Shape.Edge1
	#p1=App.ActiveDocument.Point.Shape.Vertex1
	#p2=App.ActiveDocument.Point002.Shape.Vertex1

	#eda=App.ActiveDocument.Sketch001.Shape.Edge1
	#p1a=App.ActiveDocument.Point001.Shape.Vertex1
	#p2a=App.ActiveDocument.Point003.Shape.Vertex1

	s=FreeCADGui.Selection.getSelectionEx()

	ed=s[0].SubObjects[0]
	p1=s[1].SubObjects[0]
	p2=s[2].SubObjects[0]

	eda=s[3].SubObjects[0]
	p1a=s[4].SubObjects[0]
	p2a=s[5].SubObjects[0]


	# erzeuge zwei normalisierte subkurven
	c=createSubEdge(ed,p1,p2)
	ca=createSubEdge(eda,p1a,p2a)

	kns=c.getKnots()
	knsa=ca.getKnots()

	for k in kns+knsa:
		if k not in kns:
			c.insertKnot(k,1,0)
		if k not in knsa:
			ca.insertKnot(k,1,0)

	kns=c.getKnots()
	knsa=ca.getKnots()

	pl2=c.getPoles()
	pl3=ca.getPoles()

	# tangent constraint 
	pl1x=[ p+FreeCAD.Vector(10,0,-10) for p in pl2]
	pl1xa=[ p+FreeCAD.Vector(20,0,-20) for p in pl2]
	pl1xb=[ p+FreeCAD.Vector(30,0,-30) for p in pl2]

	# bergruecken 
	pl3x=[]
	for i in range(len(pl2)):
		pl3x += [pl2[i]*0.7+pl3[i]*0.3+FreeCAD.Vector(0,0,500*random.random())]

	pl2x=[]	
	for i in range(len(pl2)):
		pl2x += [pl2[i]*0.2+pl3[i]*0.8+FreeCAD.Vector(0,0,500*random.random())]

	# tangent constraint
	pl3xa=[ p+FreeCAD.Vector(-10,0,0) for p in pl3]
	pl3xb=[ p+FreeCAD.Vector(-20,0,0) for p in pl3]
	pl3xc=[ p+FreeCAD.Vector(-30,0,0) for p in pl3]


	psta=np.array([pl2,pl1x,pl1xa,pl1xb,pl3x,pl2x,pl3xc,pl3xb,pl3xa,pl3])
	bs=machFlaeche(psta,kns,"mountains")

