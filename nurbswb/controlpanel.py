# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- a basic param controller gui
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import PySide
from PySide import  QtGui,QtCore


def createListWidget(obj=None,propname=None):

	w=QtGui.QWidget()
	box = QtGui.QVBoxLayout()
	w.setLayout(box)

	listWidget = QtGui.QListWidget() 
	listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
	listWidget.sels=[]
	ks={}
	liste=obj.getPropertyByName(propname)
	for l in liste:
		ks[l.Label]=l

	for  k in ks.keys():
		item = QtGui.QListWidgetItem(k)
		listWidget.addItem(item)
		
	def f(*arg):
		print "itemsele cahgned"
		print  (arg,listWidget)
		print listWidget.selectedItems()
		for item in  listWidget.selectedItems():
			print ks[item.text()]

		listWidget.sels= [ ks[item.text()] for item in  listWidget.selectedItems()]

	listWidget.itemSelectionChanged.connect(f)
	box.addWidget(listWidget)
	
	def remove():
		print "remove"
		print listWidget.sels
		ref=obj.getPropertyByName(propname+"Source")
		print "Source",ref.Label
		aa=ref.getPropertyByName(propname)
		bb=[]
		for a in aa:
			if not a in listWidget.sels:
				bb.append(a)
			else:
				print "skip ", a.Label

		setattr(ref,propname,bb)
		setattr(obj,propname,bb)

		obj.Proxy.dialog.hide()
		obj.Proxy.dialog=dialog(obj)

		App.activeDocument().recompute()
		print "Links",ref.Links



	def add():
		print "add"
		print  Gui.Selection.getSelection()
		sels=Gui.Selection.getSelection()
		ref=obj.getPropertyByName(propname+"Source")
		print "Source",ref.Label
		aa=ref.getPropertyByName(propname)
		print "Links orig"
		for a in aa: print a.Label
		for s in sels:
			if s not in aa:
				print a.Label +"not in aa"
				aa.append(s)
		setattr(ref,propname,aa)
		setattr(obj,propname,aa)

		obj.Proxy.dialog.hide()
		obj.Proxy.dialog=dialog(obj)

		App.activeDocument().recompute()


	w.r=QtGui.QPushButton("remove selected items")
	box.addWidget(w.r)
	w.r.pressed.connect(remove)

	w.r=QtGui.QPushButton("add Gui selection")
	box.addWidget(w.r)
	w.r.pressed.connect(add)

	return w





def clear(window):
	window.deleteLater()
	# App.activeDocument().recompute()




def createPropWidget(obj,propname):
	w=QtGui.QWidget()

	box = QtGui.QVBoxLayout()
	box.setAlignment(QtCore.Qt.AlignTop)
	w.setLayout(box)
#	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	ref=obj.getPropertyByName(propname+"Source")
	w.l=QtGui.QLabel(ref.Label+'.'+propname )
	box.addWidget(w.l)

	pt=obj.getTypeIdOfProperty(propname)
	print ("create widget for property ",propname,pt)
	
	if pt=='App::PropertyLinkList':
		w.d=createListWidget(obj,propname)
		box.addWidget(w.d)
		return w


	if obj.getPropertyByName(propname+"Slider"):
		w.d=QtGui.QSlider()
		w.d.setOrientation(QtCore.Qt.Horizontal)
		w.d.setTickPosition(QtGui.QSlider.TicksBelow)
	else:
		w.d=QtGui.QDial()
		w.d.setNotchesVisible(True)


	w.d.setMinimum(obj.getPropertyByName(propname+"Min").Value)
	w.d.setMaximum(obj.getPropertyByName(propname+"Max").Value)
	w.d.setValue(obj.getPropertyByName(propname).Value)
	w.d.setSingleStep(obj.getPropertyByName(propname+"Step"))

	def valueChangedA(val):
		ref=obj.getPropertyByName(propname+"Source")
		print (ref.Label,propname,val)
		setattr(ref,propname,val)
		setattr(obj,propname,val)
		App.activeDocument().recompute()


	# w.d.valueChanged[int].connect(valueChangedA)
	w.d.valueChanged.connect(valueChangedA)
	box.addWidget(w.d)

	return w


def dialogV(obj):
	'''erzeugen dialog vLayout'''

	w=QtGui.QWidget()
	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	for p in obj.props:
		pw=createPropWidget( obj,p)
		box.addWidget(pw)

	w.r=QtGui.QPushButton("close")
	box.addWidget(w.r)
	w.r.pressed.connect(lambda :clear(w))

	w.show()
	return w


def dialog(obj):
	'''erzeuge dialog grid'''

	w=QtGui.QWidget()

	grid = QtGui.QGridLayout()
	grid.setSpacing(10)
	w.setLayout(grid)

	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	bmax=2
	bmax=1
	b=0;l=3
	for i,p in enumerate(obj.props):
		pw=createPropWidget( obj,p)
		grid.addWidget(pw, l, b,)
		b += 1
		if b>bmax: b=0; l+=1

