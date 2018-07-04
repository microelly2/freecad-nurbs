import FreeCAD,Part
import numpy as np
import time,random
App=FreeCAD

# constraints
'''
obj=App.ActiveDocument.addObject('Part::FeaturePython','BePlane')
obj.addProperty("App::PropertyIntegerConstraint","u","huu").u=13
obj.u = (30,0,1000,100)

LowerBound	
UpperBound	
StepSize	

'''


if 0:
	faces=[
		App.ActiveDocument.Cell,
		App.ActiveDocument.Cell001,
		App.ActiveDocument.Cell002,
	#	App.ActiveDocument.Cell003,
	#	App.ActiveDocument.BePlane
		]

faces=[
#	App.ActiveDocument.Cell,
#	App.ActiveDocument.Cell001,
#	App.ActiveDocument.Cell002,
#	App.ActiveDocument.BePlane002,
#	App.ActiveDocument.BePlane001,
	App.ActiveDocument.BePlane
	]

import nurbswb.say


class Point(object):
	def __init__(self,point,sf,f):
		self.point=point
		self.sfs=[sf]
		self.fs=[f]

	def addsf(self,sf,f):
		self.sfs += [sf]
		self.fs += [f]

	def printFaces(self):
		print self.point
		for f in self.fs:

			print f.Label," ",
		print

def editcross(poles,u,v):
	comps=[]
#	v -=1
#	print ("editcross------------------",u,v,poles.shape)
	uc,vc,_=poles.shape
	umi=max(u-3,0)
	uma=min(uc-1,u+3)
	vmi=max(v-3,0)
	vma=min(vc-1,v+3)
#	print  (umi,uma,vmi,vma)
	for u in range(umi,uma):
		if u%3==0:
			for v in range(vmi,vma+1):
				if v%3==0:
					bc=Part.BSplineCurve()
					bc.buildFromPolesMultsKnots(poles[u:u+4,v],[4,4],[0,1],False,3)
					comps += [bc.toShape()]
	for u in range(umi,uma+1):
		if u%3==0:
			for v in range(vmi,vma):
				if v%3==0:
					bc=Part.BSplineCurve()
					bc.buildFromPolesMultsKnots(poles[u,v:v+4],[4,4],[0,1],False,3)
					comps += [bc.toShape()]
	return comps


class Multiface(object):
	def __init__(self):
		self.faces=faces
		self.nameF="tmp_multiFace"
		self.nameP="tmp_poles"
		self.nameE="tmp_edit"
		self.createHelper()
		self.selection=[]
		self.compe=[]
		
	def createHelper(self):
		comp=[]

		obj2=App.ActiveDocument.getObject(self.nameP)
		if obj2==None:
			#obj2=App.activeDocument().addObject("Part::Compound","Compound")
			obj2=App.ActiveDocument.addObject('Part::Feature',self.nameP)
			obj2.Placement.Base.z=100
			obj2.ViewObject.PointColor=(1.0,0.6,0.8)
			obj2.ViewObject.PointSize=6


		obj3=App.ActiveDocument.getObject(self.nameE)
		if obj3==None:
			#obj2=App.activeDocument().addObject("Part::Compound","Compound")
			obj3=App.ActiveDocument.addObject('Part::Feature',self.nameE)
			obj3.ViewObject.LineColor=(1.0,0.,0.)
			obj3.ViewObject.LineWidth=3



		obj=App.ActiveDocument.getObject(self.nameF)
		if obj==None:
			#obj=App.activeDocument().addObject("Part::Compound","Compound")
			#obj=App.ActiveDocument.addObject('Part::Feature',self.nameF)
			obj=App.ActiveDocument.addObject('Part::Spline',self.nameF)
			obj.ViewObject.Selectable=False
			obj.ViewObject.Transparency=70
			obj.ViewObject.ShapeColor=(1.0,0.3,0.2)
			for ff in self.faces:
				print ff.Label
				ff.ViewObject.hide()
				comp += ff.Shape.Faces
			obj.Shape=Part.Compound(comp)
		else:
			print "!!!!!!!!!!!!###" #,obj.Shape.Faces
#			print App.ActiveDocument.tmp_multiFace.Shape.Faces
			for ff in obj.Shape.Faces:
				comp += [ff]
#				print comp
		self.faceobj=obj
		self.comp=comp
#		print comp
		print "helper created"


	def getPoints(self):
		points={}
		for f in faces:
			sf=f.Shape.Face1.Surface
			sf.NbUPoles
			#poles=np.array(sf.getPoles()).reshape(sf.NbUPoles*sf.NbVPoles,3)
			poles=[v.Point for v in f.Shape.Vertexes]
			for p in poles:
				t=tuple(p)
				try: points[t].addsf(sf,f)
				
				except:
					points[t]=Point(p,sf,f)
		print "getPoints",len(points)
		self.points=points

	def findPoint(self,vec):
		print "findpoint ",vec
		try: 
			t=tuple(vec)
			pp=self.points[t]
			pp.printFaces()
		except:
			print "nicht gefunden"
		for i,p in enumerate(self.points):
			print (i,(vec-FreeCAD.Vector(p)).Length)
			if (vec-FreeCAD.Vector(p)).Length<0.1 :
				print "gefunden ",i
				return FreeCAD.Vector(p)



	def movePoint(self,vec,mov,scanonly=False,params=None):
			points=self.points
