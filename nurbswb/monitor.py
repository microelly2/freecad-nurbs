# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- a basic monitor object
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

def run(window):

	anz=int(window.anz.text())
	print anz

	print window.r.isChecked()

	window.r.hide()
	window.hide()


def dialog():

	w=QtGui.QWidget()

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	l=QtGui.QLabel("Anzahl" )
	w.l=l
	box.addWidget(l)

	w.mina = QtGui.QLabel("Anzahl" )
	w.mina.setText('3')
	box.addWidget(w.mina)

	w.anz = QtGui.QLabel("Anzahl" )
	w.anz.setText('13')
	box.addWidget(w.anz)

	w.maxa = QtGui.QLabel("Anzahl" )
	w.maxa.setText('3')
	box.addWidget(w.maxa)


#	w.random=QtGui.QCheckBox("Zufall")
#	box.addWidget(w.random)

#	w.r=QtGui.QPushButton("run")
#	box.addWidget(w.r)
#	w.r.pressed.connect(lambda :run(w))

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



class Monitor(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyLink","source","")
		# for a indirect dependency a 2nd source to trigger
		obj.addProperty("App::PropertyLink","source2","")
		obj.addProperty("App::PropertyFloat","val","")
		obj.addProperty("App::PropertyFloat","minVal","")
		obj.addProperty("App::PropertyFloat","maxVal","")
		obj.addProperty("App::PropertyBool","noExecute" ,"Base")
		
		ViewProvider(obj.ViewObject)

	def onDocumentRestored(self, fp):
		print "onDocumentRestored "
		print fp.Label


	def onChanged(self, fp, prop):
		if prop in ["Shape", 'Spreadsheet']: return
		print ("onChanged",prop)


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
		try: proxy.dialog
		except: 
			proxy.dialog=dialog()
		try:
			proxy.dialog.l.setText("Curve length for " + str(obj.source.Label))
		except:
			pass
		proxy.dialog.mina.setText("MIN: " +str(obj.minVal))
		proxy.dialog.maxa.setText("MAX: " +str(obj.maxVal))
		proxy.dialog.show()
		mm=20
		if obj.source <> None:
#			try:
				print obj.source.Label
				print ("Value and interval:", round(obj.source.Shape.Edge1.Length,1),obj.minVal,obj.maxVal)
				obj.source.ViewObject.LineColor=(1.0,1.0,1.0)
				if obj.source.Shape.Edge1.Length<obj.minVal:
					obj.source.ViewObject.LineColor=(0.0,.0,1.0)
				elif obj.source.Shape.Edge1.Length>obj.minVal and obj.source.Shape.Edge1.Length<obj.minVal+mm:
					j=1-(obj.minVal+mm-obj.source.Shape.Edge1.Length)/mm
					print j
					j=j*0.5
					obj.source.ViewObject.LineColor=(0.,1.0,.0)
				elif obj.source.Shape.Edge1.Length<obj.maxVal and obj.source.Shape.Edge1.Length>obj.maxVal-mm:
					j=(obj.maxVal-obj.source.Shape.Edge1.Length)/mm
					print j
					j=j*0.5
					obj.source.ViewObject.LineColor=(.0,1.0,0)
				elif obj.source.Shape.Edge1.Length>obj.maxVal:
					obj.source.ViewObject.LineColor=(1.0,0.0,.0)
				obj.val=obj.source.Shape.Edge1.Length
				print "huhu"
				proxy.dialog.anz.setText("VALUE: " + str(obj.val))
#			except:
				print "kann nichts machen"


def run():
	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyMonitor")
	m=Monitor(a)




if __name__ == '__main__':


	import Draft

	points = [
		FreeCAD.Vector(41.6618804932,-29.8381633759,0.0),FreeCAD.Vector(42.888874054,27.8303642273,0.0),
		FreeCAD.Vector(-20.4684200287,39.654083252,0.0),FreeCAD.Vector(-18.1259880066,-19.6876106262,0.0),
		FreeCAD.Vector(-230.109481812,-79.8339004517,0.0),FreeCAD.Vector(-201.932830811,105.248153687,0.0),
		FreeCAD.Vector(77.6240005493,163.258956909,0.0),FreeCAD.Vector(-91.4360580444,60.4969787598,0.0),
		FreeCAD.Vector(63.25938797,88.1211624146,0.0),FreeCAD.Vector(220.717285156,27.9004211426,0.0),
		FreeCAD.Vector(203.590301514,-89.7786178589,0.0),FreeCAD.Vector(153.866744995,14.088344574,0.0),
		FreeCAD.Vector(112.982902527,-46.1323928833,0.0)
	]

	spline = Draft.makeBSpline(points,closed=False,face=True,support=None)


	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyMonitor")
	m=Monitor(a)

	try:
		import nurbswb
		import nurbswb.createsketchspline
		reload(nurbswb.createsketchspline)
		nurbswb.createsketchspline.run()
		spline=App.ActiveDocument.ActiveObject
	except:
		spline = Draft.makeBSpline(points,closed=False,face=True,support=None)

	spline.ViewObject.LineWidth = 9.00

	a.source=spline
	a.minVal= spline.Shape.Length*0.95
	a.maxVal= spline.Shape.Length*1.05



