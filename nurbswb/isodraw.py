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

import os
import scipy
import scipy.interpolate

import nurbswb
import nurbswb.facedraw
reload (nurbswb.facedraw)

import nurbswb.isomap
reload(nurbswb.isomap)




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



def createShape(obj):
	'''create 2D or 3D mapping of a object'''

	print "CreateShape for obj:",obj.Label

	pointCount=obj.pointcount
	pointCount=50

	[uv2x,uv2y,xy2u,xy2v]=[obj.mapobject.Proxy.uv2x,obj.mapobject.Proxy.uv2y,obj.mapobject.Proxy.xy2u,obj.mapobject.Proxy.xy2v]

	if xy2v==None:
		print "Kann umkehrung nicht berechnen xy2v nicht vorhanden"
		return

	# diese daten vom mapobjekt lesen #+#

	mpv=0.5
	mpu=0.5

	u0=0
	v0=0

	fy=-1.
	fx=-1.

	#+# facenumer aus obj param holen
	face=obj.face.Shape.Face1
	bs=obj.face.Shape.Face1.Surface
	w=obj.wire.Shape.Wires[0]

	ppall=[]

	for i,w in enumerate(obj.wire.Shape.Wires):
		print "X Wire ...",i
		pts=w.discretize(pointCount)
		pts2=[]

		#refpos geht noch nicht
		mpv=0.
		mpu=0.

#		refpos=bs.value(mpu,mpv)
#		print ("refpos",mpu,mpv)
#		print refpos

		refpos=FreeCAD.Vector(0,0,0)

		for p in pts:

			y=fx*(p.x-refpos.x)
			x=fy*(p.y-refpos.y)

			#fuer ruled surface !!
			x=p.y
			y=p.x

			print  ("a",x,y)
			
			u=xy2u(x,y)
			v=xy2v(x,y)


			print(round(u,2),round(v,2))

			if 0: #macht nur Sinn fuer Bsplines 
				if u<0: u=0
				if u>1: u=1
				if v<0: v=0
				if v>1: v=1

			#faktor dazu
			su=bs.UPeriod()
			sv=bs.VPeriod()
			if su>1000: su=face.ParameterRange[1]
			if sv>1000: sv=face.ParameterRange[3]

#			print ("Skalierung ",su,sv)
			p2=bs.value(u*su,v*sv)
			
			pts2.append(p2)

		FreeCAD.pts2a=pts2
		pol=Part.makePolygon(pts2)

		obj.Shape=pol
		return

#---------------

def createShapeA(obj):
	
	pointCount=obj.pointcount


	# mittelpunkt

	mpv=0.5
	mpu=0.5

	[uv2x,uv2y,xy2u,xy2v]=[obj.mapobject.Proxy.uv2x,obj.mapobject.Proxy.uv2y,obj.mapobject.Proxy.xy2u,obj.mapobject.Proxy.xy2v]

	u0=0
	v0=0

	fy=-1.1
	fx=-1.1

	y=uv2y(u0,v0)
	x=uv2x(u0,v0)
	
	if xy2v==None:
		print "Kann umkerhung nicht berechnen xy2v nicht vorhanden"
		return

	u=xy2v(x,y)
	v=xy2u(x,y)

	# hack fier torus
	u=xy2v(-x,-y)
	v=xy2u(-x,-y)

	# print (u0,v0,x,y,u,v)
	bs=obj.face.Shape.Face1.Surface
	w=obj.wire.Shape.Wires[0]

	ppall=[]
	for w in obj.wire.Shape.Wires:
		pts=w.discretize(pointCount)
		pts2=[]

		refpos=bs.value(mpu,mpv)
		refpos=FreeCAD.Vector(0,0,0)

		for p in pts:

			x=fx*(p.x-refpos.x)
			y=fy*(p.y-refpos.y)

			x=-p.y
			y=-p.x
			u=xy2u(x,y)
			v=xy2v(x,y)

			if 0:
				if u<0: u=0
				if u>1: u=1
				if v<0: v=0
				if v>1: v=1


			p2=bs.value(u,v)

			pts2.append(p2)

		FreeCAD.pts2a=pts2
		pol=Part.makePolygon(pts2)

		obj.Shape=pol
		return







