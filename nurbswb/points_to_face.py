import numpy as np
import random


import nurbswb
from nurbswb.pyob import  FeaturePython,ViewProvider
from nurbswb.say import *
reload (nurbswb.pyob)

#-------------------------

import numpy as np
from FreeCAD import Vector
import Draft
import scipy.linalg.lapack as sp
from numpy.linalg import inv


def power(a,b):
	return a**b


def crossProduct(a,b):
	return a.cross(b)

def dotProduct(a,b):
	return a.dot(b)

def sign(x):
	return 1. if x>=0 else -1.

def sqrt(a):
	return a**0.5




def drawConeA(name,i,bounds,apex,axis,alpha,trafo,pts):

	trafo=trafo.inverse()
	v=FreeCAD.Vector(0,0,1)

	pss=[]

	[h1,h2]=bounds
	h2+=10
	h1-=10

	if alpha>np.pi/2: alpha= np.pi-alpha



	if h2>10:
		cc=Part.makeCone(0,abs(np.tan(alpha))*h2,h2)
		cc.Placement.Rotation=FreeCAD.Rotation(v,axis)
		cc.Placement.Base=apex
		pss += [cc]

	if h1<-10:
		c2c=Part.makeCone(0,abs(np.tan(alpha))*-h1,-h1)
		c2c.Placement.Rotation=FreeCAD.Rotation(-v,axis)
		c2c.Placement.Base=apex
		pss += [c2c]

	if 0:
		s=Part.makeSphere(3)
		s.Placement.Base=apex
		pss += [s]

	for p in pts:
		ps=Part.makeSphere(3)
		ps.Placement.Base=p
		ps.Placement=trafo.multiply(ps.Placement)
	#	pss += [ps]

	nn="__"+name+"_"+str(i)
	yy=App.ActiveDocument.getObject(nn)
	if yy==None:
		yy=App.ActiveDocument.addObject("Part::Feature",nn)
		yy.ViewObject.Transparency=10
		yy.ViewObject.ShapeColor=(random.random(),random.random(),random.random())

	# nure fleache als nurbs
	ccokay=True
	
	if h2>10:
		nurbs=cc.toNurbs()
#		print "---------NURBS -------", nurbs
		sf=nurbs.Face1.Surface.copy()
		us=[]
		vs=[]
		for p in pts:
			(u,v)=sf.parameter(p)
			if (sf.value(u,v)-p).Length>0.1:
				ccokay=False
			us += [u]
			vs += [v]
#		print us
#		print vs
		umi=min(us)
		uma=max(us)
		vmi=min(vs)
		vma=max(vs)
	else:
		ccokay=False

	if not ccokay:
		nurbs=c2c.toNurbs()
#		print "---------NURBS -------", nurbs
		sf=nurbs.Face1.Surface.copy()
		us=[]
		vs=[]
		for p in pts:
			(u,v)=sf.parameter(p)
			if (sf.value(u,v)-p).Length>0.1:
				ccokay=False
			us += [u]
			vs += [v]
#		print us
#		print vs
		umi=min(us)
		uma=max(us)
		vmi=min(vs)
		vma=max(vs)

	if 0:
		try:
			sf.segment(umi,uma,vmi,vma)
			yy.Shape= sf.toShape()
		except:
			yy.Shape=Part.Compound(pss)
		if not ccokay:
			yy.Shape=Part.Compound(pss)
	else:
		yy.Shape=Part.Compound(pss)

	yy.Placement=trafo
	yy.purgeTouched()


def drawCone(apex,axis,alpha,h,trafo,pts):

	trafo=trafo.inverse()
	axis=axis.normalize()
	lens=[(p-apex).dot(axis) for p in pts] #+ [-1,1]

	if 0: # display apex as ball
		s=Part.makeSphere(2)
		s.Placement.Base=apex
		pss=[s]
	else:
		pss=[]

	for p in pts:
		r=(p-apex).cross(axis).Length
		c=Part.makeCircle(r)
		c.Placement.Base=apex+axis*((p-apex).dot(axis))
		c.Placement.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),axis)
		pss += [c]

	mima=[min(lens),max(lens)]
#	print "minma",mima
	mi = min(mima[0],10)
	ma = max(mima[1],10)

	pss += [Part.makePolygon([apex,apex+axis*ma*1.1,apex-axis*mi*1.1])]

	for p in pts:
		pss += [Part.makePolygon([apex,p])]

	for p in pts:
		s=Part.makeSphere(2)
		s.Placement.Base=p
		pss += [s]

	rc=Part.Compound(pss)
	rc.Placement=trafo

	return rc, mima

'''
def normalize():
	# koerper aufrichten und wieder zurueckstellen

	#s=App.ActiveDocument.Wedge.Shape

	p1=s.Vertex6.Point
	p2=s.Vertex8.Point

	v=FreeCAD.Vector(0,0,1)
	r=FreeCAD.Rotation(p2-p1,v)

	App.ActiveDocument.Wedge001.Placement.Rotation=r
	App.ActiveDocument.Wedge001.Placement.Base=p1

def rollback():

	s=App.ActiveDocument.Wedge.Shape

	p1=s.Vertex6.Point
	p2=s.Vertex8.Point

	v=FreeCAD.Vector(0,0,1)
	r=FreeCAD.Rotation(p2-p1,v)

	sa=App.ActiveDocument.Wedge001.Shape

	p1a=sa.Vertex6.Point
	p2a=sa.Vertex8.Point
	print p1a-p2a

	rr=App.ActiveDocument.Wedge001.Placement.Rotation
	r.invert()

	App.ActiveDocument.Wedge001.Placement.Rotation=r.multiply(rr)
	App.ActiveDocument.Wedge001.Placement.Base -= p1
'''




