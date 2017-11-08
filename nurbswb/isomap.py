# -*- coding: utf-8 -*-
'''
#-------------------------------------------------
#-- isomap calculation
#--
#-- microelly 2017 v 0.2
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
'''

##\cond

from nurbswb.say import *

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


import Part,Mesh,Draft,Points

import numpy as np
import scipy
from scipy import interpolate


# altes interface
# def getmap(mapobj,obj, mpv=0.5, mpu=0.5, fx=-1, fy=-1, vc=30, uc=30 ):

##\endcond

def getmap(mapobj,obj):
	'''  berechnet vier interpolatoren zum umrechnen von xy(isomap) in uv(nurbs) und zurueck 
	mapobj liefert die parameter
	obj ist das Part mit der benutzten Face
	'''


	#default values 
	mpv=0.5
	mpu=0.5
	fx=-1
	fy=-1
	vc=30
	uc=30
	modeA='cubic'
	modeB='thin_plate'

	bs=obj.Shape.Face1.Surface
	face=obj.Shape.Face1

	su=bs.UPeriod()
	sv=bs.VPeriod()

	print "hack BB su sv aa bb"

	su=face.ParameterRange[1]
	sv=face.ParameterRange[3]

	if su>1000: su=face.ParameterRange[1]
	if sv>1000: sv=face.ParameterRange[3]

	if mapobj<>None:
		if hasattr(mapobj,'faceObject'):
			mpv=mapobj.vMapCenter/100
			mpu=mapobj.uMapCenter/100
			fx=mapobj.fx
			fy=mapobj.fy
			vc=mapobj.vCount
			uc=mapobj.uCount

		else:
			mpv=mapobj.vMapCenter/100
			mpu=mapobj.uMapCenter/100
			vc=mapobj.vCount
			uc=mapobj.uCount

			fx=mapobj.fx
			fy=mapobj.fy
			modeA=mapobj.modeA
			modeB=mapobj.modeB


	vc=mapobj.vc
	uc=mapobj.uc



	refpos=bs.value(mpv,mpu)
	ptsa=[] # abbildung des uv-iso-gitter auf die xy-Ebene

	mpv *=sv
	mpu *=su

	for v in range(vc+1):
		pts=[]
		vaa=1.0/vc*v*sv

		bbc=bs.vIso(vaa)

		for u in range(uc+1):
			uaa=1.0/uc*u*su
			ba=bs.uIso(uaa)

			ky=ba.length(vaa,mpv)
			if vaa<mpv: ky =-ky

			kx=bbc.length(mpu,uaa)
			if uaa<mpu: kx =-kx

			pts.append([kx,ky,0])

		ptsa.append(pts)


	ptsa=np.array(ptsa).swapaxes(0,1)

	vs=[1.0/vc*v for v in range(vc+1)]
	us=[1.0/uc*u for u in range(uc+1)]

	uv2x = scipy.interpolate.interp2d(us, vs, ptsa[:,:,0], kind=modeA)
	uv2y = scipy.interpolate.interp2d(us, vs, ptsa[:,:,1], kind=modeA)


	# if only 3D to 2D is needed, exit here
	if mapobj == None:
		xy2v=None
		xy2u=None
		return [uv2x,uv2y,xy2u,xy2v]

#------------------------------------------------------

	#d=mapobj.border
	d=0

	kku=[]

	for ui in range(d,uc+1-d):
		for vi in range(d,vc+1-d):
			kku.append([ptsa[ui,vi,0],ptsa[ui,vi,1], us[ui]])
	kku=np.array(kku)

	kkv=[]
	for ui in range(d,uc+1-d):
		for vi in range(d,vc+1-d):
			kkv.append([ptsa[ui,vi,0],ptsa[ui,vi,1], vs[vi]])
	kkv=np.array(kkv)

	try:
		dx=mapobj.ue
		dy=mapobj.ve
		sx=mapobj.ub
		sy=mapobj.vb

		#print ("Shape",uc+1,vc+1,(uc+1)*(vc+1),np.array(kku).shape)
		kku2=np.array(kku).reshape(uc+1,vc+1,3)
		#print(dx,dy,sx,sy)
		#print ("Shape aa",dx,dy,dx*dy,np.array(kku2[sx:sx+dx,sy:sy+dy]).shape)
		kkua=kku2[sx:sx+dx,sy:sy+dy].reshape((dx)*(dy),3)

		kkv2=np.array(kkv).reshape(uc+1,vc+1,3)
		kkva=kkv2[sx:sx+dx,sy:sy+dy].reshape(dx*dy,3)

		xy2u = scipy.interpolate.Rbf(kkua[:,0],kkua[:,1],kkua[:,2], function=modeB)
		xy2v = scipy.interpolate.Rbf(kkva[:,0],kkva[:,1],kkva[:,2], function=modeB)

