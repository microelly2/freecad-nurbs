# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a parametric tanget surface
#--
#-- microelly 2017 v 0.1
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


class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

# grundmethoden zum sichern

	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None


class ViewProvider:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None


def createShape(obj,force=False):

	poles=obj.source.Shape.Face1.Surface.getPoles()
	pts2=np.array(poles).copy()
	pts=pts2.copy()

	du=3
	dv=3


	if 1:
		dd=2
		l=pts[0].copy()
		l2=pts[0].copy()

		if obj.westSeam:
			seam=obj.westSeam
			print "Seam.....WEST........."
			print seam
			tvs=[]
			for i in range(30):
				n="t"+str(i)
				tvs.append(getattr(seam,n))
			# print tvs
			tvs=np.array(tvs)
			tvs *= obj.tangentFactor
			for i in range(l.shape[0]):
				print l[i]
				l[i,2] += tvs[i,2]
				l[i,0] += tvs[i,0]
				l[i,1] += tvs[i,1]
				l2[i,2] -= tvs[i,2]
				l2[i,0] -= tvs[i,0]
				l2[i,1] -= tvs[i,1]
				print l[i]

		r=pts[-1].copy()
		r2=pts[-1].copy()

		if obj.eastSeam:
			seam=obj.eastSeam
			print "Seam.......EAST......."
			tvs=[]
			print l.shape
			for i in range(30):
				n="t"+str(i)
				tvs.append(getattr(seam,n))
			tvs=np.array(tvs)
			#tvs *= 10
			tvs *= obj.tangentFactor
			for i in range(l.shape[0]):
				r[i,2] += tvs[i,2]
				r[i,0] += tvs[i,0]
				r[i,1] += tvs[i,1]
				r2[i,2] -= tvs[i,2]
				r2[i,0] -= tvs[i,0]
				r2[i,1] -= tvs[i,1]

		pts2=np.concatenate([[l,pts[0],pts[0],pts[0],l2],pts[1:-1],[r,pts[-1],pts[-1],pts[-1],r2]])
		#pts2=np.concatenate([[l2,pts[0],pts[0],pts[0],l],pts[2:-1],[r,pts[-1],pts[-1],pts[-1],r2]])

	pts2=pts2.swapaxes(0,1)

	if 0 or obj.nordSeam<>None or  obj.southSeam<>None:
		#----------- nord und sued

		pts=pts2.copy()


		dd=2
		l=pts[0].copy()
		l2=pts[0].copy()


		if obj.nordSeam:
			seam=obj.nordSeam
			print "Seam......NORD........"
			print seam
			tvs=[]
			for i in range(30):
				n="t"+str(i)
				tvs.append(getattr(seam,n))
			print tvs
			tvs=np.array(tvs)
			tvs *= obj.tangentFactor
			for i in range(l.shape[0]-8):
				print l[i+2]
				l[i+4,2] += tvs[i,2]
				l[i+4,0] += tvs[i,0]
				l[i+4,1] += tvs[i,1]
				l2[i+4,2] -= tvs[i,2]
				l2[i+4,1] -= tvs[i,1]
				l2[i+4,0] -= tvs[i,0]

				print (i,l[i+2])

		r=pts[-1].copy()
		r2=pts[-1].copy()

		if obj.southSeam:
			seam=obj.southSeam
			print "Seam.......South......."
			tvs=[]
			for i in range(30):
				n="t"+str(i)
				tvs.append(getattr(seam,n))
			tvs=np.array(tvs)
			tvs *= obj.tangentFactor
			for i in range(l.shape[0]-8):
				r[i+4,2] += tvs[i,2]
				r[i+4,1] += tvs[i,1]
				r[i+4,0] += tvs[i,0]
				r2[i+4,2] -= tvs[i,2]
				r2[i+4,1] -= tvs[i,1]
				r2[i+4,0] -= tvs[i,0]

		pts2=np.concatenate([[l,pts[0],pts[0],pts[0],l2],pts[1:-1],[r,pts[-1],pts[-1],pts[-1],r2]])

		#--------------------------


	(cv,cu,_x) =pts2.shape

	print ("XXXXXXXXXXXXXXXXXXXXXXX shape",cv,cu)

	kvs=[1.0/(cv-dv)*i for i in range(cv-dv+1)]
	kus=[1.0/(cu-du)*i for i in range(cu-du+1)]

	print len(kvs)
