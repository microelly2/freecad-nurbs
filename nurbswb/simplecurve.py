# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- convert a draft wire to a sketcher bspline
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import random
import Draft,Part

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt


def simplecurve(wire,ct=20,plotit=False,offset=0,debug=False):

	pts=wire.Points
	off=FreeCAD.Vector(0,0,offset)

	bc=Part.BSplineCurve()
	bc.approximate(pts,DegMax=3,Tolerance=1)
	bc.setPeriodic()
	sc=bc.toShape()

	if debug:
		sp=App.ActiveDocument.addObject("Part::Spline","approx Spline")
		sp.Shape=sc

	# calculate the interpolation points
	x=np.array(range(ct+1))
	vps=np.array([bc.value(1.0/ct*i)+off for i in x])
	y=np.array([sc.curvatureAt(1.0/ct*i) for i in x])

	# find extrema for the poles
	z=argrelextrema(y, np.greater)
	z2=argrelextrema(y, np.less)
	z=z[0]
	z2=z2[0]

	mm=y[z]
	mm2=y[z2]

	if plotit: # display for debugging
		plt.plot(x,y, 'r-')
		plt.plot(z,mm,'bo')
		plt.plot(z2,mm2,'go')
		plt.show()

	zc=np.concatenate([z,z2,[0,ct]])
	zc.sort()
	exps=vps[zc]

	ps=[tuple(p) for p in exps]

	Draft.makeBSpline(ps,closed=True,face=False)

	App.ActiveDocument.ActiveObject.Label="simple " +str(ct) 
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.0,1.0,0.0)
	App.ActiveDocument.ActiveObject.ViewObject.LineWidth=6
	App.activeDocument().recompute()
	App.activeDocument().recompute()

	if debug:
		sh=App.ActiveDocument.ActiveObject.Shape.Edge1.Curve.toShape()
		sp=App.ActiveDocument.addObject("Part::Spline","simple Spline")
		sp.Shape=sh

	Gui.updateGui()



def run():

	for obj in Gui.Selection.getSelection():

		#default parameters
		p={
			"splitcount":[10,'Integer'],
			"splits":['6,10,20','String'],
			"showplot":[False,'Boolean'],
			"test":[False,'Boolean'],
			"debug":[False,'Boolean'],
		}

		# parameter -----------------
		t=FreeCAD.ParamGet('User parameter:Plugins/nurbs/'+'simplecurve')
		l=t.GetContents()
		if l==None: l=[]
		for k in l: p[k[1]]=k[2]
		for k in p:
			if p[k].__class__.__name__=='list':
				typ=p[k][1]
				if typ=='Integer':t.SetInt(k,p[k][0]);
				if typ=='Boolean':t.SetBool(k,p[k][0])
				if typ=='String':t.SetString(k,p[k][0])
				if typ=='Float':t.SetFloat(k,p[k][0])
				p[k]=p[k][0]
		#--------------------

		ct=p["splitcount"]
		splits=eval(p["splits"])
		plotit=p["showplot"]

		print (ct,splits,plotit)

		for s in splits:
			simplecurve(obj,s,plotit,offset=-10*s-1,debug=p['debug'])
