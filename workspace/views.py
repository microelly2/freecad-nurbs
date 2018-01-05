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
v=Gui.createViewer(2,"title")

view=v.getViewer(1)
rm=view.getSoRenderManager()
c=rm.getCamera()

c.orientation
c.orientation=FreeCAD.Rotation(FreeCAD.Vector(1,1,1),15).Q

c.pointAt(coin.SbVec3f(10,10,10))
c.scaleHeight(3)

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

	def onDelete(self, obj, subelements):
		print "on Delete Quadview"
		print obj
		print subelements
		obj.Object.Proxy.v.close()
		return True

	def onChanged(self, obj, prop):
			print "onchange",prop
			if prop=="Visibility" and not obj.Visibility:
				obj.Object.Proxy.v.close()
			if prop=="Visibility" and obj.Visibility:
				fp=obj.Object
				title=fp.Label
				v=Gui.createViewer(4,title)
				updatencontent(v,fp.objs,fp)
				fp.Proxy.v=v





class QuadView(PartFeature):
	def __init__(self, obj,label=None):
		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyVector","A Axis","V00")
		obj.addProperty("App::PropertyFloat","A Angle","V00")
		obj.addProperty("App::PropertyInteger","A DisplayMode","V00")
		obj.addProperty("App::PropertyInteger","A OrientationMode","V00")
		
#		obj.addProperty("App::PropertyFloat","A Zoom","00")
#		obj.A_Zoom=0
		obj.A_Axis=FreeCAD.Vector(1,0,0)
		obj.A_Angle=90

		obj.addProperty("App::PropertyVector","B Axis","V01")
		obj.addProperty("App::PropertyFloat","B Angle","V01")
		obj.addProperty("App::PropertyInteger","B DisplayMode","V01")
		obj.addProperty("App::PropertyInteger","B OrientationMode","V01")

		obj.B_Axis=FreeCAD.Vector(1,1,1)
		obj.B_Angle=120

		obj.addProperty("App::PropertyVector","C Axis","V10")
		obj.addProperty("App::PropertyFloat","C Angle","V10")
		obj.addProperty("App::PropertyInteger","C DisplayMode","V10")
		obj.addProperty("App::PropertyInteger","C OrientationMode","V10")


		obj.addProperty("App::PropertyVector","D Axis","V11")
		obj.addProperty("App::PropertyFloat","D Angle","V11")
		obj.addProperty("App::PropertyInteger","D DisplayMode","V11")
		obj.addProperty("App::PropertyInteger","D OrientationMode","V11")

#		obj.D_Axis=FreeCAD.Vector(0,1,1)
		obj.D_Axis=FreeCAD.Vector(1,0,1)
		obj.D_Angle=45

		# oder 60 , 30

		obj.addProperty("App::PropertyBool","DisplayMode","Render")
		obj.addProperty("App::PropertyBool","fitAll","Render")

		obj.addProperty("App::PropertyLinkList","objs","Render")

		if label <> None:
			obj.Label = label


	def onChanged(self, fp, prop):

		print ("on changed .....",fp.Label,prop)
		if not fp.ViewObject.Visibility: return

		try: self.v
		except: return

		AxisAngle=[
				(FreeCAD.Vector(1,1,1),120),
				(FreeCAD.Vector(1,1,1),-120),
				
				(FreeCAD.Vector(1,0,1),45),
				(FreeCAD.Vector(1,0,1),60),
				(FreeCAD.Vector(1,0,1),30),
				
				(FreeCAD.Vector(1,0,0),90),
				(FreeCAD.Vector(1,0,0),-90),
				
				(FreeCAD.Vector(-1,0,0),90),
				(FreeCAD.Vector(-1,0,0),-90),
				
			]



		if prop=="Shape": 
			# updatencontent(self.v,fp.objs,fp,False,False)
			dpms=[fp.A_DisplayMode,fp.B_DisplayMode,fp.C_DisplayMode,fp.D_DisplayMode]
			vals=[fp.A_OrientationMode,fp.B_OrientationMode,fp.C_OrientationMode,fp.D_OrientationMode]
			for ix in range(4):
				objs=fp.objs
				view=self.v.getViewer(ix)
				val=vals[ix]
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

					if fp.A_DisplayMode==0:
						nodeA=node
					else:
						nodeA=node.copy()
						clds=nodeA.getChildren()
						s2=clds[2]
						s2.whichChild.setValue(dpms[ix])

					marker.addChild(nodeA)

				c=view.getSoRenderManager().getCamera()
				if val <>0:
					c.orientation=FreeCAD.Rotation(	AxisAngle[val-1][0],AxisAngle[val-1][1]).Q

				sg=view.getSceneGraph()
				sg.removeChild(0)
				sg.addChild(marker)






			return



		if prop.endswith("DisplayMode"):
			w=getattr(fp,prop)
			if w<0: setattr(fp,prop,0)
			if w>3: setattr(fp,prop,3)
			updatencontent(self.v,fp.objs,fp,False)
			return

		if prop.endswith("OrientationMode"):
			val=getattr(fp,prop)
			if val>=len(AxisAngle)or val<0: setattr(fp,prop,val%len(AxisAngle))
			val=getattr(fp,prop)
			if val<>0:
				if prop=="A_OrientationMode":
					fp.A_Axis=AxisAngle[val-1][0]
					fp.A_Angle=AxisAngle[val-1][1]
				if prop=="B_OrientationMode":
					fp.B_Axis=AxisAngle[val-1][0]
					fp.B_Angle=AxisAngle[val-1][1]
				if prop=="C_OrientationMode":
					fp.C_Axis=AxisAngle[val-1][0]
					fp.C_Angle=AxisAngle[val-1][1]
				if prop=="D_OrientationMode":
					fp.D_Axis=AxisAngle[val-1][0]
					fp.D_Angle=AxisAngle[val-1][1]
			return


		if prop.startswith("A_"):
			c=self.v.getViewer(0).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.A_Axis,fp.A_Angle).Q