#		xy2v = scipy.interpolate.interp2d(kkv[:,0],kkv[:,1],kkv[:,2], kind=mode)
# ideas for error
# https://stackoverflow.com/questions/34820612/scipy-interp2d-warning-and-different-result-than-expected


	except Exception as err:
		sayexc()
		print('Handling  error:', err)
		xy2v=None
		xy2u=None
		print "FEHLER BERECHNUNG bUMKEHRfunktionen"


	return [uv2x,uv2y,xy2u,xy2v]

	if 0: # testrechnung sollte auf gleiche stelle zurueck kommen
		u0=0.2
		v0=0.6

		y=uv2y(u0,v0)
		x=uv2x(u0,v0)
		u=xy2v(x,y)
		v=xy2u(x,y)

		print (u0,v0,x,y,u,v)

	return [uv2x,uv2y,xy2u,xy2v]



##\cond

def run_fulltest(obj, mpv=0.5, mpu=0.5, fx=-1, fy=-1, vc=30, uc=30 ):
	'''testmethode'''

	'''  Hilfsobjekte zeichnen   
	mittelpunkt in uv: mpv, mpu
	skalierung/lage der xy-Ebene: fx,fy 
	anzahl der gitterlinien: vc,uc
	'''

	#fx,fy=1,1

	bs=obj.Shape.Face1.Surface
	refpos=bs.value(mpv,mpu)

	if 1: # display centers
		s=App.ActiveDocument.addObject("Part::Sphere","Center Face")
		s.Placement.Base=bs.value(mpv,mpu)

		s=App.ActiveDocument.addObject("Part::Sphere","Center Map")



	if 1: # display grids
		comps=[]
		ptsa=[]

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
				ptsk.append(bs.value(vm,uv))

				pts.append([kx,ky,0])
			ptsa.append(pts)

			comps += [ Part.makePolygon(ptsk)]

		Part.show(Part.Compound(comps))
		App.ActiveDocument.ActiveObject.Label="Grid"


		if 1:
			comps=[]

			for pts in ptsa:
				comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts]) ]

			ptsa=np.array(ptsa).swapaxes(0,1)
			for pts in ptsa:
				comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts]) ]

			Part.show(Part.Compound(comps))

			# App.ActiveDocument.ActiveObject.Placement.Base=refpos

			App.ActiveDocument.ActiveObject.Label="planar Map of Grid"



	[uv2x,uv2y,xy2u,xy2v]=getmap(obj)


	if 0:
		# display 2 curves
		run_test_1(obj,bs,uv2x,uv2y,fx,fy,refpos)
		# display square grid
		run_test2_2(obj,bs,xy2u,xy2v,fx,fy,refpos)

	if 0:
		#display gird of circles 
		bs=obj.Shape.Face1.Surface
		run_test_circle(bs,xy2u,xy2v)




