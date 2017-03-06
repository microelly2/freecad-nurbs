# -*- coding: utf-8 -*-
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


def run():
	color=(random.random(),random.random(),random.random())

	pl=FreeCAD.ActiveDocument.Plane.Placement
	plst=" Base:" + str(pl.Base) +" Rot Euler:" + str(pl.Rotation.toEuler())
	plinv=pl.inverse()

	stl=FreeCAD.ActiveDocument.LastDIA.Mesh
	pts=stl.Topology[0]


	pts2=[plinv.multVec(p) for p in pts]

	zmax=0.5
	zmin=-zmax

	pts2a=[FreeCAD.Vector(p.x,p.y,0) for p in pts2 if zmin<=p.z and p.z<=zmax]

	p2=Points.Points(pts2a)
	Points.show(p2)
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
	FreeCAD.ActiveDocument.ActiveObject.Label="Points Map xy " +plst



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

	l4=ptss

	# window size for smoothing
	f=31
	path=np.array([l4[0]] * f + l4 + [l4[-1]]*f)
	tt=path.swapaxes(0,1)
	y1 = sp.signal.medfilt(tt[1],f)
	l5=[FreeCAD.Vector(p) for p in np.array([tt[0],y1,tt[2]]).swapaxes(0,1)] 

	Draft.makeWire(l5)
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.LineColor=color
	FreeCAD.ActiveDocument.ActiveObject.Label="Median filter " + str(f)  + " " + plst


	# place the wire back into the shoe
	invmin=[pl.multVec(p) for p in l5]
	Draft.makeWire(invmin)
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.LineColor=color
	FreeCAD.ActiveDocument.ActiveObject.Label="Wire "+ plst

	# diusplay the used points inside the shoe
	sels=[pl.multVec(p) for p in pts2a]
	s2=Points.Points(sels)
	Points.show(s2)
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
	FreeCAD.ActiveDocument.ActiveObject.Label="Points " +plst





if __name__ == '__main__':
	run()
