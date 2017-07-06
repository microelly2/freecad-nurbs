
import FreeCAD
import FreeCADGui as Gui


from FreeCAD import Base
import Part
App=FreeCAD




def runOnEdges():
	'''version bei selektierten geschlossenen Kanten'''

	import FreeCADGui as Gui
	import Part
	wx=Gui.Selection.getSelectionEx()
	sls=[]
	for w in wx:
		sls += w.SubObjects

	l=Part.makeLoft(sls,True,True,False)

	Part.show(l)


def run():
	ribs=Gui.Selection.getSelection()

	l=App.ActiveDocument.addObject('Part::Loft','Loft')
	l.Ruled = True
	l.Sections=ribs
	App.activeDocument().recompute()


