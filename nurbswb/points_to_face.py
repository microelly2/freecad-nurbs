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


def power(a,b):
	return a**b

def drawConeA(name,i,bounds,apex,axis,alpha,h,trafo,pts):

	trafo=trafo.inverse()
	v=FreeCAD.Vector(0,0,1)

	pss=[]

	[h1,h2]=bounds
	h2+=10
	h1 -=10

	print ("bounds",h1,h2)
	if h2>10:
		cc=Part.makeCone(0,np.tan(alpha)*h2,h2)
		cc.Placement.Rotation=FreeCAD.Rotation(v,axis)
		cc.Placement.Base=apex
		pss += [cc]

	if h1<-10:
		c2c=Part.makeCone(0,np.tan(alpha)*-h1,-h1)
		c2c.Placement.Rotation=FreeCAD.Rotation(-v,axis)
		c2c.Placement.Base=apex
		pss += [c2c]

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
	nurbs=cc.toNurbs()
	print "---------NURBS -------", nurbs
	sf=nurbs.Face1.Surface.copy()
	us=[]
	vs=[]
	for p in pts:
		(u,v)=sf.parameter(p)
		if (sf.value(u,v)-p).Length>0.1:
			ccokay=False
		us += [u]
		vs += [v]
	print us
	print vs
	umi=min(us)
	uma=max(us)
	vmi=min(vs)
	vma=max(vs)

	if not ccokay:
		nurbs=c2c.toNurbs()
		print "---------NURBS -------", nurbs
		sf=nurbs.Face1.Surface.copy()
		us=[]
		vs=[]
		for p in pts:
			(u,v)=sf.parameter(p)
			if (sf.value(u,v)-p).Length>0.1:
				ccokay=False
			us += [u]
			vs += [v]
		print us
		print vs
		umi=min(us)
		uma=max(us)
		vmi=min(vs)
		vma=max(vs)


	try:
		sf.segment(umi,uma,vmi,vma)
		yy.Shape= sf.toShape()
	except:
		yy.Shape=Part.Compound(pss)
	if not ccokay:
		yy.Shape=Part.Compound(pss)

	yy.Placement=trafo


def drawCone(apex,axis,alpha,h,trafo,pts):


	trafo=trafo.inverse()
	axis=axis.normalize()
	lens=[(p-apex).dot(axis) for p in pts] #+ [-1,1]

	if 0: # display apex as ball
		s=Part.makeSphere(4)
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
	print "minma",mima
	mi = min(mima[0],10)
	ma = max(mima[1],10)

	pss += [Part.makePolygon([apex,apex+axis*ma*1.1,apex-axis*mi*1.1])]
	#pss += [Part.makePolygon([apex,apex+axis*max(lens)*1.1])]

	for p in pts:
		pss += [Part.makePolygon([apex,p])]

	rc=Part.Compound(pss)
	rc.Placement=trafo

	return rc, mima


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

# test it
#normalize()
#rollback()





def run(name,trafo,displaynumber,displayFaces,p_1,p_2,p_3,p_4):

	print ("\n\nrun ######################")

#	#p_1 = Vector (0.0, 0.0, 0.0)
#	print "p_1 ",p_1

	if 0:
		if 1: # hard coded points
			p_2 = Vector (163.90116584858188, -52.23960964966506, 39.563506046348145)
			p_3 = Vector (-41.98924450778516, -0.7652516989222458, 21.46559140057437)
			p_4 = Vector (76.94808557453028, 9.865033156091158, 25.35513128766031)

		else: 
			p_2=App.ActiveDocument.Tripod.Shape.Vertex1.Point
			p_3=App.ActiveDocument.Tripod001.Shape.Vertex1.Point
			p_4=App.ActiveDocument.Tripod002.Shape.Vertex1.Point


#	Draft.makeWire([p for p in [p_1,p_2,p_3,p_4]])
#	Draft.makeWire([trafo.multVec(p) for p in [p_1,p_2,p_3,p_4]])
	#return (FreeCAD.Vector(),FreeCAD.Vector())


#----------------------
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


	# Matrix6d B_eigen;
	B_eigen = np.array([ 1,  0,  0,  0,  0,  0,
						0,  1,  0,  0,  0,  0,
						0,  0,  1,  0,  0,  0,
						0,  0,  0,  1,  0,  0,
						0,  0,  0,  0,  0,  2*p_2[2]*power(p_4[2],2)*p_3[2]*p_2[0]*p_2[1]+2*p_2[2]*power(p_4[0],2)*p_3[2]*p_2[0]*p_2[1]+2*p_4[2]*power(p_2[0],2)*p_2[2]*p_3[0]*p_3[1]-2*p_2[2]*power(p_3[2],2)*p_4[2]*p_2[0]*p_2[1]-2*p_2[2]*power(p_3[0],2)*p_4[2]*p_2[0]*p_2[1]-2*p_3[2]*power(p_2[0],2)*p_2[2]*p_4[0]*p_4[1]-2*power(p_4[2],2)*power(p_2[2],2)*p_3[0]*p_3[1]-2*power(p_2[2],2)*power(p_4[0],2)*p_3[0]*p_3[1]+2*p_4[2]*power(p_2[2],3)*p_3[0]*p_3[1]+2*power(p_3[2],2)*power(p_2[2],2)*p_4[0]*p_4[1]+2*power(p_2[2],2)*power(p_3[0],2)*p_4[0]*p_4[1]-2*p_3[2]*power(p_2[2],3)*p_4[0]*p_4[1],
						0,  0,  0,  0,  0,  0])

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

			l1=min((p_1-apex).dot(axis),(p_2-apex).dot(axis));
			l2=max((p_1-apex).dot(axis),(p_2-apex).dot(axis));
			myList += [("Cone",apex,axis,r0,l1,l2)];

