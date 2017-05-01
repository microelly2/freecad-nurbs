# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a shoe sole
#--
#-- microelly 2017 v 0.8
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------



import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtGui
import Part,Mesh,Draft,Points


import numpy as np
import random

import os, nurbswb

global __dir__
__dir__ = os.path.dirname(nurbswb.__file__)
print __dir__
import numpy as np

# 12 divisions 

def run():

	LL=260.0
	div12=[LL/12*i for i in range(13)]
	higha=[18,17,16,15,11,10,8,5,0,2,5,9,14]
	highb=[17,17,16,15,11,10,8,4,2,1,2,5,9,14]
	highc=[17,17,16,15,25,35,35,15,5,1,2,5,9,14]

	weia=[-15,-22,-28,-30,-32,	-33,-34,-39,-43,-42,	-37,-24,-15]
	weib=[15,26,25,22,20,			22,23,28,32,43,			45,42,15]

	la=[[div12[i],-100,higha[i]] for i in range(13)]
	lb=[[div12[i],100,highb[i]] for i in range(13)]
	lc=[[div12[i],80,highc[i]] for i in range(13)]

	try: App.getDocument("Unnamed")
	except: App.newDocument("Unnamed")
	
	App.setActiveDocument("Unnamed")
	App.ActiveDocument=App.getDocument("Unnamed")
	Gui.ActiveDocument=Gui.getDocument("Unnamed")

	import Draft
	wa=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in la])
	wa.ViewObject.LineColor=(.0,1.,.0)

	wb=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in lb])
	wb.ViewObject.LineColor=(1.,0.,.0)

	wc=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in lc])
	wc.ViewObject.LineColor=(1.,1.,.0)


	# siehe auch https://forum.freecadweb.org/viewtopic.php?f=3&t=20525&start=70#p165214

	# der 12 division shoe

	# 0 heel 0
	# 1
	# 2
	# 3
	# 4 
	# 5 
	# 6
	# 7 
	# 8  joint 173
	# 9 
	# 10 217
	# 11
	# 12 top

	pts2=[]
	for i in range(13):
		x=div12[i]
		h=higha[i]
		hc=highc[i]
		if i == 0:
			pts2 +=  [[[16,26,h],[8,18,h],[4,9,h],[0,0,h],[4,-7,h],[8,-14,h],[18,-22,h]]]
		elif i == 12:
			pts2 +=  [[[245,35,h],[252,28,h],[255,14,h],[260,0,h],[255,-8,h],[252,-16,h],[245,-20,h]]]
		else:
			pts2 += [[[x,weib[i]+1.0*(weia[i]-weib[i])*j/6,h if j<>0 else hc] for j in range(7)]]




	#------------------------------------
	pts2=np.array(pts2)

	cv=len(pts2)
	cu=len(pts2[0])

	kvs=[1.0/(cv-3)*i for i in range(cv-2)]
	kus=[1.0/(cu-3)*i for i in range(cu-2)]

	mv=[4]+[1]*(cv-4)+[4]
	mu=[4]+[1]*(cu-4)+[4]

	bs=Part.BSplineSurface()

	bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
				False,False,
				3,3,
			)

	fa=App.ActiveDocument.addObject('Part::Spline','orig')
	fa.Shape=bs.toShape()
	fa.ViewObject.ControlPoints=True


	# sohle mit rand  breit 5, hoch 15
	pts0=np.array(pts2).swapaxes(0,1)


	l=np.array(pts0[0])
	l[1:-1,1] += 5
	l[1:-1,2] += 15

	r=np.array(pts0[-1])
	r[1:-1,1] -= 5
	r[1:-1,2] += 15

	pts2=np.concatenate([[l],[pts0[0]],pts0[1:],[r]])



	pts0=np.array(pts2).swapaxes(0,1)


	l=np.array(pts0[0])
	l[:,0] -= 10
	l[:,2] += 15
	#l[0,0] -= 10

	pts0[0,0,2] += 15
	pts0[0,0,0] -= 10

	pts0[0,-1,2] += 15
	pts0[0,-1,0] -= 10

	r=np.array(pts0[-1])

	r[:,0] += 10
	r[:,2] += 15
	#r[0,0] -= 10

	pts0[-1,0,2] += 15
	pts0[-1,0,0] += 10

	pts0[-1,-1,2] += 15
	pts0[-1,-1,0] += 10


	pts2=np.concatenate([[l],[pts0[0]],pts0[1:],[r]])




	cv=len(pts2)
	cu=len(pts2[0])

	kvs=[1.0/(cv-3)*i for i in range(cv-2)]
	kus=[1.0/(cu-3)*i for i in range(cu-2)]

	mv=[4]+[1]*(cv-4)+[4]
	mu=[4]+[1]*(cu-4)+[4]


	bs=Part.BSplineSurface()

	bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
				False,False,
				3,3,
			)

	if 1:
		fa=App.ActiveDocument.addObject('Part::Spline','up')
		fa.Shape=bs.toShape()
		fa.ViewObject.ControlPoints=True


	if 1:
		for k in kus:
			Part.show(bs.vIso(k).toShape())

		for k in kvs:
			Part.show(bs.uIso(k).toShape())



	if 1:


		# sohlendicke 10 mm
		pts2[:,:,2] -= 10

		pts3=pts2

		cv=len(pts2)
		cu=len(pts2[0])

		kvs=[1.0/(cv-3)*i for i in range(cv-2)]
		kus=[1.0/(cu-3)*i for i in range(cu-2)]

		mv=[4]+[1]*(cv-4)+[4]
		mu=[4]+[1]*(cu-4)+[4]


		# fuess gewoelbe wieder runter
		'''
		pts3[4,-1,2]=14
		pts3[4,-2,2]=14

		pts3[5,-1,2]=10
		pts3[5,-2,2]=10

		pts3[6,-1,2]=6
		pts3[6,-2,2]=6
		'''



		bs.buildFromPolesMultsKnots(pts3,mv,mu,kvs,kus,
					False,False,
					3,3,
				)

		fb=App.ActiveDocument.addObject('Part::Spline','inner')
		fb.Shape=bs.toShape()
		fb.ViewObject.ControlPoints=True

		loft=App.ActiveDocument.addObject('Part::Loft','Oberteile Sohle')
		loft.Sections=[fa,fb]
		loft.Solid=True
		loft.ViewObject.ShapeColor=(.0,1.,.0)
		App.activeDocument().recompute()

		for f in loft.Sections:
			f.ViewObject.hide()


	if 1:

		points=[FreeCAD.Vector(30.0, 11.0, 0.0), FreeCAD.Vector (65., 5., 0.0), 
			FreeCAD.Vector (60., -10., 0.0), FreeCAD.Vector (19., -13., 0.0)]
		spline = Draft.makeBSpline(points,closed=True,face=True,support=None)


		s=spline.Shape.Edge1
		f=App.ActiveDocument.orig.Shape.Face1

		p=f.makeParallelProjection(s, App.Vector(0,0,1))
		Part.show(p)
		proj=App.ActiveDocument.ActiveObject

		clone=Draft.clone(spline)
		clone.Placement.Base.z=-100
		clone.Scale=(0.4,0.5,1.)


		loft=App.ActiveDocument.addObject('Part::Loft','Loft')
		loft.Sections=[proj,clone]


		points = [FreeCAD.Vector(165.,-7.,-00.0),FreeCAD.Vector(208.,-25.,-00.0),FreeCAD.Vector(233.,20.,-00.0)]
		spline = Draft.makeBSpline(points,closed=True,face=True,support=None)


		s=spline.Shape.Edge1
		f=App.ActiveDocument.orig.Shape.Face1

		p=f.makeParallelProjection(s, App.Vector(0,0,1))
		Part.show(p)
		proj=App.ActiveDocument.ActiveObject

		clone=Draft.clone(spline)
		clone.Placement.Base.z=-100

		loft=App.ActiveDocument.addObject('Part::Loft','Loft')
		loft.Sections=[proj,clone]


		App.activeDocument().recompute()
		Gui.activeDocument().activeView().viewAxonometric()
		Gui.SendMsgToActiveView("ViewFit")


		print "okay"



if __name__=='__main__':
	run()
