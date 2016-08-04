# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- nurbs editor -
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
__version__='0.3'

# idea from  FreeCAD TemplatePyMod module by (c) 2013 Werner Mayer LGPL

# http://de.wikipedia.org/wiki/Non-Uniform_Rational_B-Spline
# http://www.opencascade.com/doc/occt-6.9.0/refman/html/class_geom___b_spline_surface.html

import numpy as np
from say import *

from pivy import coin

if 0: # change render to show triangulations 

	view = Gui.ActiveDocument.ActiveView
	viewer=view.getViewer()
	render=viewer.getSoRenderManager()

	glAction=coin.SoGLRenderAction(render.getViewportRegion())
	render.setGLRenderAction(glAction)
	render.setRenderMode(render.WIREFRAME_OVERLAY)



def setNice(flag=True): 
	''' make smooth skins '''
	p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part")
	w=p.GetFloat("MeshDeviation")
	if flag:
		p.SetFloat("MeshDeviation",0.05)
	else:
		p.SetFloat("MeshDeviation",0.5)


setNice()




class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.obj2=obj

# grundmethoden zum sichern

	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None


class Nurbs(PartFeature):
	def __init__(self, obj,uc=5,vc=5):
		PartFeature.__init__(self, obj)

		self.TypeId="Nurbs"
		obj.addProperty("App::PropertyInteger","polnumber","XYZ","Length of the Nurbs").polnumber=0

		obj.addProperty("App::PropertyInteger","degree_u","Nurbs","").degree_u=2
		obj.addProperty("App::PropertyInteger","degree_v","Nurbs","").degree_v=2
		obj.addProperty("App::PropertyInteger","nNodes_u","Generator","").nNodes_u=uc
		obj.addProperty("App::PropertyInteger","nNodes_v","Generator","").nNodes_v=vc
		obj.addProperty("App::PropertyFloatList","knot_u","Nurbs","").knot_u=[0,0,0,0.33,0.67,1,1,1]
		obj.addProperty("App::PropertyFloatList","knot_v","Nurbs","").knot_v=[0,0,0,0.33,0.67,1,1,1]
		obj.addProperty("App::PropertyFloatList","weights","Nurbs","").weights=[1]*(uc*vc)

		obj.addProperty("App::PropertyEnumeration","model","Base","").model=["NurbsSuface","NurbsCylinder","NurbsSphere"]

		obj.addProperty("App::PropertyFloat","Height","XYZ", "Height of the Nurbs").Height=1.0
		obj.addProperty("App::PropertyStringList","poles","Nurbs","")

		#obj.setEditorMode("poles", 2)

		#the poles and surface helper object link
		obj.addProperty("App::PropertyLink","polobj","XYZ","")
		obj.addProperty("App::PropertyLink","gridobj","XYZ","")
		obj.addProperty("App::PropertyLink","polselection","XYZ","")
		obj.addProperty("App::PropertyLink","polgrid","XYZ","")
		obj.addProperty("App::PropertyBool","grid","Helper","create a grid object in 3D").grid=True
		obj.addProperty("App::PropertyInteger","gridCount","Helper","").gridCount=20
		obj.addProperty("App::PropertyBool","solid","Shape","close the surface by a bottom plane").solid=True
		obj.addProperty("App::PropertyBool","base","Shape","create a base cuboid under the surface").base=True
		obj.addProperty("App::PropertyBool","polpoints","Helper","display Poles as separate Points").polpoints=False
		obj.addProperty("App::PropertyFloat","baseHeight","Shape", "height of the base cuboid").baseHeight=100
		obj.addProperty("App::PropertyFloat","stepU","Generator", "size of cell in u direction").stepU=100
		obj.addProperty("App::PropertyFloat","stepV","Generator", "size of cell in u direction").stepV=100
		obj.addProperty("App::PropertyBool","generatePoles","Generator","generate Poles from model").generatePoles=True
		obj.addProperty("App::PropertyBool","expertMode","XYZ","generate Poles from model").expertMode=False

		obj.degree_u=3
		obj.degree_v=3

		if not obj.expertMode:
			# not gui editable
			for a in ['degree_u','degree_v','poles','knot_u','knot_v','nNodes_u','nNodes_v','weights']:
				obj.setEditorMode(a, 2)

		for a in ['polnumber','Height','polselection','gridobj','polgrid','polobj']:
			obj.setEditorMode(a, 2)

		if obj.generatePoles:
			for a in ['nNodes_u','nNodes_v']:
				obj.setEditorMode(a, 0)


	def attach(self,vobj):
		print "attach -------------------------------------"
		self.Object = vobj.Object
		self.obj2 = vobj.Object



	def onChanged(self, fp, prop):
		#print "changed ",prop

		if prop == 'nNodes_u' and  fp.nNodes_u <= fp.degree_u:
			fp.nNodes_u = fp.degree_u + 1
		if prop == 'nNodes_v' and  fp.nNodes_v <= fp.degree_v:
			fp.nNodes_v = fp.degree_v + 1


		if prop=="expertMode":
			if not fp.expertMode:
				v=2
			else: 
				v=0
			for a in ['degree_u','degree_v','poles','knot_u','knot_v','nNodes_u','nNodes_v','weights']:
				try: fp.setEditorMode(a, v)
				except:  pass

		if prop=="generatePoles":
			if fp.generatePoles: v = 0
			else: v = 2
			for a in ['nNodes_u','nNodes_v','stepU','stepV']:
				try: fp.setEditorMode(a, v)
				except: pass

		if prop == 'stepU' or prop  == 'stepV' or prop == 'nNodes_u' or  prop == 'nNodes_v':

			a=App.ActiveDocument.Nurbs
			a.Proxy.obj2=a
			try:
				ps=a.Proxy.getPoints()
				a.Proxy.togrid(ps)
	#			a.Proxy.elevateVline(2,100)

				a.Proxy.updatePoles()
				a.Proxy.showGriduv()
				a.Proxy.update(fp)
			except: pass

		return

