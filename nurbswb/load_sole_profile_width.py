


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

	fn= __dir__+"/../testdata/breitev3.fcstd"

	FreeCAD.open(fn)
	dok=App.getDocument("breitev3")
	s=dok.Sketch



	s.getDatum('r1').Value


	rs=[]
	ls=[]
	for i in range(1,12):
		print s.getDatum('r'+str(i)).Value
		print s.getDatum('l'+str(i)).Value
		rs += [s.getDatum('r'+str(i)).Value]
		ls += [s.getDatum('l'+str(i)).Value]


	App.closeDocument("breitev3")


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


	for s in range(1,12):
		cn=cellname(s+1,14)
		print (s,cn,ss.get(cn))
		ss.set(cn,str(rs[s-1]))
		cn=cellname(s+1,15)
		print (s,cn,ss.get(cn))
		ss.set(cn,str(ls[s-1]))



	dok2.recompute()


	App.getDocument("Unnamed").recompute()

	import nurbswb.sole
	reload(nurbswb.sole)
	nurbswb.sole.run()

	App.getDocument("Unnamed").recompute()
