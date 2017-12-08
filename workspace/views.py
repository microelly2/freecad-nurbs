import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtGui
import Part,Mesh,Draft

import numpy as np



from PySide import QtCore

from pivy import coin
import numpy as np


# obj=App.ActiveDocument.Sketch001

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
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)


	view=v.getViewer(2)

	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	t.rotation.setValue(coin.SbVec3f((0,1,0)),-np.pi/2)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)

	view.setSceneGraph(marker)


	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	t.rotation.setValue(coin.SbVec3f((1,1,1)),-np.pi/3)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)
	view=v.getViewer(3)
	view.setSceneGraph(marker)

	v.fitAll()
	#v.viewAxometric()


	rm=view.getSoRenderManager()
	cam=rm.getCamera()
#	cam.pointAt(coin.SbVec3f(10,10,10))
#	cam.scaleHeight(3)
	FreeCAD.cam=cam

	# rm.setCamera(cam)

	Gui.Selection.clearSelection()


	bg=rm.getBackgroundColor()




def updatencontenth2(viewer,obja,objb):
	v=viewer
	view=v.getViewer(0)
	node= obja.ViewObject.RootNode
	view.setSceneGraph(node)

	view=v.getViewer(1)
	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)
	view.setSceneGraph(marker)


	view=v.getViewer(2)
	node=objb.ViewObject.RootNode

	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)

	view.setSceneGraph(marker)


	marker = coin.SoSeparator()
	t = coin.SoTransform()
	t.translation.setValue((0,-2,0))
	t.center.setValue((0,2,0))
	# t.rotation.setValue(coin.SbVec3f((1,0,1)),-np.pi/2)
	c = coin.SoCone()
	c.height.setValue(4)
	marker.addChild(t)
	marker.addChild(node)
	view=v.getViewer(3)
	view.setSceneGraph(marker)

	v.fitAll()
	#v.viewAxometric()


	rm=view.getSoRenderManager()
	cam=rm.getCamera()
#	cam.pointAt(coin.SbVec3f(10,10,10))
#	cam.scaleHeight(3)
	FreeCAD.cam=cam

	# rm.setCamera(cam)


	bg=rm.getBackgroundColor()

	# rm.setBackgroundColor( coin.SbColor4f(10,0,10,10))






def createh2AAA():

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

#	try: FreeCAD.view.close()
#	except: pass

	obja=Gui.Selection.getSelection()[0]
	objb=Gui.Selection.getSelection()[1]
	title=obja.Label+objb.Label
	print title
	v=Gui.createViewer(4,title)
	FreeCAD.view=v
	FreeCAD.viewLabel=title
	updatencontenth2(v,obja,objb)



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

	 
	print v
	print "---------------"
	# das quad view fenste
	print w2.children()
	v=w2.children()[3]

	# der spliter
	print v.children()
	sp=v.children()[2]

	spa=sp.children()[0]
	spa.setSizes([10,0])

#	spa.setGeometry(400,500,100,240)
	spa=sp.children()[1]
	spa.setSizes([10,0])

	print "done"
	# pos lang, hoch
#	spa.setGeometry(0,0,800,440)

	sh=sp.children()[2]

	spa.setSizes([0,100])
	spa.setSizes([10,10])
	spa.setSizes([10,00])
	spa.hide()
	spa.show()

	#update content
	#updatecontentview(FreeCAD.view) 

	Gui.Selection.clearSelection()




