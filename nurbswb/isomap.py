


import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


from PySide import QtGui
import Part,Mesh,Draft,Points



import Draft
import numpy as np

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

	fx,fy=1,1

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

	for u in range(uc+1):
		um=1.*u/20
		#print (vu2x[u](0.025),ptsb[u,1],ptsa[1,u,0])
		print (ptsa[1,u,0], uv2x(um,0.05))


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
		print (x,y)
		ptss.append(FreeCAD.Vector(fx*x,fy*y,0))
		ptsk.append(bs.value(um,vm))

	w1=Draft.makeWire(ptss)
	w1.Label="Map uv-circle"
	w1.Placement.Base=refpos
	w2=Draft.makeWire(ptsk)
	w2.Label="uv-circle"

	w1.ViewObject.LineColor=(1.,0.,0.)
	w2.ViewObject.LineColor=(1.,0.,0.)





def run():
	[source]=Gui.Selection.getSelection()

	runA(source)




