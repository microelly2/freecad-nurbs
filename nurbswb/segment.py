# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a segemt of s bspline surface
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


import FreeCAD
import FreeCADGui
App = FreeCAD
Gui = FreeCADGui

import Part


class PartFeature:

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

# grundmethoden zum sichern

	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


class ViewProvider:

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None



class Segment(PartFeature):
	'''parametric filled face'''

	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink", "source", "Base")

		obj.addProperty("App::PropertyInteger", "umin", "Base")
		obj.addProperty("App::PropertyInteger", "umax", "Base")
		obj.addProperty("App::PropertyInteger", "vmin", "Base")
		obj.addProperty("App::PropertyInteger", "vmax", "Base")

		obj.umax=-1
		obj.vmax=-1
		ViewProvider(obj.ViewObject)


	def execute(proxy, obj):
		if  len(obj.source.Shape.Faces) >= 1:
			face=obj.source.Shape.Face1
			bs=face.Surface.copy()
			uks=bs.getUKnots()
			vks=bs.getVKnots()
			bs.segment(uks[obj.umin],uks[obj.umax],vks[obj.vmin],vks[obj.vmax])
		else:
			edge=obj.source.Shape.Edge1
			bs=edge.Curve.copy()
			ks=bs.getKnots()
			bs.segment(ks[obj.umin],ks[obj.umax])

		obj.Shape=bs.toShape()


def createSegment(name="MySegment"):

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	Segment(ffobj)
	return ffobj


class NurbsTrafo(PartFeature):
	'''parametric filled face'''

	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink", "source", "Base")

		obj.addProperty("App::PropertyInteger", "start", "Base")
		obj.addProperty("App::PropertyInteger", "umax", "Base")
		obj.addProperty("App::PropertyInteger", "vmin", "Base")
		obj.addProperty("App::PropertyInteger", "vmax", "Base")

		obj.umax=-1
		obj.vmax=-1
		ViewProvider(obj.ViewObject)


	def execute(proxy, obj):
		bc=obj.source.Shape.Edge1.Curve.copy()
		pols=bc.getPoles()
		i=obj.start
		pols2=pols[i:] +pols[:i]

		multies=bc.getMultiplicities()
		knots=bc.getKnots()
		deg=bc.Degree
		bc.buildFromPolesMultsKnots(pols2,multies,knots,True,deg)

		obj.Shape=bc.toShape()


def createNurbsTrafo(name="MyNurbsTafo"):

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	NurbsTrafo(ffobj)
	return ffobj



class FineSegment(PartFeature):

	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink", "source", "Base")

		obj.addProperty("App::PropertyInteger", "factor", "Base")

		obj.addProperty("App::PropertyInteger", "umin", "Base")
		obj.addProperty("App::PropertyInteger", "umax", "Base")
		obj.addProperty("App::PropertyInteger", "vmin", "Base")
		obj.addProperty("App::PropertyInteger", "vmax", "Base")

		obj.factor=100

		obj.umin=0
		obj.vmin=0
		obj.umax=obj.factor
		obj.vmax=obj.factor

		ViewProvider(obj.ViewObject)


	def execute(proxy, obj):
		pass

	def onChanged(self, obj, prop):
		if prop in ["vmin","vmax","umin","umax","source"]:
			face=obj.source.Shape.Face1
			bs=face.Surface.copy()

			if obj.umin<0: obj.umin=0
			if obj.vmin<0: obj.vmin=0
			
			if obj.umax>obj.factor: obj.umax=obj.factor
			if obj.vmax>obj.factor: obj.vmax=obj.factor
			if obj.umin>obj.umax: obj.umin=obj.umax
			if obj.vmin>obj.vmax: obj.vmin=obj.vmax

			umin=1.0/obj.factor*obj.umin
			umax=1.0/obj.factor*obj.umax
			vmin=1.0/obj.factor*obj.vmin
			vmax=1.0/obj.factor*obj.vmax


			if umin>0:
				bs.insertUKnot(umin,1,0)

			if umax<obj.factor:
				bs.insertUKnot(umax,1,0)

			if vmin>0:
				bs.insertVKnot(vmin,1,0)

			if vmax<obj.factor:
				bs.insertVKnot(vmax,1,0)


			bs.segment(umin,umax,vmin,vmax)
			obj.Shape=bs.toShape()


def createFineSegment(name="MyFineSegment"):

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	FineSegment(ffobj)
	return ffobj




def run():

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	s=createSegment()
	
	s.source=source
	sm.umax=-2
	sm.umin=2

if __name__ == '__main__':

#	sm=createSegment()
#	sm.source=App.ActiveDocument.Sketch
#	sm.umax=5

	k=createFineSegment()
	k.source=App.ActiveDocument.orig




