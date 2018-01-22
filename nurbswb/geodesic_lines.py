
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

def hideAllProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		obj.setEditorMode(pn,2)

def readonlyProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		try: obj.setEditorMode(pn,1)
		except: pass

def setWritableAllProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		obj.setEditorMode(pn,0)

class Geodesic(FeaturePython):
	def __init__(self, obj,patch=False,uc=5,vc=5):
		FeaturePython.__init__(self, obj)

		obj.addProperty("App::PropertyEnumeration","mode","Base").mode=["geodesic","curvature","patch"]
		obj.addProperty("App::PropertyLink","obj","","surface object")
		obj.addProperty("App::PropertyInteger","facenumber","", "number of the face")
		

		if not patch:
			obj.addProperty("App::PropertyInteger","gridsize","", "size of a grid cell").gridsize=20

			obj.addProperty("App::PropertyFloat","u","Source", "u coord start point of geodesic").u=50
			obj.addProperty("App::PropertyFloat","v","Source", "v coord start point of geodesic").v=50

			obj.addProperty("App::PropertyFloat","ue","_calculated", "calculated u coord endpoint of geodesic")
			obj.addProperty("App::PropertyFloat","ve","_calculated", "calculated coord endpoint of geodesic")

			obj.addProperty("App::PropertyFloat","ut","Target", "u coord target point of geodesic").ut=60
			obj.addProperty("App::PropertyFloat","vt","Target", "u coord target point of geodesic").vt=60
			obj.addProperty("App::PropertyInteger","lang","Generator", "size of cell in u direction").lang=24
			obj.addProperty("App::PropertyInteger","lang2","Generator", "size of cell in v direction").lang2=3
			obj.addProperty("App::PropertyInteger","lang3","Generator", "size of cell in -u direction").lang3=6
#			obj.addProperty("App::PropertyInteger","lang4","Generator", "size of cell in -v direction").lang4=10

			obj.addProperty("App::PropertyFloat","direction","Generator", "direction of backbone geodesic")
			obj.direction=0
			obj.addProperty("App::PropertyFloat","directione","_calculated", "calculated direction of backbone geodesic")
			obj.directione=0

			obj.addProperty("App::PropertyFloat","directionrib","Generator", "direction of rib geodesics")
			obj.directionrib=90

			

			obj.addProperty("App::PropertyBool","flip","Star", "flip the curvature direction")
			obj.addProperty("App::PropertyBool","redirect","Star", "flip the curvature direction")
			obj.addProperty("App::PropertyBool","star","Star", "calculate all 4 directions")

			obj.addProperty("App::PropertyFloat","dist","_calculated","calculated distance of endpoint (ue,ve) to target (ut,vt)")
			obj.addProperty("App::PropertyLink","pre","XYZ","")

			obj.addProperty("App::PropertyFloatList","uvdarray","_storage","storage data uvd for geodesic field")
			obj.addProperty("App::PropertyInteger","uvdUdim","_storage","u dimension of uvdarray")
			obj.addProperty("App::PropertyInteger","uvdVdim","_storage","v dimension of uvdarray")

			obj.addProperty("App::PropertyLink","geogrid","geodesic","")
			obj.addProperty("App::PropertyLink","geoborder","geodesic","")
			obj.addProperty("App::PropertyLink","geobone","geodesic","")

		if patch:
			obj.addProperty("App::PropertyBool","patch","patch", ).patch=True
#			obj.addProperty("App::PropertyLink","track","patch","")
#			obj.addProperty("App::PropertyLink","face","patch","")
			obj.addProperty("App::PropertyLink","wire","patch","")

			obj.addProperty("App::PropertyEnumeration","form","patch","layout fo the 3D curve").form=["polygon","bspline1","bspline3",'facecurve','face']
			obj.form='polygon'
			obj.addProperty("App::PropertyFloat","tolerance","patch").tolerance=2.0
			obj.addProperty("App::PropertyBool","closed","patch")
			obj.addProperty("App::PropertyBool","reverse","patch")
