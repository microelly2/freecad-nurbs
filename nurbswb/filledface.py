# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a parametric
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


def createShape(obj):
#	print obj.e1.Shape.Edges[obj.n1-1]
#	print obj.e2.Shape.Edges[obj.n2-1]
#	print obj.e3.Shape.Edges[obj.n3-1]
	print (obj.n1,obj.n2,obj.n3)

	ll=[]
	if obj.e1 <>None: ll += [obj.e1.Shape.Edges[obj.n1-1]]
	if obj.e2 <>None: ll += [obj.e2.Shape.Edges[obj.n2-1]]
	if obj.e3 <>None: ll += [obj.e3.Shape.Edges[obj.n3-1]]

	# check wire closed !!!

	try:
		obj.Shape=Part.makeFilledFace(Part.__sortEdges__(ll))
	except:
		obj.Shape=Part.Shape()



class FilledFace(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","e1","Base")
		obj.addProperty("App::PropertyLink","e2","Base")
		obj.addProperty("App::PropertyLink","e3","Base")
		obj.addProperty("App::PropertyInteger","n1","Base")
		obj.addProperty("App::PropertyInteger","n2","Base")
		obj.addProperty("App::PropertyInteger","n3","Base")
		obj.n1=1
		obj.n2=1
		obj.n3=1

		ViewProvider(obj.ViewObject)
		#createShape(obj)

#	def onChanged(self, fp, prop):
#		print ("onChanged",prop)
#		if prop=="Size" or prop in ["n1","n1","n2","e1","e2","e3"]:
#			createShape(fp)

	def execute(proxy,obj):
		createShape(obj)




def createFilledFace():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyFilledFace")
	bn=FilledFace(b)


if __name__=='__main__':

	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyFilledFace")
	bn=FilledFace(b)
	b.e1=App.ActiveDocument.Sketch
	b.e2=App.ActiveDocument.Sketch001
	b.e3=App.ActiveDocument.Sketch002
	b.n1=1
	b.n2=1
	b.n3=1	
	createShape(b)
	b.ViewObject.Transparency=60