#		if  prop== "Height":
#			if hasattr(fp,"polobj"):
#				if fp.polobj<>None: App.ActiveDocument.removeObject(fp.polobj.Name) 
#				fp.polobj=self.createSurface(fp,fp.poles)
#				if fp.polobj<>None:
#					fp.polobj.ViewObject.PointSize=4
#					fp.polobj.ViewObject.PointColor=(1.0,0.0,0.0)

	def update(self, fp):
		if hasattr(fp,"polobj"):
			if fp.polobj<>None: App.ActiveDocument.removeObject(fp.polobj.Name) 
			fp.polobj=self.createSurface(fp,fp.poles)
			if fp.polobj<>None:
				fp.polobj.ViewObject.PointSize=4
				fp.polobj.ViewObject.PointColor=(1.0,0.0,0.0)


	def execute(self, fp):
		print "execute"
		self.obj2=fp
		a=fp
		a.Proxy.obj2=a

		pass

	def onDocumentRestored(self, fp):
		say(["onDocumentRestored",str(fp.Label)+ ": "+str(fp.Proxy.__class__.__name__)])
		a=App.ActiveDocument.Nurbs
		a.Proxy.obj2=a

		ps=a.Proxy.getPoints()
		 
		a.Proxy.togrid(ps)
		a.Proxy.elevateVline(2,100)
		

		a.Proxy.updatePoles()
		a.Proxy.showGriduv()
		a.Proxy.update(fp)


		if not fp.expertMode: v=2
		else:  v=0
		for a in ['degree_u','degree_v','poles','knot_u','knot_v','nNodes_u','nNodes_v','weights']:
				fp.setEditorMode(a, v)

		if fp.generatePoles: v = 0
		else: v = 2
		for a in ['nNodes_u','nNodes_v','stepU','stepV']:
			fp.setEditorMode(a, v)

		for a in ['polnumber','Height','polselection','gridobj','polgrid','polobj']:
			fp.setEditorMode(a, 2)




	def create_grid(self,bs,ct=20):
		''' create a grid of BSplineSurface bs with ct lines and rows '''

		sss=[]

		st=1.0/ct
		for iu in range(ct+1):
			pps=[]
			for iv in range(ct+1):
				p=bs.value(st*iu,st*iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		for iv in range(ct+1):
			pps=[]
			for iu in range(ct+1):
	#			p=f.valueAt(st*iu,st*iv)
				p=bs.value(st*iu,st*iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		comp=Part.Compound(sss)

		Part.show(comp)
		return App.ActiveDocument.ActiveObject

	def create_uv_grid(self):
		''' create a grid of the poles '''

		print "create uv grid"
		bs=self.bs
		sss=[]

		nNodes_u=self.obj2.nNodes_u
		nNodes_v=self.obj2.nNodes_v

		for iu in range(nNodes_u):
			pps=[]
			p=bs.getPole(1+iu,1)
			pps=[p.add(FreeCAD.Vector(0,-20,0))]

			for iv in range(nNodes_v):
#				print (iu,iv)
				p=bs.getPole(1+iu,1+iv)
				pps.append(p)

			p=bs.getPole(1+iu,nNodes_v)
			pps.append(p.add(FreeCAD.Vector(0,20,0)))


			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		for iv in range(nNodes_v):
			p=bs.getPole(1,1+iv)
			pps=[p.add(FreeCAD.Vector(-20,0,0))]
			for iu in range(nNodes_u):
				p=bs.getPole(1+iu,1+iv)
				pps.append(p)

			p=bs.getPole(nNodes_u,1+iv)
			pps.append(p.add(FreeCAD.Vector(20,0,0)))


			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		comp=Part.Compound(sss)

		Part.show(comp)
		App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.0,0.0,1.0)
		App.ActiveDocument.ActiveObject.ViewObject.LineWidth=1
		return App.ActiveDocument.ActiveObject


	def create_solid(self,bs):
		''' create a solid part with the surface as top'''


		poles=np.array(bs.getPoles())
		ka,kb,tt=poles.shape

		weights=np.array(bs.getWeights())
		multies=bs.getVMultiplicities()

		cs=[]

		for n in 0,ka-1:
			pts=[FreeCAD.Vector(tuple(p)) for p in poles[n]]
			bc=Part.BSplineCurve()
			bc.buildFromPolesMultsKnots(pts,multies,bs.getVKnots(),False,2,weights[n])
			cs.append(bc.toShape())

		poles=poles.swapaxes(0,1)
		weights=weights.swapaxes(0,1)
		multies=bs.getUMultiplicities()

		for n in 0,kb-1:
			pts=[FreeCAD.Vector(tuple(p)) for p in poles[n]]
			bc=Part.BSplineCurve()
			bc.buildFromPolesMultsKnots(pts,multies,bs.getUKnots(),False,2,weights[n])
			cs.append(bc.toShape())

		comp=Part.Compound(cs)
		Part.show(comp)

		#create wire and face
		Draft.upgrade(App.ActiveDocument.ActiveObject,delete=True)
		FreeCAD.ActiveDocument.recompute()

		Draft.upgrade(App.ActiveDocument.ActiveObject,delete=True)
		FreeCAD.ActiveDocument.recompute()

		# bottom face ...
		cur=App.ActiveDocument.ActiveObject
		s1=cur.Shape
		App.ActiveDocument.removeObject(cur.Name)

		# solid ...
		sh=Part.makeShell([s1,bs.toShape()])
		return Part.makeSolid(sh)


	def createSurface(self,obj,poles=None):
		''' create the nurbs surface and aux parts '''

		starttime=time.time()
		degree_u=obj.degree_u
		degree_v=obj.degree_v
		nNodes_u=obj.nNodes_u
		nNodes_v=obj.nNodes_v

		uc=nNodes_u
		vc=nNodes_v

		l=[1.0/(uc-2)*i for i in range(uc-1)]
		obj.knot_u=[0,0]+ l + [1,1]

		l=[1.0/(vc-2)*i for i in range(vc-1)]
		obj.knot_v=[0,0]+ l + [1,1]

		if obj.degree_u==3:
			l=[1.0/(uc-3)*i for i in range(uc-2)]
			obj.knot_u=[0,0,0]+ l + [1,1,1]

		if obj.degree_v==3:
			l=[1.0/(vc-3)*i for i in range(vc-2)]
			obj.knot_v=[0,0,0]+ l + [1,1,1]


		if obj.degree_u==1:
			l=[1.0/(uc-1)*i for i in range(uc)]
			obj.knot_u=[0]+ l + [1]

		if obj.degree_v==1:
			l=[1.0/(vc-1)*i for i in range(vc)]
			obj.knot_v=[0]+ l + [1]

		try:
			weights=np.array(obj.weights)
			weights=weights.reshape(vc,uc)
		except:
			weights=np.ones(vc*uc)
			weights=weights.reshape(vc,uc)

		obj.weights=list(np.ravel(weights))

		knot_u=obj.knot_u
		knot_v=obj.knot_v

		coor=[[0,0,1],[1,0,1],[2,0,1],[3,0,1],[4,0,1],\
			   [0,1,1],[1,1,0],[2,1,0],[3,1,0],[4,1,1],\
			   [0,2,1],[1,2,0],[2,2,3],[3,2,0],[4,2,1],\
			   [0,3,1],[1,3,0],[2,3,1],[3,3,-3],[4,3,1],\
			   [0,4,1],[1,4,1],[2,4,1],[3,4,1],[4,4,1]]


		if poles<>None:
			cc=""
			for l in poles: cc += str(l)
			coor=eval(cc)


# EXPERIMENTAL START
#--------------------------------
		if 0 and obj.model=="NurbsCylinder":
			# create cylinder face
			coor=[]
			ws=[]
			zl=[0,100,200,300,400]
			rl=[1,1.5,2,1,1] 
			rl=[1,1,2,1,1] 
#			rl=[1,1,1,1,1] 
			import random
			for iz in range(5):
				z=zl[iz]
				r=rl[iz]
				zs=[[0,-100*r,z],[100*r,-100*r,z],[100*r,0,z],[100*r,100*r,z],
						[0,100*r,z],[-100*r,100*r,z],[-100*r,0,z],[-100*r,-100*r,z],[0,-100*r,z]]

#				if iz==2:
#					zs=[[0,-100*r,z],[100*r,-100*r,z],[100*r+60,0,z],[100*r,100*r,z],
#						[0,100*r,z],[-100*r,100*r,z],[-100*r-40,0,z],[-100*r,-100*r,z],[0,-100*r,z]]

				w=[1,0.7,1,0.7,1,0.7,1,0.7,1]
				coor += zs
				ws += w
			print "coord"
			print coor
			weights=np.array(ws)
#			weights=np.ones(9*5)
			weights=weights.reshape(5,9)
			
			print len(weights)
			print weights
			weights=weights.reshape(5,9)
			
			nNodes_u=9
			nNodes_v=5
			
			knot_u=[0,0,0, 0.2,0.200001,0.4,0.400001,0.6,0.600001, 1,1,1]
#			knot_u=[0,0.,0., 0.2,0.2,0.4,0.4,0.6,0.9, 0.9,0.9]
#			knot_u=[0,0.,0.1, 0.2,0.2,0.4,0.4,0.6,0.9, 0.9,0.9]
#			knot_u=[0.0,0.0,0.1,0.1,0.2,0.2,0.4,0.4,0.6,0.6,0.96, 0.96]
			knot_v=[0,0,0,0.3,0.7,1,1,1]

			obj.knot_v= knot_v
			obj.knot_u= knot_u

			obj.weights=list(np.ravel(weights))
#--------------------------------------

#--------------------------------
		if 10 and obj.model=="NurbsCylinder":
			# create cylinder face
			
			nNodes_u=5
			nNodes_v=5
			
			

			coor=[]
			ws=[]
			yl=[0,100,200,300,400]
			rl=[1,1.5,2,1,1] 
#			rl=[1,1,1,1,1] 
#			rl=[1,1,1,1,1] 
			r=1
			y=-100
#			zs2=[[-100*r,y,0],[-100*r+1,y,0],[0,y,0],[100*r-1,y,0],[100*r,y,0]]
#			coor +=zs2
			import random
			for iz in range(5):
				y=yl[iz]
				r=rl[iz]
				if iz==0 or iz==4:
					zs=[[-100*r,y,0],[-100*r+0.0001,y,0*r],[0,y,0*r],[100*r-0.0001,y,0*r],[100*r,y,0]]
				else:
					#zs=[[-100*r,y,0],[-100*r,y,100*r+60*random.random()],[0,y,100*r+60*random.random()],[100*r,y,100*r+60*random.random()],[100*r,y,0]]
					zs=[[-100*r,y,0],[-100*r,y,100*r],[0,y,100*r],[100*r,y,100*r],[100*r,y,0]]


				w=[1,0.7,1,0.7,1]
				t=3.5
				t=3.0
				t=2
				t=1.41
				w=[t,1,t,1,t]
				coor += zs
				ws += w
			
			y=600
			r=1
			
#			zs2=[[-100*r,y,0],[-100*r+1,y,0],[0,y,0],[100*r-1,y,0],[100*r,y,0]]
#			ws += w
#			ws += w
#			coor +=zs2
			print "coord"
			print coor
			weights=np.array(ws)
#			weights=np.ones(9*5)
			
			
			print len(weights)
			print weights
			weights=weights.reshape(5,5)
			#weights=weights.reshape(5,5)
			
			
			knot_u=[0,0,0, 0.33,0.67, 1,1,1]
			knot_u=[0,0,0, 0.49,0.51, 1,1,1]
			knot_u=[0,0,0, 0.499,0.501, 1,1,1]
			knot_u=[0,0,0, 0.499,0.501, 0.9,1,1,1]
			# works
			knot_u=[0,0,0, 0.4999999,0.5000001, 1,1,1]
			# fails
			# knot_u=[0,0,0, 0.49999999,0.50000001, 1,1,1]
			
#			knot_u=[0,0.,0., 0.2,0.2,0.4,0.4,0.6,0.9, 0.9,0.9]
#			knot_u=[0,0.,0.1, 0.2,0.2,0.4,0.4,0.6,0.9, 0.9,0.9]
#			knot_u=[0.0,0.0,0.1,0.1,0.2,0.2,0.4,0.4,0.6,0.6,0.96, 0.96]
			knot_v=[0,0,0,0.3,0.5,0.8,0.9, 1,1,1]
			knot_v=[0,0,0,0.3,0.7,1,1,1]

			obj.knot_v= knot_v
			obj.knot_u= knot_u

			obj.weights=list(np.ravel(weights))
#--------------------------------------
# EXPERIMENTAL END


		obj.poles=str(coor)

		bs=Part.BSplineSurface()
		self.bs=bs


		bs.increaseDegree(degree_u,degree_v)


		if obj.model=="NurbsCylinder":
			# cylinder - experimental  play with periodic nurbs 
			pass
			# bs.setUPeriodic()

		#+#+ todo split knot vectors in single values vector and multiplicity vector
		for i in range(0,len(knot_u)):
				#if knot_u[i+1] > knot_u[i]:
						 bs.insertUKnot(knot_u[i],1,0.0000001)

		for i in range(0,len(knot_v)):
				#if knot_v[i+1] > knot_v[i]:
						 bs.insertVKnot(knot_v[i],1,0.0000001)

		# set the poles
		i=0
		for jj in range(0,nNodes_v):
			for ii in range(0,nNodes_u):
				try:
					bs.setPole(ii+1,jj+1,FreeCAD.Vector((coor[i][0],coor[i][1],coor[i][2])),weights[jj,ii])
				except:
						print([ii+1,jj+1,FreeCAD.Vector((coor[i][0],coor[i][1],coor[i][2])),weights[jj,ii]])
						sayexc("setPols ii,jj:"+str([ii,jj]))
				i=i+1;

		# create aux parts
		if obj.solid: obj.Shape=self.create_solid(bs)
		else: obj.Shape=bs.toShape()

		vis=True
		if obj.grid:
			if obj.gridobj<>None: 
				vis=obj.gridobj.ViewObject.Visibility
				App.ActiveDocument.removeObject(obj.gridobj.Name)
			obj.gridobj=self.create_grid(bs,obj.gridCount)
			obj.gridobj.Label="Nurbs Grid"
			obj.gridobj.ViewObject.Visibility=vis


		if obj.base:
			# create the socket box 
			mx=np.array(coor).reshape(nNodes_v,nNodes_u,3)
			print "create box"

			print (mx.shape)
			a0=tuple(mx[0,0])
			b0=tuple(mx[0,-1])
			c0=tuple(mx[-1,-1])
			d0=tuple(mx[-1,0])
			bh=obj.baseHeight

			a=tuple(mx[0,0]+[0,0,-bh])
			b=tuple(mx[0,-1]+[0,0,-bh])
			c=tuple(mx[-1,-1]+[0,0,-bh])
			d=tuple(mx[-1,0]+[0,0,-bh])
			print (a,b,c,d)
			
			lls=[Part.makeLine(a0,b0),Part.makeLine(b0,b),Part.makeLine(b,a),Part.makeLine(a,a0)]
			fab=Part.makeFilledFace(lls)
			lls=[Part.makeLine(b0,c0),Part.makeLine(c0,c),Part.makeLine(c,b),Part.makeLine(b,b0)]
			fbc=Part.makeFilledFace(lls)
			lls=[Part.makeLine(c0,d0),Part.makeLine(d0,d),Part.makeLine(d,c),Part.makeLine(c,c0)]
			fcd=Part.makeFilledFace(lls)
			lls=[Part.makeLine(d0,a0),Part.makeLine(a0,a),Part.makeLine(a,d),Part.makeLine(d,d0)]
			fda=Part.makeFilledFace(lls)
			lls=[Part.makeLine(a,b),Part.makeLine(b,c),Part.makeLine(c,d),Part.makeLine(d,a)]
			ff=Part.makeFilledFace(lls)

			surf=bs.toShape()
			fs=[fab,fbc,fcd,fda,ff,surf]
			comp=Part.makeCompound(fs)
			Part.show(comp)
			App.ActiveDocument.ActiveObject.Label="Nurbs with Base"

			FreeCAD.ActiveDocument.recompute()
			FreeCAD.ActiveDocument.recompute()

			# bottom face ...
			cur=App.ActiveDocument.ActiveObject
			s1=cur.Shape
			App.ActiveDocument.removeObject(cur.Name)

			# solid ...
			s=Part.makeShell([s1,bs.toShape()])

			s=Part.makeShell(fs)

			sol=Part.makeSolid(s)
#			Part.show(sol)
			obj.Shape=sol


		# create a pole grid with spines
		vis=True
		try: 
			vis=obj.polgrid.ViewObject.Visibility
			App.ActiveDocument.removeObject(obj.polgrid.Name)
		except: pass
		obj.polgrid=self.create_uv_grid()
		obj.polgrid.Label="Pole Grid"
		obj.polgrid.ViewObject.Visibility=vis

		nurbstime=time.time()


		polesobj=None
		comptime=time.time()
		
		if  obj.polpoints:
			#create the poles for visualization
			#the pole point cloud
			pts=[FreeCAD.Vector(tuple(c)) for c in coor]
			vts=[Part.Vertex(pp) for pp in pts]

			#and the surface

			# vts.append(obj.Shape)
			comp=Part.makeCompound(vts)
			comptime=time.time()
			try: yy=FreeCAD.ActiveDocument.Poles
			except: yy=FreeCAD.ActiveDocument.addObject("Part::Feature","Poles")

			yy.Shape=comp
			polesobj=App.ActiveDocument.ActiveObject
		

		endtime=time.time()

		print ("create Nurbs time",round(nurbstime-starttime,2))
#		print ("create helper time",round(endtime-nurbstime,2))
		print ("create comp time",round(comptime-nurbstime,2))
		print ("create Surface time",round(endtime-comptime,2))

		return polesobj


	def getPoints(self):
		''' generic point set for grid'''
		if self.obj2.generatePoles:
			ps=[]
			vc=self.obj2.nNodes_v
			uc=self.obj2.nNodes_u
			for v in range(vc):
				for u in range(uc):
					ps.append(FreeCAD.Vector(u*self.obj2.stepU,v*self.obj2.stepV,0))
			return ps
		else:
			t=eval(str(self.obj2.poles))
			return eval(t[0])


	def togrid(self,ps):
		''' points to 2D grid'''
		self.grid=None
		self.g=np.array(ps).reshape(self.obj2.nNodes_v,self.obj2.nNodes_u,3)
		return self.g

	def showGriduv(self):
		'''recompute and show the Pole grid '''

		starttime=time.time()
		gg=self.g

		try:
			if 	not self.calculatePoleGrid: return
		except:
			return

		ls=[]
		uc=self.obj2.nNodes_v
		vc=self.obj2.nNodes_u

		# straight line grid
		for u in range(uc):
			for v in range(vc):
				if u<uc-1:
					ls.append(Part.makeLine(tuple(gg[u][v]),tuple(gg[u+1][v])))
				if v<vc-1:
					ls.append(Part.makeLine(tuple(gg[u][v]),tuple(gg[u][v+1])))




		comp=Part.makeCompound(ls)
		if self.grid <> None:
			self.grid.Shape=comp
		else:
			Part.show(comp)
			App.ActiveDocument.ActiveObject.ViewObject.hide()
			self.grid=App.ActiveDocument.ActiveObject
			self.grid.Label="Pole Grid"

		App.activeDocument().recompute()
		Gui.updateGui()
		endtime=time.time()
		print ("create PoleGrid time",endtime-starttime)


	def setpointZ(self,u,v,h=0,w=20):
		''' set height and weight of a pole point '''

		##FreeCAD.ActiveDocument.openTransaction("set Point " +str((u,v,h,w)))

		self.g[v][u][2]=h
		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v
		try:
			wl=self.obj2.weights
			wl[v*uc+u]=w
			self.obj2.weights=wl
		except:
			sayexc()

		##self.updatePoles()
		##self.showGriduv()
		##FreeCAD.ActiveDocument.commitTransaction()

	def setpointRelativeZ(self,u,v,h=0,w=0,update=False):

		''' set relative height and weight of a pole point '''
#		if update:
#			FreeCAD.ActiveDocument.openTransaction("set Point relative " + str((u,v,h,w)))

		print self.g[v][u]
		print "realtive ",h
		print "updae Flag",update
		self.g[v][u][2] = self.gBase[v][u][2] + h
		
		print self.g[v][u]
		
		if update:
			self.gBase=self.g.copy()

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v
		try:
			wl=self.obj2.weights
			wl[v*uc+u]=w
			self.obj2.weights=wl
		except:
			sayexc()

#		if update:
#			FreeCAD.ActiveDocument.commitTransaction()





	def movePoint(self,u,v,dx,dy,dz):
		''' relative move ofa pole point '''

		FreeCAD.ActiveDocument.openTransaction("move Point " + str((u,v,dx,dy,dz)))

		self.g[v][u][0] += dx
		self.g[v][u][1] += dy
		self.g[v][u][2] += dz

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()

	def elevateUline(self,vp,height=40):
		''' change the height of all poles with teh same u value'''

		FreeCAD.ActiveDocument.openTransaction("elevate ULine" + str([vp,height]))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		for i in range(1,uc-1):
			self.g[vp][i][2]=height

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()


	def elevateVline(self,vp,height=40):

		#FreeCAD.ActiveDocument.openTransaction("elevate VLine" + str([vp,height]))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		for i in range(1,vc-1):
			self.g[i][vp][2]=height

		#self.updatePoles()
		#self.showGriduv()
		#FreeCAD.ActiveDocument.commitTransaction()

	def elevateRectangle(self,v,u,dv,du,height=50):
		''' change the height of all poles inside a rectangle of the pole grid'''

		FreeCAD.ActiveDocument.openTransaction("elevate rectangle " + str((u,v,dv,du,height)))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		for iv in range(v,v+dv+1):
			for iu in range(u,u+du+1):
				try: self.g[iu][iv][2]=height
				except: pass

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()


	def elevateCircle(self,u=20,v=30,radius=10,height=60):
		''' change the height for poles around a cenral pole '''

		FreeCAD.ActiveDocument.openTransaction("elevate Circle " + str((u,v,radius,height)))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		g=self.g
		for iv in range(vc):
			for iu in range(uc):
				try:
					if (g[iu][iv][0]-g[u][v][0])**2 + (g[iu][iv][1]-g[u][v][1])**2 <= radius**2: 
						g[iu][iv][2]=height
				except:
					pass
		self.g=g

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()

	def elevateCircle2(self,u=20,v=30,radius=10,height=60):
		''' change the height for poles around a cenral pole '''

		FreeCAD.ActiveDocument.openTransaction("elevate Circle " + str((u,v,radius,height)))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		g=self.g
		for iv in range(v-radius,v+radius+1):
			for iu in range(u-radius,u+radius+1):
				try:
					g[iu][iv][2]=height
				except:
					pass
		self.g=g

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()



	def createWaves(self,height=10,depth=-5):
		'''wave pattern over all'''

		FreeCAD.ActiveDocument.openTransaction("create waves " + str((height,depth)))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		for iv in range(1,vc-1):
			for iu in range(1,uc-1):
				
				if (iv+iu)%2 == 0:
					self.g[iu][iv][2]=height
				else:
					self.g[iu][iv][2]=depth

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()


	def addUline(self,vp,pos=0.5):
		''' insert a line of poles after vp, pos is relative to the next Uline'''

		FreeCAD.ActiveDocument.openTransaction("add ULine " +str((vp,pos))) 

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		if pos<=0: pos=0.00001
		if pos>=1: pos=1-0.00001
		pos=1-pos

		g=self.g

		vline=[]
		for i in range(uc):
			vline.append([(g[vp-1][i][0]+g[vp][i][0])/2,(g[vp-1][i][1]+g[vp][i][1])/2,0] )# (g[vp-1][i][2]+g[vp][i][2])/2

		vline=[]
		for i in range(uc):
			vline.append([(pos*g[vp-1][i][0]+(1-pos)*g[vp][i][0]),(pos*g[vp-1][i][1]+(1-pos)*g[vp][i][1]),0] )# (g[vp-1][i][2]+g[vp][i][2])/2

		vline=np.array(vline)

		gg=np.concatenate((g[:vp],[vline],g[vp:]))
		self.g=gg
		
		self.obj2.nNodes_v += 1

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()



	def addVline(self,vp,pos=0.5):

		#FreeCAD.ActiveDocument.openTransaction("add Vline " + str((vp,pos)))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		if pos<=0: pos=0.00001
		if pos>=1: pos=1-0.00001
		pos=1-pos
		
		g=self.g
		g=g.swapaxes(0,1)

		vline=[]
		for i in range(vc):
			vline.append([(pos*g[vp-1][i][0]+(1-pos)*g[vp][i][0]),(pos*g[vp-1][i][1]+(1-pos)*g[vp][i][1]),0] )# (g[vp-1][i][2]+g[vp][i][2])/2

		vline=np.array(vline)

		gg=np.concatenate((g[:vp],[vline],g[vp:]))
		gg=gg.swapaxes(0,1)
		self.g=gg

		self.obj2.nNodes_u += 1

		self.updatePoles()
		self.showGriduv()
		#FreeCAD.ActiveDocument.commitTransaction()


	def addS(self,vp):
		''' harte kante links, weicher uebergang, harte kante rechts ''' 

		FreeCAD.ActiveDocument.openTransaction("add vertical S " + str(vp))

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		g=self.g
		g=g.swapaxes(0,1)

		vline=[]
		for i in range(vc):
			pos=0.5
			if i<0.3*vc: pos= 0.0001
			if i>0.6*vc: pos= 0.9999

			vline.append([(pos*g[vp-1][i][0]+(1-pos)*g[vp][i][0]),(pos*g[vp-1][i][1]+(1-pos)*g[vp][i][1]),(pos*g[vp-1][i][2]+(1-pos)*g[vp][i][2])] )

		vline=np.array(vline)

		gg=np.concatenate((g[:vp],[vline],g[vp:]))

		self.g=gg.swapaxes(0,1)
		self.obj2.nNodes_u += 1

		self.updatePoles()
		self.showGriduv()
		FreeCAD.ActiveDocument.commitTransaction()


	def updatePoles(self):
		'''recompute polestring and recompute surface'''

		uc=self.obj2.nNodes_u
		vc=self.obj2.nNodes_v

		ll=""
		gf=self.g.reshape(uc*vc,3)
		for i in gf: 
			ll += str( list(i)) +","
		ll ="[" + ll + "]"

		self.obj2.poles=ll
		#self.onChanged(self.obj2,"Height")
		self.update(self.obj2)

	def showSelection(self,pole1,pole2):
		''' show the pole grid '''
		try:
			print ("delete ", self.obj2.polselection.Name)
			App.ActiveDocument.removeObject(self.obj2.polselection.Name)
		except: pass
		print (pole1,pole2)
		[u1,v1]=pole1
		[u2,v2]=pole2
		if u1>u2: u1,u2=u2,u1
		if v1>v2: v1,v2=v2,v1
		pts=[]
		for u in range(u1,u2+1):
			for v in range(v1,v2+1):
				#print (u,v, self.bs.getPole(u+1,v+1))
				pts.append(Part.Vertex(self.bs.getPole(u+1,v+1)))
		com=Part.Compound(pts)
		Part.show(com)
		pols=App.ActiveDocument.ActiveObject
		pols.Label="Poles Selection"
		pols.ViewObject.PointSize=8
		pols.ViewObject.PointColor=(1.0,1.0,0.0)
		self.obj2.polselection=pols



class ViewProviderNurbs:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def attach(self, obj):
		''' Setup the scene sub-graph of the view provider, this method is mandatory '''
		obj.Proxy = self
		self.Object = obj
		return

	def updateData(self, fp, prop):
		''' If a property of the handled feature has changed we have the chance to handle this here '''
		return

	def getDisplayModes(self,obj):
		modes=[]
		return modes

	def getDefaultDisplayMode(self):
		''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
		return "Shaded"

	def setDisplayMode(self,mode):
		''' Map the display mode defined in attach with those defined in getDisplayModes.
		Since they have the same names nothing needs to be done. This method is optinal.
		'''
		return mode

	def onChanged(self, vp, prop):
		pass

	def showVersion(self):
		cl=self.Object.Proxy.__class__.__name__
		PySide.QtGui.QMessageBox.information(None, "About ", "Nurbs"  +"\nVersion " + __version__)


	def setupContextMenu(self, obj, menu):
		cl=self.Object.Proxy.__class__.__name__
		action = menu.addAction("About " + cl)
		action.triggered.connect(self.showVersion)

		action = menu.addAction("Edit ...")
		action.triggered.connect(self.edit)

#		for m in self.cmenu + self.anims():
#			action = menu.addAction(m[0])
#			action.triggered.connect(m[1])

	def getIcon(self):

		return """
			/* XPM */
			static const char * ViewProviderNurbs_xpm[] = {
			"16 16 6 1",
			" 	c None",
			".	c #141010",
			"+	c #615BD2",
			"@	c #C39D55",
			"#	c #000000",
			"$	c #57C355",
			"        ........",
			"   ......++..+..",
			"   .@@@@.++..++.",
			"   .@@@@.++..++.",
			"   .@@  .++++++.",
			"  ..@@  .++..++.",
			"###@@@@ .++..++.",
			"##$.@@$#.++++++.",
			"#$#$.$$$........",
			"#$$#######      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			" #$#$$$$$#      ",
			"  ##$$$$$#      ",
			"   #######      "};
			"""

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

	def edit(self):
		import nurbs_dialog
		reload (nurbs_dialog)
		FreeCAD.tt=self
		self.Object.Object.generatePoles=False
		self.Object.Object.Label="Nurbs individual"
		self.miki=nurbs_dialog.mydialog(self.Object)

	def setEdit(self,vobj,mode=0):
		self.edit()
		return True

	def unsetEdit(self,vobj,mode=0):
		return True

	def doubleClicked(self,vobj):
		return False



def makeNurbs(uc=5,vc=7):

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Nurbs")
	a.Label="Nurbs generated"
	Nurbs(a,uc,vc)
	ViewProviderNurbs(a.ViewObject)
	a.ViewObject.ShapeColor=(0.00,1.00,1.00)
	a.ViewObject.Transparency = 70
	return a




def createnurbs():

	a=makeNurbs(6,10)
	a.solid=False
	a.base=False
	#a.grid=False

	
	polestring='''[
	[0.0, 0.0, 0.0], [40.0, 0.0, 0.0], [80.0, 0.0, 0.0], [120.0, 0.0, 0.0], [160.0, 0.0, 0.0], [200.0, 0.0, 0.0], 
	[0.0, 30.0, 0.0], [40.0, 30.0, 0.0], [80.0, 30.0, 0.0], [120.0, 30.0, 0.0], [160.0, 30.0, -60.0], [200.0, 30.0, 0.0], 
	[0.0, 60.0, 0.0], [40.0, 60.0, 0.0], [80.0, 60.0, 0.0], [120.0, 60.0, -60.0], [160.0, 60.0, -60.0], [200.0, 60.0, 0.0], 
	[0.0, 90.0, 0.0], [40.0, 90.0, 0.0], [80.0, 90.0, 0.0], [120.0, 90.0, 0.0], [160.0, 90.0, 0.0], [200.0, 90.0, 0.0], 
	[0.0, 120.0, 0.0], [40.0, 120.0, 0.0], [80.0, 120.0, 0.0], [120.0, 120.0, 0.0], [160.0, 120.0, 0.0], [200.0, 120.0, 0.0], 
	[0.0, 150.0, 0.0], [40.0, 150.0, 0.0], [80.0, 150.0, 100.0], [120.0, 150.0, 100.0], [160.0, 150.0, 80.0], [200.0, 150.0, 0.0], 
	[0.0, 180.0, 0.0], [40.0, 180.0, 0.0], [80.0, 180.0, 0.0], [120.0, 180.0, 100.0], [160.0, 180.0, 80.0], [200.0, 180.0, 0.0], [
	0.0, 210.0, 0.0], [40.0, 210.0, 100.0], [80.0, 210.0, 0.0], [120.0, 210.0, 0.0], [160.0, 210.0, 0.0], [200.0, 210.0, 0.0], 
	[0.0, 240.0, 0.0], [40.0, 240.0,0.0], [80.0, 240.0, 0.0], [120.0, 240.0, 0.0], [160.0, 240.0, 0.0], [200.0, 240.0, 0.0], 
	[0.0, 270.0, 0.0], [40.0, 270.0, 0.0], [80.0, 270.0, 0.0], [120.0, 270.0, 0.0], [160.0, 270.0, 0.0], [200.0, 270.0, 0.0]]'''

	polarr=eval(polestring)
	ps=[FreeCAD.Vector(tuple(v)) for v in polarr]
	
	a.poles=polestring
	#ps=a.Proxy.getPoints()
	
	a.Proxy.togrid(ps)
	a.Proxy.updatePoles()
	a.Proxy.showGriduv()

	App.activeDocument().recompute()
	Gui.updateGui()

	Gui.activeDocument().activeView().viewAxonometric()
	Gui.SendMsgToActiveView("ViewFit")
	a.ViewObject.startEditing()
	a.ViewObject.finishEditing()
	a.polselection.ViewObject.hide()





def testRandomB():

	
	na=20
	b=10

	a=makeNurbs(b,na)

	a.solid=False
	a.base=False
	#a.grid=False
	a.gridCount=80
	
	ps=a.Proxy.getPoints()

	if 0:
		print "random .."
		ps=np.array(FreeCAD.ps).swapaxes(0,1)
		temp,ct=ps.shape
		ps[2] += 100*np.random.random(ct)
		ps=ps.swapaxes(0,1)
	#	ps[0:3]

	ps=np.array(ps)
	ps.resize(na,b,3)
	
	for k0 in range(10):
		k=random.randint(0,na-6)
		l=random.randint(1,b-1)
		for j in range(3):
			ps[k+j][l][2] += 60
		rj=random.randint(0,2)
		print (k,rj)
		for j in range(rj):
			ps[k+3+j][l][2] += 60

	for k0 in range(10):
		k=random.randint(0,na-5)
		l=random.randint(1,b-1)

		for j in range(2):
			ps[k+j][l][2] += 30
		rj=random.randint(0,2)
		print (k,rj)
		for j in range(rj):
			ps[k+2+j][l][2] += 30


	ps.resize(na*b,3)


	a.Proxy.togrid(ps)
	a.Proxy.elevateVline(2,0)

	a.Proxy.updatePoles()
	a.Proxy.showGriduv()
	
	FreeCAD.a=a
	FreeCAD.ps=ps

	Gui.activeDocument().activeView().viewAxonometric()
	Gui.SendMsgToActiveView("ViewFit")



def runtest():
	global createnurbs
	try:
		App.closeDocument("Unnamed")
	except:
		pass

	if App.ActiveDocument==None:
		App.newDocument("Unnamed")
		App.setActiveDocument("Unnamed")
		App.ActiveDocument=App.getDocument("Unnamed")
		Gui.ActiveDocument=Gui.getDocument("Unnamed")

#	createnurbs()
	testRandomB()
