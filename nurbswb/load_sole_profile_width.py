


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

def cellname(col,row):
		#limit to 26
		if col>90-64:
			raise Exception("not implement")
		char=chr(col+64)
		cn=char+str(row)
		return cn


def run():
	aktiv=App.ActiveDocument

	fn=FreeCAD.ParamGet('User parameter:Plugins/shoe').GetString("width profile")
	if fn=='':
		fn= __dir__+"/../testdata/breitev3.fcstd"
		FreeCAD.ParamGet('User parameter:Plugins/shoe').SetString("width profile",fn)


	dok=FreeCAD.open(fn)
	s=dok.Sketch

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


	sss=dok.findObjects("Sketcher::SketchObject")
	ss=sss[0]

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
