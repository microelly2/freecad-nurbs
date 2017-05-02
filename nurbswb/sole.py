# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a shoe sole
#--
#-- microelly 2017 v 0.8
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

__version__ = '0.10'




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

def runA():

	#-------------------------------------------------------------------------------
	LL=244.0
	LS=LL+30

	div12=[LL/11*i for i in range(12)]

	higha=[18,17,16,15,11,10,8,5,0,2,5,9,14]
	highb=[17,17,16,15,11,10,8,4,2,1,2,5,9,14]
	highc=[17,17,16,15,25,35,35,15,5,1,2,5,9,14]

	weia=[-15,-22,-28,-30,-32,	-33,-34,-39,-43,-42,	-37,-24,-15]
	weib=[15,26,25,22,20,			22,23,28,32,43,			45,42,15]

	rand=True
	bh=0 # randhoehe
	bw=0.1 # randbreite


	sh=5 # sohlenhoehe


	# prgramm parameter
	# grad der flaechen
	du=3
	dv=3
	drawisolines=False
	drawwires=False

	#-----------------------------------------------------------------------------

	# hilfslinien
	la=[[div12[i],-100,higha[i]] for i in range(12)]
	lb=[[div12[i],100,highb[i]] for i in range(12)]
	lc=[[div12[i],80,highc[i]] for i in range(12)]

	try: App.getDocument("Unnamed")
	except: App.newDocument("Unnamed")
	
	App.setActiveDocument("Unnamed")
	App.ActiveDocument=App.getDocument("Unnamed")
	Gui.ActiveDocument=Gui.getDocument("Unnamed")

	if drawwires:
		import Draft
		wa=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in la])
		wa.ViewObject.LineColor=(.0,1.,.0)

		wb=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in lb])
		wb.ViewObject.LineColor=(1.,0.,.0)

		wc=Draft.makeWire([FreeCAD.Vector(tuple(p)) for p in lc])
		wc.ViewObject.LineColor=(1.,1.,.0)

	# siehe auch https://forum.freecadweb.org/viewtopic.php?f=3&t=20525&start=70#p165214


	pts2=[]
	print "Koordianten ..."
	for i in range(12):
		x=div12[i]
		h=higha[i]
		hc=highc[i]
		if i == 0:
			# fersenform
			tt=[[[16,26,h],[8,18,h],[4,9,h],[0,0,h],[4,-7,h],[8,-14,h],[18,-22,h]]]
			pts2 += tt 
			print (i,tt)
		elif i == 11:
			# Spitze
			# spitzenform
			tt=[[[LS-15,35,h],[LS-8,28,h],[LS-5,14,h],[LS,0,h],[LS-5,-15,h],[LS-8,-20,h],[LS-15,-35,h]]]
			pts2 += tt 
			print (i,tt)
		else:
			# mit innengewoelbe
			# pts2 += [[[x,weib[i]+1.0*(weia[i]-weib[i])*j/6,h if j<>0 else hc] for j in range(7)]]
			pts2 += [[[x,weib[i]+1.0*(weia[i]-weib[i])*j/6,h ] for j in range(7)]]
			print (i,round(x,1),h,weib[i],weia[i])


	pts2=np.array(pts2)

	cv=len(pts2)
	cu=len(pts2[0])

	kvs=[1.0/(cv-dv)*i for i in range(cv-dv+1)]
	kus=[1.0/(cu-du)*i for i in range(cu-du+1)]

	mv=[dv+1]+[1]*(cv-dv-1)+[dv+1]
	mu=[du+1]+[1]*(cu-du-1)+[du+1]

	bs=Part.BSplineSurface()

	bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)

	try:
		fa=App.ActiveDocument.orig
	except:
		fa=App.ActiveDocument.addObject('Part::Spline','orig')

	fa.Shape=bs.toShape()
	fa.ViewObject.ControlPoints=True


	if rand:

		pts0=np.array(pts2).swapaxes(0,1)

		l=np.array(pts0[0])
		l[1:-1,1] += bw
		l[1:-1,2] += bh

		r=np.array(pts0[-1])
		r[1:-1,1] -= bw
		r[1:-1,2] += bh

		pts2=np.concatenate([[l],[pts0[0]],pts0[1:],[r]])



		pts0=np.array(pts2).swapaxes(0,1)

		l=np.array(pts0[0])
		l[:,0] -= bw
		l[:,2] += bh

		pts0[0,0,2] += bh
		pts0[0,0,0] -= bw

		pts0[0,-1,2] += bh
		pts0[0,-1,0] -= bw

		r=np.array(pts0[-1])

		r[:,0] += bw
		r[:,2] += bh

		pts0[-1,0,2] += bh
		pts0[-1,0,0] += bw

		pts0[-1,-1,2] += bh
		pts0[-1,-1,0] += bw

		pts2=np.concatenate([[l],[pts0[0]],pts0[1:],[r]])




	cv=len(pts2)
	cu=len(pts2[0])

	kvs=[1.0/(cv-dv)*i for i in range(cv-dv+1)]
	kus=[1.0/(cu-du)*i for i in range(cu-du+1)]

	mv=[dv+1]+[1]*(cv-dv-1)+[dv+1]
	mu=[du+1]+[1]*(cu-du-1)+[du+1]

	bs=Part.BSplineSurface()

	bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)



	if 1:
		try: fa= App.ActiveDocument.up
		except: fa=App.ActiveDocument.addObject('Part::Spline','up')

		fa.Shape=bs.toShape()
		fa.ViewObject.ControlPoints=True


	if drawisolines:
		for k in kus:
			Part.show(bs.vIso(k).toShape())

		for k in kvs:
			Part.show(bs.uIso(k).toShape())



	if 1:


		pts2[:,:,2] -= sh

		pts3=pts2

		# fuess gewoelbe wieder runter
		'''
		pts3[4,-1,2]=14
		pts3[4,-2,2]=14

		pts3[5,-1,2]=10
		pts3[5,-2,2]=10

		pts3[6,-1,2]=6
		pts3[6,-2,2]=6
		'''


		cv=len(pts2)
		cu=len(pts2[0])

		kvs=[1.0/(cv-dv)*i for i in range(cv-dv+1)]
		kus=[1.0/(cu-du)*i for i in range(cu-du+1)]

		mv=[dv+1]+[1]*(cv-dv-1)+[dv+1]
		mu=[du+1]+[1]*(cu-du-1)+[du+1]

		bs=Part.BSplineSurface()

		bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
					False,False,
					dv,du,
				)



		try: fb= App.ActiveDocument.inner
		except: fb=App.ActiveDocument.addObject('Part::Spline','inner')

		fb.Shape=bs.toShape()
		fb.ViewObject.ControlPoints=True

		try:  loft=App.ActiveDocument.sole
		except: loft=App.ActiveDocument.addObject('Part::Loft','sole')

		loft.Sections=[fa,fb]
		loft.Solid=True
		loft.ViewObject.ShapeColor=(.0,1.,.0)
		App.activeDocument().recompute()

		for f in loft.Sections:
			f.ViewObject.hide()



def createheel():

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


def run():
	runA()
	#createheel()



if __name__=='__main__':
	run()