#---------------




class Isodraw(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
#		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","face","Source")
		obj.addProperty("App::PropertyLink","wire","Source")
		obj.addProperty("App::PropertyLink","mapobject","Details","configuration objekt for mapping")
		obj.addProperty("App::PropertyBool","drawFace","Output","display subface cut by the wire projection")
		obj.addProperty("App::PropertyBool","reverseFace","Output","display inner or outer subface")
		obj.addProperty("App::PropertyInteger","pointcount","Details","count of points to discretize source wire")
		obj.pointcount=20

		obj.addProperty("App::PropertyLink","backref","Workspace")

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)

#	def onChanged(self, fp, prop):
#		print ("onChanged",prop)

	def execute(proxy,obj):
		createShape(obj)
		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()
		face=obj.face.Shape.Face1
		nurbswb.facedraw.drawcurve(obj,face)


def createIsodrawFace():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","IsoDrawFace")
	bn=Isodraw(b)
	return b

#------------------------------------------------------


class Map(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		obj.addProperty("App::PropertyVector","Size","Base").Size=FreeCAD.Vector(300,-100,200)
		obj.addProperty("App::PropertyLink","face","Base")
		obj.addProperty("App::PropertyLink","faceObject","Base")
		#obj.addProperty("App::PropertyLink","wire","Base")
		#raender
		obj.addProperty("App::PropertyInteger","border","Interpolation","border offset in uv space")
		obj.addProperty("App::PropertyInteger","ub","Interpolation","minimum u value for interpolation base")
		obj.addProperty("App::PropertyInteger","ue","Interpolation","maximum u value for interpolation base")
		obj.addProperty("App::PropertyInteger","vb","Interpolation","minimum v value for interpolation base")
		obj.addProperty("App::PropertyInteger","ve","Interpolation","minimum v value for interpolation base")
		obj.addProperty("App::PropertyInteger","uc","Interpolation","count u segments")
		obj.addProperty("App::PropertyInteger","vc","Interpolation","count v segments")
#		obj.addProperty("App::PropertyInteger","uCount","Interpolation","count u segments").uCount=30
#		obj.addProperty("App::PropertyInteger","vCount","Interpolation","count v segments").vCount=30


		obj.addProperty("App::PropertyEnumeration","modeA","Interpolation","interpolation mode uv to iso-xy")
		obj.modeA=['cubic','linear']
		obj.addProperty("App::PropertyEnumeration","modeB","Interpolation","interpolation mode iso-xy to uv")
		obj.modeB=['thin_plate','cubic','linear']


		obj.addProperty("App::PropertyInteger","pointsPerEdge","Map","discretize for 3D to 2D")
		obj.pointsPerEdge=3

		#mitte
#		obj.addProperty("App::PropertyFloat","vm","Map","v center")
#		obj.addProperty("App::PropertyFloat","um","Map","u center")

#		obj.addProperty("App::PropertyFloat","fx","Map","Scale factor for x").fx=-1.
#		obj.addProperty("App::PropertyFloat","fy","Map","Scale factor for y").fy=-1.


#		obj.vm=0.5
#		obj.um=0.5
		obj.ve=-1
		obj.ue=-1
		
		obj.border=14
		obj.ub=8
		obj.vb=8
		obj.ue=20
		obj.ve=20

		obj.uc=30
		obj.vc=30

		obj.addProperty("App::PropertyLink","backref","Base")


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
		obj.addProperty("App::PropertyBool","flipuv","Base")
		obj.addProperty("App::PropertyBool","flipxy","Base")

		obj.addProperty("App::PropertyFloat","fx","Base")
		obj.addProperty("App::PropertyFloat","fy","Base")
		
		obj.addProperty("App::PropertyFloat","vMapCenter","Map")
		obj.addProperty("App::PropertyFloat","uMapCenter","Map")

		obj.addProperty("App::PropertyBool","display2d","Map")
		obj.addProperty("App::PropertyBool","display3d","Map")
		
		obj.display2d=True
	
		obj.fx=1.
		obj.fy=1.
		obj.flipxy=True

		obj.uMapCenter=50
		obj.vMapCenter=50


		obj.uCount=30
		obj.vCount=30

		obj.uMax=31
		obj.uMin=0
		obj.vMax=31
		obj.vMin=0





		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)

