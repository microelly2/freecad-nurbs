# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a parametric
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------



import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtGui
import Part,Mesh,Draft,Points


import numpy as np
import random

import os, nurbswb

global __dir__
__dir__ = os.path.dirname(nurbswb.__file__)
print __dir__


class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

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
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

	def onChanged(self, fp, prop):
		#print ("onChanged",prop)
		pass


import nurbswb.isomap
reload(nurbswb.isomap)

def createShape(obj):
	
	
	# mittelpunkt
#	mpv=0.5
#	mpu=0.5

	mpv=0.5
	mpu=0.5

#	mpv=.0
#	mpu=.0


	# skalierung/lage
	fx=-1.
	fy=-1.
	
#	fy=-0.5
#	fx=-0.5
#	fy=-0.5
	
	#[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(obj.face)
	[uv2x,uv2y,xy2u,xy2v]=[obj.mapobject.Proxy.uv2x,obj.mapobject.Proxy.uv2y,obj.mapobject.Proxy.xy2u,obj.mapobject.Proxy.xy2v]
	
	print "getmap done2"
	
	u0=0
	v0=0
	
	fy=-1.1
	fx=-1.1

	y=uv2y(u0,v0)
	x=uv2x(u0,v0)
	u=xy2v(x,y)
	v=xy2u(x,y)
	# print (u0,v0,x,y,u,v)
	bs=obj.face.Shape.Face1.Surface
	w=obj.wire.Shape.Wires[0]

	ppall=[]
	for w in obj.wire.Shape.Wires:
		pts=w.discretize(30)
		pts2=[]
		
		refpos=bs.value(mpu,mpv)
		
		refpos=FreeCAD.Vector(0,0,0)

		print "uv fuer Wires ..."
		for p in pts:
			x=fx*(p.x-refpos.x)
			y=fy*(p.y-refpos.y)
			u=xy2u(x,y)
			v=xy2v(x,y)
			# print (round(x,2),round(y,2),round(u,2),round(v,2))
			# nicht ausreisen lassen
			print (u,v)
			if u<0: u=0
			if u>1: u=1
			if v<0: v=0
			if v>1: v=1
			

			p2=bs.value(u,v)
			pts2.append(p2)
		
		#Draft.makeWire(pts2)
	#	print pts2
		FreeCAD.pts2=pts2

		pts3=[]
		for p in FreeCAD.pts2:
			# print p
			if p.Length<1000:
				pts3.append(p)
			else:
				print ("AFehler bei ",p)

		#Draft.makeWire(pts3)

		# return

		pp=Part.makePolygon(pts3)
		ppall.append(pp)
	# pp=Part.makePolygon(pts)

	pp=Part.Compound(ppall)

	#-----------------
	if 1:
		pass

	ppall=[]
	for w in obj.wire.Shape.Wires:

		#w=obj.wire.Shape.Wires[0]
		pts=w.discretize(30)
#		print pts

		#[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(face)
		
		[uv2x,uv2y,xy2u,xy2v]=[obj.mapobject.Proxy.uv2x,obj.mapobject.Proxy.uv2y,obj.mapobject.Proxy.xy2u,obj.mapobject.Proxy.xy2v]
		
		ptbb=[]
		for p in pts:
#			print "--",p
			x=-p.y
			y=-p.x
			u=xy2v(x,y)
			v=xy2u(x,y)
			pt=bs.value(u,v)
			ptbb.append(pt)
#			print pt

		#Draft.makeWire(ptbb)
#		print "yy"
#		print ptbb
#		print "xx"
		pp=Part.makePolygon(ptbb)
		ppall.append(pp)
	#---------------


	ppc=Part.Compound(ppall)
	obj.Shape=ppc
	obj.Label="3D for " + obj.wire.Label+" "
	
	print ("Mittelpunkt ", bs.value(0.5,0.5))
	print "MOA:",obj.mapobject.Label
	#print "MOA:",obj.mapobject.Proxy.uv2x




class Isodraw(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","face","Base")
		obj.addProperty("App::PropertyLink","wire","Base")
		obj.addProperty("App::PropertyLink","mapobject","Base")
		obj.addProperty("App::PropertyInteger","n1","Base")
		obj.addProperty("App::PropertyInteger","n2","Base")
		obj.addProperty("App::PropertyInteger","n3","Base")
		obj.n1=1
		obj.n2=1
		obj.n3=1

		obj.addProperty("App::PropertyLink","backref","Base")

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)
		#createShape(obj)

