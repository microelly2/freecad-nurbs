'''-- scan cut --- shoe last - get cut wires from a scan'''

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
import sys,traceback,random,os

import Points
import nurbswb

global __dir__
__dir__ = os.path.dirname(nurbswb.__file__)
print __dir__

# Points.export(__objs__,u"/home/thomas/Dokumente/freecad_buch/b235_shoe/shoe_last_scanned.asc")

try: 
	FreeCAD.ActiveDocument.shoe_last_scanned
except: 
#	Points.insert(u"/home/thomas/Dokumente/freecad_buch/b235_shoe/shoe_last_scanned.asc","Shoe")
	Points.insert(__dir__+"/../testdata/shoe_last_scanned.asc","Shoe")

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

def displayCut(label,pl,pts,showpoints=True,showwire=False,showxypoints=False,showxywire=False):
	''' display approx cut of a plane with a point cloud '''
	z0=0

	color=(random.random(),random.random(),random.random())

	#pl=FreeCAD.ActiveDocument.Plane.Placement
	plst=" Base:" + str(pl.Base) +" Rot Euler:" + str(pl.Rotation.toEuler())
	plst="FreeCAD.Placement(FreeCAD." + str(pl.Base) +", FreeCAD.Rotation" + str(pl.Rotation.toEuler())+") "

	plinv=pl.inverse()
	rot2=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),90))
	plinv=rot2.multiply(plinv)

	print "rotation A"
	print " Base:" + str(plinv.Base) +" Rot Euler:" + str(plinv.Rotation.toEuler())

	plaa=plinv.inverse()
	print "rotation B"
	print " Base:" + str(plaa.Base) +" Rot Euler:" + str(plaa.Rotation.toEuler())


	plcc=plaa.multiply(plinv)
	print "rotation C"
	print " Base:" + str(plcc.Base) +" Rot Euler:" + str(plcc.Rotation.toEuler())


	pts2=[plinv.multVec(p) for p in pts]
	#pts2=[FreeCAD.Vector(round(p.x),round(p.y),round(p.z)) for p in pts2]

	zmax=0.5
	zmin=-zmax

	#pts2a=[FreeCAD.Vector(p.x,p.y,0) for p in pts2 if zmin<=p.z and p.z<=zmax]

	pts2a=[FreeCAD.Vector(round(p.x),round(p.y),round(p.z)) for p in pts2 if round(p.z)==z0]

	#pts2a=[FreeCAD.Vector(round(p.z),round(p.y),round(p.x)) for p in pts2 if round(p.z)==z0]

	try: scp=FreeCAD.ActiveDocument.Scanpoints
	except: scp=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Scanpoints")
	try: scps=FreeCAD.ActiveDocument.ScanpointsSource
	except: scps=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","ScanpointsSource")


	if len(pts2a)==0: 
		print ("len ptsa == 0",pts2)
		if showxypoints:
			Points.show(Points.Points([]))
			FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
			FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
			FreeCAD.ActiveDocument.ActiveObject.Label="Points Map xy " +plst
			FreeCAD.ActiveDocument.ActiveObject.Label=label+"t=" +plst + "#"
			FreeCAD.ActiveDocument.ActiveObject.Label="t=" +plst + "#"
			#FreeCAD.ActiveDocument.ActiveObject.Placement.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,1,0),-90)
			scp.addObject(FreeCAD.ActiveDocument.ActiveObject)

		if showpoints:
			# diusplay the used points inside the shoe
			# rot2=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-90))
			#plaa=rot2.multiply(pl)
			#plaa=pl.multiply(rot2)
			
			sels=[plaa.multVec(p) for p in pts2a]
			s2=Points.Points([])
			Points.show(s2)
			FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
			FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
			FreeCAD.ActiveDocument.ActiveObject.Label="Points " +plst
			scps.addObject(FreeCAD.ActiveDocument.ActiveObject)
		return




	p2=Points.Points(pts2a)
	if showxypoints:
		Points.show(p2)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
		FreeCAD.ActiveDocument.ActiveObject.Label="Points Map xy " +plst
		FreeCAD.ActiveDocument.ActiveObject.Label=label+"t=" +plst + "#"
		FreeCAD.ActiveDocument.ActiveObject.Label="t=" +plst + "#"
		#FreeCAD.ActiveDocument.ActiveObject.Placement.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,1,0),-90)
		scp.addObject(FreeCAD.ActiveDocument.ActiveObject)


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
		sels=[plaa.multVec(p) for p in pts2a]

		s2=Points.Points(sels)
		Points.show(s2)
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
		FreeCAD.ActiveDocument.ActiveObject.ViewObject.PointSize=5
		FreeCAD.ActiveDocument.ActiveObject.Label="Points " +plst
		scps.addObject(FreeCAD.ActiveDocument.ActiveObject)

	return plaa

def run():

	bbpsY=[ 
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

	print "import ............"
	import nurbswb.shoedata
	reload(nurbswb.shoedata)
	bbps=nurbswb.shoedata.bbps
	twister=nurbswb.shoedata.twister
	# labels=nurbswb.shoedata.labels
	trafos=[]
	for i,b in enumerate(bbps):
		# if i<>5 : continue
		alpha=twister[i][1]
		beta=twister[i][2]

	#p2.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),FreeCAD.Rotation(FreeCAD.Vector(0,1,0),beta).multiply(FreeCAD.Rotation(FreeCAD.Vector(1,0,0),xa)))

		pla=FreeCAD.Placement(FreeCAD.Vector(b),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-beta).multiply(FreeCAD.Rotation(FreeCAD.Vector(0,1,0),alpha-90)))
		pcl=FreeCAD.ActiveDocument.shoe_last_scanned.Points.Points



		print ("display cut ",i,beta,alpha)
		#displayCut(pla,pcl,showpoints=False,showxywire=False,showxypoints=True)
		trafo=displayCut("cut "+str(i),pla,pcl,showpoints=True,showxywire=False,showxypoints=True)
		trafos.append(trafo)



	#pla=FreeCAD.Placement()
	#displayCut(pla,pcl,showpoints=True,showwire=True)

	import nurbswb
	import nurbswb.createsketchspline
	reload(nurbswb.createsketchspline)

	App=FreeCAD
	jj=App.ActiveDocument.Scanpoints.OutList

	clo=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","clones2")

	for i,p in enumerate(App.ActiveDocument.Scanpoints.OutList):
		scp=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","GRP "+str(i+1))
		try:
			l2=App.ActiveDocument.Profiles.OutList[2].Label
			scp.addObject(jj[i])
			ao=App.ActiveDocument.Profiles.OutList[2]
			scp.addObject(ao)
		except:
			pass

		try:
			obj=App.ActiveDocument.getObject('rib_'+str(i+1))
			scp.addObject(jj[i])
			scp.addObject(obj)
			
			skaa=Draft.clone(obj)
			# skaa.Scale=FreeCAD.Vector(-1,1,1)
			skaa.Placement=trafos[i]
			clo.addObject(skaa)
		except:
			pass

		#rc=nurbswb.createsketchspline.runobj(ao,jj[i].Label)
		#scp.addObject(rc)
		#cl=Draft.clone(rc)
		#cl.Label=rc.Label
		#clo.addObject(cl)

	for i in App.ActiveDocument.Objects:
		i.ViewObject.hide()

	for i in [App.ActiveDocument.shoe_last_scanned] + App.ActiveDocument.clones2.OutList :
		i.ViewObject.show()