#			print "Move points........"
#			print "suche ", vec

			arc=50-random.random()*100
			arc=0

			comp=[]
			compe=self.compe
			pts=[]

			if params <> None:
				mov=FreeCAD.Vector(
					params.root.ids['xdial'].value()*params.root.ids['scale'].value(),
					params.root.ids['ydial'].value()*params.root.ids['scale'].value(),
					params.root.ids['zdial'].value()*params.root.ids['scale'].value(),
				)
#			upn=int(self.root.ids['ux'].text())
#			vpn=int(self.root.ids['vx'].text())


			for sfi,sfa in enumerate(self.comp):
				try:
				#if 1:
					ta=time.time()
					sf=sfa.Surface
#					print (self.faces[sfi].Label,"###################",sfi)
					poles=np.array(sf.getPoles()).reshape(sf.NbUPoles*sf.NbVPoles,3)
					found=-1
					for i,p in enumerate(poles):
						if vec != None  and (vec-FreeCAD.Vector(p)).Length<0.1 :
#							print "gefunden ",i
							found=i
					if found == -1:
#						print "NICHT gefunden /kein Vector"
						comp += [self.comp[sfi]]
					else:
						base=poles[found]
						#poles[found]=vec+mov


						vi=found % sf.NbVPoles
						ui=found // sf.NbVPoles

						self.selection += [(sfi,ui,vi,base.copy())]

						pps=[(ui,vi)]
						pps=[]
						umi=max(ui-1,0)
						uma=min(sf.NbUPoles-1,ui+1)
						vmi=max(vi-1,0)
						vma=min(sf.NbVPoles-1,vi+1)
						
						pps += [(uk,vk) for uk in range(umi,uma+1) for vk in range(vmi,vma+1)]

						if 0:
							if ui>0 and ui<sf.NbUPoles-1:
								pps +=[(ui-1,vi),(ui+1,vi)]
							if vi>0 and vi<sf.NbVPoles-1:
								pps +=[(ui,vi-1),(ui,vi+1)]

							if ui==0: 
		#						print "south"
								pps +=[(ui+1,vi)]
							if vi==0:
		#						print "west"
								pps +=[(ui,vi+1)]
							if ui==sf.NbUPoles-1:
		#						print "north"
								pps +=[(ui-1,vi)]
							if vi==sf.NbVPoles-1:
		#						print "east"
								pps +=[(ui,vi-1)]

						poles=poles.reshape(sf.NbUPoles,sf.NbVPoles,3)
	#					print "nachbarn ",pps
						# nachbaren mitnehmen
						for (u,v) in pps:
	#						print (u,v)
							
							rot=FreeCAD.Rotation(arc,0,0)
							vv=FreeCAD.Vector(poles[u,v]-base)
							vv=rot.multVec(vv)
							# vv *= 3.
							poles[u,v] =base+vv+mov



						compe += editcross(poles,ui,vi)

						ptsa=[[3*uii,3*vii] for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
						if scanonly:
							poles=np.array(sf.getPoles())


						ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]

						ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
						pts += [FreeCAD.Vector(p) for p in ptsa]


						bs=Part.BSplineSurface()
						bs.buildFromPolesMultsKnots(poles,
								sf.getUMultiplicities(),sf.getVMultiplicities(),
								sf.getUKnots(),sf.getVKnots(),
								False,False,sf.UDegree,sf.VDegree)

						comp += [bs.toShape()]
#					print "Time step ",time.time()-ta
				except:
				#else:
					print "Problem bei ",sfi
					nurbswb.say.sayexc("sfi-problem")
					comp += [self.comp[sfi]]

				poles=np.array(sf.getPoles())

				ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
				ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
				pts += [FreeCAD.Vector(p) for p in ptsa]

				



			ta=time.time()
			obj=App.ActiveDocument.getObject(self.nameF)
			obj.Shape=Part.Compound(comp)

#			print "Time compA  ",time.time()-ta
			ta=time.time()
			obj2=App.ActiveDocument.getObject(self.nameP)
			pm=obj2.Placement
			comp2=[Part.Vertex(FreeCAD.Vector(p)) for p in pts]
			obj2.Shape=Part.Compound(comp2)
			obj2.Placement=pm


			obj3=App.ActiveDocument.getObject(self.nameE)
			obj3.Shape=Part.Compound(compe)

			self.comp=comp
			
			
			print "Time compB  ",time.time()-ta

			if 0:
				ta=time.time()
				obj=App.ActiveDocument.getObject(self.nameF)
				for c in comp:
					Part.show(c)
				print "Time compC  ",time.time()-ta


	# neue version ohne suchen
	def XmovePoint(self,vec,mov,scanonly=False,params=None,useselections=False):
			points=self.points
			print "Move points...XXX....."