def run_pnppp(name,trafo,displaynumber,displayFaces,p_1,p_2,p_3,p_4):

	N=6
	A_eigen =np.array([  
		0,  0,  0,  0,  -p_4[2]*power(p_2[2],3)*power(p_3[1],2)-power(p_2[2],2)*power(p_3[2],2)*power(p_4[1],2)+p_3[2]*power(p_2[2],3)*power(p_4[1],2)+power(p_2[2],2)*power(p_4[2],2)*power(p_3[1],2)-p_2[2]*power(p_4[2],2)*p_3[2]*power(p_2[1],2)+p_2[2]*power(p_3[2],2)*p_4[2]*power(p_2[1],2),
										-2*power(p_2[2],2)*power(p_4[2],2)*p_3[2]*p_2[0]+2*power(p_2[2],2)*power(p_4[2],2)*p_3[0]*p_3[2]-2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[2]+2*power(p_2[2],2)*power(p_3[2],2)*p_4[2]*p_2[0]-2*power(p_2[2],2)*power(p_3[2],2)*p_4[0]*p_4[2]+2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[2],
					0,  0,  0,  0,  2*p_2[2]*p_4[0]*p_4[2]*p_3[2]*power(p_2[1],2)-2*p_2[2]*p_3[0]*p_3[2]*p_4[2]*power(p_2[1],2)+2*power(p_2[2],2)*power(p_3[2],2)*p_4[2]*p_2[0]+2*p_4[2]*p_2[0]*power(p_2[2],2)*power(p_3[1],2)-2*power(p_2[2],2)*power(p_3[2],2)*p_4[0]*p_4[2]-2*power(p_2[2],2)*p_4[0]*p_4[2]*power(p_3[1],2)+2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[2]-2*power(p_2[2],2)*power(p_4[2],2)*p_3[2]*p_2[0]-2*p_3[2]*p_2[0]*power(p_2[2],2)*power(p_4[1],2)+2*power(p_2[2],2)*power(p_4[2],2)*p_3[0]*p_3[2]+2*power(p_2[2],2)*p_3[0]*p_3[2]*power(p_4[1],2)-2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[2],
										-p_4[2]*power(p_2[2],3)*power(p_3[1],2)-power(p_2[2],2)*power(p_3[2],2)*power(p_4[1],2)+p_3[2]*power(p_2[2],3)*power(p_4[1],2)+power(p_2[2],2)*power(p_4[2],2)*power(p_3[1],2)-p_2[2]*power(p_4[2],2)*p_3[2]*power(p_2[1],2)+p_2[2]*power(p_3[2],2)*p_4[2]*power(p_2[1],2),
					1,  0,  0,  0,  2*p_2[2]*p_4[1]*p_4[2]*p_3[2]*power(p_2[1],2)-2*p_2[2]*p_3[1]*p_3[2]*p_4[2]*power(p_2[1],2)-2*power(p_2[2],3)*p_3[1]*p_3[2]*p_4[2]+2*p_4[2]*p_2[1]*power(p_2[2],2)*power(p_3[2],2)+2*p_4[2]*p_2[1]*power(p_2[2],2)*power(p_3[1],2)-2*power(p_2[2],2)*p_4[1]*p_4[2]*power(p_3[2],2)-2*power(p_2[2],2)*p_4[1]*p_4[2]*power(p_3[1],2)+2*power(p_2[2],3)*p_4[1]*p_4[2]*p_3[2]-2*p_3[2]*p_2[1]*power(p_2[2],2)*power(p_4[2],2)-2*p_3[2]*p_2[1]*power(p_2[2],2)*power(p_4[1],2)+2*power(p_2[2],2)*p_3[1]*p_3[2]*power(p_4[2],2)+2*power(p_2[2],2)*p_3[1]*p_3[2]*power(p_4[1],2),
										4*p_4[2]*p_2[1]*power(p_2[2],2)*p_3[0]*p_3[2]+4*power(p_2[2],2)*p_4[1]*p_4[2]*p_3[2]*p_2[0]-4*power(p_2[2],2)*p_4[1]*p_4[2]*p_3[0]*p_3[2]-4*p_3[2]*p_2[1]*power(p_2[2],2)*p_4[0]*p_4[2]-4*power(p_2[2],2)*p_3[1]*p_3[2]*p_4[2]*p_2[0]+4*power(p_2[2],2)*p_3[1]*p_3[2]*p_4[0]*p_4[2]-2*p_2[2]*power(p_3[2],2)*p_4[2]*p_2[0]*p_2[1]+2*p_2[2]*power(p_4[2],2)*p_3[2]*p_2[0]*p_2[1]+2*power(p_3[2],2)*power(p_2[2],2)*p_4[0]*p_4[1]-2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[1]-2*power(p_4[2],2)*power(p_2[2],2)*p_3[0]*p_3[1]+2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[1],
					0,  1,  0,  0,  -2*p_2[2]*power(p_3[2],2)*p_4[2]*p_2[0]*p_2[1]-2*p_4[2]*p_2[0]*p_2[1]*p_2[2]*power(p_3[1],2)-2*p_2[2]*p_4[0]*p_4[1]*p_3[2]*power(p_2[1],2)+2*p_2[2]*power(p_4[2],2)*p_3[2]*p_2[0]*p_2[1]+2*p_3[2]*p_2[0]*p_2[1]*p_2[2]*power(p_4[1],2)+2*p_2[2]*p_3[0]*p_3[1]*p_4[2]*power(p_2[1],2)+2*power(p_3[2],2)*power(p_2[2],2)*p_4[0]*p_4[1]+2*power(p_2[2],2)*p_4[0]*p_4[1]*power(p_3[1],2)-2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[1]-2*power(p_4[2],2)*power(p_2[2],2)*p_3[0]*p_3[1]-2*power(p_2[2],2)*p_3[0]*p_3[1]*power(p_4[1],2)+2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[1],
										2*p_2[2]*p_4[1]*p_4[2]*p_3[2]*power(p_2[1],2)-2*p_2[2]*p_3[1]*p_3[2]*p_4[2]*power(p_2[1],2)-2*power(p_2[2],3)*p_3[1]*p_3[2]*p_4[2]+2*p_4[2]*p_2[1]*power(p_2[2],2)*power(p_3[2],2)+2*p_4[2]*p_2[1]*power(p_2[2],2)*power(p_3[1],2)-2*power(p_2[2],2)*p_4[1]*p_4[2]*power(p_3[2],2)-2*power(p_2[2],2)*p_4[1]*p_4[2]*power(p_3[1],2)+2*power(p_2[2],3)*p_4[1]*p_4[2]*p_3[2]-2*p_3[2]*p_2[1]*power(p_2[2],2)*power(p_4[2],2)-2*p_3[2]*p_2[1]*power(p_2[2],2)*power(p_4[1],2)+2*power(p_2[2],2)*p_3[1]*p_3[2]*power(p_4[2],2)+2*power(p_2[2],2)*p_3[1]*p_3[2]*power(p_4[1],2),
					0,  0,  1,  0,  -power(p_2[2],2)*power(p_4[0],2)*power(p_3[1],2)+power(p_2[2],3)*power(p_4[0],2)*p_3[2]+p_4[2]*power(p_2[2],3)*power(p_3[1],2)+power(p_2[2],2)*power(p_3[2],2)*power(p_4[1],2)+power(p_2[2],2)*power(p_3[0],2)*power(p_4[2],2)+power(p_2[2],2)*power(p_3[0],2)*power(p_4[1],2)-power(p_2[2],3)*power(p_3[0],2)*p_4[2]-p_3[2]*power(p_2[2],3)*power(p_4[1],2)-power(p_2[2],2)*power(p_4[2],2)*power(p_3[1],2)-power(p_2[2],2)*power(p_4[0],2)*power(p_3[2],2)+p_2[2]*power(p_4[2],2)*p_3[2]*power(p_2[1],2)+p_2[2]*power(p_4[0],2)*p_3[2]*power(p_2[1],2)+p_4[2]*power(p_2[0],2)*p_2[2]*power(p_3[2],2)+p_4[2]*power(p_2[0],2)*p_2[2]*power(p_3[1],2)-p_2[2]*power(p_3[2],2)*p_4[2]*power(p_2[1],2)-p_2[2]*power(p_3[0],2)*p_4[2]*power(p_2[1],2)-p_3[2]*power(p_2[0],2)*p_2[2]*power(p_4[2],2)-p_3[2]*power(p_2[0],2)*p_2[2]*power(p_4[1],2),
										2*p_4[2]*power(p_2[0],2)*p_2[2]*p_3[0]*p_3[2]-4*p_2[1]*p_4[2]*power(p_2[2],2)*p_3[0]*p_3[1]+4*power(p_2[2],2)*p_4[1]*p_4[2]*p_3[0]*p_3[1]-2*p_3[2]*power(p_2[0],2)*p_2[2]*p_4[0]*p_4[2]+4*p_2[1]*p_3[2]*power(p_2[2],2)*p_4[0]*p_4[1]-4*power(p_2[2],2)*p_3[1]*p_3[2]*p_4[0]*p_4[1]+2*power(p_2[2],2)*power(p_4[2],2)*p_3[2]*p_2[0]-2*power(p_2[2],2)*power(p_4[2],2)*p_3[0]*p_3[2]+2*power(p_2[2],2)*power(p_4[0],2)*p_3[2]*p_2[0]-2*power(p_2[2],2)*power(p_4[0],2)*p_3[0]*p_3[2]+2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[2]-2*power(p_2[2],2)*power(p_3[2],2)*p_4[2]*p_2[0]+2*power(p_2[2],2)*power(p_3[2],2)*p_4[0]*p_4[2]-2*power(p_2[2],2)*power(p_3[0],2)*p_4[2]*p_2[0]+2*power(p_2[2],2)*power(p_3[0],2)*p_4[0]*p_4[2]-2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[2]+4*p_2[2]*p_3[1]*p_3[2]*p_4[2]*p_2[0]*p_2[1]-4*p_2[2]*p_4[1]*p_4[2]*p_3[2]*p_2[0]*p_2[1],
					0,  0,  0,  1,  0,  -power(p_2[2],2)*power(p_4[0],2)*power(p_3[1],2)+power(p_2[2],3)*power(p_4[0],2)*p_3[2]+p_4[2]*power(p_2[2],3)*power(p_3[1],2)+power(p_2[2],2)*power(p_3[2],2)*power(p_4[1],2)+power(p_2[2],2)*power(p_3[0],2)*power(p_4[2],2)+power(p_2[2],2)*power(p_3[0],2)*power(p_4[1],2)-power(p_2[2],3)*power(p_3[0],2)*p_4[2]-p_3[2]*power(p_2[2],3)*power(p_4[1],2)-power(p_2[2],2)*power(p_4[2],2)*power(p_3[1],2)-power(p_2[2],2)*power(p_4[0],2)*power(p_3[2],2)+p_2[2]*power(p_4[2],2)*p_3[2]*power(p_2[1],2)+p_2[2]*power(p_4[0],2)*p_3[2]*power(p_2[1],2)+p_4[2]*power(p_2[0],2)*p_2[2]*power(p_3[2],2)+p_4[2]*power(p_2[0],2)*p_2[2]*power(p_3[1],2)-p_2[2]*power(p_3[2],2)*p_4[2]*power(p_2[1],2)-p_2[2]*power(p_3[0],2)*p_4[2]*power(p_2[1],2)-p_3[2]*power(p_2[0],2)*p_2[2]*power(p_4[2],2)-p_3[2]*power(p_2[0],2)*p_2[2]*power(p_4[1],2)
	])

	B_eigen = np.array([ 
		1,  0,  0,  0,  0,  0,
		0,  1,  0,  0,  0,  0,
		0,  0,  1,  0,  0,  0,
		0,  0,  0,  1,  0,  0,
		0,  0,  0,  0,  0,  2*p_2[2]*power(p_4[2],2)*p_3[2]*p_2[0]*p_2[1]+2*p_2[2]*power(p_4[0],2)*p_3[2]*p_2[0]*p_2[1]+2*p_4[2]*power(p_2[0],2)*p_2[2]*p_3[0]*p_3[1]-2*p_2[2]*power(p_3[2],2)*p_4[2]*p_2[0]*p_2[1]-2*p_2[2]*power(p_3[0],2)*p_4[2]*p_2[0]*p_2[1]-2*p_3[2]*power(p_2[0],2)*p_2[2]*p_4[0]*p_4[1]-2*power(p_4[2],2)*power(p_2[2],2)*p_3[0]*p_3[1]-2*power(p_2[2],2)*power(p_4[0],2)*p_3[0]*p_3[1]+2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[1]+2*power(p_3[2],2)*power(p_2[2],2)*p_4[0]*p_4[1]+2*power(p_2[2],2)*power(p_3[0],2)*p_4[0]*p_4[1]-2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[1],
		0,  0,  0,  0,  0,  0
	])

	A= A_eigen.reshape(N,N)
	B= B_eigen.reshape(N,N)

	[alphar,alphai,beta,vi,vr,work,info] =sp.dggev(A,B,compute_vl=0,compute_vr=1,lwork=16*N    )

	vr2=vr.reshape(N*N)

	myList=[]
	cols=[]
	anz=0

	for i in range(N):
		# print ("found solution",i,beta[i],alphai[i])
		if beta[i]!=0 and alphai[i]==0:
			#print ("real solution ",i,anz,displaynumber)
			print ("found real solution",i,anz,displaynumber,"beta, alphai",beta[i],alphai[i])
			anz += 1
			if not (anz==displaynumber or displaynumber==0):
				continue

			a=vr[N-2,i]/vr[N-1,i];
			b=alphar[i]/beta[i];
			r=((a*a+b*b-1)*p_2[2]*p_2[2]+2*(a*p_2[0]+b*p_2[1])*p_2[2]+(b*p_2[0]-a*p_2[1])*(b*p_2[0]-a*p_2[1]))/(2*(a*a+b*b)*p_2[2]);
			q=FreeCAD.Vector(0,0,r);

			apex=FreeCAD.Vector(a*r,b*r,0);
			axis=(q-apex).normalize();

			print ("apex ",apex)
			print ("axis ",axis)

			sin_angle = (p_1-apex).dot(axis)/((p_1-apex).Length*axis.Length);
			cos_angle = ((p_1-apex).cross(axis)).Length/((p_1-apex).Length*axis.Length);
			
			r0 = np.arctan2(sin_angle , cos_angle);
			#alpha=np.pi/2-r0

			l1=min((p_1-apex).dot(axis),(p_2-apex).dot(axis));
			l2=max((p_1-apex).dot(axis),(p_2-apex).dot(axis));
			myList += [("Cone",apex,axis,r0,l1,l2)];

			pts=[apex,p_1,apex,p_2,apex,p_3,apex,p_4]

			if 0:
				print "Laengen"
				print axis.dot((apex-p_1).normalize())
				print axis.dot((apex-p_2).normalize())
				print axis.dot((apex-p_3).normalize())
				print axis.dot((apex-p_4).normalize())

			h=500

			cmps=[]
			for p in [p_4,p_1,p_2,p_3,apex]:
				s=Part.makeSphere( 12)
				s.Placement.Base=p
				cmps += [s]

			alpha=np.pi/2-r0
			print ("alpha ",alpha*180/np.pi)

			[a,bounds]=	drawCone(apex,axis,alpha,h,trafo,[p_4,p_1,p_2,p_3])
			cols += [a]

			if displayFaces:
				drawConeA(name,anz,bounds,apex,axis,alpha,trafo,[p_4,p_1,p_2,p_3]) # kegelflaeche zeigen 

	return cols