#	def onChanged(self, fp, prop):
#		print ("onChanged",prop)
#		if prop=="Size" or prop in ["uMin","uMax","n2","e1","e2","e3"]:
#			createShape(fp)

	def execute(proxy,obj):
		createShape(obj)
		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()





def createIsodrawFace():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyFilledFace")
	bn=Isodraw(b)
	return b

#------------------------------------------------------


class Map(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","face","Base")
		#obj.addProperty("App::PropertyLink","wire","Base")
		#raender
		obj.addProperty("App::PropertyInteger","ub","Base")
		obj.addProperty("App::PropertyInteger","ue","Base")
		obj.addProperty("App::PropertyInteger","vb","Base")
		obj.addProperty("App::PropertyInteger","ve","Base")
		#mitte
		obj.addProperty("App::PropertyFloat","vm","Base")
		obj.addProperty("App::PropertyFloat","um","Base")

		obj.addProperty("App::PropertyFloat","fx","Base").fx=-1.
		obj.addProperty("App::PropertyFloat","fy","Base").fy=-1.


		obj.vm=0.4
		obj.um=0.5
		obj.ve=-1
		obj.ue=-1

		obj.addProperty("App::PropertyLink","backref","Base")

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)
		#createShape(obj)

#	def onChanged(self, fp, prop):
#		print ("onChanged",prop)
#		if prop=="Size" or prop in ["uMin","uMax","n2","e1","e2","e3"]:
#			createShape(fp)

	def execute(proxy,obj):

		[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(obj.face)
		proxy.uv2x=uv2x
		proxy.uv2y=uv2y
		proxy.xy2u=xy2u
		proxy.xy2v=xy2v
		print "getmap done"

		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()

def createMap():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MAP")
	bn=Map(b)
	return b



import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from PySide import QtGui
import Part,Mesh,Draft,Points



import Draft
import numpy as np
import scipy
import scipy.interpolate




#def interpolate(x,y,z, gridsize,mode=,rbfmode=True,shape=None):


#		rbf = scipy.interpolate.Rbf(x, y, z, function='thin_plate')
	#	rbf = scipy.interpolate.interp2d(x, y, z, kind=mode)

	#	zi=rbf2(yi,xi)




def createGrid(obj,upmode=False):
	try: bs=obj.faceObject.Shape.Face1.Surface
	except: return Part.Shape()

	# mittelpunkt
	mpv=0.5
	mpu=0.5

	# skalierung/lage
	fx=-1
	fy=-1

	#fx,fy=1,1

	comps=[]


	refpos=bs.value(mpv,mpu)


	vc=obj.uCount
	uc=obj.vCount


	ptsa=[]
	ptska=[]

	ba=bs.uIso(mpu)
	comps += [ba.toShape()]


	for v in range(vc+1):
		pts=[]
		vm=1.0/vc*v

		ky=ba.length(vm,mpv)

		if vm<mpv: ky =-ky
		bbc=bs.vIso(vm)

		comps += [bbc.toShape()]

		ptsk=[]
		for u in range(uc+1):
			uv=1.0/uc*u

			ba=bs.uIso(uv)

			ky=ba.length(vm,mpv)
			if vm<mpv: ky =-ky


			kx=bbc.length(mpu,uv)
			if uv<mpu: kx =-kx

			# ptsk.append(bs.value(vm,uv))
			ptsk.append(bs.value(uv,vm))

			pts.append([kx,ky,0])
		ptsa.append(pts)
		ptska.append(ptsk)

#	comps += [ Part.makePolygon(ptsk[obj.vMin:obj.vMax])]


#	comps =[]

#	for pts in ptska[obj.vMin:obj.vMax]:
#		comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.uMin:obj.uMax]]) ]

#	ptska=np.array(ptska).swapaxes(0,1)

#	for pts in ptska[obj.uMin:obj.uMax]:
#		comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.vMin:obj.vMax]]) ]



	comps=[]
	for pts in ptska[obj.uMin:obj.uMax]:
		comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.vMin:obj.vMax]]) ]

	ptska=np.array(ptska).swapaxes(0,1)

	for pts in ptska[obj.vMin:obj.vMax]:
		comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.uMin:obj.uMax]]) ]



	if upmode:
		return Part.Compound(comps)
		#return Part.Compound(comps[obj.vMin:obj.vMax])



	print ("ptsa.shape",np.array(ptsa).shape)

	if 10:
		comps=[]
		for pts in ptsa[obj.uMin:obj.uMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts[obj.vMin:obj.vMax]]) ]

		ptsa=np.array(ptsa).swapaxes(0,1)

		for pts in ptsa[obj.vMin:obj.vMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts[obj.uMin:obj.uMax]]) ]


		return Part.Compound(comps)