#			print "suche ", vec

			print "useselections ",useselections
			
			arc=50-random.random()*100
			arc=0

			comp=[]
			compe=self.compe
			pts=[]

			if params <> None:
				mov=FreeCAD.Vector(
					params.root.ids['xdial'].value()*params.root.ids['scale'].value(),
					params.root.ids['ydial'].value()*params.root.ids['scale'].value(),
					params.root.ids['zdial'].value()*params.root.ids['scale'].value(),
				)
#			upn=int(self.root.ids['ux'].text())
#			vpn=int(self.root.ids['vx'].text())


			if not useselections:
				for sfi,sfa in enumerate(self.comp):
					try:
					#if 1:
						ta=time.time()
						sf=sfa.Surface
	#					print (self.faces[sfi].Label,"###################",sfi)
						poles=np.array(sf.getPoles()).reshape(sf.NbUPoles*sf.NbVPoles,3)
						found=-1
						for i,p in enumerate(poles):
							if vec != None  and (vec-FreeCAD.Vector(p)).Length<0.1 :
	#							print "gefunden ",i
								found=i
						if found == -1:
	#						print "NICHT gefunden /kein Vector"
							comp += [self.comp[sfi]]
						else:
							base=poles[found]
							#poles[found]=vec+mov


							vi=found % sf.NbVPoles
							ui=found // sf.NbVPoles

							self.selection += [(sfi,ui,vi,base.copy())]

							pps=[(ui,vi)]
							pps=[]
							umi=max(ui-1,0)
							uma=min(sf.NbUPoles-1,ui+1)
							vmi=max(vi-1,0)
							vma=min(sf.NbVPoles-1,vi+1)
							
							pps += [(uk,vk) for uk in range(umi,uma+1) for vk in range(vmi,vma+1)]

							if 0:
								if ui>0 and ui<sf.NbUPoles-1:
									pps +=[(ui-1,vi),(ui+1,vi)]
								if vi>0 and vi<sf.NbVPoles-1:
									pps +=[(ui,vi-1),(ui,vi+1)]

								if ui==0: 
			#						print "south"
									pps +=[(ui+1,vi)]
								if vi==0:
			#						print "west"
									pps +=[(ui,vi+1)]
								if ui==sf.NbUPoles-1:
			#						print "north"
									pps +=[(ui-1,vi)]
								if vi==sf.NbVPoles-1:
			#						print "east"
									pps +=[(ui,vi-1)]

							poles=poles.reshape(sf.NbUPoles,sf.NbVPoles,3)
		#					print "nachbarn ",pps
							# nachbaren mitnehmen
							for (u,v) in pps:
		#						print (u,v)
								
								rot=FreeCAD.Rotation(arc,0,0)
								vv=FreeCAD.Vector(poles[u,v]-base)
								vv=rot.multVec(vv)
								# vv *= 3.
								poles[u,v] =base+vv+mov



							compe += editcross(poles,ui,vi)

							ptsa=[[3*uii,3*vii] for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
							if scanonly:
								poles=np.array(sf.getPoles())


							ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]

							ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
							pts += [FreeCAD.Vector(p) for p in ptsa]


							bs=Part.BSplineSurface()
							bs.buildFromPolesMultsKnots(poles,
									sf.getUMultiplicities(),sf.getVMultiplicities(),
									sf.getUKnots(),sf.getVKnots(),
									False,False,sf.UDegree,sf.VDegree)

							comp += [bs.toShape()]
	#					print "Time step ",time.time()-ta
					except:
					#else:
						print "Problem bei ",sfi
						nurbswb.say.sayexc("sfi-problem")
						comp += [self.comp[sfi]]

					poles=np.array(sf.getPoles())

					ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
					ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
					pts += [FreeCAD.Vector(p) for p in ptsa]

			else:
				print "useselections"
				print self.selection
			#--------------------------------------------
				for (sfi,ui,vi,p) in self.selection:
						sf=self.comp[sfi].Surface
						poles=np.array(sf.getPoles())
						base=poles[ui,vi]

						pps=[(ui,vi)]
						pps=[]
						umi=max(ui-1,0)
						uma=min(sf.NbUPoles-1,ui+1)
						vmi=max(vi-1,0)
						vma=min(sf.NbVPoles-1,vi+1)

						pps += [(uk,vk) for uk in range(umi,uma+1) for vk in range(vmi,vma+1)]

						if 0:
								if ui>0 and ui<sf.NbUPoles-1:
									pps +=[(ui-1,vi),(ui+1,vi)]
								if vi>0 and vi<sf.NbVPoles-1:
									pps +=[(ui,vi-1),(ui,vi+1)]

								if ui==0: 
			#						print "south"
									pps +=[(ui+1,vi)]
								if vi==0:
			#						print "west"
									pps +=[(ui,vi+1)]
								if ui==sf.NbUPoles-1:
			#						print "north"
									pps +=[(ui-1,vi)]
								if vi==sf.NbVPoles-1:
			#						print "east"
									pps +=[(ui,vi-1)]

						for (u,v) in pps:
							rot=FreeCAD.Rotation(arc,0,0)
							vv=FreeCAD.Vector(poles[u,v]-base)
							vv=rot.multVec(vv)
							poles[u,v] =base+vv+mov

							compe += editcross(poles,ui,vi)

							ptsa=[[3*uii,3*vii] for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
							if scanonly:
								poles=np.array(sf.getPoles())

							ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]

							ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
							pts += [FreeCAD.Vector(p) for p in ptsa]


							bs=Part.BSplineSurface()
							bs.buildFromPolesMultsKnots(poles,
									sf.getUMultiplicities(),sf.getVMultiplicities(),
									sf.getUKnots(),sf.getVKnots(),
									False,False,sf.UDegree,sf.VDegree)

							comp += [bs.toShape()]

						poles=np.array(sf.getPoles())

						ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
						ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
						pts += [FreeCAD.Vector(p) for p in ptsa]


			#--------------------------------------------

			ta=time.time()
			obj=App.ActiveDocument.getObject(self.nameF)
			obj.Shape=Part.Compound(comp)

