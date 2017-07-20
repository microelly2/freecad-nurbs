'''python objects for freecad'''

# -*- coding: utf-8 -*-
#-- microelly 2017 v 0.1
#-- GNU Lesser General Public License (LGPL)


##\cond
import FreeCAD
import FreeCADGui
App = FreeCAD
Gui = FreeCADGui

import Part
import numpy as np


class FeaturePython:
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

	def __init__(self, obj,icon=None):
		obj.Proxy = self
		self.Object = obj
		self.icon=icon

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


	def getIcon(self):
		if self.icon.startswith('/'): return self.icon
		else: return FreeCAD.ConfigGet("UserAppData") +'/Mod/' + self.icon 
##\endcond


# proxies for the python objects 
#
def _Sketch(FeaturePython):

	def __init__(self,obj):
		FeaturePython.__init__(self, obj)
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj

def _Sheet(FeaturePython):

	def __init__(self,obj):
		FeaturePython.__init__(self, obj)



# anwendungsklassen 


def Sketch(name='MySketch'):
	'''creates a SketchObjectPython'''

	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	obj.addProperty("App::PropertyBool", "off", "Base",)
	_Sketch(obj)
	ViewProvider(obj.ViewObject,'freecad-nurbs/icons/sketchdriver.svg')
	return obj


def Spreadsheet(name='MySketch'):
	'''creates a Spreadsheet'''

	obj = FreeCAD.ActiveDocument.addObject('Spreadsheet::Sheet',name)
	obj.addProperty("App::PropertyBool", "off", "Base",)
	_Sheet(obj)
	return obj


a=Sketch()
b=Spreadsheet()

