
import FreeCAD
import FreeCADGui as Gui


from FreeCAD import Base
import Part
App=FreeCAD



def run():
	ribs=Gui.Selection.getSelection()

	l=App.ActiveDocument.addObject('Part::Loft','Loft')
	l.Ruled = True
	l.Sections=ribs
	App.activeDocument().recompute()