class PointFace(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","L1")
		obj.addProperty("App::PropertyLink","L2")
		obj.addProperty("App::PropertyLink","L3")
		obj.addProperty("App::PropertyLink","L4")

		obj.addProperty("App::PropertyVector","P1").P1=FreeCAD.Vector(50,0,0)
		obj.addProperty("App::PropertyVector","P2").P2=FreeCAD.Vector(0,50,5)
		obj.addProperty("App::PropertyVector","P3").P3=FreeCAD.Vector(-50,0,-1)
		obj.addProperty("App::PropertyVector","P4").P4=FreeCAD.Vector(0,-50,-5)
		obj.addProperty("App::PropertyVector","P5").P5=FreeCAD.Vector(0,-50,-5)
		obj.addProperty("App::PropertyVector","P6").P6=FreeCAD.Vector(0,-50,-5)

		obj.addProperty("App::PropertyVector","N1").N1=FreeCAD.Vector(10,0,10)
		obj.addProperty("App::PropertyVector","N2").N2=FreeCAD.Vector(-5,0,10)
		obj.addProperty("App::PropertyVector","N3").N3=FreeCAD.Vector(-5,0,10)
		obj.addProperty("App::PropertyVector","N4").N4=FreeCAD.Vector(-5,0,10)

		
		obj.addProperty("App::PropertyInteger","number").number=0
		obj.addProperty("App::PropertyBool","displayPoints").displayPoints=1
		obj.addProperty("App::PropertyBool","displayFaces").displayFaces=1
		obj.addProperty("App::PropertyEnumeration","mode")
		obj.mode=['parameters','tripod','spheres and cones','vertexes']

		obj.addProperty("App::PropertyEnumeration","pattern")
		obj.pattern=['pnpn','pnppp','pnpnpnpn']
		obj.addProperty("App::PropertyEnumeration","target")
		obj.target=['Cone','Shpere','Cylinder','Torus','Plane']


		obj.addProperty("App::PropertyVector","apex",'~aux').apex=FreeCAD.Vector(30,30,30)
		obj.addProperty("App::PropertyVector","axis",'~aux').axis=FreeCAD.Vector(10,0,0)
		obj.setEditorMode('apex',2)
		obj.setEditorMode('axis',2)

# experiments with attributes
		obj.addProperty("App::PropertyString", "TA", "Base", "Type of the solver", 0, True,True)
		obj.addProperty("App::PropertyString", "TB0", "Base", "Type of the solver", 0,)
		obj.addProperty("App::PropertyString", "TB1", "Base", "Type of the solver", 1,)#ro
		obj.addProperty("App::PropertyString", "TB2", "Base", "Type of the solver", 2,)# was bring tdas
		obj.addProperty("App::PropertyString", "TB4", "Base", "Type of the solver", 4,)#hidden
		obj.addProperty("App::PropertyString", "TB8", "Base", "Type of the solver", 8)# no impact recompute




	def myOnChanged(self,obj,prop):

		if prop in ["Shape","Label"]:
			return


		try: # start not befor the last prop is created
			obj.axis
		except:
			return

		if prop=='pattern':
			if obj.pattern=='pnpn':
				for a in 'P3','P4','P5','P6','L3','L4','N3','N4':
					obj.setEditorMode(a,2)
			if obj.pattern=='pnppp':
				for a in 'N2','P5','P6','N3','N4':
					obj.setEditorMode(a,2)

		print "---------prop          changed       ",prop
		if prop not in ["_init_","number",'N1','N2','P1','P2','P3','P4','P5','P6']: return

		# generic testdata
		if obj.mode=='parameters':
			sp= [obj.P1,obj.P2,obj.P3,obj.P4]
			dirs=[obj.N1,obj.N2,obj.N3,obj.N4]

		# 1. Variante Tripod
		elif obj.mode=='tripod':
			sp=[]
			dirs=[]
			if obj.L1 != None: 
				sp += [obj.L1.Shape.Vertex1.Point]
				dirs += [obj.L1.Shape.Vertex6.Point-obj.L1.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P1]
				dirs += [obj.N1]
			if obj.L2 != None: 
				dirs += [obj.L2.Shape.Vertex6.Point-obj.L2.Shape.Vertex1.Point]
				sp += [obj.L2.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P2]
				dirs += [obj.N2]
			if obj.L3 != None: 
				sp += [obj.L3.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P3]
			if obj.L4 != None: 
				sp += [obj.L4.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P4]

		# 2. Variante Parts
		elif obj.mode== 'spheres and cones':
			sp=[]
			dirs=[]
			if obj.L1 != None: 
				sf=obj.L1.Shape.Face1.Surface
				if sf.__class__.__name__ =='Sphere':
					sp += [obj.L1.Placement.Base]
					dirs +=  [obj.N1]
				elif sf.__class__.__name__ =='Cone':
					sp += [sf.Apex]
					dirs += [sf.Axis]
				else:
					sp += [obj.L1.Shape.Vertex1.Point]
					dirs +=  [obj.N1]
			else: 
				sp += [ obj.P1]
				dirs +=  [obj.N1]

			if obj.L2 != None: 
				sf=obj.L2.Shape.Face1.Surface
				if sf.__class__.__name__ =='Sphere':
					sp += [obj.L2.Placement.Base]
					dirs +=  [obj.N1]
				elif sf.__class__.__name__ =='Cone':
					sp += [ sf.Apex ]
					dirs += [sf.Axis]
				else:
					sp += [obj.L2.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P2]

			if obj.L3 != None: 
				sf=obj.L3.Shape.Face1.Surface
				if sf.__class__.__name__ =='Sphere':
					sp += [obj.L3.Placement.Base]
					dirs +=  [obj.N1]
				elif sf.__class__.__name__ =='Cone':
					sp += [ sf.Apex ]
					dirs += [sf.Axis]
				else:
					sp += [obj.L3.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P3]

			if obj.L4 != None: 
				sf=obj.L4.Shape.Face1.Surface
				if sf.__class__.__name__ =='Sphere':
					sp += [obj.L4.Placement.Base]
					dirs +=  [obj.N1]
				elif sf.__class__.__name__ =='Cone':
					sp += [ sf.Apex ]
					dirs += [sf.Axis]
				else:
					sp += [obj.L4.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P4]

		print dirs
		dirsa=[FreeCAD.Vector(p).normalize() for p in dirs]
		dirs=dirsa

		p1=sp[0]
		pma=FreeCAD.Placement(-p1,FreeCAD.Rotation())
		pmb=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(dirs[0],FreeCAD.Vector(0,0,1)))
		trafo=pmb.multiply(pma)

		cmps=[]

		if obj.displayPoints:
			for p in sp[0:2]:
					s=Part.makeSphere(2)
					s.Placement.Base=p
					cmps += [s]

		pts_norm=[trafo.multVec(p) for p in sp]
		dirs_norm=[pmb.multVec(p) for p in dirs]

		name=obj.Name

		if obj.pattern=='pnppp':
			rc=run_pnppp(name,trafo,obj.number,obj.displayFaces,*pts_norm)

		elif obj.pattern=='pnpn':

			[p_1,p_2]=pts_norm[0:2]
			[n_1,n_2]=dirs_norm[0:2]

			rc=run_pnpn(p_1,n_1,p_2,n_2,name,trafo,obj.number,obj.displayFaces)

		elif obj.pattern=='pnpnpnpn':

			[p_1,p_2,p_3,p_4]=pts_norm[0:4]
			[n_1,n_2,n_3,n_4]=dirs_norm[0:4]

			rc=run_4pn(p_1,n_1,p_2,n_2,p_3,n_3,p_4,n_4,name,trafo,obj.number,obj.displayFaces)

		obj.Shape= Part.Compound(rc +cmps)

		return

		print ("config debug info")
		for i,p in enumerate(sp):
			print ("Point",i,p)
		for i,p in enumerate(dirs[:1]):
			print ("Direction",i,p)


	def myExecute(self,obj):
		self.onChanged(obj,"_init_")
		# print obj.Label," executed"



