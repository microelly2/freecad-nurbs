# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- convert a draft bspline to a sketcher bspline
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import random
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt

import Draft,Part,Sketcher
import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtGui
import sys,traceback,random


def showdialog(title="Fehler",text="Schau in den ReportView fuer mehr Details",detail=None):
	msg = QtGui.QMessageBox()
	msg.setIcon(QtGui.QMessageBox.Warning)
	msg.setText(text)
	msg.setWindowTitle(title)
	if detail<>None:   msg.setDetailedText(detail)
	msg.exec_()


def sayexc(title='Fehler',mess=''):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=lls[(l-3):]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))
	showdialog(title,text=mess,detail="--> ".join(l2))


def createSketchSpline(pts=None,label="BSpline Sketch",periodic=True):

	try: body=App.activeDocument().Body
	except:	body=App.activeDocument().addObject('PartDesign::Body','Body')

	sk=App.activeDocument().addObject('Sketcher::SketchObject','Sketch')
	sk.Label=label
	sk.MapMode = 'FlatFace'

	App.activeDocument().recompute()

	if pts==None: # some test data
		pts=[FreeCAD.Vector(a) for a in [(10,20,30), (30,60,30), (20,50,40),(50,80,90)]]

	for i,p in enumerate(pts):
		sk.addGeometry(Part.Circle(App.Vector(int(round(p.x)),int(round(p.y)),0),App.Vector(0,0,1),10),True)
		#if i == 1: sk.addConstraint(Sketcher.Constraint('Radius',0,10.000000)) 
		#if i>0: sk.addConstraint(Sketcher.Constraint('Equal',0,i)) 

		radius=2.0
		sk.addConstraint(Sketcher.Constraint('Radius',i,radius)) 
		sk.renameConstraint(i, 'Weight ' +str(i+1))

		#i=5; App.ActiveDocument.Sketch016.setDatum(i,40))

	k=i+1

	l=[App.Vector(int(round(p.x)),int(round(p.y))) for p in pts]

	if not periodic:
		# open spline
#		sk.addGeometry(Part.BSplineCurve(l,False),False)
		ll=sk.addGeometry(Part.BSplineCurve(l,None,None,False,3,None,False),False)

	else:
		# periodic spline
#		sk.addGeometry(Part.BSplineCurve(l,True),False)
		ll=sk.addGeometry(Part.BSplineCurve(l,None,None,True,3,None,False),False)


	conList = []
	for i,p in enumerate(pts):
		conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',i,3,k,i))
	sk.addConstraint(conList)

	App.activeDocument().recompute()

 	sk.Placement = App.Placement(App.Vector(0,0,p.z),App.Rotation(App.Vector(1,0,0),0))
	sk.ViewObject.LineColor=(random.random(),random.random(),random.random())
	App.activeDocument().recompute()
	return sk


def runobj(obj,label=None):
	''' erzeugt fuer ein objekt den SktchSpline'''

	bc=obj.Shape.Edge1.Curve
	pts=bc.getPoles()
	l=obj.Label
	print (l,len(pts))
	sk=createSketchSpline(pts,str(l) + " Sketch" )
	if label <>None:
		sk.Label=label
	return sk


def run():
	''' erzeugt fuer jedes selektierte Objekte  aus Edge1 einen Sketch'''

	if len( Gui.Selection.getSelection())==0:
		showdialog('Oops','nothing selected - nothing to do for me','Plese select a Draft Bspline or Draft Wire')

	for obj in Gui.Selection.getSelection():
		try:
			bc=obj.Shape.Edge1.Curve
			pts=bc.getPoles()
			l=obj.Label
			print (l,len(pts))
			periodic=bc.isPeriodic()
			createSketchSpline(pts,str(l) + " Sketch" ,periodic)
		except:
			sayexc(title='Error',mess='somethinq wrong with ' + obj.Label)