# ------------

class Drawgrid(PartFeature):
	''' draw the isomap grid'''
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","faceObject","Base")
		obj.addProperty("App::PropertyInteger","faceNumber","Base")
		

		obj.addProperty("App::PropertyLink","wire","Base")
		
		obj.addProperty("App::PropertyInteger","uMin","Base")
		obj.addProperty("App::PropertyInteger","uMax","Base")
		obj.addProperty("App::PropertyInteger","uCenter","Base")
		obj.addProperty("App::PropertyInteger","uCount","Base")
		
		obj.addProperty("App::PropertyInteger","vMin","Base")
		obj.addProperty("App::PropertyInteger","vMax","Base")
		obj.addProperty("App::PropertyInteger","vCenter","Base")
		obj.addProperty("App::PropertyInteger","vCount","Base")

		obj.addProperty("App::PropertyLink","backref","Base")

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)

		obj.uCount=30
		obj.vCount=30

		obj.uMax=-1
		obj.uMin=1
		obj.vMax=-1
		obj.vMin=1


	def onChanged(self, obj, prop):
		if obj == None: return
		# print ("onChanged",prop,obj)
		if prop in ["uMin","uMax","vMin","vMax","e2","e3"]:
				obj.Shape=createGrid(obj)


	def execute(proxy,obj):
		print "exe",obj
		if obj.faceObject != None:
			obj.Shape=createGrid(obj)
		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()



class Draw3Dgrid(PartFeature):
	''' draw the grid onto to 3d face obj'''
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyLink","drawgrid","Base")
		obj.addProperty("App::PropertyLink","backref","Base")

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(0.,1.,1.)


	def onChanged(self, obj, prop):
		print("aaaa",prop)
		if prop=="drawgrid":
			obj.Shape=createGrid(obj.drawgrid,True)



	def execute(proxy,obj):
		print "exe",obj
		if obj.drawgrid != None:
			obj.Shape=createGrid(obj.drawgrid,True)
		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()



class ViewProviderSL(ViewProvider):

	def onChanged(self, obj, prop):
		#print ("onChanged",prop)
		if obj.Visibility:
			ws=WorkSpace(obj.Object.workspace)
			ws.show()
		else:
			ws=WorkSpace(obj.Object.workspace)
			ws.hide()

	def onDelete(self, obj, subelements):
		print "on Delete Sahpelink"
		print ("from", obj.Object.workspace,obj.Object.Label,obj.Object.Name)
		ws=WorkSpace(obj.Object.workspace)
		objs=ws.dok.findObjects()
		for jj in objs:
			print (jj.Label,jj.Name)
			s=jj.Name+"@"
			print (s,obj.Object.Name)
			if obj.Object.Label.startswith(s):
				ws.dok.removeObject(jj.Name)
				print "gguutt"
				return True
#		return False
		return(True)






class ShapeLink(PartFeature):

	def __init__(self,obj,sobj,dokname):
		print "create shape link"
		PartFeature.__init__(self,obj)
		obj.addProperty("App::PropertyLink","source","Base")
		obj.addProperty("App::PropertyBool","nurbs","Base")
		obj.addProperty("App::PropertyInteger","gridcount","Base")
		obj.addProperty("App::PropertyString","workspace","Base")
		

		obj.source=sobj
		obj.workspace=dokname
		obj.gridcount=20
		obj.gridcount=3

		ViewProviderSL(obj.ViewObject)


	def execute(proxy,obj):
		if not obj.ViewObject.Visibility:
			return

		print ("update shape",obj.source.Name,obj.workspace,obj.gridcount)

		tw=WorkSpace(obj.workspace)
		print "!!",tw
		print tw.dok
		target=tw.dok.getObject(obj.source.Name)
		print target
		if target==None:
			tw.addObject2(obj.source,obj.gridcount)
		print target
		if 1 or obj.nurbs:
			target.Shape=obj.source.Shape.toNurbs()

			cs=[]
			count=obj.gridcount
			f=obj.source.Shape.Face1.toNurbs()
			f=f.Face1.Surface
			
			for ui in range(count+1):
					cs.append(f.uIso(1.0/count*ui).toShape())
			for vi in range(count+1):
					cs.append(f.vIso(1./count*vi).toShape())
			target.Shape=Part.Compound(cs)
			FreeCAD.cs=cs
		else:
			target.Shape=obj.source.Shape
		tw.recompute()







