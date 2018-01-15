
# from say import *
# import nurbswb.pyob
#------------------------------
import FreeCAD,FreeCADGui,Sketcher,Part

App = FreeCAD
Gui = FreeCADGui

import numpy as np
import time


class FeaturePython:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


class ViewProvider:
	''' basic defs '''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

#-------------------------------


class Geodesic(FeaturePython):
	def __init__(self, obj,uc=5,vc=5):
		FeaturePython.__init__(self, obj)

		obj.addProperty("App::PropertyFloat","u","Source", "size of cell in u direction").u=50
		obj.addProperty("App::PropertyFloat","v","Source", "size of cell in u direction").v=50

		obj.addProperty("App::PropertyFloat","ue","Base", "size of cell in u direction")
		obj.addProperty("App::PropertyFloat","ve","Base", "size of cell in u direction")

		obj.addProperty("App::PropertyFloat","ut","Target", "size of cell in u direction").ut=60
		obj.addProperty("App::PropertyFloat","vt","Target", "size of cell in u direction").vt=60
		obj.addProperty("App::PropertyInteger","lang","Generator", "size of cell in u direction").lang=40

		obj.addProperty("App::PropertyFloat","direction","Generator", "size of cell in u direction")
		obj.direction=0
		obj.addProperty("App::PropertyFloat","directione","Generator", "size of cell in u direction")
		obj.directione=0

		obj.addProperty("App::PropertyFloat","directionrib","Generator", "direction of ribs")
		obj.directionrib=90

		
		obj.addProperty("App::PropertyLink","obj","XYZ","")
		obj.addProperty("App::PropertyInteger","facenumber","XYZ", "number of the face")
		obj.addProperty("App::PropertyBool","flip","XYZ", "flip the cirvature direction")
		obj.addProperty("App::PropertyBool","redirect","XYZ", "flip the cirvature direction")
		obj.addProperty("App::PropertyBool","star","XYZ", "all 4 directions")
		obj.addProperty("App::PropertyEnumeration","mode","Base").mode=["geodesic","curvature"]
		obj.addProperty("App::PropertyFloat","dist","Base")
		obj.addProperty("App::PropertyLink","pre","XYZ","")


	def attach(self,vobj):
		print "attach -------------------------------------"
		self.Object = vobj.Object
		self.obj2 = vobj.Object

	def onChanged(self, fp, prop):
		if prop=="direction":
			try:  self.execute(fp)
			except: pass


	def execute(self, fp):
		if fp.mode=="geodesic":
			fp.Shape=updateStarG(fp)
		if fp.mode=="curvature":
			fp.Shape=updateStarC(fp)



def createGeodesic(obj=None):
	'''create a testcase sketch'''

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Geodesic")

	Geodesic(a)
	a.obj=obj
#	a.u=60
#	a.v=40
	ViewProvider(a.ViewObject)
	if obj<>None:
		a.Label="Geodesic for "+obj.Label
	a.mode="geodesic"
	return a

def createCurvature(obj=None):
	'''create a testcase sketch'''

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Curvature")

	Geodesic(a)
	a.obj=obj
	a.u=60
	a.v=40
	ViewProvider(a.ViewObject)
	a.Label="Curvature for "+obj.Label
	a.mode="curvature"
	a.star=True
	a.lang=10
	return a




import numpy as np

def updateStarG(fp):
#		print "run updateStarG"

		d=fp.direction
		d2=fp.directionrib
		u=fp.u
		v=fp.v
		obj=fp.obj

		if fp.pre<>None:
			obj=fp.pre.obj
			d=fp.pre.directionrib
			d=fp.pre.directione+fp.pre.directionrib
			
			u=fp.pre.ue
			v=fp.pre.ve
			if fp.obj<>obj: fp.obj=obj
			if fp.u<>u: fp.u=u
			if fp.v<>v: fp.v=v
			if fp.direction<>d:	
				fp.direction=d


		u *= 0.01
		v *= 0.01

		pts=[]

		f=obj.Shape.Faces[fp.facenumber]
		sf=f.Surface
		#print (f,sf,fp.facenumber,obj.Shape.Faces)
		umin,umax,vmin,vmax=f.ParameterRange

		# print (umin,umax)
		
		u=umin + (umax-umin)*u
		v=vmin + (vmax-vmin)*v

		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*d/180)*t1+np.sin(np.pi*d/180)*t2)

		for i in range(fp.lang):
			pot=sf.value(u,v)
#			print ("punt ", u*100,v*100,pot)
			u2=(u-umin)/(umax-umin)
			v2=(v-vmin)/(vmax-vmin)