#			if fp.A_Zoom<0:
#				c.scaleHeight(0.9)
#			if fp.A_Zoom>0:
#				c.scaleHeight(1.0/0.9)
			view=self.v.getViewer(0)
			reg=view.getSoRenderManager().getViewportRegion()
			marker=view.getSoRenderManager().getSceneGraph()
			c.viewAll(marker,reg)

		if prop.startswith("B_"):
			c=self.v.getViewer(1).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.B_Axis,fp.B_Angle).Q

			view=self.v.getViewer(1)
			reg=view.getSoRenderManager().getViewportRegion()
			marker=view.getSoRenderManager().getSceneGraph()
			c.viewAll(marker,reg)

		if prop.startswith("C_"):
			c=self.v.getViewer(2).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.C_Axis,fp.C_Angle).Q

			view=self.v.getViewer(2)
			reg=view.getSoRenderManager().getViewportRegion()
			marker=view.getSoRenderManager().getSceneGraph()
			c.viewAll(marker,reg)

		if prop.startswith("D_"):
			c=self.v.getViewer(3).getSoRenderManager().getCamera()
			c.orientation=FreeCAD.Rotation(fp.D_Axis,fp.D_Angle).Q

			view=self.v.getViewer(3)
			reg=view.getSoRenderManager().getViewportRegion()
			marker=view.getSoRenderManager().getSceneGraph()
			c.viewAll(marker,reg)

		if fp.fitAll:
			self.v.fitAll()


	def onDocumentRestored(self, fp):
		print(["onDocumentRestored",str(fp.Label)+ ": "+str(fp.Proxy.__class__.__name__)])
		fp.ViewObject.Visibility=False
		return
		title=fp.Label
		v=Gui.createViewer(4,title)
		updatencontent(v,fp.objs,fp)
		fp.Proxy.v=v







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

	FreeCAD.viewLabel=title
	
	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","MyQuadView")
	QuadView(a,"QuadView for "+ title )
	ViewProvider(a.ViewObject)
	updatencontent(v,objs,a)
	a.Proxy.v=v
	a.Proxy.objs=objs
	a.objs=objs
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

def updatencontent(viewer,objs,fp,clearSel=True,fit=True):

	print ("update content",fp,fp.Label)

	v=viewer

	try:
		view=v.getViewer(0)
	except:
		title=fp.Label
		v=Gui.createViewer(4,title)
		fp.Proxy.v=v
		view=v.getViewer(0)


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

		if fp.A_DisplayMode==0:
			nodeA=node
		else:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(fp.A_DisplayMode)

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.A_Axis,fp.A_Angle).Q

#-

	#view=self.v.getViewer(0)
	reg=view.getSoRenderManager().getViewportRegion()
	marker=view.getSoRenderManager().getSceneGraph()
	c.viewAll(marker,reg)


	#------------------------------------

	view=v.getViewer(1)
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

		if fp.B_DisplayMode==0:
			nodeA=node
		else:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(fp.B_DisplayMode)


		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.B_Axis,fp.B_Angle).Q

	#------------------------------------

	view=v.getViewer(2)
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

		if fp.C_DisplayMode==0:
			nodeA=node
		else:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(fp.C_DisplayMode)

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.C_Axis,fp.C_Angle).Q

	#------------------------------------

	view=v.getViewer(3)
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

		if fp.D_DisplayMode==0:
			nodeA=node
		else:
			nodeA=node.copy()
			clds=nodeA.getChildren()
			s2=clds[2]
			s2.whichChild.setValue(fp.D_DisplayMode)

		marker.addChild(nodeA)

	view.setSceneGraph(marker)

	c=view.getSoRenderManager().getCamera()
	c.orientation=FreeCAD.Rotation(fp.D_Axis,fp.D_Angle).Q

	#------------------------------------

	if fit:
		v.fitAll()

	if clearSel:
		Gui.Selection.clearSelection()


#
# two horizontal windows ...
#

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

