import sys
import numpy as np


from PySide import QtGui

import FreeCAD,FreeCADGui
App=FreeCAD

import nurbswb.needle
import nurbswb.needle_models
reload(nurbswb.needle_models)


def getdata(index):
	ri=index.row()-2
	c=index.column()
	ci=0

	if c == 0: # command fuer curve
		sel="ccmd"
		return sel,ci,ri,index.data()

	if c == 5: # command fuer curve
		sel="bcmd"
		return sel,ci,ri,index.data()

	if c in range(1,4):
		sel="rib"
		ci=c-1
	elif c in range(6,9):
		sel="bb"
		ci=c-6
	else:
		sel=None
		ci=-1

	return sel,ci,ri,index.data()

def initmodel():
	App.ActiveDocument.MyNeedle.Proxy.lock=False
	App.ActiveDocument.MyNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelBanana)
	#App.ActiveDocument.MyNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelEd4)


def addRib(dialog):
	# read 
	(curve,bb,scaler,twister)=App.ActiveDocument.MyNeedle.Proxy.Model()

	# modifications 
	i=dialog.pos

	t=(bb[i]+bb[i+1])*0.5
	b=np.concatenate([bb[0:i+1],[t],bb[i+1:]])
	bb=b
	t=(scaler[i]+scaler[i+1])*0.5
	b=np.concatenate([scaler[0:i+1],[t],scaler[i+1:]])
	scaler=b
	t=(twister[i]+twister[i+1])*0.5
	b=np.concatenate([twister[0:i+1],[t],twister[i+1:]])
	twister=b

	# write back
	App.ActiveDocument.MyNeedle.Proxy.lock=False
	App.ActiveDocument.MyNeedle.Proxy.setModel(curve,bb,scaler,twister)
	dialog.obj.Proxy.showRib(i)
	dialog.close()


def CaddRib(obj,i):
	# read 
	(curve,bb,scaler,twister)=obj.Proxy.Model()

	t=(bb[i]+bb[i+1])*0.5
	b=np.concatenate([bb[0:i+1],[t],bb[i+1:]])
	bb=b
	t=(scaler[i]+scaler[i+1])*0.5
	b=np.concatenate([scaler[0:i+1],[t],scaler[i+1:]])
	scaler=b
	t=(twister[i]+twister[i+1])*0.5
	b=np.concatenate([twister[0:i+1],[t],twister[i+1:]])
	twister=b

	# write back
	obj.Proxy.lock=False
	obj.Proxy.setModel(curve,bb,scaler,twister)
	obj.Proxy.showRib(i)


def addMeridian(dialog):
	# read 
	(curve,bb,scaler,twister)=App.ActiveDocument.MyNeedle.Proxy.Model()

	# modifications 
	i=dialog.pos
	t=(curve[i]+curve[i+1])*0.5
	c=np.concatenate([curve[0:i+1],[t],curve[i+1:]])
	curve=c

	# write back
	App.ActiveDocument.MyNeedle.Proxy.lock=False
	App.ActiveDocument.MyNeedle.Proxy.setModel(curve,bb,scaler,twister)
	dialog.obj.Proxy.showMeridian(i)
	dialog.close()


def CaddMeridian(obj,i):
	(curve,bb,scaler,twister)=obj.Proxy.Model()
	t=(curve[i]+curve[i+1])*0.5
	c=np.concatenate([curve[0:i+1],[t],curve[i+1:]])
	curve=c
	obj.Proxy.lock=False
	obj.Proxy.setModel(curve,bb,scaler,twister)
	obj.Proxy.showMeridian(i)


def delMeridian(dialog):
	# read 
	(curve,bb,scaler,twister)=App.ActiveDocument.MyNeedle.Proxy.Model()

	if curve.shape[0]<5:
		print "zu wenig Punkte "
		return

	# modifications 
	i=dialog.pos
	c=np.concatenate([curve[0:i],curve[i+1:]])
	curve=c

	# write back
	App.ActiveDocument.MyNeedle.Proxy.lock=False
	App.ActiveDocument.MyNeedle.Proxy.setModel(curve,bb,scaler,twister)
	dialog.obj.Proxy.showMeridian(i)
	dialog.close()

def CdelMeridian(obj,i):
	# read 
	(curve,bb,scaler,twister)=obj.Proxy.Model()

	if curve.shape[0]<5:
		print "zu wenig Punkte "
		return

	# modifications 
	c=np.concatenate([curve[0:i],curve[i+1:]])
	curve=c

	# write back
	obj.Proxy.lock=False
	obj.Proxy.setModel(curve,bb,scaler,twister)
	obj.Proxy.showMeridian(i-2)