def PointstoConePNPPP():
	'''create a cone by point,normal and 3 points'''  

	sel=Gui.Selection.getSelection()
#	if len(sel) != 4:
#		print "selection reicht nicht 4 "
#		return
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","PointFace")
	PointFace(yy)
	yy.pattern='pnppp'
	
	if len(sel)==4:
		# mode p n p p p

		y=sel[0]
		if y.TypeId == 'Part::Cone':
			yy.mode = 'spheres and cones'
		elif y.TypeId == 'Part::FeaturePython' and y.Proxy.__class__.__name__ =='Tripod':
			yy.mode = 'tripod'

		[yy.L1,yy.L2,yy.L3,yy.L4]=sel

	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.9,.0,0.)
	yy.ViewObject.LineColor=(.9,.9,0.)
	#yy.Proxy.myOnChanged(yy,"_init_")
	return yy


def PointstoConePNPN():
	'''create a cone by point,normal, point2.normal2'''

	sel=Gui.Selection.getSelection()
#	if len(sel) != 2:
#		print "selection reicht nicht 4 "
#		return
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","PointFace")
	PointFace(yy)
	
#	yy.P1=FreeCAD.Vector()
#	yy.P2=FreeCAD.Vector(50,0,70)
#	yy.N1=FreeCAD.Vector(0,0,1)
#	yy.N2=FreeCAD.Vector(37,0,26)# .normalize()

	
	yy.pattern='pnpn'#,'pnppp']
	if len(sel)==4:
		# mode p n p p p

		y=sel[0]
		if y.TypeId == 'Part::Cone':
			yy.mode = 'spheres and cones'
		elif y.TypeId == 'Part::FeaturePython' and y.Proxy.__class__.__name__ =='Tripod':
			yy.mode = 'tripod'

		[yy.L1,yy.L2,yy.L3,yy.L4]=sel

	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.9,.0,0.)
	yy.ViewObject.LineColor=(.9,.9,0.)
	#yy.Proxy.myOnChanged(yy,"_init_")
	return yy