#			print "Time compA  ",time.time()-ta
			ta=time.time()
			obj2=App.ActiveDocument.getObject(self.nameP)
			pm=obj2.Placement
			comp2=[Part.Vertex(FreeCAD.Vector(p)) for p in pts]
			obj2.Shape=Part.Compound(comp2)
			obj2.Placement=pm


			obj3=App.ActiveDocument.getObject(self.nameE)
			obj3.Shape=Part.Compound(compe)

#			self.comp=comp


			print "Time compB  ",time.time()-ta

			if 0:
				ta=time.time()
				obj=App.ActiveDocument.getObject(self.nameF)
				for c in comp:
					Part.show(c)
				print "Time compC  ",time.time()-ta


	def update(self,params,force):
		
		mov=FreeCAD.Vector(
					params.root.ids['xdial'].value()*params.root.ids['scale'].value(),
					params.root.ids['ydial'].value()*params.root.ids['scale'].value(),
					params.root.ids['zdial'].value()*params.root.ids['scale'].value(),
				)

		rot=FreeCAD.Rotation(
					params.root.ids['xrot'].value(),
					params.root.ids['yrot'].value(),
					params.root.ids['zrot'].value(),
		)


		compe=[]
		comp=[c for c in self.comp]

		print "SELECTION LOOP"
		for sel in self.selection:
			si,ui,vi,p=sel
			print si
			print comp[si]
			poles=np.array(comp[si].Surface.getPoles())
			print poles[ui,vi]
			base=FreeCAD.Vector(poles[ui,vi])
			print p
			print "------------------"
		
			sf=comp[si].Surface

			pps=[]
			umi=max(ui-1,0)
			uma=min(sf.NbUPoles-1,ui+1)
			vmi=max(vi-1,0)
			vma=min(sf.NbVPoles-1,vi+1)

			pps += [(uk,vk) for uk in range(umi,uma+1) for vk in range(vmi,vma+1)]

			try:
				(t1,t2)=sf.tangent(ui,vi)
				t1=t1.normalize()
				t2=t2.normalize()
				n=sf.normal(ui,vi)
				n=n.normalize()
				vectn=t1*params.root.ids['udial'].value()*params.root.ids['scale'].value()+\
								t2*params.root.ids['vdial'].value()*params.root.ids['scale'].value()+\
								n*params.root.ids['ndial'].value()*params.root.ids['scale'].value()
				print "NORMAL/TAN", vectn
			except:
				vectn=FreeCAD.Vector()

			#	ttp += vec + center +vectn
			#	poles[startu:endu,startv:endv]=ttp



			for (u,v) in pps:
#				rot=FreeCAD.Rotation(arc,0,0)
				vv=FreeCAD.Vector(poles[u,v]-base)
				vv=rot.multVec(vv)
				poles[u,v] =base+vv+mov+vectn

			compe += editcross(poles,ui,vi)