def CdelRib(obj,i):
	# read 
	(curve,bb,scaler,twister)=obj.Proxy.Model()

	i = i
	
	if bb.shape[0]<5:
		print "zu wenig Punkte "
		return

	# modifications 
	b=np.concatenate([bb[0:i],bb[i+1:]])
	bb=b
	
	s=np.concatenate([scaler[0:i],scaler[i+1:]])
	scaler=s

	t=np.concatenate([twister[0:i],twister[i+1:]])
	twister=t
	
	

	# write back
	obj.Proxy.lock=False
	obj.Proxy.setModel(curve,bb,scaler,twister)
	obj.Proxy.showRib(i-2)


class RibEditor(QtGui.QWidget):

	def __init__(self,obj,title="undefined",pos=-1):

		super(RibEditor, self).__init__()
		self.title=title
		self.pos=pos
		self.obj=obj
		print self.obj.Spreadsheet.Label
		self.initUI()

	def initUI(self):      

		self.btn = QtGui.QPushButton('Init Model', self)
		self.btn.move(20, 20)
		self.btn.clicked.connect(initmodel)

#		self.btn = QtGui.QPushButton('Add Point', self)
#		self.btn.move(20, 50)
#		self.btn.clicked.connect(self.showDialog)

		self.btn = QtGui.QPushButton('Delete Rib', self)
		self.btn.move(20, 50)
		f=lambda:delRib(self)
		self.btn.clicked.connect(f)
		
		self.btn = QtGui.QPushButton('Add Rib', self)
		self.btn.move(20, 80)
		f=lambda:addRib(self)
		
		self.btn.clicked.connect(f)


		self.btn2 = QtGui.QPushButton('End', self)
		self.btn2.move(20, 110)
		self.btn2.clicked.connect(self.close)


		self.le = QtGui.QLineEdit(self)
		self.le.setText("pos "+ str(self.pos))
		self.le.move(150, 22)

		self.setGeometry(300, 300, 290, 150)
		self.setWindowTitle(self.title)
		self.show()

	def showDialog(self):
		text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
			'Enter your name:')
		
		if ok:
			self.le.setText(str(text))

class BackboneEditor(QtGui.QWidget):

	def __init__(self,obj,title="undefined",pos=-1):

		super(BackboneEditor, self).__init__()
		self.title=title
		self.pos=pos
		self.obj=obj
		print self.obj.Spreadsheet.Label
		self.initUI()

	def initUI(self):      

		self.btn = QtGui.QPushButton('Init Model', self)
		self.btn.move(20, 20)
		self.btn.clicked.connect(initmodel)

#		self.btn = QtGui.QPushButton('Add Point', self)
#		self.btn.move(20, 50)
#		self.btn.clicked.connect(self.showDialog)

		self.btn = QtGui.QPushButton('Delete Meridian', self)
		self.btn.move(20, 50)
		self.btn.clicked.connect(lambda:delMeridian(self))

		self.btn = QtGui.QPushButton('Add Meridian', self)
		self.btn.move(20, 80)
		self.btn.clicked.connect(lambda:addMeridian(self))

		self.btn2 = QtGui.QPushButton('End', self)
		self.btn2.move(20, 110)
		self.btn2.clicked.connect(self.close)

		self.le = QtGui.QLineEdit(self)
		self.le.setText("pos "+ str(self.pos))
		self.le.move(150, 22)

		self.setGeometry(50, 30, 290, 150)
		self.setWindowTitle(self.title)
		self.show()

	def showDialog(self):
		text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
			'Enter your name:')
		
		if ok:
			self.le.setText(str(text))



def pressed(index,obj):
	sel,ci,ri,data = getdata(index)
	if sel == "bcmd":
		FreeCAD.t=RibEditor(obj,"Rib Editor",ri)
	elif  sel == "ccmd":
		FreeCAD.t=BackboneEditor(obj,"Backbone Editor",ri)
	else:
		pass


def cmdAdd():
	''' add some curves to selections '''

	s=FreeCADGui.Selection.getSelectionEx()[0]

	s.Object.Label
	print s.Object.Name
	print s.SubElementNames


	needle=s.Object.InList[0]
	needle.Label

	for sen in s.SubElementNames:
		print sen[4:]
		if s.Object.Name[0:4]=='Ribs':
			print "ribs ..."
			CaddRib(needle,int(sen[4:]))
		if s.Object.Name[0:9]=='Meridians':
			print "meridians ..."
			CaddMeridian(needle,int(sen[4:]))



def cmdDel():
	''' add some curves to selections '''

	s=FreeCADGui.Selection.getSelectionEx()[0]

	s.Object.Label
	print s.Object.Name
	print s.SubElementNames


	needle=s.Object.InList[0]
	needle.Label

	for sen in s.SubElementNames:
		print sen[4:]
		if s.Object.Name[0:4]=='Ribs':
			print "ribs ..."
			CdelRib(needle,int(sen[4:]))
		if s.Object.Name[0:9]=='Meridians':
			print "meridians ..."
			CdelMeridian(needle,int(sen[4:]))


