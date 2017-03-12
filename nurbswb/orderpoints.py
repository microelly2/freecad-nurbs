import random
import Draft,Part

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import scipy as sp
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt


''' punktmenge in pfad ueberfuehren '''

def orderdata(obj,inner=False,plotit=False,medianfil=0):
	pts=None
	try:
		pts=obj.Points.Points
		print "Points"
	except:
		pts=obj.Points
		print "Draft"

	npts=np.array(pts).swapaxes(0,1)
	mp=(npts[0].mean(),npts[1].mean(),npts[2].mean())

	vm=FreeCAD.Vector(mp)
	lengths=np.array([(FreeCAD.Vector(p)-vm).Length for p in pts])

	lax=lengths.max()
	lin=lengths.min()
	lea=lengths.mean()

	pl2=FreeCAD.Placement()
	pl2.Base=vm

	# beschraenkende kreise
	cf=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetBool("DrawCircles",True)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetBool("DrawCircles",cf)
	if cf:
		if medianfil>0:
				circle = Draft.makeCircle(radius=lea,placement=pl2,face=False)
				circle.Label="Mean Circle"
				App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,0.,1.)

		else:
			if inner:
				circle = Draft.makeCircle(radius=lin,placement=pl2,face=False)
				circle.Label="Inner Circle"
				App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,1.,0.)
			else:
				circle = Draft.makeCircle(radius=lax,placement=pl2,face=False)
				circle.Label="Outer Circle"
				App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,0.,0.)

	aps={}
	rads={}

	for v in pts:
		vn=v-vm
		#	print np.arctan2(vm.x,vm.y)
		try:
			if aps[np.arctan2(vn.x,vn.y)] <> vn:
				print "Fehler 2 punkte gleiche richtung"
				print v
				print aps[np.arctan2(vn.x,vn.y)]
		except:
			aps[np.arctan2(vn.x,vn.y)]=vn
			rads[np.arctan2(vn.x,vn.y)]=vn.Length

	kaps=aps.keys()
	kaps.sort()
	ptss=[aps[k] for k in kaps]
	radss=[rads[k] for k in kaps]
	print ("lens ",len(ptss),len(pts))


	'''
	l4=radss


	# window size for smoothing
	f=1
	path=np.concatenate([[l4[0]] * f,l4,[l4[-1]]*f])
	#tt=path.swapaxes(0,1)
	y1 = sp.signal.medfilt(path,f)
	y1=y1[f:-f]
	len(l4)
	len(kaps)
	len(y1)
	'''

	radss=np.array(radss)




	if medianfil>0:
		l4=np.array(radss)
		# window size for smoothing
		f=medianfil
		path=np.concatenate([[l4[0]] * f,l4,[l4[-1]]*f])
		#tt=path.swapaxes(0,1)
		y2 = sp.signal.medfilt(path,f)
		pf=y2[f:-f]

		if plotit:
			plt.plot(kaps,radss, 'bx')
			plt.plot(kaps,pf, 'r-')
			plt.show()

		mmaa=pf

	else:

		if inner:
			z1=argrelextrema(radss, np.less)
		else:
			z1=argrelextrema(radss, np.greater)

		z1=z1[0]
		zaps=np.array(kaps)[z1]
		mm1=radss[z1]

		if inner:
			z=argrelextrema(mm1, np.less)
		else:
			z=argrelextrema(mm1, np.greater)

		z=z[0]
		zaps2=np.array(z1)[z]
		zaps=np.array(kaps)[zaps2]
		mm=mm1[z]

		mmaa=np.interp(kaps, zaps, mm)


		if plotit:
			plt.plot(kaps,radss, 'r-')
			#plt.plot(kaps,y1, 'g-')
			plt.plot(zaps,mm, 'bo-')
			plt.plot(kaps,mmaa, 'b-')
			plt.show()

	y= np.cos(kaps)
	x=np.sin(kaps)
	x *= mmaa
	y *= mmaa
	z  =  x*0

	pps=np.array([x,y,z]).swapaxes(0,1)
	goods=[FreeCAD.Vector(tuple(p))+vm for p in pps[1:]]
	Draft.makeWire(goods,closed=True,face=False)



def run():
	mf=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetInt("MedianFilterWindow",21)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetInt("MedianFilterWindow",mf)
	print mf
	dp=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetBool("ShowDataPlots",True)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetBool("ShowDataPlots",dp)

	inner=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetBool("inner",True)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetBool("inner",inner)

	outer=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetBool("outer",True)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetBool("outer",outer)

	median=FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').GetBool("median",True)
	FreeCAD.ParamGet('User parameter:Plugins/nurbs/orderpoints').SetBool("median",median)


	for obj in Gui.Selection.getSelection():
		if median:
			orderdata(obj,medianfil=mf,plotit=dp)
			App.ActiveDocument.ActiveObject.Label="Median " + str(mf) + " Approx for " + obj.Label
			App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,0.,1.)
			Gui.updateGui()
		if inner:
			orderdata(obj,inner=True,plotit=dp)
			App.ActiveDocument.ActiveObject.Label="Inner Approx for " + obj.Label
			App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,1.,0.)
			Gui.updateGui()
		if outer:
			orderdata(obj,inner=False,plotit=dp)
			App.ActiveDocument.ActiveObject.Label="Outer Approx for " + obj.Label
			App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,0.,0.)
			Gui.updateGui()


