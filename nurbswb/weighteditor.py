# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- change sketcher constrains from a separate dialog
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
import FreeCAD as App
import FreeCADGui as Gui
import matplotlib.colors as colors

import PySide
from PySide import  QtGui,QtCore

def runex(window):
	window.hide()


def wrun(w):
	for q in w.box:
		print (w.sk.Label,q.i,q.value(),q.c.Name)
		w.sk.setDatum(q.i,q.value())
	App.activeDocument().recompute()




def dialog(sk=None):

	if sk==None:
		[sk]=Gui.Selection.getSelection()
	if 1:

		w=QtGui.QWidget()
		w.sk=sk

		tc=sk.ViewObject.LineColor
		color=colors.rgb2hex(sk.ViewObject.LineColor)    
		invers=(1.0-tc[0],1.0-tc[1],1.0-tc[2])
		icolor=colors.rgb2hex(invers) 
		mcolor='#808080'   
		w.setStyleSheet("QWidget { background-color:"+color+"}\
			QPushButton { margin-right:0px;margin-left:0px;margin:0 px;padding:0px;;\
			background-color:#ccc;text-align:left;;padding:6px;padding-left:4px;color:#333; }")

		box = QtGui.QVBoxLayout()
		w.setLayout(box)
		w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

		l=QtGui.QLabel(sk.Label)
		l.setText( '<font color='+icolor+'>your labelcontent</font>' ) 
		box.addWidget(l)

		w.box=[]
		for i,c in enumerate(sk.Constraints):
			print (c.Name,c.Value)
			if c.Name.startswith("Weight"):
				l=QtGui.QLabel(c.Name)
				l.setText( '<font color='+icolor+'>'+c.Name+'</font>' ) 
				box.addWidget(l)

				d=QtGui.QSlider(QtCore.Qt.Horizontal)
				d.c=c
				d.i=i

				box.addWidget(d)
				d.setValue(c.Value)
				d.setMaximum(100)
				d.setMinimum(0)
				d.valueChanged.connect(lambda:wrun(w))
				w.box.append(d)

		w.r=QtGui.QPushButton("close")
		box.addWidget(w.r)
		w.r.pressed.connect(lambda :runex(w))

		w.show()

	return w




def run():
	for sk in  Gui.Selection.getSelection():
		w=dialog(sk)
