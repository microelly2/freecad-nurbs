# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- change sketcher constrains from a separate dialog
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
import FreeCAD as App
import FreeCADGui
import Points,Part,Draft
import numpy as np
import random
import scipy as sp
from scipy import signal

from PySide import QtGui
import sys,traceback,random

import Points


import FreeCADGui as Gui
import numpy as np
import Draft



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

		box = QtGui.QVBoxLayout()
		w.setLayout(box)
		w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

		l=QtGui.QLabel(sk.Label)
		box.addWidget(l)

		w.box=[]
		for i,c in enumerate(sk.Constraints):
			print (c.Name,c.Value)
			if c.Name.startswith("Weight"):
				l=QtGui.QLabel(c.Name)
				box.addWidget(l)

				d=QtGui.QSlider(QtCore.Qt.Horizontal)
				d.c=c
				d.i=i

				box.addWidget(d)
				d.setValue(c.Value)
				d.setMaximum(100)
				d.setMinimum(0)
				w.box.append(d)
				d.valueChanged.connect(lambda:wrun(w))

		w.r=QtGui.QPushButton("close")
		box.addWidget(w.r)
		w.r.pressed.connect(lambda :runex(w))



		w.show()

	return w




def run():
	for sk in  Gui.Selection.getSelection():
		w=dialog(sk)