#			obj.addProperty("App::PropertyInteger","ind1Face","patch","v dimension of uvdarray").ind1Face=0
#			obj.addProperty("App::PropertyInteger","ind2Face","patch","v dimension of uvdarray").ind2Face=0


		readonlyProps(obj,['mode','pre','directionrib','lang4','directione','dist','ue','ve'])
		if obj.mode=='patch':
			obj.Shape=updatePatch(obj)



	def attach(self,vobj):
		print "attach -------------------------------------"
		self.Object = vobj.Object
		self.obj2 = vobj.Object

	def onChanged(self, fp, prop):
		return
		if prop=="direction":
			try:  self.execute(fp)
			except: pass


	def execute(self, fp):
		try: fp.mode
		except:pass
		if fp.mode=="geodesic":
			fp.Shape=updateStarG(fp)
		if fp.mode=="patch":
			fp.Shape=updatePatch(fp)
			if fp.form=='face':
				fp.Placement=fp.obj.obj.Placement
			else:
				fp.Placement=FreeCAD.Placement()	
		if fp.mode=="curvature":
			fp.Shape=updateStarC(fp)





def createGeodesic(obj=None):
	'''create a testcase sketch'''

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Geodesic")

	Geodesic(a)
	a.obj=obj
	ViewProvider(a.ViewObject)
	if obj<>None:
		a.Label="Geodesic for "+obj.Label
	a.mode="geodesic"


	a.lang=40
	a.lang2=20
	a.lang3=40
	a.direction=30

#	hideAllProps(a,['patch'])
	return a


def createPatch(obj=None,wire=None):
	'''create a testcase sketch'''

	try: _=obj.uvdUdim
	except: obj,wire=wire,obj


	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Patch")

	Geodesic(a,True)
	a.obj=obj
	a.wire=wire

	ViewProvider(a.ViewObject)
	if obj<>None:
		a.Label="Patch for "+obj.Label
	a.mode="patch"
	
#	hideAllProps(a)
	return a
#	a.u=10
#	a.v=55
	a.lang=20
	a.direction=-60

	# ovben drauf
#	a.u=1
#	a.v=50
	a.lang=204
	a.lang=120+24
	a.lang=36
#	a.u=40
	
	a.direction=0


	return a






def createCurvature(obj=None):
	'''create a testcase sketch'''

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Curvature")

	Geodesic(a)
	a.obj=obj
	a.u=10
	a.v=55
	ViewProvider(a.ViewObject)
	a.Label="Curvature for "+obj.Label
	a.mode="curvature"
	a.star=True
	a.lang=120
	a.direction=-60
	return a





def colorPath(pts,color='0 1 0',name=None):

	def ivPts(pts):
		'''  points to iv format '''
		s=''
		for p in pts:
			s +=  "{} {} {}, ".format(p.x,p.y,p.z) 
		return s

	buf='''
	#Inventor V2.1 ascii
	  Separator {
		 Transform { translation %s }
		 Material { diffuseColor %s specularColor 1 1 1 shininess 0.9 }
#		 Shuttle { translation0 -1 0 -1 translation1 1 0 1 speed 0.3 on TRUE }
		 Coordinate3 { point [ %s ] }
		 LineSet { 
			#numVertices [ 7 ]
		 }
	  }
	'''
	if name <>None:
		iv=App.ActiveDocument.getObject(name)
		if iv==None:iv=App.ActiveDocument.addObject("App::InventorObject",name)

		iv.Buffer=buf % ('0 0 0','0 1 0',ivPts(pts2)) +bufa + buf % ('10 2 10','1 0 1',ivPts(pts2))
		iv.Buffer=buf % ('0 0 0',color,ivPts(pts))
	else: 
		return buf % ('0 0 0',color,ivPts(pts))

def uvtopt(uvs,sf,uvsarr):

	pts=[[5,7],[12,15],[20,15],[20,2],[7,7]]
	pts2=[]
	for [uk,vk] in pts:
			(u,v)=arr[uk,vk]
			pt=sf.value(u,v)
			print pt
			pts2 += [pt]
	return pts2




