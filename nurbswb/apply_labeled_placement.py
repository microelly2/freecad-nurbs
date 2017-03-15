
import FreeCAD
import FreeCADGui as Gui


def run():
	for y in Gui.Selection.getSelection():
		if y.Label.startswith('t='):
			exec(y.Label)
			print t
			print y.Placement
			y.Placement=t #.inverse()
