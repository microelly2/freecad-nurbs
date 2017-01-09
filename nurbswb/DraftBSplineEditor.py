from PySide import QtGui, QtCore

from PySide.QtCore import *
from PySide.QtGui import *
import numpy as np
 
 
import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

# data=np.array([[1,2,3],[5,6,7],[9,10,11]])

def np2tab(arr,tab):
		(xc,yc)=arr.shape
		for x in range(xc):
			for y in range(yc):
				newitem = QTableWidgetItem(str(arr[x,y]))
				tab.setItem(x, y, newitem)

def getArr(obj):
	arr=[[p.x,p.y,p.z] for p in obj.Points]
	return np.array(arr)


def setArr(arr,obj):
	obj.Points=[FreeCAD.Vector(tuple(p)) for p in arr]
	App.ActiveDocument.recompute()


def tab2np(tab):
	arr=[]
	for r in [0,1,2,3]:
		for c in [0,1,2]:
			v=tab.item(r,c)
			arr.append(float(v.text()))
	return np.array(arr).reshape(4,3)



class MyTable(QTableWidget):
	def __init__(self, data, *args):
		QTableWidget.__init__(self, *args)
		self.data = data
		self.setdata()
#		self.resizeColumnsToContents()
#		self.resizeRowsToContents()


	def setdata(self):
 
		(xc,yc)=self.data.shape
		for x in range(xc):
			for y in range(yc):
				newitem = QTableWidgetItem(str(self.data[x,y]))
				self.setItem(x, y, newitem)
		horHeaders=['x','y','z']
		#newitem = QTableWidgetItem('a888')
		#self.setItem(3, 5, newitem)
		self.setHorizontalHeaderLabels(horHeaders)
		# self.setVerticalHeaderLabels(["aa","b"])


def pressed(index):
		print "pressed"
		print index.column()
		print index.row()

def rowcol(*args):
		print "selection row/column changed"
		print args

def button(widget):
		arr=tab2np(widget.table)
		setArr(arr,widget.obj)


def reload(widget):
	arr=getArr(widget.obj)
	np2tab(arr,widget.table)


def pointEditor(obj):

	w=QtGui.QWidget()
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setGeometry(50, 30, 350, 630)


	l=QtGui.QLabel("Interpolation Points of: " + obj.Label)
	box.addWidget(l)

	w.obj=obj
	arr=getArr(obj)
	rs=arr.shape[0]
	table = MyTable(arr,rs,3)
	box.addWidget(table)
	w.table=table
# 	np2tab(arr,w.table)


	table.pressed.connect(pressed)
	table.currentCellChanged.connect(rowcol)


	b=QtGui.QPushButton("Reload from Draft BSpline")
	b.pressed.connect(lambda:reload(w))
	box.addWidget(b)

	b=QtGui.QPushButton("Apply Table to Draft BSpline")
	b.pressed.connect(lambda:button(w))
	box.addWidget(b)

	b=QtGui.QPushButton("Close Dialog")
	b.pressed.connect(w.close)
	box.addWidget(b)
	w.show()
	return w


if __name__=='__main__':
	import Draft

	#create the Bspline
	p1 = FreeCAD.Vector(0,0,0)
	p2 = FreeCAD.Vector(1,1,0)
	p3 = FreeCAD.Vector(0,2,0)
	p4 = FreeCAD.Vector(-1,1,0)
	Draft.makeBSpline([p1,p2,p3,p4],closed=True)

	obj=App.ActiveDocument.ActiveObject
	w=pointEditor(obj)
	w.show()



def run():
	obj=Gui.Selection.getSelection()[0]
	print obj
	j=pointEditor(obj)
	print j
	
	return j