def genrib(fp,u,v,d,lang,ribflag,color='0 1 1'):
		''' erzeugt eine rippe) '''

		obj=fp.obj
		pts=[]

		f=obj.Shape.Faces[fp.facenumber]
		sf=f.Surface
		umin,umax,vmin,vmax=f.ParameterRange


		uvs=[(u,v)]
		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*d/180)*t1+np.sin(np.pi*d/180)*t2)

		lang=int(round(lang))
		#print "loops genrib",lang
		for i in range(lang):
			pot=sf.value(u,v)
			u2=(u-umin)/(umax-umin)
			v2=(v-vmin)/(vmax-vmin)
			pts += [pot]


			if ribflag:
				pts += [pot+ sf.normal(u,v)*0.5*fp.gridsize*0.1,pot]
				pts += [pot+ sf.normal(u,v).cross(t)*2.5*fp.gridsize*0.1,pot]
				pts += [pot+ sf.normal(u,v).cross(t)*-2.5*fp.gridsize*0.1,pot]


			last=sf.value(u,v)
			p2=last+t*fp.gridsize*0.1
			print "p2xx ",p2
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)
			if u<umin:u=umin
			if v<vmin:v=vmin
			if u>umax:u=umax
			if v>vmax:v=vmax
			uvs += [(u,v)]


			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
				break
			p=sf.value(u,v)

			pts += [ p]
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()

		cps=None
		if ribflag:
			try: 
				#shape=Part.makePolygon(pts)
				cps=colorPath(pts,color=color,name=None)
			except: shape=None
		else: shape=None

		return (cps,(u,v),uvs)



def getface(count=10):
	faceobj=App.ActiveDocument.BSpline
	bs=faceobj.Shape.Face1
	track=App.ActiveDocument.Line.Shape

	ptsa=[]
	ptsb=[]

	try: curve=track.Curve
	except: curve=track.Edges[0].Curve


	#print track.Edges

	cc=int(round(track.Length))
	tps=track.discretize(cc)

	col2=[]
	for p in tps:
			v=curve.parameter(p)
			t=curve.tangent(v)
			n=t[0].cross(FreeCAD.Vector(0,0,1))
			polg=Part.makePolygon([p+10000*n,p-10000*n])
			col2 += [polg]
			
			ss=bs.makeParallelProjection(polg,FreeCAD.Vector(0,0,1))
			sps=[v.Point for v in ss.Vertexes]
			#print sps
			if len(sps) == 2:
				ptsa += [sps[0]]
				ptsb += [sps[1]]
			if len(sps) == 1:
				ptsa += [sps[0]]
				ptsb += [sps[0]]

	ppsa=[]
	ppsb=[]

	segments=App.ActiveDocument.getObject("Segments")
	if segments==None:
		segments=App.ActiveDocument.addObject("Part::Feature","Segments")

	pls=[]
	nls=[]
	comp=[]
	f=0.4
	f=count/track.Length
	f=1
	for i,p in enumerate(ptsa):
		if ptsa[i]<>ptsb[i]:
			pol=Part.makePolygon([ptsa[i],ptsb[i]])
			comp.append(pol)
#			print(i, (ptsa[i]-tps[i]).Length,(ptsb[i]-tps[i]).Length)

			pls += [(ptsa[i]-tps[i]).Length*f]
			nls += [(ptsb[i]-tps[i]).Length*f]
	segments.Shape=Part.Compound(comp)
	return track.Length, pls,nls


def drawColorLines(fp,name,ivs):
	iv=App.ActiveDocument.getObject(fp.Name+"_"+name)
	if iv==None:iv=App.ActiveDocument.addObject("App::InventorObject",fp.Name+"_"+name)
	iv.Label=name + " for " +fp.Label
	iv.Buffer=ivs




def updateStarG(fp):
		print "run updateStarG"

		gridon=True

		ta=time.time()
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

		u0,v0=u,v
		
		u=umin + (umax-umin)*u
		v=vmin + (vmax-vmin)*v

		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*-d/180)*t1*-1+np.sin(-np.pi*-d/180)*t2*-1)

		shapas=''
		puvs=[(u,v)]
		nuvs=[(u,v)]

		puvs=[]
		nuvs=[]


		uvsarr=[]


		lang3=int(round(10.0*fp.lang3/fp.gridsize))
		lang=int(round(10*fp.lang/fp.gridsize))
		lang2=int(round(10*fp.lang2/fp.gridsize))

		#rueckwaerts
		ribb=''
		riba=''

		for i in range(lang3+1):
			taa=time.time()
			if 1 or i % 2 == 0 or i==fp.lang:
				ribflag= i%5 == 0 and gridon
				if i==lang3: ribflag=True
				
