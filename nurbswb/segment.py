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
		face=obj.source.Shape.Face1
		bs=face.Surface.copy()
		uks=bs.getUKnots()
		vks=bs.getVKnots()
		bs.segment(uks[obj.umin],uks[obj.umax],vks[obj.vmin],vks[obj.vmax])
		obj.Shape=bs.toShape()


def createSegment(name="MySegment"):

	ffobj = FreeCAD.activeDocument().addObject(
		"Part::FeaturePython", name)
	Segment(ffobj)
	return ffobj

def run():
	createSegment()

if __name__ == '__main__':

	sm=createSegment()
	sm.source=App.ActiveDocument.orig
	sm.umax=5


