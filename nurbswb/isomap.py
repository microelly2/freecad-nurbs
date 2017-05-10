


import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from PySide import QtGui
import Part,Mesh,Draft,Points



import Draft
import numpy as np
import scipy




#def interpolate(x,y,z, gridsize,mode=,rbfmode=True,shape=None):


#		rbf = scipy.interpolate.Rbf(x, y, z, function='thin_plate')
	#	rbf = scipy.interpolate.interp2d(x, y, z, kind=mode)

	#	zi=rbf2(yi,xi)




def runA(obj):
	#bs=App.ActiveDocument.orig.Shape.Face1.Surface
	#bs=App.ActiveDocument.MyShoe.Shape.Face1.Surface
	#bs=App.ActiveDocument.Poles.Shape.Face1.Surface
	bs=obj.Shape.Face1.Surface


	# mittelpunkt
	mpv=0.5
	mpu=0.5

	# skalierung/lage
	fx=-1
	fy=-1

	#fx,fy=1,1

	comps=[]

	s=App.ActiveDocument.addObject("Part::Sphere","Center Face")
	s.Placement.Base=bs.value(mpv,mpu)
	refpos=bs.value(mpv,mpu)

#	s=App.ActiveDocument.addObject("Part::Sphere","Center Map")

	vc=30
	uc=30

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
	#		bc=bs.uIso(uv)

			ba=bs.uIso(uv)

			ky=ba.length(vm,mpv)
			if vm<mpv: ky =-ky

	##		if v==0:
		##		bb=bs.uIso(uv)
		##		#Part.show(bb.toShape())

			kx=bbc.length(mpu,uv)
			if uv<mpu: kx =-kx
			ptsk.append(bs.value(vm,uv))

	#		print (v,u,round(kx),round(ky))#,bs.value(uv,vm))
			pts.append([kx,ky,0])
		ptsa.append(pts)

		comps += [ Part.makePolygon(ptsk)]

	Part.show(Part.Compound(comps))
	App.ActiveDocument.ActiveObject.Label="Grid"

	if 10:
		comps=[]
		for pts in ptsa:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts]) ]

		ptsa=np.array(ptsa).swapaxes(0,1)

		for pts in ptsa:
			comps += [ Part.makePolygon([FreeCAD.Vector(fx*p[0],fy*p[1],0) for p in pts]) ]

		Part.show(Part.Compound(comps))
		App.ActiveDocument.ActiveObject.Placement.Base=refpos
		App.ActiveDocument.ActiveObject.Label="planar Map of Grid"

	vs=[1.0/vc*v for v in range(vc+1)]
	us=[1./uc*u for u in range(uc+1)]

	import matplotlib.pyplot as plt
	from scipy import interpolate

	ptsa=np.array(ptsa)
	v2y = interpolate.interp1d(vs, ptsa[0,:,1])

	#vnew = np.arange(0, 1.2, 0.2)
	#ynew = x2u(vnew)   # use interpolation function returned by `interp1d`

	#plt.plot(vs, ptsa[0,:,1], 'o', vnew, ynew, '-')
	#plt.show()

	ptsb=ptsa.swapaxes(0,1)
	vu2x=[]
	for u in range(uc+1):
		um=1.*u/20
		u2x = interpolate.interp1d(us, ptsb[u,:,0], kind='cubic')
		vu2x.append(u2x)

	uv2x = interpolate.interp2d(us, vs, ptsa[:,:,0], kind='cubic')

	# geht so nicht besser 
	uv2y = interpolate.interp2d(us, vs, ptsa[:,:,1], kind='cubic')

	#--------------- reverse map
	print ("aaaaaaaaaaaaaa",len(us),len(ptsa[:,:,0]))
	print ("aaaaaaaaaaaaaa",len(vs),len(ptsa[:,:,1]))
	print ptsa.shape
	kku=[]
	for ui in range(uc+1):
		for vi in range(vc+1):
			kku.append([ptsa[ui,vi,0],ptsa[ui,vi,1], us[ui]])
	kku=np.array(kku)

	kkv=[]
	for ui in range(uc+1):
		for vi in range(vc+1):
			kkv.append([ptsa[ui,vi,0],ptsa[ui,vi,1], vs[vi]])
	kkv=np.array(kkv)
	FreeCAD.kkv=kkv.copy()
	FreeCAD.kku=kku.copy()

	import Points

	FreeCAD.kku[:,2] *=100
	pp=Points.Points([FreeCAD.Vector(tuple(p))  for  p in FreeCAD.kku])
	Points.show(pp)


	FreeCAD.kkv[:,2] *=100
	pp=Points.Points([FreeCAD.Vector(tuple(p))  for  p in FreeCAD.kkv])
	Points.show(pp)