#				print ("erzeuge ribbe",i)
				a=t.dot(t1)
				b=t.dot(t2)
				de=-180./np.pi*np.arctan2(b,a)
				if i==lang3 : color='0 1 0'
				#else: color='0 1 1'
				else: color='1 1 0'
				r1,(u1,v1),uvs1 = genrib(fp,u,v,de+90+2*d,lang2,ribflag,color)
				r2,(u2,v2),uvs2 = genrib(fp,u,v,de-90+2*d,lang2,ribflag,color)
				nuvs += [(u1,v1)]
				puvs += [(u2,v2)]
				uvs2.reverse()
				if i<>0:
					uvsarr += [uvs2[:-1]+uvs1]
				if ribflag:
					if i<>0:
						shapas += r1 + r2
				if i==0:
					ribm=r1+r2
				if i==lang3:
					ribb=r1+r2


			pot=sf.value(u,v)
			u2=(u-umin)/(umax-umin)
			v2=(v-vmin)/(vmax-vmin)
			pts += [pot]

			pts += [sf.value(u,v)+ sf.normal(u,v)*2,sf.value(u,v)]

			# ribs
			if 1:
				rib=FreeCAD.Vector(np.cos(np.pi*d2/180)*t+np.sin(np.pi*d2/180)*sf.normal(u,v).cross(t))
				pts += [sf.value(u,v)+ rib*-2,sf.value(u,v)]
				pts += [sf.value(u,v)+ rib*2,sf.value(u,v)]


			last=sf.value(u,v)
			p2=last+t*0.1*fp.gridsize
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)
			
			if u<umin:u=umin
			if v<vmin:v=vmin
			if u>umax:u=umax
			if v>vmax:v=vmax


			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
			
				break
			p=sf.value(u,v)

			pts += [ p]
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()
			tbb=time.time()
			# print ("time aa bb,loop",tbb-taa,i,(tbb-taa)/fp.lang*1000000/lang2)





		#-------------------------------------

		u=umin + (umax-umin)*u0
		v=vmin + (vmax-vmin)*v0

		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*d/180)*t1+np.sin(np.pi*d/180)*t2)

#		shapas=''

#		puvs += [(u,v)]
#		nuvs += [(u,v)]

		puvs.reverse()
		nuvs.reverse()
		aa=[]
		for j in range(len(uvsarr)):
			a= uvsarr[-1-j]
			a.reverse()
			aa += [a]
		uvsarr=aa

		for i in range(lang+1):
			taa=time.time()
			if 1 or i % 2 == 0 or i==lang:
				ribflag= i%5 == 0 and gridon
				if i==lang: ribflag=True
				
#				print ("erzeuge ribbe",i)
				a=t.dot(t1)
				b=t.dot(t2)
				de=180./np.pi*np.arctan2(b,a)
				if i==lang: color='1 0 0'
				else: color='1 1 0'
				r1,(u1,v1),uvs1 = genrib(fp,u,v,de+90,lang2,ribflag,color)
				r2,(u2,v2),uvs2 = genrib(fp,u,v,de-90,lang2,ribflag,color)
				if 1:
					puvs += [(u1,v1)]
					nuvs += [(u2,v2)]
				uvs2.reverse()
				uvsarr += [uvs2[:-1]+uvs1]
				if ribflag:
					shapas += r1 + r2
