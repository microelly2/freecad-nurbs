
from say import *

sk = App.ActiveDocument.getObject('rib_10')


def toggleShoeSketch():
	if len( Gui.Selection.getSelection())<>0:
		sk=Gui.Selection.getSelection()[0]
	print "toogle sketch constraints for " + sk.Label
	for i,c in enumerate(sk.Constraints):
		if c.Name.startswith('p') or c.Name.startswith('tang') or c.Name.startswith('Width'):
			print c.Name
			try:
				sk.toggleDriving(i)
		#		sk.setDriving(i,False)
			except: pass
