''' save sketches into a sketch lib, load sketches into models ''' 
from say import *
import nurbswb
import nurbswb.pyob

import time
import glob

from PySide import QtGui, QtCore




import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import PySide
from PySide import  QtGui,QtCore


def run(w):
	print ("I'm run")
	print (w)
	print (w.obj)
	print ("-------------")
	FreeCAD.oo=w.obj
	sk=w.obj.Object #.Object
	print (sk.Label)
	print (sk.Name)


def dialog(obj):

	w=QtGui.QWidget()
	w.obj=obj

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	l=QtGui.QLabel("Anzahl" )
	w.l=l
	box.addWidget(l)

	w.r=QtGui.QPushButton("run")
	box.addWidget(w.r)
	w.r.pressed.connect(lambda :run(w))


	return w



#-------------











#\cond
class _ViewProvider(nurbswb.pyob.ViewProvider):
	''' base class view provider '''

	def __init__(self, vobj):
		self.Object = vobj.Object
		vobj.Proxy = self

	def getIcon(self):
		return FreeCAD.ConfigGet("UserAppData") +'/Mod/freecad-nurbs/icons/sketchdriver.svg'

	def setupContextMenu(self, obj, menu):
		menu.clear()
		action = menu.addAction("MyMethod #1")
		action.triggered.connect(lambda:self.methodA(obj.Object))
		action = menu.addAction("MyMethod #2")
		menu.addSeparator()
		action.triggered.connect(lambda:self.methodB(obj.Object))
		action = menu.addAction("Edit Sketch")
		action.triggered.connect(lambda:self.myedit(obj.Object))


	def myedit(self,obj):
		self.methodB(None)
		Gui.activeDocument().setEdit(obj.Name)
		self.methodA(None)

	def methodA(self,obj):
#		print ("my Method A Finisher")
#		Gui.activateWorkbench("DraftWorkbench")
		FreeCAD.activeDocument().recompute()

	def methodB(self,obj):
		print ("my method B Starter")
		# test starting an extra dialog
		FreeCAD.d=dialog(self)
		FreeCAD.d.show()
		FreeCAD.activeDocument().recompute()

	def methodC(self,obj):
		print ("my method C After Edit finished")
		Gui.activateWorkbench("NurbsWorkbench")
		FreeCAD.activeDocument().recompute()

	def unsetEdit(self,vobj,mode=0):
		self.methodC(None)


	def doubleClicked(self,vobj):
		print ("double clicked")
		self.myedit(vobj.Object)
		print ("Ende double clicked")



#\endcond


def copySketch(sketch,name):
	'''kopiert sketch in sketchobjectpython'''
	sb=sketch
	gs=sb.Geometry
	cs=sb.Constraints

	sk=App.activeDocument().addObject('Sketcher::SketchObjectPython',name)
	_ViewProvider(sk.ViewObject)

	for g in gs:
		rc=sk.addGeometry(g)
		sk.setConstruction(rc,g.Construction)
	#	sk.solve()

	for c in cs:
		rc=sk.addConstraint(c)
	#	sk.solve()

	sk.solve()
	sk.recompute()
	App.activeDocument().recompute()


def replaceSketch(sketch,name):
	'''kopiert sketch in sketchobjectpython'''
	sb=sketch
	gs=sb.Geometry
	cs=sb.Constraints

	sk=App.activeDocument().getObject(name)
	if sk == None or name=='ufo':
		sk=App.activeDocument().addObject('Sketcher::SketchObjectPython',name)
		_ViewProvider(sk.ViewObject)
	rr=range(len(sk.Geometry))
	rr.reverse()

	sk.deleteAllGeometry()

	for g in gs:
#		print (g)
		rc=sk.addGeometry(g)
		sk.setConstruction(rc,g.Construction)

#	print ("Constraints ...")
	for c in cs:
#		print (c)
		rc=sk.addConstraint(c)

	sk.solve()
	sk.recompute()
	App.activeDocument().recompute()
	return sk




