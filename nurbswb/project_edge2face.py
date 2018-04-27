


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


def runAll():

		wires=[]
		alls=Gui.Selection.getSelection()
		target=alls[-1]
		for source in alls[:-1]:
			for s in source.Shape.Edges:

				f=target.Shape.Face1

				p=f.makeParallelProjection(s, App.Vector(0,0,1))
				wires += p.Wires[0].Edges
				print p.Vertexes[0].Point
				print p.Vertexes[1].Point
#				Part.show(p)

		#FreeCAD.w=wires
		ww=Part.__sortEdges__(w)
		Part.show(Part.Compound(ww))
