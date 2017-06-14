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
import numpy as np



class PartFeature:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


class ViewProvider:
	''' basic defs '''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None



class Segment(PartFeature):
	'''segment einer bspline  flaeche oder kurve
	Einschraenkung:
	es wird die erste flaeche Face1 bzw. die erste Kante Edge1 verarbeitet
	'''

	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink", "source", "Base")
		obj.addProperty("App::PropertyInteger", "umin", "Base")
		obj.addProperty("App::PropertyInteger", "umax", "Base")
		obj.addProperty("App::PropertyInteger", "vmin", "Base")
		obj.addProperty("App::PropertyInteger", "vmax", "Base")
		obj.addProperty("App::PropertyBool", "closeV", "Base")

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

		if obj.closeV:
			bs.setVPeriodic()

		obj.Shape=bs.toShape()


def createSegment(name="MySegment"):
	''' erzeugt ein segment aus der source Flaeche oder Kurve
	Segmente sind nur fuer die gegebenen Knoten mieglich
	umin, ... vmax: Eingabe der Knotennummer
	'''

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	Segment(ffobj)
	return ffobj


class NurbsTrafo(PartFeature):
	'''rotieren des pole-array, um naht zu verschieben'''

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
		if  len(obj.source.Shape.Faces) >= 1:
			face=obj.source.Shape.Face1
			bs=face.Surface.copy()

			poles=bs.getPoles()
			ku=bs.getUKnots()
			kv=bs.getVKnots()
			mu=bs.getUMultiplicities()
			mv=bs.getVMultiplicities()

			y=np.array(poles).swapaxes(0,1)
			k=obj.start

			poles2=np.concatenate([y[k:],y[:k]]).swapaxes(0,1)
			print poles2

			bs2=Part.BSplineSurface()
			bs2.buildFromPolesMultsKnots(poles2,
				mu,mv,
				ku,kv,
				False,True,3,3,)

			obj.Shape=bs2.toShape()

		else:
			bc=obj.source.Shape.Edge1.Curve.copy()
			pols=bc.getPoles()

			multies=bc.getMultiplicities()
			knots=bc.getKnots()
			deg=bc.Degree

			i=obj.start
			pols2=pols[i:] +pols[:i]
			bc.buildFromPolesMultsKnots(pols2,multies,knots,True,deg)

			obj.Shape=bc.toShape()



def createNurbsTrafo(name="MyNurbsTafo"):
	''' erzeugt ein NurbsTrafo Objekt '''

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	NurbsTrafo(ffobj)
	return ffobj



class FineSegment(PartFeature):
	''' erzeugt ein feines Segment, dass feienr ist als die normale Segmentierung des nurbs
	factor gibt die Anzahl der Abstufungen an
	die Zahlen umin, ... vmax sind ganzzahlige Anteile von factor
	'''

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
#			bs.setUNotPeriodic()
#			bs.setVNotPeriodic()

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

			if bs.isVPeriodic() and not vmax< bs.getVKnots()[-1]:
				vmax=bs.getVKnots()[-1]
# geht so nicht: 
#				obj.vmax=int(round(vmax*obj.factor,0))

			if bs.isUPeriodic() and not umax< bs.getUKnots()[-1]:
				umax=bs.getUKnots()[-1]
#				obj.umax=int(round(umax*obj.factor,0))

			print  bs.getUKnots()
			print  bs.getVKnots()
			print ("interval",umin,umax,vmin,vmax)

			if umin>0 and umin not in bs.getUKnots():
				bs.insertUKnot(umin,1,0)

			if umax<obj.factor and umax not in bs.getUKnots():
				bs.insertUKnot(umax,1,0)

			if vmin>0 and vmin not in bs.getVKnots():
				bs.insertVKnot(vmin,1,0)

			if vmax<obj.factor and vmax not in bs.getVKnots(): # and vmax< bs.getVKnots()[-1]:
				bs.insertVKnot(vmax,1,0)

			uks=bs.getUKnots()
			if umin<uks[0]: umin=uks[0]
			
			print ("interval",umin,umax,vmin,vmax)
			bs.segment(umin,umax,vmin,vmax)
			obj.Shape=bs.toShape()



def createFineSegment(name="MyFineSegment"):
	''' erzeugt ein FineSegment Objekt '''

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	FineSegment(ffobj)
	return ffobj



def runsegment():
	'''anwendungsfall fuer die selection wird ein segment erzeugt'''

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	s=createSegment()
	s.source=source
	sm.umax=-2
	sm.umin=2

def runfinesegment():
	'''anwendungsfall fuer die selection wird ein segment erzeugt'''

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	s=createFineSegment()
	s.source=source

def runnurbstrafo():
	'''anwendungsfall fuer die selection wird ein segment erzeugt'''

	source=None
	if len( Gui.Selection.getSelection())<>0:
		source=Gui.Selection.getSelection()[0]
	s=createNurbsTrafo()
	s.source=source




if __name__ == '__main__':

#	sm=createSegment()
#	sm.source=App.ActiveDocument.Sketch
#	sm.umax=5

	k=createFineSegment()
	k.source=App.ActiveDocument.orig






