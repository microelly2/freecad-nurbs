# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- special view support
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtCore
from pivy import coin
import numpy as np



def createquadview():

	try: FreeCAD.view.close()
	except: pass

	obj=Gui.Selection.getSelection()[0]
	title=obj.Label
	print title
	v=Gui.createViewer(4,title)
	FreeCAD.view=v
	FreeCAD.viewLabel=title
	updatencontent(v,obj)


def updatencontent(viewer,obj):

	v=viewer

	view=v.getViewer(0)
	node= obj.ViewObject.RootNode
	view.setSceneGraph(node)

	view=v.getViewer(1)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)

	view=v.getViewer(2)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.rotation.setValue(coin.SbVec3f((0,1,0)),-np.pi/2)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)

	view=v.getViewer(3)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.rotation.setValue(coin.SbVec3f((1,1,1)),-np.pi/3)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)

	v.fitAll()

	rm=view.getSoRenderManager()
	cam=rm.getCamera()
#	cam.pointAt(coin.SbVec3f(10,10,10))
#	cam.scaleHeight(3)

	Gui.Selection.clearSelection()


def updatencontenth2(viewer,obja,objb):

	v=viewer

	node= obja.ViewObject.RootNode

	view=v.getViewer(0)
	view.setSceneGraph(node)

	view=v.getViewer(1)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)

	node=objb.ViewObject.RootNode

	view=v.getViewer(2)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)

	view=v.getViewer(3)
	marker = coin.SoSeparator()
	marker.addChild(node)
	view.setSceneGraph(marker)

	v.fitAll()


def createh2_firstVersion():

	title=FreeCAD.viewLabel
	mw=FreeCADGui.getMainWindow()
	mdiarea=mw.findChild(QtGui.QMdiArea)

	sws=mdiarea.subWindowList()

	print mdiarea.geometry()
	a=mdiarea.geometry()
	l=a.left()
	r=a.right()
	t=a.top()
	b=a.bottom()
	h=b-t
	ls=len(sws)
	hh=h//ls-ls

	print "windows ..."
	for i,w2 in enumerate(sws):
		print str(w2.windowTitle())
		if  w2.windowTitle()==title:
			break
		print ("size",w2.size())
		# w2.setGeometry(0,i*hh,r-l,50)

	 

	# das quad view fenste
	v=w2.children()[3]

	# der spliter
	sp=v.children()[2]

	spa=sp.children()[0]
	spa.setSizes([0,100])

#	spa.setGeometry(400,500,100,240)
	spa=sp.children()[1]
	spa.setSizes([0,100])
	# pos lang, hoch
#	spa.setGeometry(0,0,800,440)

	sh=sp.children()[2]

	#spa.setSizes([0,100])
	#spa.setSizes([10,10])
#	spa.setSizes([10,00])

	#update content
	#updatecontentview(FreeCAD.view) 
	


def createh2():

	obja=Gui.Selection.getSelection()[0]
	objb=Gui.Selection.getSelection()[1]

	title=obja.Label+" "+objb.Label

	v=Gui.createViewer(4,title)

	mw=FreeCADGui.getMainWindow()
	mdiarea=mw.findChild(QtGui.QMdiArea)

	sws=mdiarea.subWindowList()

	print "windows ..."
	for i,w2 in enumerate(sws):
		print str(w2.windowTitle())
		if  w2.windowTitle()==title:

			print w2.children()
			va=w2.children()[3]

			print va.children()
			sp=va.children()[2]

			spa=sp.children()[0]
			spa.setSizes([10,0])

			spa=sp.children()[1]
			spa.setSizes([10,0])

			Gui.Selection.clearSelection()
			updatencontenth2(v,obja,objb)


