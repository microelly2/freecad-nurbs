
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

		obj.addProperty("App::PropertyFloat","ut","Target", "size of cell in u direction").ut=10
		obj.addProperty("App::PropertyFloat","vt","Target", "size of cell in u direction").vt=50
		obj.addProperty("App::PropertyInteger","lang","Generator", "size of cell in u direction").lang=200

		obj.addProperty("App::PropertyFloat","direction","Generator", "size of cell in u direction").direction=0
		obj.addProperty("App::PropertyLink","obj","XYZ","")
		obj.addProperty("App::PropertyInteger","facenumber","XYZ", "number of the face")


	def attach(self,vobj):
		print "attach -------------------------------------"
		self.Object = vobj.Object
		self.obj2 = vobj.Object

	def onChanged(self, fp, prop):
		if prop=="direction":
			try: fp.Shape=updateStar(fp)
			except: pass

	def execute(self, fp):
		fp.Shape=updateStar(fp)


def createGeodesic(obj=None):
	'''create a testcase sketch'''


	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Geodesic")

	Geodesic(a)
	a.obj=obj
	a.u=60
	a.v=40
	ViewProvider(a.ViewObject)
	a.Label="Geodesic for "+obj.Label
	return a




import numpy as np

def updateStar(fp):
		
		d=fp.direction
		u=fp.u
		v=fp.v
		obj=fp.obj
		u *= 0.01
		v *= 0.01

		pts=[]

		f=obj.Shape.Faces[fp.facenumber]
		sf=f.Surface
		print (f,sf,fp.facenumber,obj.Shape.Faces)
		umin,umax,vmin,vmax=f.ParameterRange

		u=umin + (umax-umin)*u
		v=vmin + (vmax-vmin)*v

		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*d/180)*t1+np.sin(np.pi*d/180)*t2)

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
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()

		shape=Part.makePolygon(pts)

		ut=fp.ut*0.01
		vt=fp.vt*0.01
		pt=Part.Point(sf.value(ut,vt))
#		print "Abstand"
#		print pt
#		print shape.distToShape(pt.toShape())
		print (pt,shape.distToShape(pt.toShape())[0])

		return shape
	#Draft.makeWire(pts)


if 0:
	a=createGeodesic(obj=App.ActiveDocument.Poles)
	b=createGeodesic(obj=App.ActiveDocument.Cylinder)
	d=createGeodesic(obj=App.ActiveDocument.Cone)
	d=createGeodesic(obj=App.ActiveDocument.Sphere)


def run():
	a=createGeodesic(obj=Gui.Selection.getSelection()[0])

def runall():
	for j in range(36):
		a=createGeodesic(obj=Gui.Selection.getSelection()[0])
		a.direction=j*10