#				if i==0:
#					riba=r1+r2
				if i==lang:
					riba=r1+r2


			pot=sf.value(u,v)
			u2=(u-umin)/(umax-umin)
			v2=(v-vmin)/(vmax-vmin)
			pts += [pot]

			pts += [sf.value(u,v)+ sf.normal(u,v)*2,sf.value(u,v)]

			# ribs
			if 1:
				rib=FreeCAD.Vector(np.cos(np.pi*d2/180)*t+np.sin(np.pi*d2/180)*sf.normal(u,v).cross(t))
				pts += [sf.value(u,v)+ rib*-2,sf.value(u,v)]
				pts += [sf.value(u,v)+ rib*2,sf.value(u,v)]


			last=sf.value(u,v)
			p2=last+t*fp.gridsize*0.1
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)

			if u<umin:u=umin
			if v<vmin:v=vmin
			if u>umax:u=umax
			if v>vmax:v=vmax

			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
				break

			p=sf.value(u,v)

			pts += [ p]
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()
			tbb=time.time()
			# print ("time aa bb,loop",tbb-taa,i,(tbb-taa)/fp.lang*1000000/lang2)


		FreeCAD.uvsarr=np.array(uvsarr)
		FreeCAD.sf=sf
		print "size uvs arr",FreeCAD.uvsarr.shape
		print (fp.lang,lang2)
		ar=np.array(uvsarr)
		(a,b,c)=ar.shape
		fp.uvdarray=list(ar.reshape(a*b*c))
		fp.uvdUdim=a
		fp.uvdVdim=b

		puvs+=[(u,v)]
		nuvs+=[(u,v)]


		shape=Part.makePolygon(pts)
		cp1=colorPath(pts,color='1 1 0',name=None)
		
		ppts=[sf.value(u,v) for (u,v) in puvs]
		pshape=Part.makePolygon(ppts)
		cp2=colorPath(ppts[:-1],color='0 0 1',name=None)
		
		npts=[sf.value(u,v) for (u,v) in nuvs]
		nshape=Part.makePolygon(npts)
		cp3=colorPath(npts[:-1],color='0 0 1',name=None)



		name="VBound"
		drawColorLines(fp,name,cp1+cp2+cp3)
		#drawColorLines(fp,name,cp1)

		tb=time.time()
		print ("time a - b:",tb-ta)

		ut=fp.ut*0.01
		vt=fp.vt*0.01
#		pt=Part.Point(sf.value(ut,vt))
#		print "Abstand"
#		print pt
#		print shape.distToShape(pt.toShape())
#		print (pt,shape.distToShape(pt.toShape())[0])


		pend=sf.value(ut,vt)
		pt=Part.Point(sf.value(ut,vt))
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
				])]+[pshape] )

		shape2=Part.Compound([shape,pshape,nshape])
		shape2=shape

		if gridon:
			name="Grid"
			drawColorLines(fp,name,shapas)

			name="UBound"
			drawColorLines(fp,name,riba+ribm+ribb)


		#shape2=shape
		return shape2
	#Draft.makeWire(pts)


def updatePatch_old(fp):
		print "run update Patch"

		gridon=True

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
		umin,umax,vmin,vmax=f.ParameterRange

		u=umin + (umax-umin)*u
		v=vmin + (vmax-vmin)*v

		(t1,t2)=sf.tangent(u,v)
		t=FreeCAD.Vector(np.cos(np.pi*d/180)*t1+np.sin(np.pi*d/180)*t2)

		shapas=''
		puvs=[(u,v)]
		nuvs=[(u,v)]

		lang,ptsa,ntsa=getface(2+fp.lang+1)

		pds=[4+p for p in ptsa]
		nds=[4+p for p in ntsa]

		uvsp=[]

		for i in range(fp.lang+1):

			if i % 2 == 0 or i==fp.lang:
				ribflag= i%5 == 0 and gridon
				if i==fp.lang: ribflag=True
 