#	print len(kus)
#	kvs=[-1,-0.6,-0.4,-0.2]+ obj.source.Shape.Face1.Surface.getVKnots() +[1.2,1.4,1.6,1.8]
# knotenvektor stimmt nicht .#+#
	kvs=obj.source.Shape.Face1.Surface.getVKnots()
#	kus=[-1]+ obj.source.Shape.Face1.Surface.getUKnots() +[1.5]

	print len(kvs)
	print obj.source.Shape.Face1.Surface.getVKnots()


	mv=[dv+1]+[1]*(cv-dv-1)+[dv+1]
	mu=[du+1]+[1]*(cu-du-1)+[du+1]

	bs=Part.BSplineSurface()

	bs.buildFromPolesMultsKnots(pts2,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)


#	bs.segment(kvs[1],kvs[-2],kus[1],kus[-2])

#	bs.segment(kvs[1],kvs[-2],kus[2],kus[-2])

#ok	bs.segment(kvs[6],kvs[-7],kus[1],kus[-2])
#	bs.segment(kvs[4],kvs[-5],kus[1],kus[-2])

	bs.segment(0,1,kus[1],kus[-2])

#	try: fa=App.ActiveDocument.orig
#	except: fa=App.ActiveDocument.addObject('Part::Spline','orig')

#	fa=App.ActiveDocument.addObject('Part::Spline','orig')
#	fa.Shape=bs.toShape()
#	fa.ViewObject.ControlPoints=True


	if 0:
		print "tangenten links"
		print pts[0]-l

		print "kurve links"
		print pts[0]


		print "tangenten rechts"
		print pts[-1]-r
		print "kurve rechts"
		print pts[-1]



	if 0 and FreeCAD.tangentsleft == [] and obj.tangentsleft==[] and force:
		print "create tangents"
		for i in range(cu):
			t=Draft.makeWire([FreeCAD.Vector(pts[0,i]),FreeCAD.Vector(l[i])])
			t.ViewObject.LineColor=(1.0,1.,0.)
			t.ViewObject.LineWidth=10
			t.Label="Tangent left " + str(i+1)
			FreeCAD.tangentsleft.append(t)
			t=Draft.makeWire([FreeCAD.Vector(pts[-1,i]),FreeCAD.Vector(r2[i])])
			t.ViewObject.LineColor=(1.0,1.,0.)
			t.ViewObject.LineWidth=10
			t.Label="Tangent right " + str(i+1)
	else:
		if obj.tangentsleft <> []:
			print "setze tvektoren neu"
			for i in range(cu):
				obj.tangentsleft[i].Start=FreeCAD.Vector(pts[0,i])
				obj.tangentsleft[i].End=FreeCAD.Vector(l[i])
				obj.tangentsleft[i].Proxy.execute(obj.tangentsleft[i])


	obj.Shape=bs.toShape()
	print "tangenten linksAA"
	print obj.tangentsleft
	hp=App.ActiveDocument.getObject(obj.Name+"BS")
	print hp
	if hp == None:
		hp=App.ActiveDocument.addObject('Part::Spline',obj.Name+"BS")

	hp.Shape=bs.toShape()
	print "2kkoay"



