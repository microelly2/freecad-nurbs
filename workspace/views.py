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


from PySide import QtCore,QtGui
from pivy import coin
import numpy as np


'''
v=Gui.createViewer(2,title)

view=v.getViewer(1)
rm=view.getSoRenderManager()
c=rm.getCamera()

c.orientation
c.orientation=FreeCAD.Rotation(FreeCAD.Vector(1,1,1),15).Q


'''


Gui=FreeCADGui
import Part

class PartFeature:
	''' base class for part feature '''
	def __init__(self, obj):
		obj.Proxy = self

# grundmethoden zum sichern

	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

class ViewProvider:
	''' view provider class for Tripod'''
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj






class QuadView(PartFeature):
	def __init__(self, obj,label=None):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyVector","A Axis","V00")
		obj.addProperty("App::PropertyFloat","A Angle","V00")
#		obj.addProperty("App::PropertyFloat","A Zoom","00")
#		obj.A_Zoom=0
		obj.A_Axis=FreeCAD.Vector(1,0,0)
		obj.A_Angle=90

		obj.addProperty("App::PropertyVector","B Axis","V01")
		obj.addProperty("App::PropertyFloat","B Angle","V01")
		obj.B_Axis=FreeCAD.Vector(1,1,1)
		obj.B_Angle=120

		obj.addProperty("App::PropertyVector","C Axis","V10")
		obj.addProperty("App::PropertyFloat","C Angle","V10")

		obj.addProperty("App::PropertyVector","D Axis","V11")
		obj.addProperty("App::PropertyFloat","D Angle","V11")
#		obj.D_Axis=FreeCAD.Vector(0,1,1)
		obj.D_Axis=FreeCAD.Vector(1,0,1)
		obj.D_Angle=45
		# oder 60 , 30

		obj.addProperty("App::PropertyBool","DisplayMode","Render")
		obj.addProperty("App::PropertyBool","fitAll","Render")
		if label <>None:
			obj.Label=label
		

	def onChanged(self, fp, prop):

		if prop=="Shape": return

		# abbruch
		try: self.v
		except: return

		c=self.v.getViewer(0).getSoRenderManager().getCamera()

		if prop=="DisplayMode":
			updatencontent(self.v,self.objs,fp)
			

		if prop.startswith("A_"):
			c.orientation=FreeCAD.Rotation(fp.A_Axis,fp.A_Angle).Q
#			if fp.A_Zoom<0:
#				c.scaleHeight(0.9)
#			if fp.A_Zoom>0:
#				c.scaleHeight(1.0/0.9)
			
		if prop.startswith("B_"):
			c=self.v.getViewer(1).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.B_Axis,fp.B_Angle).Q
		if prop.startswith("C_"):
			c=self.v.getViewer(2).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.C_Axis,fp.C_Angle).Q
		if prop.startswith("D_"):
			c=self.v.getViewer(3).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.D_Axis,fp.D_Angle).Q
#			c.pointAt(coin.SbVec3f(fp.D_Axis))

		if fp.fitAll:
			self.v.fitAll()
		print prop 







#---------------------------



def createquadview():

	try: FreeCAD.view.close()
	except: pass

	obj=Gui.Selection.getSelection()[0]
	objs=Gui.Selection.getSelection()

	title=obj.Label

	if len(objs)<>1:
		labels=[obj.Label for obj in objs]
		title=', '.join(labels)

	v=Gui.createViewer(4,title)
#	FreeCAD.view=v
	try: FreeCAD.views['title']=v
	except:
		FreeCAD.views={}
		FreeCAD.views['title']=v

	FreeCAD.viewLabel=title
	
	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","MyQuadView")
	QuadView(a,"QuadView for "+ title )
	ViewProvider(a.ViewObject)
	updatencontent(v,objs,a)
	a.Proxy.v=v
	a.Proxy.objs=objs
#	for y in ['A_','B_','C_','D_']:
#		a.Proxy.onChanged(a, y)

#	v.fitAll()