def run_test_1(obj,bs,uv2x,uv2y,fx,fy,refpos):
	'''testmethode'''
	
	ptss=[]
	ptsk=[]

	for a in range(21):

		um=1./20*a
		vm=0.7/20*a
		y=uv2y(vm,um)
		x=uv2x(vm,um)
		ptss.append(FreeCAD.Vector(fx*x,fy*y,0))
		ptsk.append(bs.value(um,vm))

	w1=Draft.makeWire(ptss)
	w1.Placement.Base=refpos
	w1.Label="Map uv-line"
	w1.ViewObject.LineColor=(1.,0.,1.)

	w2=Draft.makeWire(ptsk)
	w2.Label="uv-line"
	w2.ViewObject.LineColor=(1.,0.,1.)


	ptss=[]
	ptsk=[]


	for a in range(21):
		um=0.7+ 0.3*np.sin(2*np.pi*a/20)
		vm=0.5+ 0.5*np.cos(2*np.pi*a/20)

		y=uv2y(vm,um)
		x=uv2x(vm,um)
		ptss.append(FreeCAD.Vector(fx*x,fy*y,0))
		ptsk.append(bs.value(um,vm))

	w1=Draft.makeWire(ptss)
	w1.Label="Map uv-circle"
	w1.Placement.Base=refpos
	w1.ViewObject.LineColor=(1.,0.,0.)

	w2=Draft.makeWire(ptsk)
	w2.Label="uv-circle"
	w2.ViewObject.LineColor=(1.,0.,0.)




def run_test_2(obj,bs,xy2u,xy2v,fx,fy,refpos):
	'''testmethode'''

	col=[]
	col2=[]

	for m in range(-2,20):
		for n in range(2,24):
			ptsk=[]
			ptss=[]
			r=10

			xm=-100+10*m
			ym=-130+10*n
			u=xy2u(xm,ym)
			v=xy2v(xm,ym)
			
			zp=bs.value(u,v)

			#ost
			xm=-100+10*m+r
			ym=-130+10*n
			u=xy2u(xm,ym)
			v=xy2v(xm,ym)
			ze=bs.value(u,v)

			xm=-100+10*m-r
			ym=-130+10*n
			u=xy2u(xm,ym)
			v=xy2v(xm,ym)
			zw=bs.value(u,v)

			xm=-100+10*m
			ym=-130+10*n+r
			u=xy2u(xm,ym)
			v=xy2v(xm,ym)
			zn=bs.value(u,v)

			xm=-100+10*m
			ym=-130+10*n-r
			u=xy2u(xm,ym)
			v=xy2v(xm,ym)
			zs=bs.value(u,v)

			d=np.array([(zp-ze).Length,(zp-zn).Length,(zp-zw).Length,(zp-zs).Length])
			
			d *= 100/r
			d -= 100
			try:
				#if np.abs(d).max()>10:
				if np.abs(d).mean()>5:
					col2 += [Part.makePolygon([ze,zn,zw,zs,ze])]
				else:
					col += [Part.makePolygon([ze,zn,zw,zs,ze])]
			except:
				print "error polxygon"


#			print(m-10,n-13,"!", np.round(d,1))

	Part.show(Part.Compound(col))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,0.,1.)

	Part.show(Part.Compound(col2))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,0.,0.)


# drawcircle2
def run_test_circle(bs,xy2u,xy2v,RM=15,uc=10,vc=10):
	''' zeichnet Kreise auf die Flaeche bs '''

	col=[]

	for m in range(-10,10):
		for n in range(-10,10):
			ptsk=[]
			ptss=[]

			xm=10*m
			ym=10*n
			um=xy2u(xm,ym)
			vm=xy2v(xm,ym)

			pss=[]
			pm=bs.value(um,vm)

			for a in range(17):
				r=0.03
				try:
					for i in range(5):
						pa=bs.value(um+r*np.cos(np.pi*a/8),vm+r*np.sin(np.pi*a/8))
#						print ((pa-pm).Length, RM/(pa-pm).Length)
						r=r*RM/(pa-pm).Length
						pa=bs.value(um+r*np.cos(np.pi*a/8),vm+r*np.sin(np.pi*a/8))
					#print ((pa-pm).Length, RM/(pa-pm).Length)
					#print
					l=(pa-pm).Length
					pss.append(pa)
				except:
					print "error circle2 line near 408"
			try:
				col +=[Part.makePolygon(pss+[pm])]
			except:
				print "error 412"

	Part.show(Part.Compound(col))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,1.,0.)


def run():
	''' main test'''


	[source]=Gui.Selection.getSelection()

	mapa=App.ActiveDocument.MAP
	[uv2x,uv2y,xy2u,xy2v]=getmap(mapa,source)
	
	bs=source.Shape.Face1.Surface

	run_test_circle(bs,xy2u,xy2v,RM=5,uc=10,vc=10)



#run()
##\endcond
