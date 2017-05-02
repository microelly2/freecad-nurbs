


import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from PySide import QtGui
import Part,Mesh,Draft,Points


def run():

	try:
		[sourcex,targetx]=Gui.Selection.getSelectionEx()
		s=sourcex.SubObjects[0]
		f=targetx.SubObjects[0]

	except:
		[source,target]=Gui.Selection.getSelection()

		s=source.Shape.Edge1
		f=target.Shape.Face1

	p=f.makeParallelProjection(s, App.Vector(0,0,1))
	Part.show(p)