#			print ("sin,cos,angle",sin_angle,cos_angle,r0)

			pts=[apex,p_1,apex,p_2,apex,p_3,apex,p_4]
			#_=Draft.makeWire(pts)

			if 10:
				print "Laengen"
				print axis.dot((apex-p_1).normalize())
				print axis.dot((apex-p_2).normalize())
				print axis.dot((apex-p_3).normalize())
				print axis.dot((apex-p_4).normalize())

			h=500

			cmps=[]
			for p in [p_4,p_1,p_2,p_3,apex]:
				s=Part.makeSphere( 2)
				s.Placement.Base=p
				cmps += [s]
			#Part.show(Part.Compound(cmps))


			alpha=np.pi/2-r0
			#alpha=r0
			print ("alpha ",alpha*180/np.pi)
			#print "ro ", r0*180/np.pi
			#alpha=np.pi/2+r0

#			tt=trafo.inverse()
#			tt.Base -= apex
#			print i,"!trafo hu",trafo
			[a,bounds]=	drawCone(apex,axis,alpha,h,trafo,[p_4,p_1,p_2,p_3])
			cols += [a]
			if displayFaces:
				drawConeA(name,anz,bounds,apex,axis,alpha,h,trafo,[p_4,p_1,p_2,p_3]) # kegelflaeche zeigen 


	return cols


#run()


# App.ActiveDocument.addObject('PartDesign::CoordinateSystem','LCS_1')



#---------------------------

class PointFace(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","L1")
		obj.addProperty("App::PropertyLink","L2")
		obj.addProperty("App::PropertyLink","L3")
		obj.addProperty("App::PropertyLink","L4")

		obj.addProperty("App::PropertyVector","P1").P1=FreeCAD.Vector(50,0,0)
		obj.addProperty("App::PropertyVector","P2").P2=FreeCAD.Vector(0,50,5)
		obj.addProperty("App::PropertyVector","P3").P3=FreeCAD.Vector(-50,0,0)
		obj.addProperty("App::PropertyVector","P4").P4=FreeCAD.Vector(0,-50,-5)
		obj.addProperty("App::PropertyVector","N1").N1=FreeCAD.Vector(-10,2,10)

		obj.addProperty("App::PropertyVector","apex",'~aux').apex=FreeCAD.Vector(30,30,30)
		obj.addProperty("App::PropertyVector","axis",'~aux').axis=FreeCAD.Vector(10,0,0)
		
		obj.addProperty("App::PropertyInteger","number").number=0
		obj.addProperty("App::PropertyBool","displayPoints") #.displayPoints=True
		obj.addProperty("App::PropertyBool","displayFaces").displayFaces=1
		obj.addProperty("App::PropertyEnumeration","mode")
		obj.mode=['parameters','tripod','spheres and cones','vertexes']

		obj.setEditorMode('apex',2)
		obj.setEditorMode('axis',2)



	def myOnChanged(self,obj,prop):

		if prop in ["Shape","Label"]:
			return



		try:
			obj.axis
		except:
			return
		print "---------prop          changed       ",prop
		if prop not in ["_init_","number",'N1','P1','P2','P3','P4',"L4"]: return

		if obj.mode=='parameters':
			sp= [obj.P1,obj.P2,obj.P3,obj.P4]
			dirs=[obj.N1]
			
		# 1. Variante Tripod
		if obj.mode=='tripod':
			sp=[]
			dirs=[]
			if obj.L1 != None: 
				sp += [obj.L1.Shape.Vertex1.Point]
				dirs += [obj.L1.Shape.Vertex6.Point-obj.L1.Shape.Vertex1.Point]
			else: 
				sp += [ obj.P1]
				dirs += [obj.N1]
			if obj.L2 != None: sp += [obj.L2.Shape.Vertex1.Point]
			else: sp += [ obj.P2]
			if obj.L3 != None: sp += [obj.L3.Shape.Vertex1.Point]
			else: sp += [ obj.P3]
			if obj.L4 != None: sp += [obj.L4.Shape.Vertex1.Point]
			else: sp += [ obj.P4]

		# 2. Variante Parts
		if obj.mode== 'spheres and cones':
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

		p1=sp[0]
		pma=FreeCAD.Placement(-p1,FreeCAD.Rotation())
		#pmb=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-dirs[0],))
		pmb=FreeCAD.Placement(FreeCAD.Vector(),FreeCAD.Rotation(dirs[0],FreeCAD.Vector(0,0,1)))
		trafo=pmb.multiply(pma)

		print "dirs",dirs[0]
		print "Richtung N1 ",pmb.multVec(-dirs[0])

		cmps=[]

		if obj.displayPoints:
			for p in sp:
					s=Part.makeSphere(5)
					s.Placement.Base=p
					cmps += [s]

		pts_norm=[trafo.multVec(p) for p in sp]

#		for pp in pts_norm:
#			s=Part.makeSphere(3)
#			s.Placement.Base=pp

		name=obj.Name
		rc=run(name,trafo,obj.number,obj.displayFaces,*pts_norm)

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


def createPointFace():

	sel=Gui.Selection.getSelection()
#	if len(sel) != 4:
#		print "selection reicht nicht 4 "
#		return
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","PointFace")
	PointFace(yy)
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
	yy.Proxy.myOnChanged(yy,"_init_")
	return yy


def AA():
	createPointFace()