class ViewProviderWSL(ViewProvider):

	def onChanged(self, obj, prop):
		print ("onChanged",prop)
		if obj.Visibility:
			ws=WorkSpace(obj.Object.workspace)
			ws.show()
		else:
			ws=WorkSpace(obj.Object.workspace)
			ws.hide()

	def onDelete(self, obj, subelements):
		print "on Delete"
		App.closeDocument(obj.Object.workspace)
		#return False
		return(True)




class WSLink(PartFeature):

	def __init__(self,obj,dokname):
		PartFeature.__init__(self,obj)
		obj.addProperty("App::PropertyString","workspace","Base")
		obj.workspace=dokname
		ViewProviderWSL(obj.ViewObject)


	def execute(proxy,obj):
		if obj.ViewObject.Visibility:
			ws=WorkSpace(obj.workspace)
			ws.show()
		else:
			ws=WorkSpace(obj.workspace)
			ws.hide()




class WorkSpace():


	def __init__(self, name):
		try:lidok= App.getDocument(name)
		except:	lidok=App.newDocument(name)
		self.dok=lidok
		self.name=name

	def delete(self):
		App.closeDocument(self.name)


	def addObject2(self,obj,count=10):
		if 0:
			res=self.dok.addObject("Part::FeaturePython",obj.Name)
			ViewProvider(res.ViewObject)
		#return
		res=self.dok.addObject("Part::Spline",obj.Name)
		res.Shape=obj.Shape.toNurbs()
		#return
		f=obj.Shape.Face1.Surface
		cs=[]

		for ui in range(count+1):
				cs.append(f.uIso(1.0/count*ui).toShape())
		for vi in range(count+1):
				cs.append(f.vIso(1./count*vi).toShape())
		res.Shape=Part.Compound(cs)




	def recompute(self):
		self.dok.recompute()


	def show(self):
		self.getWidget().show()

	def hide(self):
		self.getWidget().hide()


	def getWidget(self):
		mw=FreeCADGui.getMainWindow()
		mdiarea=mw.findChild(QtGui.QMdiArea)

		sws=mdiarea.subWindowList()
		print "windows ..."
		for w2 in sws:
			print str(w2.windowTitle())
			s=str(w2.windowTitle())
			if s == self.name + '1 : 1[*]':
				print "gefundne"
				return w2
		print self.name + '1:1[*]'







def createLink(obj,dokname="Linkdok"):
	ad=App.ActiveDocument
	print ad.Name

	lidok= WorkSpace(dokname)
	link=lidok.addObject2(obj)
	lidok.recompute()
	
	bares=obj.Document.addObject("Part::FeaturePython","Base Link "+obj.Label)
	bares.Label=obj.Label+"@"+dokname

	ShapeLink(bares,obj,dokname)

	return link

def createWsLink(dokname="Linkdok"):
	ad=App.ActiveDocument
	bares=ad.addObject("Part::FeaturePython","WS "+dokname+"")
	WSLink(bares,dokname)
	return bares
	

if 0:

	link.source=obj

	try:obj.backref=link
	except: pass

	print lidok.Name
	gad=Gui.getDocument(lidok.Name)
	lidok.recompute()
	Gui.SendMsgToActiveView("ViewSelection")
	Gui.SendMsgToActiveView("ViewFit")
	print ad.Name
	App.setActiveDocument(ad.Name)
	Gui.ActiveDocument=Gui.getDocument(ad.Name)
	return  link




'''

if __name__=='__main__':

	for w in [App.ActiveDocument.Sketch]:
		b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyIsodraw")
		bn=Isodraw(b)
		b.face=App.ActiveDocument.Poles
		b.wire=w
		createShape(b)
		b.ViewObject.Transparency=60
		App.activeDocument().recompute()
		createLink(b,"A3D")


if __name__=='__main__':

		b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyDrawGrid")

		Drawgrid(b)
		b.faceObject=App.ActiveDocument.Poles


		b.ViewObject.Transparency=60
		App.activeDocument().recompute()
		createLink(b,"A2D")



if __name__=='__main__':

		b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyGrid")

		Draw3Dgrid(b)
		b.drawgrid=App.ActiveDocument.MyDrawGrid


		b.ViewObject.Transparency=60
		ss=createLink(b,"A3D")








'''