#	def onChanged(self, fp, prop):
#		print ("onChanged",prop)

	def execute(proxy,obj):

		[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(obj,obj.face)
		proxy.uv2x=uv2x
		proxy.uv2y=uv2y
		proxy.xy2u=xy2u
		proxy.xy2v=xy2v
		print "getmap done"

		print "erzeuge grid"
		obj.faceObject=obj.face
		cps=[]
		if obj.display2d:
			cps.append(createGrid(obj))
		if obj.display3d:
			cps.append(createGrid(obj,upmode=True))
		obj.Shape=	Part.Compound(cps)


		if obj.backref <>None:
			obj.backref.touch()
			obj.backref.Document.recompute()

def createMap():
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MAP")
	Map(b)
	return b




def createGrid(obj,upmode=False):
	try: bs=obj.faceObject.Shape.Face1.Surface
	except: return Part.Shape()

	face=obj.faceObject.Shape.Face1
	


	mpu=obj.uMapCenter/100
	mpv=obj.vMapCenter/100

	# skalierung/lage
	fx=obj.fx
	fy=obj.fy


	comps=[]

	refpos=bs.value(mpv,mpu)

	su=bs.UPeriod()
	sv=bs.VPeriod()
	if su>1000: su=face.ParameterRange[1]
	if sv>1000: sv=face.ParameterRange[3]

	# mittelpunkt
	mpu2=mpu*sv
	mpv2=mpv*su
	mpu=mpv2
	mpv=mpu2

	vc=obj.uCount
	uc=obj.vCount


	ptsa=[]
	ptska=[]

	ba=bs.uIso(mpu)
	comps += [ba.toShape()]


	for v in range(vc+1):
		pts=[]
		vm=1.0/vc*v*sv

		ky=ba.length(vm,mpv)

		if vm<mpv: ky =-ky
		bbc=bs.vIso(vm)

		comps += [bbc.toShape()]

		ptsk=[]
		for u in range(uc+1):
			uv=1.0/uc*u*su

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



	if upmode:

		comps=[]
		for pts in ptska[obj.uMin:obj.uMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.vMin:obj.vMax]]) ]

		ptska=np.array(ptska).swapaxes(0,1)

		for pts in ptska[obj.vMin:obj.vMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(tuple(p)) for p in pts[obj.uMin:obj.uMax]]) ]

		# markiere zentrum der karte
		z=bs.value(0.5*su,0.5*sv)
		print z
		
		circ=Part.Circle()
		circ.Radius=10
		circ.Location=z
		circ.Axis=bs.normal(0.5*su,0.5*sv)
		comps += [circ.toShape()]

		# mapcenter
		z=bs.value(mpu,mpv)
		print z
		
		circ=Part.Circle()
		circ.Radius=20
		circ.Location=z
		circ.Axis=bs.normal(mpu,mpv)
		comps += [circ.toShape()]


		return Part.Compound(comps)





	print ("ptsa.shape",np.array(ptsa).shape)

	comps=[]

	# markiere zentrum der karte
	uv=0.5*su
	vm=0.5*sv
	
	ky=ba.length(vm,mpv)
	if vm<mpv: ky =-ky

	kx=bbc.length(mpu,uv)
	if uv<mpu: kx =-kx
	if obj.flipxy:
		z=FreeCAD.Vector(fy*ky,fx*kx,0)
	else:
		z=FreeCAD.Vector(fx*kx,fy*ky,0)
	circ=Part.Circle()
	circ.Radius=10
	circ.Location=z
	comps += [circ.toShape()]

	z=FreeCAD.Vector(0,0,0)
	circ=Part.Circle()
	circ.Radius=20
	circ.Location=z
	comps += [circ.toShape()]




	if obj.flipxy:

		for pts in ptsa[obj.uMin:obj.uMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[1],fy*p[0],0) for p in pts[obj.vMin:obj.vMax]]) ]

		ptsa=np.array(ptsa).swapaxes(0,1)

		for pts in ptsa[obj.vMin:obj.vMax]:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[1],fy*p[0],0) for p in pts[obj.uMin:obj.uMax]]) ]

	else :
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
		obj.addProperty("App::PropertyBool","flipuv","Base")
		obj.addProperty("App::PropertyBool","flipxy","Base")
		obj.addProperty("App::PropertyFloat","fx","Base")
		obj.addProperty("App::PropertyFloat","fy","Base")
		
		obj.addProperty("App::PropertyFloat","vMapCenter","Map")
		obj.addProperty("App::PropertyFloat","uMapCenter","Map")
		
		obj.fx=1.
		obj.fy=1.
		obj.flipxy=True

		obj.uMapCenter=50
		obj.vMapCenter=50

		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(1.,0.,1.)

		obj.uCount=30
		obj.vCount=30

		obj.uMax=31
		obj.uMin=0
		obj.vMax=31
		obj.vMin=0


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