#				print ("erzeuge ribbe",i)
				a=t.dot(t1)
				b=t.dot(t2)
				de=180./np.pi*np.arctan2(b,a)
				r1,(u1,v1),uvs1 = genrib(fp,u,v,de+90,ptsa[i],ribflag)
				r2,(u2,v2),uvs2 = genrib(fp,u,v,de-90,ntsa[i],ribflag)
				puvs += [(u1,v1)]
				nuvs += [(u2,v2)]
				uvsp += [uvs1]
				if ribflag:
					shapas += r1 + r2
				if i==0:
					riba=r1+r2
				if i==fp.lang:
					ribb=r1+r2


			pot=sf.value(u,v)
			u2=(u-umin)/(umax-umin)
			v2=(v-vmin)/(vmax-vmin)
			pts += [pot]

			pts += [sf.value(u,v)+ sf.normal(u,v)*2,sf.value(u,v)]

			# ribs
			if 1:
				rib=FreeCAD.Vector(np.cos(np.pi*d2/180)*t+np.sin(np.pi*d2/180)*sf.normal(u,v).cross(t))
				pts += [sf.value(u,v)+ rib*-3,sf.value(u,v)]
				pts += [sf.value(u,v)+ rib*3,sf.value(u,v)]

			last=sf.value(u,v)
			p2=last+t*1
			(u1,v1)=sf.parameter(p2)
			(u,v)=(u1,v1)

			if u<umin:u=umin
			if v<vmin:v=vmin
			if u>umax:u=umax
			if v>vmax:v=vmax

			if u<umin or v<vmin or u>umax or v>vmax:
				print "qaBBruch!"
				break
			p=sf.value(u,v)

			pts += [ p]
			(t1,t2)=sf.tangent(u,v)
			t=p-last
			t.normalize()


		FreeCAD.uvsp=uvsp
		FreeCAD.sf=sf
#		if hasattr(obj,"uvdarray"):
#		fp.uvdarray=list(np.array(uvsp).reshape(lang*lang2*2))

		puvs+=[(u,v)]
		nuvs+=[(u,v)]




		shape=Part.makePolygon(pts)
		cp1=colorPath(pts,color='1 0 0',name=None)
		
		ppts=[sf.value(u,v) for (u,v) in puvs[1:-1]]
		pshape=Part.makePolygon(ppts)
		cp2=colorPath(ppts,color='0 1 0',name=None)
		
		npts=[sf.value(u,v) for (u,v) in nuvs[1:-1]]
		nshape=Part.makePolygon(npts)
		cp3=colorPath(npts,color='0 0 1',name=None)


		name="geodesicBorder"
		drawColorLines(name,cp1+cp2+cp3)




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
				])]+[pshape] )

		shape2=Part.Compound([shape,pshape,nshape])

		if gridon:
			name="geodesicGrid"
			drawColorLines(name,shapas)

			name="borders"
			drawColorLines(name,riba+ribb)


		#shape2=shape
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
			
			if u<umin:u=umin
			if v<vmin:v=vmin
			if u>umax:u=umax
			if v>vmax:v=vmax

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




def runtest1():
	a=createGeodesic(obj=App.ActiveDocument.Poles)
	b=createGeodesic(obj=App.ActiveDocument.Cylinder)
	d=createGeodesic(obj=App.ActiveDocument.Cone)
	d=createGeodesic(obj=App.ActiveDocument.Sphere)


def run():
	a=createGeodesic(obj=Gui.Selection.getSelection()[0])

def runP():
	a=createPatch(obj=Gui.Selection.getSelection()[0],
	wire=Gui.Selection.getSelection()[1])


def runD():
	a=createGeodesic()
	a.pre=Gui.Selection.getSelection()[0]



def runC():
	a=createCurvature(obj=Gui.Selection.getSelection()[0])


def runall():
	for j in range(36):
		a=createGeodesic(obj=Gui.Selection.getSelection()[0])
		a.direction=j*10



# http://cyberware.com/wb-vrml/index.html

def  wireToPolygon(w):
	pts=[]
	yy=0.2
	for e in w.Edges:
		print (e, e.Length)
		if e.Length>1:
			zz=e.discretize(int(round(e.Length)+1))
			zz[0],zz[0]+yy*(zz[1]-zz[0])
			pts += [zz[0],zz[0]+yy*(zz[1]-zz[0])]+zz[1:-1]+ [zz[-1]+yy*(zz[-2]-zz[-1]),zz[-1]]
	#pol=Part.makePolygon(pts)
	return pts