def PointstoBezierPNPNPNPN():
	'''create a cone by 4 point,normal,'''

	sel=Gui.Selection.getSelection()
#	if len(sel) != 2:
#		print "selection reicht nicht 4 "
#		return
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","PointFace")
	PointFace(yy)
	
#	yy.P1=FreeCAD.Vector()
#	yy.P2=FreeCAD.Vector(50,0,70)
#	yy.N1=FreeCAD.Vector(0,0,1)
#	yy.N2=FreeCAD.Vector(37,0,26)# .normalize()

	
	yy.pattern='pnpnpnpn'
	if len(sel)==4:
		# mode p n p p p

		y=sel[0]
		if y.TypeId == 'Part::Cone':
			yy.mode = 'spheres and cones'
		elif y.TypeId == 'Part::FeaturePython' and y.Proxy.__class__.__name__ =='Tripod':
			yy.mode = 'tripod'

		[yy.L1,yy.L2,yy.L3,yy.L4]=sel

	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.9,.0,0.)
	yy.ViewObject.LineColor=(.9,.9,0.)
	#yy.Proxy.myOnChanged(yy,"_init_")
	return yy



def	run_pnpn(p_1,n_1,p_2,n_2,name='PNPN_Test',trafo=None,displaynumber=0,displayFaces=True):
	'''2 points p1,p2 with normals n1,n2'''

	THRESHOLD=0.1
	cols=[]

	if displaynumber in  [0,1]:
		l_1=p_2.dot(n_2)/(n_2[2]+1);
		l_2=-p_2[2]/(1+n_2[2]);

		A1 = l_1 * n_1;
		A2 = l_2 * n_2 + p_2;


		if ((A2-A1).Length>THRESHOLD):

			axis = (A2-A1).normalize();
			apex=FreeCAD.Vector(l_1*(n_2[0]*l_2+p_2[0])/(-l_2*n_2[2]+l_1-p_2[2]),
						  l_1*(n_2[1]*l_2+p_2[1])/(-l_2* n_2[2]+l_1-p_2[2]),
						  0);

		else:
			apex=FreeCAD.Vector()
			axis= (A2X-A1X).normalize();
			
			axis = (A1-(p_1+p_2)/2).normalize();
			apex = FreeCAD.Vector(l_1*p_2[0]/(2*l_1-p_2[2]),
								l_1*p_2[0]/(2*l_1-p_2[2]),
								0);


		print ("apex",apex)
		print ("axis",axis)

		if 0:
			print "Laengen"
			print axis.dot((apex-p_1).normalize())
			print axis.dot((apex-p_2).normalize())

		sin_angle = (p_1-apex).dot(axis)/((p_1-apex).Length*axis.Length);
		cos_angle = ((p_1-apex).cross(axis)).Length/((p_1-apex).Length*axis.Length);
				
		r0 = np.arctan2(sin_angle , cos_angle);
		alpha=np.pi/2-r0
		print ("alpha",alpha)

		h=100
		pts=[p_1,p_2]
		#trafo=FreeCAD.Placement()

		[a,bounds]=	drawCone(apex,axis,alpha,h,trafo,pts)
		cols += [a]
		if displayFaces:
			drawConeA(name,0,bounds,apex,axis,alpha,trafo,pts) # kegelflaeche zeigen 


	if displaynumber  in [0,2]:
		#+# 2. Loesung noch dazu 

		l_1=p_2.dot(n_2)/(n_2[2]-1);
		l_2=p_2[2]/(1-n_2[2]);

		A1 = l_1 * n_1;
		A2 = l_2 * n_2 + p_2;

		if ((A2-A1).Length>THRESHOLD) :
			axis = (A2-A1).normalize();
			apex= FreeCAD.Vector(	l_1*(n_2[0]*l_2+p_2[0])/(-l_2*n_2[2]+l_1-p_2[2]),
							l_1*(n_2[1]*l_2+p_2[1])/(-l_2* n_2[2]+l_1-p_2[2]),
							0);

		else :
			axis = (A1-(p_1+p_2)/2).normalize();
			apex = FreeCAD.Vector(l_1*p_2[0]/(2*l_1-p_2[2]),
				l_1*p_2[1]/(2*l_1-p_2[2]),
				0);

		print ("apex",apex)
		print ("axis",axis)
		
		if 0:
			print "Laengen"
			print axis.dot((apex-p_1).normalize())
			print axis.dot((apex-p_2).normalize())

		
		sin_angle = (p_1-apex).dot(axis)/((p_1-apex).Length*axis.Length);
		cos_angle = ((p_1-apex).cross(axis)).Length/((p_1-apex).Length*axis.Length);
				
		r0 = np.arctan2(sin_angle , cos_angle);
		alpha=np.pi/2-r0
		print ("alpha",alpha)
		h=100

		pts=[p_1,p_2]
		#trafo=FreeCAD.Placement()

		[a,bounds]=	drawCone(apex,axis,alpha,h,trafo,pts)
		cols += [a]
		if displayFaces:
			drawConeA(name,1,bounds,apex,axis,alpha,trafo,pts) # kegelflaeche zeigen 

	return cols


def run4pn(p_1,n_1,p_2,n_2,p_3,n_3,p_4,n_4,name,trafo,number,displayFaces):
	
	bs=Part.BSplineSurface()
	t1=(p_2-p_1).normalize()
	t2=(p_4-p_1).normalize()
	t1,t2=-n_1.cross(t2),n_1.cross(t1)
	
	k=30
	
	poles=np.array([
		p_1,p_1+k*t1,p_2-k*t1,p_2,
		p_1+k*t2,p_1+k*t1+k*t2,p_2-k*t1+k*t2,p_2+k*t2,
		p_4-k*t2,p_4+k*t1-k*t2,p_3-k*t1-k*t2,p_3-k*t2,
		p_4,p_4+k*t1,p_3-k*t1,p_3]).reshape(4,4,3)
	um=[4,4]
	uk=[0,1]

	bs.buildFromPolesMultsKnots(poles, 
								um,um,range(len(um)),range(len(um)),False,False,3,3)
	return [bs.toShape()]