#	w.l=QtGui.QLabel(obj.Label)
#	grid.addWidget(w.l, 1, 0,1,4)

	w.r=QtGui.QPushButton("close")
	grid.addWidget(w.r, 1, 0,1,4)
		
	w.r.pressed.connect(lambda :clear(w))

	w.show()
	return w





class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj


	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None


class ViewProvider:

	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

#-------------------
# contextmenu und double click 

	def setupContextMenu(self, obj, menu):
		action = menu.addAction("Open Editor Dialog ...")
		action.triggered.connect(self.edit)


	def edit(self):
		obj=self.Object.Object
		try: obj.Proxy.dialog.hide()
		except: pass 
		obj.Proxy.dialog=dialog(obj)

	def setEdit(self,vobj,mode=0):
		self.edit()
		return True

	def unsetEdit(self,vobj,mode=0):
		return False

	def doubleClicked(self,vobj):
		self.setEdit(vobj,1)




#-------------------


class ControlPanel(PartFeature):

	def __init__(self, obj):

		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyStringList","props","ZZConfig")
		obj.addProperty("App::PropertyBool","noExecute" ,"ZZConfig")

		ViewProvider(obj.ViewObject)
		self.dialog=None


	def onChanged(proxy,obj, prop):
		if prop in ["noExecute"]: 
			print ("onChanged",prop)
			proxy.dialog=dialog(obj)


	def execute(proxy,obj):
		if obj.noExecute: return
		try: 
			if proxy.lock: return
		except:
			print("except proxy lock")
		proxy.lock=True
		proxy.myexecute(obj)
		proxy.lock=False


	def myexecute(proxy,obj):
		try: 
			proxy.dialog
		except: 
			proxy.dialog=dialog(obj)


	def refresh(proxy):
		print "aktualisiere attribute"
		obj=proxy.Object
		for propname in obj.props:
			print obj
			# ref holen
			pp=obj.getPropertyByName(propname)
			ref=obj.getPropertyByName(propname+"Source")
			print "Source",ref.Label
			aa=ref.getPropertyByName(propname)
			print "value",aa
			setattr(obj,propname,aa)



	def addTarget(self,obj,propname,maxV=None,minV=None):
		gn=obj.Label +"." + propname
		pp=obj.getPropertyByName(propname)

		self.Object.props= self.Object.props +[propname]

		pt=obj.getTypeIdOfProperty(propname)
		print pt
		# App::PropertyAngle
		# App::PropertyLength
		if pt=='App::PropertyLinkList':
			self.Object.addProperty(pt,propname,gn,)
			self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
			setattr(self.Object,propname+"Source",obj)
			setattr(self.Object,propname,pp)
			return


		self.Object.addProperty(pt,propname,gn,"Commnetar")
		self.Object.addProperty(pt,propname+"Min",gn)
		self.Object.addProperty(pt,propname+"Max",gn)
		self.Object.addProperty("App::PropertyFloat",propname+"Step",gn)
		self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
		self.Object.addProperty("App::PropertyBool",propname+"Slider",gn)


		setattr(self.Object,propname+"Source",obj)
		try:
			setattr(self.Object,propname,pp.Value)
			#st=0.01*pp.Value
			st=1
			
			if maxV==None: maxV=pp.Value+20
			setattr(self.Object,propname+"Max",maxV)
			#m=pp.Value-20*st
			
			if minV==None: minV=max(0,pp.Value-20)
			setattr(self.Object,propname+"Min",minV)
			setattr(self.Object,propname+"Step",st)
		except:
			pass

		try: self.dialog.hide()
		except: print "no dialog to hide"
		try: self.dialog=dialog(obj);print "dialog created"
		except: print "cannot create dialog"


def run():

	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyMonitor")
	ControlPanel(a)





if __name__ == '__main__':

	#-- create test infrastructure
	b=App.ActiveDocument.addObject("Part::Box","Box")
	c=App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	co=App.ActiveDocument.addObject("Part::Cone","Cone")

	cp=App.activeDocument().addObject("Part::Compound","Compound")
	cp.Links = [c,co]

#	fu=App.activeDocument().addObject("Part::MultiFuse","Fusion")
#	fu.Shapes = [b,co]

	cm=App.activeDocument().addObject("Part::MultiCommon","Common")
	cm.Shapes = [b,co]

	for k in  [b,c,co,cp]:
		k.ViewObject.Transparency=70

	App.ActiveDocument.recompute()

	#-------------------------------
	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyControlPanel")
	m=ControlPanel(a)
	#-----------------------------

	#-- add some parameters to control
	m.addTarget(c,"Angle",maxV=360,minV=0)

	m.addTarget(c,"Radius")
	m.addTarget(co,"Radius1")
	m.addTarget(co,"Radius2")
	

	m.addTarget(co,"Height")
	m.addTarget(b,'Length')

	m.addTarget(cp,'Links')
	m.addTarget(cm,'Shapes')

	m.Object.Radius2Slider = True

	App.activeDocument().recompute()

	#start the dialog
	m.Object.ViewObject.Proxy.edit()

