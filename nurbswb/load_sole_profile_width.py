


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
import numpy as np

import nurbswb.spreadsheet_lib
reload (nurbswb.spreadsheet_lib)
from nurbswb.spreadsheet_lib import ssa2npa, npa2ssa, cellname


def run():
	aktiv=App.ActiveDocument

	fn=FreeCAD.ParamGet('User parameter:Plugins/shoe').GetString("width profile")
	if fn=='':
		fn= __dir__+"/../testdata/breitev3.fcstd"
		FreeCAD.ParamGet('User parameter:Plugins/shoe').SetString("width profile",fn)


	dok=FreeCAD.open(fn)
	sss=dok.findObjects("Sketcher::SketchObject")
	s=sss[0]


	# werte aus sketch holen
	rs=[]
	ls=[]
	for i in range(1,12):
		rs += [s.getDatum('r'+str(i)).Value]
		ls += [s.getDatum('l'+str(i)).Value]

	App.closeDocument(dok.Name)



	#eigentliche Arbeitsdatei
	dok2=aktiv
	App.setActiveDocument(dok2.Name)


	sss=dok2.findObjects("Sketcher::SketchObject")
#	print sss,dok2.Name
	ss=dok2.Spreadsheet

	# daten ins spreadsheet
	for s in range(1,12):
		cn=cellname(s+1,14)
		ss.set(cn,str(rs[s-1]))
		cn=cellname(s+1,15)
		ss.set(cn,str(ls[s-1]))


	# aktualisieren
	dok2.recompute()
	import nurbswb.sole
	reload(nurbswb.sole)
	nurbswb.sole.run()
	dok2.recompute()