#			print ("--2",u2,v2)
			pts += [pot]
			
			if 10:
				pts += [sf.value(u,v)+ sf.normal(u,v)*5,sf.value(u,v)]
				pts += [sf.value(u,v)+ sf.normal(u,v).cross(t)*3,sf.value(u,v)]
				pts += [sf.value(u,v)+ sf.normal(u,v).cross(t)*-3,sf.value(u,v)]

			# ribs
			rib=FreeCAD.Vector(np.cos(np.pi*d2/180)*t+np.sin(np.pi*d2/180)*sf.normal(u,v).cross(t))
			pts += [sf.value(u,v)+ rib*-5,sf.value(u,v)]



			last=sf.value(u,v)
			p2=last+t*1
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)
			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
				break
			p=sf.value(u,v)
			
			pts += [ p]
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()


		shape=Part.makePolygon(pts)

		ut=fp.ut*0.01
		vt=fp.vt*0.01
#		pt=Part.Point(sf.value(ut,vt))
#		print "Abstand"
#		print pt
#		print shape.distToShape(pt.toShape())
#		print (pt,shape.distToShape(pt.toShape())[0])


		pend=sf.value(ut,vt)
		pt=Part.Point(sf.value(ut,vt))
#		print "Abstand"
#		print pt
#		print shape.distToShape(pt.toShape())
		fp.dist= shape.distToShape(pt.toShape())[0]

#		print ("Abstand",pts[-1],pend,shape.distToShape(pt.toShape())[0],(pts[-1]-pend).Length)
#		print (u,v)
		fp.ue=u2*100
		fp.ve=v2*100

		a=t.dot(t1)
		b=t.dot(t2)
		fp.directione=180./np.pi*np.arctan2(b,a)

		shape2=Part.Compound([shape,Part.makePolygon([
				pend,pend+FreeCAD.Vector(0,10,0),
				pend,pend+FreeCAD.Vector(0,-10,0),
				pend,pend+FreeCAD.Vector(10,0,0),
				pend,pend+FreeCAD.Vector(-10,0,0),
				pend,pend+FreeCAD.Vector(0,0,10),
				pend,pend+FreeCAD.Vector(0,0,-10),
				])])



		shape2=shape
		return shape2
	#Draft.makeWire(pts)


def updatepath(fp,redirect,flip):

		d=fp.direction
		u=fp.u
		v=fp.v
		obj=fp.obj
		u *= 0.01
		v *= 0.01

		pts=[]
		pts2=[]

		f=obj.Shape.Faces[fp.facenumber]
		sf=f.Surface
		print (f,sf,fp.facenumber,obj.Shape.Faces)
		umin,umax,vmin,vmax=f.ParameterRange

		u=umin + (umax-umin)*u
		v=vmin + (vmax-vmin)*v

#		(t1,t2)=sf.tangent(u,v)
		tsa=sf.curvatureDirections(u,v)
		
		if flip: t=tsa[1]
		else: t=tsa[0]
		if redirect:
			t *= -1

		for i in range(fp.lang):

			pts += [sf.value(u,v)]

			last=sf.value(u,v)
			p2=last+t*1
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)
			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
				break
			p=sf.value(u,v)
			
			pts += [ p]
			# (t1,t2)=sf.tangent(u,v)
			(t1,t2)=sf.curvatureDirections(u,v)
#			print "---------t ",t
#			print t1
#			print t2
			print (round(t.dot(t1)*100),round(t.dot(t2)*100))
			dt1=t.dot(t1)
			dt2=t.dot(t2)
			pts += [p+t1,p,p+t2,p]
			if abs(dt1)<0.82 and abs(dt2)<0.82:
				print "worry "
				pts += [p+t1,p,p+t2,p]
#			else:

			if abs(dt1)>abs(dt2):
				t=t1
			else: 
				t=t2

			if (p-last).Length>(p+t-last).Length:
				t *= -1

			t.normalize()

		shape=Part.makePolygon(pts)

		ut=fp.ut*0.01
		vt=fp.vt*0.01
		pend=sf.value(ut,vt)
		pt=Part.Point(sf.value(ut,vt))
#		print "Abstand"
#		print pt
#		print shape.distToShape(pt.toShape())
		fp.dist= shape.distToShape(pt.toShape())
		print ("Abstand",pt,pend,shape.distToShape(pt.toShape())[0],(pt-pend).Length)

		return shape
	#Draft.makeWire(pts)


def updateStarC(fp):
	if fp.star:
		rc=Part.Compound([
			updatepath(fp,False,False),
			updatepath(fp,False,True),
			updatepath(fp,True,False),
			updatepath(fp,True,True)
		])
	else:
		rc=updatepath(fp,fp.redirect,fp.flip)
	return rc




if 0:
	a=createGeodesic(obj=App.ActiveDocument.Poles)
	b=createGeodesic(obj=App.ActiveDocument.Cylinder)
	d=createGeodesic(obj=App.ActiveDocument.Cone)
	d=createGeodesic(obj=App.ActiveDocument.Sphere)


def run():
	a=createGeodesic(obj=Gui.Selection.getSelection()[0])

def runD():
	a=createGeodesic()
	a.pre=Gui.Selection.getSelection()[0]



def runC():
	a=createCurvature(obj=Gui.Selection.getSelection()[0])


def runall():
	for j in range(36):
		a=createGeodesic(obj=Gui.Selection.getSelection()[0])
		a.direction=j*10

