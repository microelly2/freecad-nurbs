# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- tripod for uv coords
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD, FreeCADGui

Gui=FreeCADGui
App=FreeCAD
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


def kruemmung(sf,u,v):
	''' calculates curvature for  point (u,v)  on surface  sf '''
	# aus tripod_2.pyon 
	d=0.01
	t1,t2=sf.tangent(u,v)
	t1=t1.multiply(d)
	t2=t2.multiply(d)
	
	vf=sf.value(u,v)

	vfw=vf+t1
	uu,vv=sf.parameter(vfw)
	vfw=sf.value(uu,vv)

	vfe=vf-t1
	uu,vv=sf.parameter(vfe)
	vfe=sf.value(uu,vv)

	ku=(vfw+vfe-vf-vf)
	ddu=(vfw-vf).Length
	ku= ku.multiply(1.0/ddu/ddu)

	vfn=vf+t2
	uu,vv=sf.parameter(vfn)
	vfn=sf.value(uu,vv)

	vfs=vf-t2
	uu,vv=sf.parameter(vfs)
	vfs=sf.value(uu,vv)

	kv=(vfn+vfs-vf-vf)
	ddv=(vfn-vf).Length
	kv= kv.multiply(1.0/ddv/ddv)

	ku=round(ku.Length,3)
	kv=round(kv.Length,3)

	ru=None
	rv=None

	if ku<>0: ru=round(1/ku,3)
	if kv<>0: rv=round(1/kv,3)

	print ("Curvature:",ku,kv,"Radius :", ru,rv)
	
	return ku,kv




class Tripod(PartFeature):
	def __init__(self, obj,uc=5,vc=5):
		PartFeature.__init__(self, obj)
		self.Type="Tripod"
		self.TypeId="Tripod"
		obj.addProperty("App::PropertyLink","source","Source","Bezugskoerper")
		obj.addProperty("App::PropertyInteger","faceNumber","Source","Nummer der Flaeche").faceNumber=0
		obj.addProperty("App::PropertyEnumeration","mode","Format","Darstellung als Dreibein oder Kruemmungskreise").mode="UV-Tripod","Curvature"
		obj.addProperty("App::PropertyFloat","u","UV","u position un uv space").u=50
		obj.addProperty("App::PropertyFloat","v","UV","v position in uv space").v=50
		
		obj.addProperty("App::PropertyFloat","scale","Format","Size of the tripod legs").scale=100
		obj.addProperty("App::PropertyFloat","maxRadius","Format","maximum curvature circle").maxRadius=1000
		obj.addProperty("App::PropertyBool","directionNormal","Format","Auf dem Fuss oder auf dem Kopf stehen").directionNormal=True
		obj.ViewObject.LineColor=(1.0,0.0,1.0)

	def onChanged(self, fp, prop):
		''' recompute the shape, compute and print the curvature '''
		if prop=="Shape": return

		try: fp.u, fp.v, fp.directionNormal,fp.Shape,fp.source,fp.faceNumber
		except: return
		if fp.source==None: return

		u=fp.u/12*3.14
		v=fp.v/12*3.14

		if fp.u<0:fp.u=0
		if fp.v<0:fp.v=0

		u=0.01*fp.u
		v=0.01*fp.v

#		u=fp.u/12*3.14/100
#		v=fp.v/12*3.14/100

		if fp.mode=="Curvature":
			self.runmode2(fp,prop)
			return


		f=fp.source.Shape.Faces[fp.faceNumber-1]
		nf=f.toNurbs()

		sf=nf.Face1.Surface

		#sf=fp.source.Shape.Faces[fp.faceNumber-1].Surface

		# point
		vf=sf.value(u,v)

		# tangents
		t1,t2=sf.tangent(u,v)
		t1 *= fp.scale
		t2 *= fp.scale

		l1=t1.add(vf)
		#li1=Part.Line(vf,l1)
		print vf
		
		li1=Part.makePolygon([vf,l1])
		l2=t2.add(vf)
		#li2=Part.Line(vf,l2)
		li2=Part.makePolygon([vf,l2])

		# normal
		if fp.directionNormal: n=t1.cross(t2).normalize()
		else: 
			n=t2.cross(t1).normalize()

		n *= fp.scale
		l3=n.add(vf)
		#li3=Part.Line(vf,l3)
		li3=Part.makePolygon([vf,l3])

		# tripod
		lins=[li1,li2,li3]
		comp=Part.Compound([lu for lu in lins])
		fp.Shape=comp
		
		if 0:
			try:
				
				self.pts += [vf]
				#pts=self.w.Points + [vf]
				print "++++",self.pts
			except:
				self.pts = [FreeCAD.Vector(),vf]
			self.w.Shape=Part.makePolygon(self.pts)
			#self.w.Closed=False
			#App.ActiveDocument.recompute()


		kruemmung(sf,u,v)



	def runmode2(self, fp, prop):

		f=fp.source.Shape.Faces[fp.faceNumber-1]
		nf=f.toNurbs()

		ff=nf.Face1
		ff.ParameterRange

		sf=ff.Surface

		u=0.01*fp.u
		v=0.01*fp.v

		p=sf.value(u,v)
		[t1,t2]=sf.tangent(u,v)
		sf.parameter(t1)
		sf.parameter(t2)

		c1,c2=sf.curvatureDirections(u,v)

		cmax=sf.curvature(u,v,"Max")
		cmin=sf.curvature(u,v,"Min")

		if cmax <>0:
			rmax=1.0/cmax
		else:
			rmax=0 

		if cmin <>0:
			rmin=1.0/cmin
		else:
			rmin=0

		n=sf.normal(u,v)

		if rmax>fp.maxRadius:
			rmax=fp.maxRadius
			cmax=0
		if rmax<-fp.maxRadius:
			rmax=-fp.maxRadius
			cmax=0
		if rmin>fp.maxRadius:
			rmin=fp.maxRadius
			cmin=0
		if rmin<-fp.maxRadius:
			rmin=-fp.maxRadius
			cmin=0

		m2=p+n*rmin 
		m1=p+n*rmax 

		pts=[p,m2,p,m1]
		print (rmin,rmax)
		comp=[]

		try:
			comp +=[Part.makePolygon([p,m2])]
		except:
			pass

		try:
			comp += [Part.makePolygon([p,m1])]
		except:
			pass

		k=fp.maxRadius


		if cmax==0:
			c=Part.makePolygon([p-c1*k,p+c1*k])
		else:	
			c=Part.makeCircle(abs(rmax),m1,c2)

		comp += [c]

		if cmin==0:
			c=Part.makePolygon([p-c2*k,p+c2*k])
		else:	
			c=Part.makeCircle(abs(rmin),m2,c1)

		comp += [c]

		print "done"
		fp.Shape=Part.Compound(comp)
		# fp.Shape=Part.Compound(comp[:1])



def createTripod():

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Tripod")
	Tripod(a)
	a.ViewObject.LineWidth = 2
	a.source=Gui.Selection.getSelection()[0]
	ViewProvider(a.ViewObject)