class TangentFace(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","source","Base")
		obj.addProperty("App::PropertyLink","westSeam","Base")
		obj.addProperty("App::PropertyLink","eastSeam","Base")
		obj.addProperty("App::PropertyLink","nordSeam","Base")
		obj.addProperty("App::PropertyLink","southSeam","Base")
		obj.addProperty("App::PropertyLinkList","tangentsleft","Base")
		obj.addProperty("App::PropertyFloat","tangentFactor","Base").tangentFactor=1.0

		ViewProvider(obj.ViewObject)



	def xexecute(proxy,obj):
#		print("execute ")
#		if obj.noExecute: return
		try: 
			if proxy.lock: return
		except:
			print("except proxy lock")
		proxy.lock=True
#		print("myexecute")
		proxy.myexecute(obj)
		proxy.lock=False




	def execute(proxy,obj):
		print "myexecute tanface"
		if hasattr(obj,"westSeam"):
			print "run proxy seam"
			createShape(obj)
		print "done myex"


class Seam(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink","source","Base")
		obj.addProperty("App::PropertyBool","sourceSwap","Base")
		obj.addProperty("App::PropertyInteger","tCount","Base").tCount=30
		obj.addProperty("App::PropertyInteger","index","Base").index=0
#		obj.addProperty("App::PropertyVectorList","tl","Base")
#		obj.removeProperty("tl")
		ViewProvider(obj.ViewObject)
		obj.PropertiesList
		for i in range(30):
			n="t"+str(i)
			obj.addProperty("App::PropertyVector",n,"Base")
			setattr(obj,n,FreeCAD.Vector(-2,0,0.6))

	def onChanged(self, obj, prop):
		if prop in ["vmin","vmax","umin","umax","source"]:
			pass

	def execute(proxy,obj):
		print("execute ")
		if obj.source<>None:
			if obj.sourceSwap:
				poles=np.array(obj.source.Shape.Face1.Surface.getPoles()).swapaxes(0,1)
			else:
				poles=np.array(obj.source.Shape.Face1.Surface.getPoles())
#			for i,p in enumerate(poles[0]):
#				v=poles[0][i]-poles[1][i]
#				setattr(obj,"t"+str(i),FreeCAD.Vector(v)*5)

			sf=obj.source.Shape.Face1.Surface
			index=obj.index
			for i,p in enumerate(poles[index]):
				(u,v)=sf.parameter(FreeCAD.Vector(tuple(p)))
				(t1,t2)=sf.tangent(u,v)
#				print (u,v,t1)
				setattr(obj,"t"+str(i),FreeCAD.Vector(t1))



def createTangentFace():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyTangentFace")
	bn=FilledFace(b)




#	seam=FreeCAD.activeDocument().addObject("Part::FeaturePython","Seam")
#	Seam(seam)



if __name__=='__main__':




	#create the test faces

	cu=6
	cv=6
	du=3
	dv=3

	pts=np.zeros(cu*cv*3).reshape(cu,cv,3)
	for u in range(cu): pts[u,:,0]=10*u 
	for v in range(cv): pts[:,v,1]=10*v 

	pts[4,4,2]=40
	pts[1,2,2]=-80
	pts[1,3,2]=-80
	pts[1,4,2]=-80
	pts[3,1,2]=180

	kvs=[1.0/(cv-dv)*i for i in range(cv-dv+1)]
	kus=[1.0/(cu-du)*i for i in range(cu-du+1)]

	mv=[dv+1]+[1]*(cv-dv-1)+[dv+1]
	mu=[du+1]+[1]*(cu-du-1)+[du+1]

	try: fa=App.ActiveDocument.source
	except: fa=App.ActiveDocument.addObject('Part::Spline','source')

	bs=Part.BSplineSurface()
	bs.buildFromPolesMultsKnots(pts,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)

	fa.Shape=bs.toShape()
	fa.ViewObject.ControlPoints=True
	fa.ViewObject.ShapeColor=(1.0,1.0,0.6)
	source=fa


	try: fa2=App.ActiveDocument.targetE
	except: fa2=App.ActiveDocument.addObject('Part::Spline','targetE')

	pts=np.zeros(cu*cv*3).reshape(cu,cv,3)
	for u in range(cu): pts[u,:,0]=10*u +50
	for v in range(cv): pts[:,v,1]=10*v 
	bs.buildFromPolesMultsKnots(pts,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)

	fa2.Shape=bs.toShape()
	fa2.ViewObject.ControlPoints=True
	fa2.ViewObject.ShapeColor=(1.0,.6,1.0)

	'''
	# some more testfaces
	try: fa3=App.ActiveDocument.targetN
	except: fa3=App.ActiveDocument.addObject('Part::Spline','targetN')

	pts=np.zeros(cu*cv*3).reshape(cu,cv,3)
	for u in range(cu): pts[u,:,0]=10*u 
	for v in range(cv): pts[:,v,1]=10*v +50
	bs.buildFromPolesMultsKnots(pts,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)

	fa3.Shape=bs.toShape()
	fa3.ViewObject.ControlPoints=True
	fa3.ViewObject.ShapeColor=(1.0,.6,1.0)

	try: fa4=App.ActiveDocument.targetW
	except: fa4=App.ActiveDocument.addObject('Part::Spline','targetW')
	pts=np.zeros(cu*cv*3).reshape(cu,cv,3)
	for u in range(cu): pts[u,:,0]=10*u -50
	for v in range(cv): pts[:,v,1]=10*v 
	bs.buildFromPolesMultsKnots(pts,mv,mu,kvs,kus,
				False,False,
				dv,du,
			)

	fa4.Shape=bs.toShape()
	fa4.ViewObject.ControlPoints=True
	fa4.ViewObject.ShapeColor=(1.0,.6,1.0)
	'''



if __name__ == '__main__':
	# create the segment for tangents
	import nurbswb.segment
	ke= nurbswb.segment.createFineSegment()
	ke.source=App.ActiveDocument.source
	ke.Label="SeamBase E"
	ke.umax=100
	ke.umin=99

	kw= nurbswb.segment.createFineSegment()
	kw.source=App.ActiveDocument.source
	kw.Label="SeamBase W"
	kw.umax=1
	kw.umin=0

	kn= nurbswb.segment.createFineSegment()
	kn.source=App.ActiveDocument.source
	kn.Label="SeamBase N"
	kn.vmax=100
	kn.vmin=99


	ks= nurbswb.segment.createFineSegment()
	ks.source=App.ActiveDocument.source
	ks.Label="SeamBase S"
	ks.vmax=1
	ks.vmin=0

	#create the seam
	wseam=FreeCAD.activeDocument().addObject("Part::FeaturePython","SeamW")
	Seam(wseam)

	eseam=FreeCAD.activeDocument().addObject("Part::FeaturePython","SeamE")
	Seam(eseam)

	nseam=FreeCAD.activeDocument().addObject("Part::FeaturePython","SeamN")
	Seam(nseam)

	sseam=FreeCAD.activeDocument().addObject("Part::FeaturePython","SeamS")
	Seam(sseam)


	# seams aus streifen berechnen 
	poles=ke.Shape.Face1.Surface.getPoles()
	for i,p in enumerate(poles[0]):
		v=poles[0][i]-poles[1][i]
		setattr(wseam,"t"+str(i),v*5)


	poles=kw.Shape.Face1.Surface.getPoles()
	for i,p in enumerate(poles[0]):
		v=poles[0][i]-poles[1][i]
		setattr(eseam,"t"+str(i),v*5)

	poles=np.array(kn.Shape.Face1.Surface.getPoles()).swapaxes(0,1)
	for i,p in enumerate(poles[0]):
		v=poles[0][i]-poles[1][i]
		setattr(nseam,"t"+str(i),FreeCAD.Vector(v)*5)

	poles=np.array(ks.Shape.Face1.Surface.getPoles()).swapaxes(0,1)
	for i,p in enumerate(poles[0]):
		v=poles[0][i]-poles[1][i]
		setattr(sseam,"t"+str(i),FreeCAD.Vector(v)*5)


	# seams von segmenten abhaengig machen
	eseam.source=ke
	nseam.source=kn
	nseam.sourceSwap=True
	sseam.source=ks
	sseam.sourceSwap=True
	wseam.source=kw


	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyTangentialFace")
	bn=TangentFace(b)
	b.westSeam=wseam
	b.eastSeam=eseam
	b.nordSeam=nseam
	b.southSeam=sseam
	b.source=fa2
	createShape(b,force=True)



	# some placements to see the tangent effect
	if 0:
		b2=Draft.clone(b)
		b2.Placement.Base.x=-100

		b3=Draft.clone(b)
		b3.Placement.Base.x=-50
		b3.Placement.Base.y=50


		b3=Draft.clone(b)
		b3.Placement.Base.x=-50
		b3.Placement.Base.y=-50


		ss=Draft.clone(source)
		ss.Placement.Base.x=50
		ss.Placement.Base.y=50


		ss=Draft.clone(source)
		ss.Placement.Base.x=-50
		ss.Placement.Base.y=50


		ss=Draft.clone(source)
		ss.Placement.Base.x=50
		ss.Placement.Base.y=-50

		ss=Draft.clone(source)
		ss.Placement.Base.x=-50
		ss.Placement.Base.y=-50



	App.activeDocument().recompute()




	# quality check
	c1=App.ActiveDocument.source.Shape.Edge3.Curve
	c2=App.ActiveDocument.MyTangentialFace.Shape.Edge2.Curve

	a1=c1.discretize(100)
	a2=c2.discretize(100)

	for i,p in  enumerate(a1):
		assert (p-a2[i]).Length <1e-9





def runseam():

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	s=FreeCAD.activeDocument().addObject("Part::FeaturePython","SeamW")
	Seam(s)
	s.source=source


def runtangentsurface():

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyTangentialFace")
	TangentFace(b)
	b.source=source