def run_cylinder(): 
	
	p_1=FreeCAD.Vector()
	p_2=FreeCAD.Vector(100,0,100)
	p_3=FreeCAD.Vector(50,80,50)
	n1=FreeCAD.Vector(0,0,1)
	p1=p_1

	a = (p_2[1]*p_2[1]+p_2[2]*p_2[2])*p_3[2] - (p_3[1]*p_3[1]+p_3[2]*p_3[2])*p_2[2];
	b = -2*(p_2[0]*p_2[1]*p_3[2] - p_3[0]*p_3[1]*p_2[2]);
	c = (p_2[0]*p_2[0]+p_2[2]*p_2[2])*p_3[2] - (p_3[0]*p_3[0]+p_3[2]*p_3[2])*p_2[2];

	if ((a == 0) and (b == 0) and (c == 0)):
		print  ("// Infinite solutions")
		return;

	cyls=[]
	# Different cases
	if (a == 0) :
		if ((c!=0)) :
			l=1;
			m=-b/c;
			v =FreeCAD.Vector(l,m,0)
			if (p_2[2]!=0):
				r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				## this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

			if (p_3[2]!=0):
				r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				## this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
		l=1;
		m=0;
		
		v =FreeCAD.Vector(l,m,0)

		if (p_2[2]!=0):
			r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
			r=abs(r);

			center=FreeCAD.Vector(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

		if (p_3[2]!=0):
			r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
			r=abs(r);

			center=FreeCAD.Vector(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

	elif (c == 0):
		m=1;
		l=-b/a;

		v =FreeCAD.Vector(l,m,0)
		if (p_2[2]!=0):
			r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
			r=abs(r);

			center=FreeCAD.Vector(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# # this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

		if (p_3[2]!=0):
			r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
			r=abs(r);

			center=FreeCAD.Vector(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

		l=0;
		m=1;
		
		v =FreeCAD.Vector(l,m,0)
		if (p_2[2]!=0):
			r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
			r=abs(r);

			(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]

		if (p_3[2]!=0):
			r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
			r=abs(r);

			center=FreeCAD.Vector(0,0,-r);
			l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
			# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
			cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
		
	else:
		delta = b*b-4*a*c;
		if (delta == 0):
			m = 1;
			l = -b/(2*a);
			
			v =FreeCAD.Vector(l,m,0)
			if (p_2[2]!=0):
				r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
			elif (p_3[2]!=0):
				r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
		elif (delta > 0):
			m = 1;
			l = (- b + sqrt(delta)) / (2 * a);
			v =FreeCAD.Vector(l,m,0)
			if (p_2[2]!=0):
				r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
			
			elif (p_3[2]!=0):
				r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
			
			l = (- b - sqrt(delta)) / (2 * a);
			v =FreeCAD.Vector(l,m,0)
			if (p_2[2]!=0):
				r = 1/(2*p_2[2]) * (1/(l*l+m*m) * (-p_2[0]*m+p_2[1]*l) * (-p_2[0]*m+p_2[1]*l) + p_2[2]*p_2[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
			
			elif (p_3[2]!=0):
				r = 1/(2*p_3[2]) * (1/(l*l+m*m) * (-p_3[0]*m+p_3[1]*l) * (-p_3[0]*m+p_3[1]*l) + p_3[2]*p_3[2]);
				r=abs(r);

				center=FreeCAD.Vector(0,0,-r);
				l1=min(dotProduct(p_1-center,v.normalize()),min(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				l2=max(dotProduct(p_1-center,v.normalize()),max(dotProduct(p_2-center,v.normalize()),dotProduct(p_3-center,v.normalize())));
				# this->list.push_back(Cylinder(p1+sign(p_2[2])*r*n1,Rotation*v,r,l1,l2));
				cyls += [(p1+sign(p_2[2])*r*n1,v,r,l1,l2)]
	for cyl in  cyls:
		print "center",cyl[0],"axsi",cyl[1],"radius",cyl[3]
		Part.show(Part.makeCylinder(cyl[2],200,cyl[0],cyl[1]))
		App.ActiveDocument.ActiveObject.ViewObject.Transparency=60
		Part.show(Part.makeCylinder(cyl[2],200,cyl[0],-cyl[1]))
		App.ActiveDocument.ActiveObject.ViewObject.Transparency=60

	Part.show(Part.Compound([Part.makeSphere(5,p) for p in [p_1,p_2,p_3]]))
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.,0.,0.)



def PointstoCylinderPNPP():
	'''create a cylinder by point,normal, point2, poimnt3'''


	run_cylinder()
	raise Exception("muss noch eingebettet werden")


	sel=Gui.Selection.getSelection()
#	if len(sel) != 2:
#		print "selection reicht nicht 4 "
#		return
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","PointFace")
	PointFace(yy)
	
#	yy.P1=FreeCAD.Vector()
#	yy.P2=FreeCAD.Vector(50,0,70)
#	yy.N1=FreeCAD.Vector(0,0,1)
#	yy.N2=FreeCAD.Vector(37,0,26)# .normalize()

	
	yy.pattern='pnpp'#,'pnppp']
	
	if len(sel)==4:
		# mode p n p p p

		y=sel[0]
		if y.TypeId == 'Part::Cone':
			yy.mode = 'spheres and cones'
		elif y.TypeId == 'Part::FeaturePython' and y.Proxy.__class__.__name__ =='Tripod':
			yy.mode = 'tripod'

		[yy.L1,yy.L2,yy.L3,yy.L4]=sel

	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.9,.0,0.)
	yy.ViewObject.LineColor=(.9,.9,0.)
	#yy.Proxy.myOnChanged(yy,"_init_")
	return yy


def run_sphere4P():

	# tesdaten hard  coded 
	p1=FreeCAD.Vector(0,-50,0)
	p2=FreeCAD.Vector(0,140,0)
	p3=FreeCAD.Vector(70,0,0)
	p4=FreeCAD.Vector(0,0,60)


#    // Test if 2 points are equals
#   if (((p1-p2).norm() < THRESHOLD) || ((p1-p3).norm() < THRESHOLD) || ((p1-p4).norm() < THRESHOLD)|| ((p2-p3).norm() < #HRESHOLD)|| ((p2-p4).norm() < THRESHOLD)|| ((p3-p4).norm() < THRESHOLD)){
#        std::cerr<< "2 points are equals"<< endl;
#        return;
#    }
	A=np.array([(p2-p1), (p3-p2), (p4-p3)])

	b =FreeCAD.Vector(
			0.5*(p2.Length**2-p1.Length**2),
			0.5*(p3.Length**2-p2.Length**2),
			0.5*(p4.Length**2-p3.Length**2),
		);

	center=FreeCAD.Vector()
	AI=inv(A)
	for i in range(3):
		for j in range(3):
			center[i] += AI[i,j]*b[j]
	radius = (p1-center).Length;  

	Part.show(Part.makeSphere(radius,center))
	Part.show(Part.Compound([Part.makeSphere(5,p) for p in [p1,p2,p3,p4]]))
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.,0.,0.)


def run_spherePNP(): # pn p 
#   // Test if the Normal is not 0 0 0
 #   if ((abs(N(0))<THRESHOLD) && (abs(N(1))<THRESHOLD) && (abs(N(2))<THRESHOLD)){
  #      std::cerr<< "Normal is undefined"<< endl;
   #     return;
   # }
   # // Test if 2 points are equals
   # if ((p1-p2).norm() < THRESHOLD) {
   #     std::cerr<< "2 points are equals"<< endl;
   #     return;
   # }
	p1=FreeCAD.Vector(10,140,0)
	p2=FreeCAD.Vector(-100,0,-100)
	N=FreeCAD.Vector(0,0,-1).normalize()

	A =np.array([
		1, 0, 0, N[0],
		0, 1, 0, N[1],
		0, 0, 1, N[2],
		(p2-p1)[0], (p2-p1)[1], (p2-p1)[2], 0]).reshape(4,4)
 
	b = np.array([p1[0],p1[1],p1[2],0.5*(p2.Length**2-p1.Length**2)]);
 	s=np.zeros(4)
	AI=inv(A)
	for i in range(4):
		for j in range(4):
			s[i] += AI[i,j]*b[j]

	center =FreeCAD.Vector(s[0:3])
	radius = abs(s[3]);

	Part.show(Part.makeSphere(radius,center))
	Part.show(Part.Compound([Part.makeSphere(5,p) for p in [p1,p2]]))
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.,0.,0.)

def run_cyl5p():

	THRESHOLD = 0.001


	# Five Points ##############################
	p_1=FreeCAD.Vector(0,0,0)
	p_2=FreeCAD.Vector(100,0,0)
	p_3=FreeCAD.Vector(50,50,0)
	p_4=FreeCAD.Vector(0,0,50)
	p_5=FreeCAD.Vector(100,0,51)


	print "Points ..."
	for p in [p_1,p_2,p_3,p_4,p_5]:
		print p

	#    if ((abs(p_3(1)) < THRESHOLD) && (abs(p_3(0)) > THRESHOLD) ){ // p_1 p_2 p_3 are alligned so infinite or no cylinder
	#
	 #       return;
	  #  }        
	#
	 #   if ((abs(p_4(2)) < THRESHOLD) && (abs(p_5(2)) < THRESHOLD)) {
	#
	  #      return;
	 #   }

#	if (abs(p_4[2]) < THRESHOLD): 
#		p_4,p_5 = p_5,p_4

	N = 12;
	A = np.array([
			0,  0,  0,  0,  0,  0,  0,  0,  -p_2[0]*p_3[1]*(-p_3[1]*p_4[1]+power(p_4[1],2)+power(p_4[2],2)),
												-power(p_2[0],2)*p_3[1]*p_4[2]+2*p_2[0]*p_4[0]*p_3[1]*p_4[2],
													-power(p_2[0],2)*p_3[0]*p_4[1]+power(p_2[0],2)*p_4[0]*p_3[1]+p_2[0]*power(p_3[0],2)*p_4[1]-p_2[0]*power(p_4[0],2)*p_3[1]+p_2[0]*power(p_3[1],2)*p_4[1]-p_2[0]*p_3[1]*power(p_4[1],2),
														0,
			0,  0,  0,  0,  0,  0,  0,  0,  0,  -p_2[0]*p_3[1]*(-p_3[1]*p_4[1]+power(p_4[1],2)+power(p_4[2],2)),
													-power(p_2[0],2)*p_3[1]*p_4[2]+2*p_2[0]*p_4[0]*p_3[1]*p_4[2],
														-power(p_2[0],2)*p_3[0]*p_4[1]+power(p_2[0],2)*p_4[0]*p_3[1]+p_2[0]*power(p_3[0],2)*p_4[1]-p_2[0]*power(p_4[0],2)*p_3[1]+p_2[0]*power(p_3[1],2)*p_4[1]-p_2[0]*p_3[1]*power(p_4[1],2),
			0,  0,  0,  0,  0,  0,  0,  0,  power(p_3[1],2)*p_4[1]*p_5[2]-power(p_3[1],2)*p_5[1]*p_4[2]-p_3[1]*power(p_4[1],2)*p_5[2]+p_3[1]*power(p_5[1],2)*p_4[2]-p_3[1]*power(p_4[2],2)*p_5[2]+p_3[1]*p_4[2]*power(p_5[2],2),
												2*p_4[0]*p_3[1]*p_4[2]*p_5[2]-2*p_5[0]*p_3[1]*p_4[2]*p_5[2],
													-p_2[0]*p_3[0]*p_4[1]*p_5[2]+p_2[0]*p_3[0]*p_5[1]*p_4[2]+p_2[0]*p_4[0]*p_3[1]*p_5[2]-p_2[0]*p_5[0]*p_3[1]*p_4[2]+power(p_3[0],2)*p_4[1]*p_5[2]-power(p_3[0],2)*p_5[1]*p_4[2]-power(p_4[0],2)*p_3[1]*p_5[2]+power(p_5[0],2)*p_3[1]*p_4[2]+power(p_3[1],2)*p_4[1]*p_5[2]-power(p_3[1],2)*p_5[1]*p_4[2]-p_3[1]*power(p_4[1],2)*p_5[2]+p_3[1]*power(p_5[1],2)*p_4[2],
														0,
			0,  0,  0,  0,  0,  0,  0,  0,  0,  power(p_3[1],2)*p_4[1]*p_5[2]-power(p_3[1],2)*p_5[1]*p_4[2]-p_3[1]*power(p_4[1],2)*p_5[2]+p_3[1]*power(p_5[1],2)*p_4[2]-p_3[1]*power(p_4[2],2)*p_5[2]+p_3[1]*p_4[2]*power(p_5[2],2),
													2*p_4[0]*p_3[1]*p_4[2]*p_5[2]-2*p_5[0]*p_3[1]*p_4[2]*p_5[2],
														-p_2[0]*p_3[0]*p_4[1]*p_5[2]+p_2[0]*p_3[0]*p_5[1]*p_4[2]+p_2[0]*p_4[0]*p_3[1]*p_5[2]-p_2[0]*p_5[0]*p_3[1]*p_4[2]+power(p_3[0],2)*p_4[1]*p_5[2]-power(p_3[0],2)*p_5[1]*p_4[2]-power(p_4[0],2)*p_3[1]*p_5[2]+power(p_5[0],2)*p_3[1]*p_4[2]+power(p_3[1],2)*p_4[1]*p_5[2]-power(p_3[1],2)*p_5[1]*p_4[2]-p_3[1]*power(p_4[1],2)*p_5[2]+p_3[1]*power(p_5[1],2)*p_4[2],
			1,  0,  0,  0,  0,  0,  0,  0,  -p_4[2]*power(p_3[1],2)*p_2[0],
												-2*p_2[0]*p_3[0]*p_3[1]*p_4[1]+2*p_2[0]*p_4[0]*p_3[1]*p_4[1],
													power(p_2[0],2)*p_3[0]*p_4[2]-p_2[0]*power(p_3[0],2)*p_4[2]-p_4[2]*power(p_3[1],2)*p_2[0]+2*p_2[0]*p_3[1]*p_4[1]*p_4[2],
														0,
			0,  1,  0,  0,  0,  0,  0,  0,  0,  -p_4[2]*power(p_3[1],2)*p_2[0],
													-2*p_2[0]*p_3[0]*p_3[1]*p_4[1]+2*p_2[0]*p_4[0]*p_3[1]*p_4[1],
														power(p_2[0],2)*p_3[0]*p_4[2]-p_2[0]*power(p_3[0],2)*p_4[2]-p_4[2]*power(p_3[1],2)*p_2[0]+2*p_2[0]*p_3[1]*p_4[1]*p_4[2],
			0,  0,  1,  0,  0,  0,  0,  0,  0,  -2*p_3[0]*p_3[1]*p_4[1]*p_5[2]+2*p_3[0]*p_3[1]*p_5[1]*p_4[2]+2*p_4[0]*p_3[1]*p_4[1]*p_5[2]-2*p_5[0]*p_3[1]*p_5[1]*p_4[2],
													2*p_3[1]*p_4[1]*p_4[2]*p_5[2]-2*p_3[1]*p_5[1]*p_4[2]*p_5[2],
														0,
			0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  -2*p_3[0]*p_3[1]*p_4[1]*p_5[2]+2*p_3[0]*p_3[1]*p_5[1]*p_4[2]+2*p_4[0]*p_3[1]*p_4[1]*p_5[2]-2*p_5[0]*p_3[1]*p_5[1]*p_4[2],
														2*p_3[1]*p_4[1]*p_4[2]*p_5[2]-2*p_3[1]*p_5[1]*p_4[2]*p_5[2],
			0,  0,  0,  0,  1,  0,  0,  0,  0,  -power(p_2[0],2)*p_3[1]*p_4[2]+2*p_2[0]*p_3[0]*p_3[1]*p_4[2],
													-power(p_2[0],2)*p_3[0]*p_4[1]+power(p_2[0],2)*p_4[0]*p_3[1]+p_2[0]*power(p_3[0],2)*p_4[1]-p_2[0]*power(p_4[0],2)*p_3[1]-p_2[0]*p_3[1]*power(p_4[2],2),
														0,
			0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  -power(p_2[0],2)*p_3[1]*p_4[2]+2*p_2[0]*p_3[0]*p_3[1]*p_4[2],
														-power(p_2[0],2)*p_3[0]*p_4[1]+power(p_2[0],2)*p_4[0]*p_3[1]+p_2[0]*power(p_3[0],2)*p_4[1]-p_2[0]*power(p_4[0],2)*p_3[1]-p_2[0]*p_3[1]*power(p_4[2],2),
			0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  -p_2[0]*p_3[0]*p_4[1]*p_5[2]+p_2[0]*p_3[0]*p_5[1]*p_4[2]+p_2[0]*p_4[0]*p_3[1]*p_5[2]-p_2[0]*p_5[0]*p_3[1]*p_4[2]+power(p_3[0],2)*p_4[1]*p_5[2]-power(p_3[0],2)*p_5[1]*p_4[2]-power(p_4[0],2)*p_3[1]*p_5[2]+power(p_5[0],2)*p_3[1]*p_4[2]-p_3[1]*power(p_4[2],2)*p_5[2]+p_3[1]*p_4[2]*power(p_5[2],2),
														0,
			0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  -p_2[0]*p_3[0]*p_4[1]*p_5[2]+p_2[0]*p_3[0]*p_5[1]*p_4[2]+p_2[0]*p_4[0]*p_3[1]*p_5[2]-p_2[0]*p_5[0]*p_3[1]*p_4[2]+power(p_3[0],2)*p_4[1]*p_5[2]-power(p_3[0],2)*p_5[1]*p_4[2]-power(p_4[0],2)*p_3[1]*p_5[2]+power(p_5[0],2)*p_3[1]*p_4[2]-p_3[1]*power(p_4[2],2)*p_5[2]+p_3[1]*p_4[2]*power(p_5[2],2)
			]).reshape(N,N)

	B = np.array([
			1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
			0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
			0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,
			0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,
			0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,
			0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,
			0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,
			0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,
			0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  
				-power(p_2[0],2)*p_3[0]*p_4[2]+p_2[0]*power(p_3[0],2)*p_4[2],0,
			0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  
				-power(p_2[0],2)*p_3[0]*p_4[2]+p_2[0]*power(p_3[0],2)*p_4[2],
			0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
			0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
			]).reshape(N,N)

	#A=A.swapaxes(0,1)
	#B=B.swapaxes(0,1)

	[alphar,alphai,beta,vi,vr,work,info] =sp.dggev(A,B,compute_vl=1,compute_vr=1,lwork=16*N    )

	vr2=vr.reshape(N*N)
	myList=[]
	cols=[]
	anz=0

	cyls=[]
	# Generating the cones correspondinng to the real non-infinite eigenvalues
	for i in range(N):
		if(beta[i]!=0 and alphai[i]==0):
			print 
			print ("solution",i)
			print ("beta ",beta[i])
			print ("alphar[i]",alphar[i])
			axis = FreeCAD.Vector(vr2[N-2+i*N]/vr2[N-1+i*N],alphar[i]/beta[i],1).normalize();
			# axis = FreeCAD.Vector(vr2[N-1+i*N]/vr2[N-2+i*N],1.0/(alphar[i]/beta[i]),1).normalize();
			print ("axis",axis)

			a = p_1 - dotProduct(p_1,axis)*axis;
			b = p_2 - dotProduct(p_2,axis)*axis;
			c = p_3 - dotProduct(p_3,axis)*axis;
			a = p_1 - p_1.dot(axis)*axis;
			b = p_2 - p_2.dot(axis)*axis;
			c = p_3 - p_3.dot(axis)*axis;

			print "a,b,c"
			print a
			print b
			print c
			print 

			la = (b-c).Length;
			lb = (c-a).Length;
			lc = (a-b).Length;
			sa = .5*(-la*la + lb*lb + lc*lc);
			sb = .5*( la*la - lb*lb + lc*lc);
			sc = .5*( la*la + lb*lb - lc*lc);
			print "sa,sb,sc"
			print sa
			print sb
			print sc
			print


			center_bar = FreeCAD.Vector(la*la*sa,lb*lb*sb,lc*lc*sc);

			center_bar = center_bar / (center_bar[0]+center_bar[1]+center_bar[2]);
			center = center_bar[0]*a + center_bar[1]*b + center_bar[2]*c;

			r0 = ((la*la*lb*lb*lc*lc)/ (4*power((crossProduct(b-a,c-a).Length),2)))**0.5;

			l1=min(dotProduct(p_1-center,axis),min(dotProduct(p_2-center,axis),min(dotProduct(p_3-center,axis),min(dotProduct(p_4-center,axis),dotProduct(p_5-center,axis)))));
			l2=max(dotProduct(p_1-center,axis),max(dotProduct(p_2-center,axis),max(dotProduct(p_3-center,axis),max(dotProduct(p_4-center,axis),dotProduct(p_5-center,axis)))));

			print ("center",center)
#			print ("axis",axis)
			print ("r0",r0)
			print (l1,l2)
			cyls += [[center,axis,r0,l1,l2]]

	print 
	print "create 3D objects---------------------------------------------"
	for cyl in  cyls:
			if np.isnan(cyl[3]):
				print "nan abbruch"
				continue
			if 10:
				print ("center ",cyl[0])
				print ("axis",cyl[1])
				print ("radius",cyl[2])
				print cyl[3]
				print cyl[4]
				print
			comps=[]
			comps += [Part.makeCylinder(cyl[2],200,cyl[0],cyl[1])]
			comps += [Part.makeCylinder(cyl[2],200,cyl[0],-cyl[1])]
			comps += [Part.makePolygon([cyl[0]-cyl[1]*200,cyl[0]+cyl[1]*200])]

			Part.show(Part.Compound(comps))
			App.ActiveDocument.ActiveObject.ViewObject.Transparency=60

	Part.show(Part.Compound([Part.makeSphere(1+ik,p) for ik,p in enumerate([p_1,p_2,p_3,p_4,p_5])]))
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.,0.,0.)





def PointstoCylinder5P ():
	'''5 Punkte zu cylinder'''

	run_cyl5p()


def PointstoSpherePNP ():
	run_spherePNP()

def PointstoSphere4P ():
	run_sphere4P()

def AA():
	'''5 Punkte zu cylinder'''
	PointstoCylinder5P ()
	