#			poles[ui,vi] += mov


			bs=Part.BSplineSurface()
			bs.buildFromPolesMultsKnots(poles,
					sf.getUMultiplicities(),sf.getVMultiplicities(),
					sf.getUKnots(),sf.getVKnots(),
					False,False,sf.UDegree,sf.VDegree)
			comp[si]=bs.toShape()

		obj=App.ActiveDocument.getObject(self.nameF)
		obj.Shape=Part.Compound(comp)
		if force:
			self.comp=comp


		# alle poles ausrechnen
		pts=[]
		for c in comp:
			sf=c.Surface
			poles=np.array(c.Surface.getPoles())
			ptsa=[FreeCAD.Vector(poles[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]
			ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
			pts += [FreeCAD.Vector(p) for p in ptsa]


		obj2=App.ActiveDocument.getObject(self.nameP)
		pm=obj2.Placement
		comp2=[Part.Vertex(FreeCAD.Vector(p)) for p in pts]
		obj2.Shape=Part.Compound(comp2)
		obj2.Placement=pm

		obj3=App.ActiveDocument.getObject(self.nameE)
		obj3.Shape=Part.Compound(compe)




import FreeCADGui as Gui





#----------------------------
# Gui
#---------------------------







def flattenRegion(selections):





	def flattenregion(bs,ua,ub,va,vb):


		poles=np.array(bs.getPoles())
		poles2=np.zeros(4*4*3).reshape(4,4,3)

		v=va
		u=ua

		poles2[0:2,0:2]=poles[u:u+2,v:v+2]
		u=ub

		poles2[2:4,0:2]=poles[u-1:u+1,v:v+2]


		v=vb
		u=ua
		poles2[0:2,2:4]=poles[u:u+2,v-1:v+1]
		u=ub
		poles2[2:4,2:4]=poles[u-1:u+1,v-1:v+1]


		bs2=Part.BSplineSurface()
		bs2.buildFromPolesMultsKnots(poles2, 
			[4,4],[4,4],
			[0,1],[0,1],
			False,False,3,3)

		Part.show(bs2.toShape())


		for u in range(ua,ub+1):
			for v in range(va,vb+1):
				(uu,vv)=bs2.parameter(FreeCAD.Vector(poles[u,v]))
				pos=bs2.value(uu,vv)
				poles[u,v]=pos

		n=(ub-ua)/3
		for i in range(1,n):
			bs2.insertUKnot(1.0/n*i,3,0)

		n=(vb-va)/3
		for i in range(1,n):
			bs2.insertVKnot(1.0/n*i,3,0)

		Part.show(bs2.toShape())
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
		App.ActiveDocument.ActiveObject.ViewObject.Transparency=70
		App.ActiveDocument.BeGrid002.Source=App.ActiveDocument.ActiveObject

		poles2=np.array(bs2.getPoles())
		print poles2.shape
		
		#return bs2
		poles[ua:ub+1,va:vb+1]=poles2
		if 0:
			poles[ua-1,va+1:vb]=poles[ua,va+1:vb]*2-poles[ua+1,va+1:vb]
			poles[ub+1,va+1:vb]=poles[ub,va+1:vb]*2-poles[ub-1,va+1:vb]

			poles[ua+1:ub,va-1]=poles[ua+1:ub,va]*2-poles[ua+1:ub,va+1]
			poles[ua+1:ub,vb+1]=poles[ua+1:ub,vb]*2-poles[ua+1:ub,vb-1]


		poles[ua-1,va+2:vb-1]=poles[ua,va+2:vb-1]*2-poles[ua+1,va+2:vb-1]
		poles[ub+1,va+2:vb-1]=poles[ub,va+2:vb-1]*2-poles[ub-1,va+2:vb-1]

		poles[ua+2:ub-1,va-1]=poles[ua+2:ub-1,va]*2-poles[ua+2:ub-1,va+1]
		poles[ua+2:ub-1,vb+1]=poles[ua+2:ub-1,vb]*2-poles[ua+2:ub-1,vb-1]


		bs3=Part.BSplineSurface()
		bs3.buildFromPolesMultsKnots(poles, 
						bs.getUMultiplicities(),
						bs.getVMultiplicities(),
						bs.getUKnots(),
						bs.getVKnots(),
						False,False,3,3)
		return bs3


	bs=App.ActiveDocument.BePlane.Shape.Face1.Surface
	print selections

	ua=selections[0][1]
	va=selections[0][2]
	ub=selections[1][1]
	vb=selections[1][2]
	
	try:
		App.ActiveDocument.ActiveObject.ViewObject.hide()
	except:
		pass

	bs=flattenregion(bs,ua,ub,va,vb)

	if 0: #repeat with multiple areas 
		ua,va=6,6
		ub,vb=12,15
		bs=flattenregion(bs,ua,ub,va,vb)

	Part.show(bs.toShape())
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
	App.ActiveDocument.BeGrid001.Source=App.ActiveDocument.ActiveObject





def SurfaceEditor():

	from nurbswb.miki_g import createMikiGui2, MikiApp

	layout = '''
	MainWindow:
		QtGui.QLabel:
			setText:"***  Multi Face Poles Editor   D E M O  V 0.4 ***"
#		HorizontalGroup:
#			setTitle: "Pole u v"
#			QtGui.QLineEdit:
#				id: 'ux'
#				setText:"1"
#				textChanged.connect: app.relativeMode
#			QtGui.QLineEdit:
#				id: 'vx'
#				setText:"1"
#				textChanged.connect: app.relativeMode

		HorizontalGroup:
			setTitle: "Position UV-tangential Normal"
			QtGui.QDial:
				id: 'udial'
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.relativeMode
				setMinimum: -100
				setMaximum: 100
			QtGui.QDial:
				id: 'vdial'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.relativeMode
			QtGui.QDial:
				id: 'ndial'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.relativeMode

		HorizontalGroup:
			setTitle: "Position XYZ"
			QtGui.QDial:
				id: 'xdial'
				setMinimum: -100
				setMaximum: 100
				#setValue: 90
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.update
			QtGui.QDial:
				id: 'ydial'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.update
			QtGui.QDial:
				id: 'zdial'
				setMinimum: -100.
				setMaximum: 100.
				#setValue: 90.
				valueChanged.connect: app.update

		HorizontalGroup:
			setTitle: "Rotation Euler"
			QtGui.QDial:
				id: 'xrot'
				setMinimum: -100
				setMaximum: 100
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.relativeMode
			QtGui.QDial:
				id: 'yrot'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.relativeMode
			QtGui.QDial:
				id: 'zrot'
				setMinimum: -100.
				setMaximum: 100.
				valueChanged.connect: app.relativeMode

		HorizontalGroup:
			setTitle: "scale"
			QtGui.QSlider:
				id: 'scale'
				setValue: 10.0
				setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
				valueChanged.connect: app.update

		QtGui.QCheckBox:
			id: 'showface'
			setText: 'Show Face'
			stateChanged.connect: app.relativeMode
			setChecked: True

		QtGui.QCheckBox:
			id: 'showtangents'
			setText: 'Show Tangents'
			stateChanged.connect: app.relativeMode
			setChecked: True

		QtGui.QCheckBox:
			id: 'showcurves'
			setText: 'Show Curves'
			stateChanged.connect: app.relativeMode
			setChecked: True



#		HorizontalGroup:
#			setTitle: "Mode"
#			QtGui.QComboBox:
#				id: 'mode'
#				addItem: "u"
#				addItem: "v"
#		QtGui.QPushButton:
#			setText: "Run Action"
#			clicked.connect: app.run

		QtGui.QPushButton:
			setText: "connect to selected point"
#			clicked.connect: app.connectSelection


		QtGui.QPushButton:
			setText: "apply"
			clicked.connect: app.apply

		QtGui.QPushButton:
			setText: "apply and close"
			clicked.connect: app.applyandclose

		QtGui.QPushButton:
			setText: "cancel and close"
			clicked.connect: app.myclose

		QtGui.QPushButton:
			setText: "reset dialog"
			clicked.connect: app.resetDialog

		QtGui.QPushButton:
			setText: "init data"
			clicked.connect: app.initData

		QtGui.QPushButton:
			setText: "clear selection"
			clicked.connect: app.clearSelection

		QtGui.QPushButton:
			setText: "set selection"
			clicked.connect: app.setSelection

		QtGui.QPushButton:
			setText: "add selection"
			clicked.connect: app.addSelection

		QtGui.QPushButton:
			setText: "update"
			clicked.connect: app.update

		QtGui.QPushButton:
			setText: "merge"
			clicked.connect: app.merge

		QtGui.QPushButton:
			setText: "flatten region"
			clicked.connect: app.flattenregion


		setSpacer:
		'''

	def edit(u,v,s=10):

		print ("u,v,scale",u,v,s)
		#fp=App.ActiveDocument.Seam_ProductFace001
		
		App.activeDocument().recompute()



	class EditorApp(MikiApp):

		def resetDialog(self):
			for idx in  'udial','vdial','ndial','scale','xdial','ydial','zdial','xrot','yrot','zrot':
				if self.root.ids[idx].value()<>0:
					self.root.ids[idx].setValue(0)

			self.root.ids['scale'].setValue(10)
#			upn=int(self.root.ids['ux'].text())
#			vpn=int(self.root.ids['vx'].text())


			App.activeDocument().recompute()

		def flattenregion(self):
			for s in self.multiface.selection:
				print s

			flattenRegion(self.multiface.selection)

		def save(self):
			tt=time.time()
			try: obj=self.resultobj
			except:
				obj=App.ActiveDocument.addObject('Part::Spline','result')
				try:
					App.ActiveDocument.removeObject(self.NameObj2)
				except:
					pass
				try:
					App.ActiveDocument.removeObject(self.NameObj)
				except:
					pass
#			print "savet ",time.time()-tt

			tt=time.time()
			obj.ViewObject.hide()
			obj.Shape=self.Shape
			print "savetime hidden ",time.time()-tt
			tt=time.time()
			obj.ViewObject.show()
			obj.Shape=self.Shape
			print "savetime show ",time.time()-tt

			tt=time.time()
			z=self.Shape
			z=self.Shape
			print "savetime intern ",time.time()-tt

			self.obj=obj
			self.resultobj=obj
#			print "savetb ",time.time()-tt

		def applyandclose(self):
			fp=self.obj
			self.save()
			try:
				App.ActiveDocument.removeObject(self.NameObj2)
				App.ActiveDocument.removeObject(self.NameObj)
			except:
				pass
			self.close()


		def myclose(self):
			try:
				App.ActiveDocument.removeObject(self.NameObj2)
				App.ActiveDocument.removeObject(self.NameObj)
			except:
				pass
			self.close()

		def run(self):
			print "run"
			edit(
				self.root.ids['udial'].value(),
				self.root.ids['vdial'].value(),
				self.root.ids['scale'].value(),
			)




		def relativeMode(self):
			print "relative mode called"
			self.update()

		def Xapply(self,save=True):
#			print "apply  implemented"
			st=time.time()

			vec=FreeCAD.Vector(
						self.root.ids['xdial'].value()*self.root.ids['scale'].value(),
						self.root.ids['ydial'].value()*self.root.ids['scale'].value(),
						self.root.ids['zdial'].value()*self.root.ids['scale'].value()
						)
			App.activeDocument().recompute()
			print "Time C ",time.time()-st

		def initData(self):
			print "init data a"
			m=Multiface()
			m.getPoints()
			self.multiface=m
			self.multiface.movePoint(None,FreeCAD.Vector(0,0,1000),True)
			print ("comp anz", len(self.multiface.comp))





		def clearSelection(self):
			self.multiface.selection=[]


		def setSelection(self):
			print 
			selps=Gui.Selection.getSelectionEx()[0].PickedPoints
			self.multiface.compe=[]
			self.multiface.selection=[]
			for vt in selps:
				print vt 
				vt -= App.ActiveDocument.tmp_poles.Placement.Base
				self.multiface.movePoint(vt,FreeCAD.Vector(0,0,2000),True,params=self)
			print "SELECTIONS"
			for s in self.multiface.selection:
				print s
			App.activeDocument().recompute()
			App.ActiveDocument.getObject(self.multiface.nameE).ViewObject.show()

		def update(self):
			ta=time.time()
			self.multiface.update(params=self,force=False)
			App.activeDocument().recompute()
			print len(self.multiface.selection)
			print "update ",time.time()-ta

		def apply(self):
			ta=time.time()
			self.multiface.update(params=self,force=True)
			App.activeDocument().recompute()
			print len(self.multiface.selection)
			print "update ",time.time()-ta
			App.ActiveDocument.getObject(self.multiface.nameE).ViewObject.hide()
			App.activeDocument().recompute()



		def Xupdate(self):
			ta=time.time()
			
			print len(self.multiface.selection)
			selps=[FreeCAD.Vector(p[3]) for p in self.multiface.selection]
			sels=self.multiface.selection
			self.multiface.selection=[]
			self.multiface.compe=[]
			for vt in selps:
				print "X"
				self.multiface.movePoint(vt,FreeCAD.Vector(0,0,2000),True,params=self,useselections=True)
			App.activeDocument().recompute()
			print len(self.multiface.selection)
			print "update ",time.time()-ta


		def addSelection(self):
			print 
			selps=Gui.Selection.getSelectionEx()[0].PickedPoints
			#self.multiface.compe=[]
			# self.multiface.selection=[]
			for vt in selps:
				print vt 
				vt -= App.ActiveDocument.tmp_poles.Placement.Base
				self.multiface.movePoint(vt,FreeCAD.Vector(0,0,2000),True)
			print "SELECTIONS"
			for s in self.multiface.selection:
				print s
			App.activeDocument().recompute()
			App.ActiveDocument.getObject(self.multiface.nameE).ViewObject.show()


		def Xapply(self):
			print "SELECTIONS pre"	
			for s in self.multiface.selection:
				print s
			selps=[FreeCAD.Vector(p[3]) for p in self.multiface.selection]
#			for (s,u,v,p) in self.multiface.selection:
#				pp=self.multiface.comp[s].Surface.getPoles()
#				print pp[u][v]
#				print p
			
			self.multiface.selection=[]
			for vt in selps:
		#		vt -= App.ActiveDocument.tmp_poles.Placement.Base
				self.multiface.movePoint(vt,FreeCAD.Vector(0,0,1500),False,params=self)

			print "SELECTIONS post"	
			for s in self.multiface.selection:
				print s

			App.ActiveDocument.getObject(self.multiface.nameE).ViewObject.hide()
			App.activeDocument().recompute()


		def merge(self):
			print "SELECTIONS"

			for s in self.multiface.selection:
				print s

			comp=[c for c in self.multiface.comp]
			compe=self.multiface.compe
			pts=[]

			for i in range(len(self.multiface.selection)/2):
				sa=self.multiface.selection[2*i]
				sb=self.multiface.selection[2*i+1]


				sia,uia,via,p=sa
				polesa=np.array(comp[sia].Surface.getPoles())
				print polesa[uia,via]
				ma=polesa[uia,via]

				sib,uib,vib,p=sb
				polesb=np.array(comp[sib].Surface.getPoles())
				print polesb[uib,vib]
				mb=polesb[uib,vib]

				#merge point
				mm=(ma+mb)*0.5

				sf=comp[sia].Surface
				pps=[]
				umia=max(uia-1,0)
				umaa=min(sf.NbUPoles-1,uia+1)
				vmia=max(via-1,0)
				vmaa=min(sf.NbVPoles-1,via+1)

				mova= mm-ma
				print "move a",mova

				sf=comp[sib].Surface
				pps=[]
				umib=max(uib-1,0)
				umab=min(sf.NbUPoles-1,uib+1)
				vmib=max(vib-1,0)
				vmab=min(sf.NbVPoles-1,vib+1)

				movb= mm-mb
				print "move b",movb

				print ("Bereich a",umia,umaa,vmia,vmaa)
				pps=[]
				pps += [(uk,vk) for uk in range(umia,umaa+1) for vk in range(vmia,vmaa+1)]
				for (u,v) in pps:
#							rot=FreeCAD.Rotation(arc,0,0)
#							vv=FreeCAD.Vector(poles[u,v]-base)
#							vv=rot.multVec(vv)
					polesa[u,v] +=  mova 
					print (u,v)
				print "result a",polesa[uia,via]

				sf=comp[sib].Surface
				bs=Part.BSplineSurface()
				bs.buildFromPolesMultsKnots(polesa,
								sf.getUMultiplicities(),sf.getVMultiplicities(),
								sf.getUKnots(),sf.getVKnots(),
								False,False,sf.UDegree,sf.VDegree)

				comp[sia] = bs.toShape()

				if sib != sia:
					ptsa=[FreeCAD.Vector(polesa[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]

					ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
					pts += [FreeCAD.Vector(p) for p in ptsa]

				print "Xresult a",polesa[uia,via]
				if sib==sia:
					polesb=polesa
				else:
					polesb=np.array(comp[sib].Surface.getPoles())
				print "result ab",polesb[uia,via]

				print ("Bereich b" ,umib,umab,vmib,vmab)
				pps=[]
				pps += [(uk,vk) for uk in range(umib,umab+1) for vk in range(vmib,vmab+1)]
				print "ha----------"
				for (u,v) in pps:
#							rot=FreeCAD.Rotation(arc,0,0)
#							vv=FreeCAD.Vector(poles[u,v]-base)
#							vv=rot.multVec(vv)
					polesb[u,v] +=  movb 
					print (u,v)
					print "result abb",polesb[uia,via]
				print "hu-------------------"

				print "result _b",polesb[uib,vib]
				print (uib,vib)
				print "result aa",polesa[uia,via]
				print "result a(b)",polesb[uia,via]
				print (uia,via)
				print 
				
				if sib == sia:
					print ("!aaaa!!",sia,sib,uia,uib,via,vib)
					if uia == uib:
						print ("!ccc!!",sia,sib,uia,uib,via,vib)
						mm=polesb[uia,via]
						if via>vib: via,vib=vib,via
						for v in range(via,vib+1):
								print "XX"
								polesb[uia,v]=mm 
								polesb[uia-1,v]=polesb[uia-1,via]
								polesb[uia+1,v]=polesb[uia+1,via]
					if via == vib:
						print ("!ddd!!",sia,sib,uia,uib,via,vib)
						mm=polesb[uia,via]
						if uia>uib: uia,uib=uib,uia
						for u in range(uia,uib+1):
								print "YYY"
								polesb[u,via]=mm 
								polesb[u,via-1]=polesb[uia,via-1]
								polesb[u,via+1]=polesb[uia,via+1]
				else:
					print ("!!!",sia,sib,uia,uib,via,vib)

	
				bs=Part.BSplineSurface()
				bs.buildFromPolesMultsKnots(polesb,
								sf.getUMultiplicities(),sf.getVMultiplicities(),
								sf.getUKnots(),sf.getVKnots(),
								False,False,sf.UDegree,sf.VDegree)



				comp[sib] = bs.toShape()

				compe += editcross(polesa,uia,via)
				compe += editcross(polesb,uib,vib)

				ptsa=[FreeCAD.Vector(polesb[3*uii,3*vii]) for uii in range(sf.NbUPoles/3+1) for vii in  range(sf.NbVPoles/3+1) ]

				ptsa = np.array(ptsa).reshape((sf.NbUPoles/3+1)*(sf.NbVPoles/3+1),3)
				pts += [FreeCAD.Vector(p) for p in ptsa]





			obj=App.ActiveDocument.getObject(self.multiface.nameF)
			obj.Shape=Part.Compound(comp)

			obj3=App.ActiveDocument.getObject(self.multiface.nameE)
			obj3.Shape=Part.Compound(compe)

			self.multiface.comp=comp
			self.multiface.compe=compe

			obj2=App.ActiveDocument.getObject(self.multiface.nameP)
			pm=obj2.Placement
			comp2=[Part.Vertex(FreeCAD.Vector(p)) for p in pts]
			obj2.Shape=Part.Compound(comp2)
			obj2.Placement=pm



#			Part.show(Part.Compound(comp))











	mikigui = createMikiGui2(layout, EditorApp)
	print mikigui
#	mikigui.obj=fp
#	mikigui.NameObj=obj.Name
	mikigui.initData()




def multiEdit():
	SurfaceEditor()
