
# auswertung heel -Linie



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

def run():

	fn= __dir__+"/../testdata/heelsv3.fcstd"
	FreeCAD.open(fn)

	dok=App.getDocument("heelsv3")
	s=dok.Sketch001
	c=s.Shape.Edge1.Curve

	pts=c.discretize(86)

	mpts=[]
	for i in [0,15,25,35,45,55,65,75,85]:
		print pts[i]
		mpts.append(pts[i])

	App.closeDocument("heelsv3")


	dok2=App.getDocument("Unnamed")
	App.setActiveDocument(dok2.Name)

	def cellname(col,row):
		#limit to 26
		if col>90-64:
			raise Exception("not implement")
		char=chr(col+64)
		cn=char+str(row)
		return cn

	ss=dok2.Spreadsheet

	for s in range(8):
		cn=cellname(s+3,9)
		print (s,cn,ss.get(cn), mpts[-s-1])
		ss.set(cn,str(mpts[-s-1].y))

	for j in range(7):
		cn=cellname(j+2,26)
		ss.set(cn,str((mpts[-1].y)))


	dok2.recompute()


	App.getDocument("Unnamed").recompute()

	import nurbswb.sole
	reload(nurbswb.sole)
	nurbswb.sole.run()

	App.getDocument("Unnamed").recompute()
