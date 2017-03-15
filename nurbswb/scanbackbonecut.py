#-*- coding: utf-8 -*-
#-------------------------------------------------
#-- scan cut --- shoe last - get cut wires from a scan
#--
#-- microelly 2017v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
import FreeCAD
import FreeCADGui
import Points,Part,Draft
import numpy as np
import random
import scipy as sp
from scipy import signal

from PySide import QtGui
import sys,traceback,random

import Points


# Points.export(__objs__,u"/home/thomas/Dokumente/freecad_buch/b235_shoe/shoe_last_scanned.asc")

Points.insert(u"/home/thomas/Dokumente/freecad_buch/b235_shoe/shoe_last_scanned.asc","Shoe")


FreeCADGui.runCommand("Draft_ToggleGrid")


import FreeCAD
import FreeCADGui
import Points,Part,Draft
import numpy as np
import random
import scipy as sp
from scipy import signal
import Points
import random

def displayCut(pl,pts,showpoints=True,showwire=False,showxypoints=False,showxywire=False):
	''' display approx cut of a plane with a point cloud '''
	z0=0

	color=(random.random(),random.random(),random.random())

	#pl=FreeCAD.ActiveDocument.Plane.Placement
	plst=" Base:" + str(pl.Base) +" Rot Euler:" + str(pl.Rotation.toEuler())
	plst="FreeCAD.Placement(FreeCAD." + str(pl.Base) +", FreeCAD.Rotation" + str(pl.Rotation.toEuler())+") "

	plinv=pl.inverse()




	pts2=[plinv.multVec(p) for p in pts]
	#pts2=[FreeCAD.Vector(round(p.x),round(p.y),round(p.z)) for p in pts2]

	zmax=0.5
	zmin=-zmax

	#pts2a=[FreeCAD.Vector(p.x,p.y,0) for p in pts2 if zmin<=p.z and p.z<=zmax]

	pts2a=[FreeCAD.Vector(round(p.x),round(p.y),round(p.z)) for p in pts2 if round(p.z)==z0]
	
	if len(pts2a)==0: return

	p2=Points.Points(pts2a)
	if showxypoints:
		Points.show(p2)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
		FreeCAD.ActiveDocument.ActiveObject.Label="Points Map xy " +plst
		FreeCAD.ActiveDocument.ActiveObject.Label="t=" +plst + "#"



	# create a wire from a central projection
	(px,py,pz)=np.array(pts2a).swapaxes(0,1)
	mymean=FreeCAD.Vector(px.mean(),py.mean(),pz.mean())
	aps={}
	for v in pts2a:
		vm=v-mymean
	#	print np.arctan2(vm.x,vm.y)
		aps[np.arctan2(vm.x,vm.y)]=v

	kaps=aps.keys()
	kaps.sort()
	ptss=[aps[k] for k in kaps]
	print ("lens ",len(ptss),len(pts2a))

	l4=ptss

	# window size for smoothing
	f=5
	path=np.array([l4[0]] * f + l4 + [l4[-1]]*f)
	tt=path.swapaxes(0,1)
	y1 = sp.signal.medfilt(tt[1],f)
	y0 = sp.signal.medfilt(tt[0],f)
	#l5=[FreeCAD.Vector(p) for p in np.array([tt[0],y1,tt[2]]).swapaxes(0,1)] 
	l5=[FreeCAD.Vector(p) for p in np.array([y0,y1,tt[2]]).swapaxes(0,1)] 

	if showxywire:
		Draft.makeWire(l5)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.LineColor=color
		FreeCAD.ActiveDocument.ActiveObject.Label="Median filter " + str(f)  + " " + plst


	if showwire:
		# place the wire back into the shoe
		invmin=[pl.multVec(p) for p in l5]
		Draft.makeWire(invmin)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.LineColor=color
		FreeCAD.ActiveDocument.ActiveObject.Label="Wire "+ plst
	if showpoints:
		# diusplay the used points inside the shoe
		sels=[pl.multVec(p) for p in pts2a]
		s2=Points.Points(sels)
		Points.show(s2)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
		FreeCAD.ActiveDocument.ActiveObject.Label="Points " +plst
		


def run():

	bbps=[ 
					[255,0,13], #b
					[250,0,11.5], #b
					[245,0,10], #b
					[218,0,4], #st
					[168,0,0], # joint j
					[132,0,6], # girth
					[110,0,10], # waist
					[68,0,14], # instep ik
					[3,0,19], # heel pk
					[15,0,110], # heel2 ph
					[15,0,180], # wade aa
					[15,0,190], # wade aa
					[15,0,199], # wade aa
			]

	twister= [[0,75,0]]+[[0,0,0]]*3 + [[0,30,0]]*4 +[[0,48,0]]+ [[0,90,0]]+ [[0,90,0]]*3

	for i,b in enumerate(bbps):
		# if i<>6 : continue
		alpha=twister[i][1] 

		pla=FreeCAD.Placement(FreeCAD.Vector(b),FreeCAD.Rotation(FreeCAD.Vector(0,1,0),alpha-90))
		pcl=FreeCAD.ActiveDocument.shoe_last_scanned.Points.Points

		displayCut(pla,pcl,showpoints=False,showxywire=False,showxypoints=True)
		#displayCut(pla,pcl,showpoints=True,showxywire=False,showxypoints=True)

	#pla=FreeCAD.Placement()
	#displayCut(pla,pcl,showpoints=True,showwire=True)