#	xy2u = interpolate.interp2d(ptsa[:,:,0],ptsa[:,:,1],us,   kind='cubic')
#	xy2v = interpolate.interp2d(ptsa[:,:,0],ptsa[:,:,1],vs,  kind='cubic')

	xy2u=56
	xy2v=34
	xy2u = scipy.interpolate.Rbf(kku[:,0],kku[:,1],kku[:,2], function='thin_plate')
	xy2v = scipy.interpolate.Rbf(kkv[:,0],kkv[:,1],kkv[:,2], function='thin_plate')
	print "okay"




	for u in range(uc+1):
		um=1.*u/20
		#print (vu2x[u](0.025),ptsb[u,1],ptsa[1,u,0])
		# print (ptsa[1,u,0], uv2x(um,0.05))


	ptss=[]
	ptsk=[]
	for a in range(21):
		um=1./20*a
		vm=0.7/20*a
	#	y=v2y(vm)
		y=uv2y(vm,um)
		x=uv2x(vm,um)
		ptss.append(FreeCAD.Vector(fx*x,fy*y,0))
		ptsk.append(bs.value(um,vm))

	w1=Draft.makeWire(ptss)
	w1.Placement.Base=refpos
	w1.Label="Map uv-line"
	w2=Draft.makeWire(ptsk)
	w2.Label="uv-line"


	w1.ViewObject.LineColor=(1.,0.,1.)
	w2.ViewObject.LineColor=(1.,0.,1.)


	ptss=[]
	ptsk=[]
	for a in range(21):
		um=0.7+ 0.3*np.sin(2*np.pi*a/20)
		vm=0.5+ 0.5*np.cos(2*np.pi*a/20)
		# print (um,vm)
		
		y=v2y(vm)
		y=uv2y(vm,um)
		x=uv2x(vm,um)
		# print (x,y)
		ptss.append(FreeCAD.Vector(fx*x,fy*y,0))
		ptsk.append(bs.value(um,vm))

	w1=Draft.makeWire(ptss)
	w1.Label="Map uv-circle"
	w1.Placement.Base=refpos
	w2=Draft.makeWire(ptsk)
	w2.Label="uv-circle"

	w1.ViewObject.LineColor=(1.,0.,0.)
	w2.ViewObject.LineColor=(1.,0.,0.)


	print "reverse"
	if 0:
	#	for m in range(26):
		for m in  [0,5,10,15,20,25]:
			for n in range(27):
				ptsk=[]
				ptss=[]
				for a in range(21):
					xm=-100+10*m+ 25.*np.sin(2*np.pi*a/20)
					ym=-130+10*n+25.*np.cos(2*np.pi*a/20)
					# print (um,vm)
					u=xy2u(xm,ym)
					v=xy2v(xm,ym)
					print (round(xm),round(ym),round(u,2),round(v,2))
					ptsk.append(bs.value(u,v))
					ptss.append(FreeCAD.Vector(fx*xm,fy*ym,-10))



				w2=Draft.makeWire(ptsk)
				w2.Label="reverse" + str(m)

				w2.ViewObject.LineColor=(0.,1.,1.)

				w1=Draft.makeWire(ptss)
				w1.Label="Planar circle"
				w1.Placement.Base=refpos

	col=[]
	col2=[]

	for m in range(-2,24):
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

			#if np.abs(d).max()>10:
			if np.abs(d).mean()>5:
				col2 += [Part.makePolygon([ze,zn,zw,zs,ze])]
			else:
				col += [Part.makePolygon([ze,zn,zw,zs,ze])]
			print(m-10,n-13,"!", np.round(d,1))

	Part.show(Part.Compound(col))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,0.,1.)
	Part.show(Part.Compound(col2))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,0.,0.)


	bs=App.ActiveDocument.Poles.Shape.Face1.Surface
	drawcircle2(bs,xy2u,xy2v)


def run():
	[source]=Gui.Selection.getSelection()

	runA(source)





def drawcircle2(bs,xy2u,xy2v,RM=5,uc=10,vc=10):
	col=[]
#	for  ui in range(1,10):
#		for vi in range(1,10):
#			
	for m in range(-2,24):
		for n in range(2,24):
			ptsk=[]
			ptss=[]
			RM=5


			xm=-100+10*m
			ym=-130+10*n
			um=xy2u(xm,ym)
			vm=xy2v(xm,ym)

	#		um=0.1*ui
	#		vm=0.1*vi
#			um=1.0/uc*ui
#			vm=1.0/vc*vi

			pss=[]
			pm=bs.value(um,vm)
			for a in range(17):
	#			RM=5
				r=0.03
				for i in range(5):
					pa=bs.value(um+r*np.cos(np.pi*a/8),vm+r*np.sin(np.pi*a/8))
				#	print ((pa-pm).Length, RM/(pa-pm).Length)
					r=r*RM/(pa-pm).Length
					pa=bs.value(um+r*np.cos(np.pi*a/8),vm+r*np.sin(np.pi*a/8))
				#print ((pa-pm).Length, RM/(pa-pm).Length)
				#print
				l=(pa-pm).Length
				pss.append(pa)
			col +=[Part.makePolygon(pss+[pm])]
	Part.show(Part.Compound(col))
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,1.,0.)