def testF():

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

def testA():
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



def testB():
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
	#face=App.ActiveDocument.Poles
	#wire=App.ActiveDocument.UUUU_Drawing_on_Poles__Face1002_Spline

	s0=Gui.Selection.getSelection()
	base=s0[-1]

	if hasattr(base,"faceObject"):
		face=base.faceObject
		mapobj=base
	else:
		face=base
		mapobj=None

	s=s0[:-1]


	for wire in s:
		[uv2x,uv2y,xy2u,xy2v]=nurbswb.isomap.getmap(mapobj,face)

		bs=face.Shape.Face1.Surface
		pts2=[]
		firstEdge=True
		for e in wire.Shape.Edges:
			# auf 5 millimeter genau
			if mapobj<>None:
				dd=mapobj.pointsPerEdge
			else:
				dd=int(round(e.Length/5))
				dd=30
			ptsa=e.discretize(dd)
			if not firstEdge:
				pts=ptsa[1:]
			else:
				pts=ptsa
			firstEdge=False

			FreeCAD.ptsaa=pts
			
			for p in pts:
				(u,v)=bs.parameter(p)
				(v,u)=bs.parameter(p)
#				print (u,v)
				x=uv2x(u,v)
				y=uv2y(u,v)
				if mapobj<>None and mapobj.flipxy:
					p2=FreeCAD.Vector(y,x,0)
				else:
					p2=FreeCAD.Vector(-y,-x,0)
#				p2=FreeCAD.Vector(y,x,0)
				pts2.append(p2)

		Draft.makeWire(pts2)


def map2Dto3D():
	''' 2D Kante(Sketch) auf  3D Flaeche Poles '''

	# last selection == face
	# other sels: wires to project

	s0=Gui.Selection.getSelection()
	moa=s0[-1]
	s=s0[:-1]

#	moa=createMap()
#	moa.face=face

	for w in s:
		f=createIsodrawFace()
		f.mapobject=moa
		f.face=moa.face
		f.wire=w
		f.Label="map3D_for_"+w.Label+"_on_"+f.face.Label + "_by_" + moa.Label
		App.activeDocument().recompute()


#------------------------


# pruefe qualitaet der umrechnung
def testC():
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

def testD():
#	kku2=np.array(FreeCAD.kku).reshape(31,31,3)
#	kku=kku2[10:25,10:20].reshape(150,3)

	ptsu=[FreeCAD.Vector(tuple(i)) for i in kku]
	Draft.makeWire(ptsu)
	Points.show(Points.Points(ptsu))


	mode='thin_plate'
	xy2u = scipy.interpolate.Rbf(kku[:,0],kku[:,1],kku[:,2], function=mode)


def testE():
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
