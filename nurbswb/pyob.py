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

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None
##\endcond