def updatePatch(fp):


	gd=fp.obj

	try:
		udim=gd.uvdUdim
		vdim=gd.uvdVdim
	except:
		return Part.Shape()

	usvarr=np.array(gd.uvdarray).reshape(udim,vdim,2)
	sf=gd.obj.Shape.Face1.Surface

	# bound box fuer rahmen
	print fp.wire.Shape.BoundBox
	bb=fp.wire.Shape.BoundBox
	l3=-bb.XMin
	if l3<0: l3=0
	l=bb.XMax
	l2=max(bb.YMax,abs(bb.YMin))
	print (l,l2,l3)
	
	needupd=False
	if gd.lang<l: gd.lang=int(round(l))+1;needupd=True
	if gd.lang2<l2:	gd.lang2=int(round(l2))+1;needupd=True
	if gd.lang3<l3:	gd.lang3=int(round(l3))+1;needupd=True
	if needupd:
		gd.Proxy.execute(gd.obj)


	# erster fall nur ein wire #+#
	try: ws= fp.wire.Shape.Wires
	except: ws=None
	
	if ws <> None: ws2=ws
	else: ws2=[fp.wire.Shape]

	print ws
	print ws2
	ress=[]
	for w in ws2:
		print ("loop",w,ress)
		pts=w.discretize(1000)

		# anderer weg der zerlegnung
		pts=wireToPolygon(w)

		uvs=[]
		ul,vl=(-10000,-10000)
		


		for p in pts:
			(u,v) = int(round(p.x*10.0/gd.gridsize)),int(round(p.y*10.0/gd.gridsize))
			print (u,v)

#			u += gd.lang3
#			v += gd.lang2

			u += int(round(gd.lang3*10.0/gd.gridsize))
			v += int(round(gd.lang2*10.0/gd.gridsize))


			if u>=udim: u=udim-1
			if v>=vdim: v=vdim-1


			if (u,v) <>(ul,vl):
				uvs += [(u,v)]
				ul,vl=u,v

		# ausgangskurve 2D
		pts2=[FreeCAD.Vector(u,v,0) for (u,v) in uvs]

		# berechne 3D Kurve ..
		pts=[]
		print usvarr.shape
		print "A"
		
		for up,vp in uvs:
			print (up,vp)
			(u,v)=usvarr[up,vp]
			print (up,vp,u,v,sf.value(u,v))
			pts += [sf.value(u,v)]

#		pts=pts[:-1]
		if fp.closed:
			pts=pts[5:]+pts[1:6]


		#---------------------
		if fp.form=='facecurve':
			t=sf
			pts2da=[sf.parameter(p) for p in pts[1:]]
			pts2d=[FreeCAD.Base.Vector2d(p[0],p[1]) for p in pts2da]

			bs2d = Part.Geom2d.BSplineCurve2d()
			bs2d.setPeriodic()

			bs2d.interpolate(pts2d)
			bs2d.setPeriodic()

			e1 = bs2d.toShape(t)
			print "huhu"
			return e1
		#----------------------

		if fp.form=='face':
			t=sf
			pts2da=[sf.parameter(p) for p in pts[1:]]
			pts2d=[FreeCAD.Base.Vector2d(p[0],p[1]) for p in pts2da]

			bs2d = Part.Geom2d.BSplineCurve2d()
			bs2d.setPeriodic()

			bs2d.interpolate(pts2d)
			bs2d.setPeriodic()

			e1 = bs2d.toShape(t)
			if fp.reverse:
				e1.reverse()

			face=gd.obj.Shape.Face1
			splita=[(e1,face)]
			r=Part.makeSplitShape(face, splita)
			rc=r[0][0]
#			rc.Placement=gd.obj.Placement
			return rc


		if fp.form=='polygon':
			shape=Part.makePolygon(pts)
			if ws <> None: ress += [shape]
			else:
				return shape

		if fp.form=='bspline1':
			bc=Part.BSplineCurve()
			bc.approximate(pts,DegMin=1,DegMax=1,Tolerance=fp.tolerance)
			#if fp.closed: bc.setPeriodic()
			if ws <> None: ress += [bc.toShape()]
			else:
				return bc.toShape()

		if fp.form=='bspline3':
			bc=Part.BSplineCurve()
			bc.approximate(pts,DegMax=3,Tolerance=fp.tolerance)
			#if fp.closed: bc.setPeriodic()
			if ws <> None: ress += [bc.toShape()]
			else:
				return bc.toShape()

			# schnelle unexakte flaeche
#			ss=bc.toShape()
#			return Part.makeFilledFace(ss.Edges)
#			return bc.toShape()


	print "liefere compound"
	print ress
	comp=Part.Compound(ress)
	return comp


	