def loadSketch(fn,sourcename='Sketch',targetname='Sketch'):
	'''load sketch from file into sketcher object with name'''

	ad=App.ActiveDocument
	if ad==None:
		ad=App.newDocument("Unnamed")

	rc=FreeCAD.open(fn)
	print ("read ",fn)
	print ("active document",ad,ad.Label,ad.Name)

	for obj in rc.Objects:
		print (obj.Name,obj.Label,obj.ViewObject.Visibility)
		if obj.ViewObject.Visibility:
			print ("found")
			sb=obj
			break

	#sb=rc.getObject(sourcename)
	assert sb is not None


	# App.setActiveDocument(ad.Label)
	App.setActiveDocument(ad.Name)
	App.ActiveDocument=ad

	sk=replaceSketch(sb,targetname)
	
	sk.Label="Copy of "+sourcename+"@"+fn
	App.closeDocument(rc.Label)





def getfiles():
	'''list sketcher files library''' 
	files=glob.glob(FreeCAD.ConfigGet("UserAppData") +'sketchlib/'+'*_sk.fcstd')
	files.sort()
	return files



def saveSketch(w=None):
	'''save Gui.Selection  sketch into a file inside the sketch lib directory'''

	sel=Gui.Selection.getSelection()[0]
	fn=FreeCAD.ConfigGet("UserAppData") +'sketchlib/'+sel.Name+"_"+str(int(round(time.time())))+"_sk.fcstd"
	nd=App.newDocument("XYZ")
	App.ActiveDocument=nd
	copySketch(sel,"Sketch")
	print (sel.Label+" - speichere als " + fn)
	App.ActiveDocument.saveAs(fn)
	App.closeDocument("XYZ")



#\cond
def srun(w):
	a=w.target
	lm=getfiles()

	model=lm[w.m.currentIndex()]

	import nurbswb.sketchmanager
	reload(nurbswb.sketchmanager)

	target='ufo'

	s=Gui.Selection.getSelection()
	if s != []: 
		target=s[0].Name
	print ("target is: ",target)

	cmd="nurbswb.sketchmanager.loadSketch('" + model +"','Sketch',target)"
	print ("Run command:",cmd)
	eval(cmd)
	Gui.SendMsgToActiveView("ViewFit")
	# w.hide()
#\endcond


def MyLoadDialog(target=None):
	'''widget for load sketch from file into a sketch object''' 

	lm=getfiles()
	w=QtGui.QWidget()
	w.target=target

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	l=QtGui.QLabel("Select the model" )
	box.addWidget(l)

	combo = QtGui.QComboBox()
	for item in lm:
		combo.addItem(str(item))
	w.m=combo
	combo.activated.connect(lambda:srun(w))  
	box.addWidget(combo)

#	w.r=QtGui.QPushButton("save selected sketch as file")
#	box.addWidget(w.r)
#	w.r.pressed.connect(lambda :saveSketch(w))

	w.show()
	return w


# hier names dialog einbauen
def MySaveDialog(target=None):
	'''widget for save sketch into a file''' 

	lm=getfiles()
	w=QtGui.QWidget()
	w.target=target

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)


	w.r=QtGui.QPushButton("save selected sketch as file")
	box.addWidget(w.r)
	w.r.pressed.connect(lambda :saveSketch(w))

	w.show()
	return w




def runLoadSketch():
	'''method called from Gui menu'''
	#[target]=FreeCADGui.Selection.getSelection()
	target=None
	return MyLoadDialog(target)

def runSaveSketch():
	'''method saveSketch called from Gui menu'''
	#[target]=FreeCADGui.Selection.getSelection()
#	target=None
#	return MySaveDialog(target)
	saveSketch()

def runSketchLib():
	'''method called from Gui menu'''
	sayexc2("Ups","Noch nicht implementiert")

if __name__=='__main__':
	runLoadSketch()