if 0:
	ad=App.ActiveDocument
	App.ActiveDocument=ad

	#bb=App.ActiveDocument.Poles
	#cc=App.ActiveDocument.orig
	cc=App.ActiveDocument.Cylinder


	#lidok= WorkSpace("A3D")
	#try: lidok.delete()
	#except: pass

	wl=createWsLink("Shoe")
	App.ActiveDocument=ad

	a=createLink(cc,"Shoe")



if 0:
	wl=createWsLink("Sole")
	App.ActiveDocument=ad
	ad.recompute()

	wl=createWsLink("Both")
	App.ActiveDocument=ad
	ad.recompute()


	a=createLink(bb,"Shoe")
	a=createLink(cc,"Sole")

	App.ActiveDocument=ad
	a=createLink(bb,"Both")
	a=createLink(cc,"Both")
	App.ActiveDocument=ad


	App.ActiveDocument=ad
	'''
	b=createLink(cc,"DD")
	b2=createLink(bb,"AA")

	a=createLink(bb,"DD")

	WorkSpace("AA").show()
	WorkSpace("DD").hide()
	'''


def map3Dto2D():
	# 3D Kante zu 2D Kante
	face=App.ActiveDocument.Poles
	#wire=App.ActiveDocument.UUUU_Drawing_on_Poles__Face1002_Spline
	s=Gui.Selection.getSelection()
	for wire in s:
		#wire=s[0]
		[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(face)

		bs=face.Shape.Face1.Surface
		for e in wire.Shape.Edges:
			pts=e.discretize(10)
			FreeCAD.ptsaa=pts
			pts2=[]
			for p in pts:
				(u,v)=bs.parameter(p)
				print (u,v)
				x=uv2x(u,v)
				y=uv2y(u,v)
				p2=FreeCAD.Vector(-y,-x,0)
				pts2.append(p2)

			Draft.makeWire(pts2)


def map2Dto3D():
	# 2D Kante(Sketch) auf  3D Flaeche Poles
	#import nurbswb.isodraw
	moa=createMap()
	moa.face=App.ActiveDocument.Poles
	
	s=Gui.Selection.getSelection()
	for w in s:
		f=createIsodrawFace()
		f.mapobject=moa
		f.face=App.ActiveDocument.Poles
		#f.wire=App.ActiveDocument.Sketch
		try:f.wire=w
		except:f.wire=App.ActiveDocument.DWire
		App.activeDocument().recompute()



# pruefe qualitaet der umrechnung
if 0:
	face=App.ActiveDocument.Poles
	#face=App.ActiveDocument.MySegment
	bs=face.Shape.Face1.Surface
	#wire=App.ActiveDocument.UUUU_Drawing_on_Poles__Face1002_Spline
	wire=App.ActiveDocument.UUUU_Drawing_on_Poles__Face1001_Spline
	#wire=App.ActiveDocument.Shape001
	p=wire.Shape.Vertex1.Point
	p
	print "huu"
	[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(face)

	(u,v)=bs.parameter(p)
	(u,v)=bs.parameter(p)
	pt0=bs.value(u,v)
	print (u,v)
	x=uv2x(u,v)
	y=uv2y(u,v)
	print (x,y)
	u=xy2v(x,y)
	v=xy2u(x,y)
	print(u,v)
	pt=bs.value(u,v)
#	print pt
#	print p
	print p-pt

if 0:
#	kku2=np.array(FreeCAD.kku).reshape(31,31,3)
#	kku=kku2[10:25,10:20].reshape(150,3)

	ptsu=[FreeCAD.Vector(tuple(i)) for i in kku]
	Draft.makeWire(ptsu)
	Points.show(Points.Points(ptsu))


	mode='thin_plate'
	xy2u = scipy.interpolate.Rbf(kku[:,0],kku[:,1],kku[:,2], function=mode)


if 0:
	[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(face)
	ptbb=[]
	for p in FreeCAD.ptsaa:
		(u,v)=bs.parameter(p)
		(u,v)=bs.parameter(p)
		pt0=bs.value(u,v)
#		print (u,v)
		x=uv2x(u,v)
		y=uv2y(u,v)
#		print (x,y)
		u=xy2v(x,y)
		v=xy2u(x,y)
#		print(u,v)
		pt=bs.value(u,v)
	#	print pt
	#	print p
		print p-pt
		ptbb.append(pt)

	Draft.makeWire(ptbb)
