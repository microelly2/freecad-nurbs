#
# objekt auf curve positionieren und ausrichten
#
import FreeCAD 
import FreeCADGui

import numpy as np

def srun(w):

	bc=w.path.Shape.Edge1.Curve
	c=w.target
	v=w.ha.value()*0.01
	movepos(bc,c,v)


def movepos(bc,c,v):

	pa=bc.LastParameter
	ps=bc.FirstParameter

	v=ps +(pa-ps)*v

	t=bc.tangent(v)[0]
	p=bc.value(v)

	zarc=np.arctan2(t.y,t.x)
	zarc *=180.0/np.pi

	harc=np.arcsin(t.z)
	harc *=180.0/np.pi

	pl=FreeCAD.Placement()
	pl.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,1,0,),90-harc)

	pa=FreeCAD.Placement()
	pa.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1,),zarc)
	pl2=pa.multiply(pl)

	pl2.Base=p
	c.Placement=pl2




from PySide import QtGui, QtCore

def MyDialog(path,target):

	w=QtGui.QWidget()
	w.path=path
	w.target=target

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)



	l=QtGui.QLabel("Position" )
	box.addWidget(l)

	h=QtGui.QDial()
	
	h.setMaximum(100)
	h.setMinimum(0)
	w.ha=h
	srun(w)

	h.valueChanged.connect(lambda:srun(w))
	box.addWidget(h)


	w.show()
	return w


def run():
	[path,target]=FreeCADGui.Selection.getSelection()
	MyDialog(path,target)

# selektion:
# 1. pfad spline
# 2. zu platzierendes objekt


run()
