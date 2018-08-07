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
		obj.addProperty("App::PropertyBool","_noExecute",'zzz')
		obj.addProperty("App::PropertyBool","_debug",'zzz')


	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def onBeforeChange(self, fp, prop):
		pass

	def onDocumentRestored(self, fp):
		pass

class ViewProvider:
	''' basic defs '''

	def __init__(self, obj,icon=None):
		obj.Proxy = self
		self.Object = obj
		self.icon=icon
		if icon==None:
			icon= 'freecad-nurbs/icons/BB.svg'
		if icon.startswith('/'): ic= self.icon
		else: ic= FreeCAD.ConfigGet("UserAppData") +'/Mod/' + icon 

		obj.addProperty("App::PropertyString",'icon').icon=ic

#	def onDelete(self, obj, subelements):
#		return False

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object


	def getIcon(self):
		try: return self.Object.ViewObject.icon
		except: return self.Object.Object.ViewObject.icon

	def claimChildren(self):
		try: s=self.Object.Object
		except: s=self.Object
		rc=[]
		for prop in  s.PropertiesList:
			if s.getTypeIdOfProperty(prop) in ['App::PropertyLink']:
				v=s.getPropertyByName(prop)
				if v <>None:
					rc += [v]
			elif s.getTypeIdOfProperty(prop) in ['App::PropertyLinkList']:
				v=s.getPropertyByName(prop)
				if len(v) <> 0:
					rc += v
		return rc







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


#a=Sketch()
#b=Spreadsheet()