'''
The Gui.createViewer-Object has the method fitAll, viewLeft ...
I think its better to have these methods for each view and not only as global method
So it is possible to display  in each window another view direction


view=v.getViewer(2)
rm=view.getSoRenderManager()
c=rm.getCamera()

c has pointAt, scaleHeight


but I look for position, orientation setters an getters.
'''

def updatencontent(viewer,objs,fp):


	obj=objs[0]
	v=viewer

	view=v.getViewer(0)

	'''
	node= obj.ViewObject.RootNode

	if fp.DisplayMode:
		nodeA=node.copy()
		clds=nodeA.getChildren()
		s2=clds[2]
		s2.whichChild.setValue(0)
	else:
		nodeA=node

	view.setSceneGraph(nodeA)
	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.A_Axis,fp.A_Angle).Q
	'''

	#--------------------
	marker = coin.SoSeparator()
	for objx in objs:
		print "run ",objx.Label
		node= objx.ViewObject.RootNode

		if fp.DisplayMode:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(0)
		else:
			nodeA=node

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.A_Axis,fp.A_Angle).Q
	#------------------------------------

	view=v.getViewer(1)

	#--------------------
	marker = coin.SoSeparator()
	for objx in objs:
		print "run ",objx.Label
		node= objx.ViewObject.RootNode

		if fp.DisplayMode:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(1)
		else:
			nodeA=node

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.B_Axis,fp.B_Angle).Q
	#------------------------------------

	'''
	marker = coin.SoSeparator()
	t = coin.SoTransform()
#	t.rotation.setValue(coin.SbVec3f((1,0,0)),-np.pi/2)
	marker.addChild(t)

	if fp.DisplayMode:
		nodeA=node.copy()
		clds=nodeA.getChildren()
		s2=clds[2]
		s2.whichChild.setValue(1)
	else:
		nodeA=node

	marker.addChild(nodeA)
	view.setSceneGraph(marker)
#	view.getSoRenderManager().setCamera(coin.SoOrthographicCamera())
	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.B_Axis,fp.B_Angle).Q
	'''

	view=v.getViewer(2)
	#--------------------
	marker = coin.SoSeparator()
	for objx in objs:
		print "run ",objx.Label
		node= objx.ViewObject.RootNode

		if fp.DisplayMode:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(2)
		else:
			nodeA=node

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.C_Axis,fp.C_Angle).Q
	#------------------------------------


	'''
	marker = coin.SoSeparator()
	t = coin.SoTransform()
#	t.rotation.setValue(coin.SbVec3f((0,1,0)),-np.pi/2)
	marker.addChild(t)

	if fp.DisplayMode:
		nodeA=node.copy()
		clds=nodeA.getChildren()
		s2=clds[2]
		s2.whichChild.setValue(3)
	else:
		nodeA=node

	marker.addChild(nodeA)
	view.setSceneGraph(marker)
	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.C_Axis,fp.C_Angle).Q
	'''
	

	view=v.getViewer(3)
	#--------------------
	marker = coin.SoSeparator()
	for objx in objs:
		print "run ",objx.Label
		node= objx.ViewObject.RootNode

		if fp.DisplayMode:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(3)
		else:
			nodeA=node

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.D_Axis,fp.D_Angle).Q
	#------------------------------------


	'''
	marker = coin.SoSeparator()
	t = coin.SoTransform()
#	t.rotation.setValue(coin.SbVec3f((1,1,1)),-np.pi/3)
	marker.addChild(t)

	if fp.DisplayMode:
		nodeA=node.copy()
		clds=nodeA.getChildren()
		s2=clds[2]
		s2.whichChild.setValue(2)
	else:
		nodeA=node

	marker.addChild(nodeA)
	view.setSceneGraph(marker)
	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.D_Axis,fp.D_Angle).Q
	'''


	v.fitAll()


#	rm=view.getSoRenderManager()
#	cam=rm.getCamera()
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
	v.viewTop()


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

	v.viewLeft()

