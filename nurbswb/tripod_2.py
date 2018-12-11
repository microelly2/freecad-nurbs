# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- tripod for uv coords
#--
#-- microelly 2019 v 0.2
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


class Tripod(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		self.Type="Tripod"
		self.TypeId="Tripod"
		obj.addProperty("App::PropertyLink","source","Source","Bezugskoerper")
		obj.addProperty("App::PropertyInteger","faceNumber","Source","Nummer der Flaeche").faceNumber=0
		obj.addProperty("App::PropertyEnumeration","mode","Format","Darstellung als Dreibein oder Kruemmungskreise").mode=["UV-Tripod","Curvature","Sketch"]
		obj.addProperty("App::PropertyFloat","u","UV","u position un uv space").u=50
		obj.addProperty("App::PropertyFloat","v","UV","v position in uv space").v=50
		
		obj.addProperty("App::PropertyFloat","scale","Format","Size of the tripod legs").scale=100
		obj.addProperty("App::PropertyFloat","maxRadius","Format","maximum curvature circle").maxRadius=1000
		obj.addProperty("App::PropertyBool","directionNormal","Format","Auf dem Fuss oder auf dem Kopf stehen").directionNormal=True
		obj.ViewObject.LineColor=(1.0,0.0,1.0)
		obj.addProperty("App::PropertyBool","wireMode")
		obj.addProperty("App::PropertyBool","binormalMode")

	def onChanged(self, fp, prop):
		''' recompute the shape, compute and print the curvature '''
		if prop=="Shape": return
		if prop=="Placement": return
		#print "on change ",prop

		try: fp.u, fp.v, fp.directionNormal,fp.Shape,fp.source,fp.faceNumber
		except: return
		if fp.source==None: return
		
#		print "change",prop

		u=fp.u/12*3.14
		v=fp.v/12*3.14

		if fp.u<0:fp.u=0
		if fp.v<0:fp.v=0

		u=0.01*fp.u
		v=0.01*fp.v

#		u=fp.u/12*3.14/100
#		v=fp.v/12*3.14/100

		if fp.mode=="Curvature2":
			self.runmode2(fp,prop)
			return

		wiremode = len(fp.source.Shape.Faces)==0
		wiremode=False
		
		if fp.wireMode:
			wiremode=True

		if wiremode:
			w=fp.source.Shape.Edges[fp.faceNumber-1]
			nn=w.toNurbs().Edges[0]

			(mi,ma)=nn.ParameterRange
			u=mi+(ma-mi)*fp.u*0.01
			vf=nn.valueAt(u)
			t1=nn.tangentAt(u)
			try:
				t2=nn.normalAt(u)
			except:
				print "Problem ERstellung Normale"
				t2=FreeCAD.Vector(t1.y,t1.z,t1.x)
				t2=t1.cross(t2)
			if fp.binormalMode:
				t2=t1.cross(t2)

		else:
			f=fp.source.Shape.Faces[fp.faceNumber-1]
			nf=f.toNurbs()

			sf=nf.Face1.Surface
#			print "Range",nf.Face1.ParameterRange
			[umi,uma,vmi,vma]=nf.Face1.ParameterRange

			#sf=fp.source.Shape.Faces[fp.faceNumber-1].Surface
			u=umi+u*(uma-umi)
			v=vmi+v*(vma-vmi)

			# point
			vf=sf.value(u,v)
#			print ("u,v,vf",u,v,vf)

			# tangents
			t1,t2=sf.tangent(u,v)
			#-------------------------


		#------------------------
			t1=t1.normalize()
			t2=t2.normalize()
		if fp.directionNormal: 
			n=t1.cross(t2).normalize()
		else: 
			n=t2.cross(t1).normalize()

		n=n.normalize()

		r=FreeCAD.Rotation(t1,t2,n)
#		print "Rotation A",r.toEuler()

		if wiremode:
#			print "Wiremode"
			r=FreeCAD.Rotation(n,t1,t2)
			r=FreeCAD.Rotation(t2,n,t1)
			#hack binormal
			r=FreeCAD.Rotation(n,t1,t2)
		else:
			r=FreeCAD.Rotation(t1,t2,n)
		
		#print "Rotation",r.toEuler()
		pm=FreeCAD.Placement(vf,r)
		#pm=FreeCAD.Placement()
		#pm.Rotation=r
		if fp.mode=='Sketch':
			if len(fp.Geometry)==0:
				dist=fp.source.Shape.BoundBox.DiagonalLength*0.05
				fp.addGeometry(Part.Circle(App.Vector(0,0,0),App.Vector(0,0,1),dist),False)
				fp.addGeometry(Part.LineSegment(App.Vector(0,0,0),App.Vector(dist*3.,0,0)),False)
				fp.addGeometry(Part.LineSegment(App.Vector(0.,0,0),App.Vector(0,dist*2,0)),False)
				fp.addGeometry(Part.LineSegment(App.Vector(0,0,0),App.Vector(-dist*3.,0,0)),False)
				fp.addGeometry(Part.LineSegment(App.Vector(0.,0,0),App.Vector(0,-dist*2,0)),False)
				fp.recompute()
			fp.Placement=pm
			return



		t1 *= fp.scale
		t2 *= fp.scale

		l1=t1.add(vf)
		#li1=Part.Line(vf,l1)
#		print vf
		
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
		
		#-------------------
		# the placement
		#vf=sf.value(u,v)
#		print vf
		#[t1,t2]=sf.tangent(u,v)
#		print t1,t2
		#n=t2.cross(t1).normalize()

		#---------------------
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

def createTripodSketch(): #sketcher
	'''creae a tripod sketch'''

	ss=Gui.Selection.getSelectionEx()
	if len(ss) != 0:
		for s in ss:
			s.Object
			subs=s.SubElementNames
			for sub in subs:

				if sub.startswith('Edge'):
					nr=sub[4:]
					print( s.Object.Name, sub, int(nr))
					a=FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython","TripodSketch")
					#Tripod(a,mode='Sketch')
					Tripod(a)
					a.mode="Sketch"
					a.ViewObject.LineWidth = 1
					a.faceNumber=int(nr)
					a.wireMode=True
					a.source=s.Object
					ViewProvider(a.ViewObject)

				if sub.startswith('Face'):
					nr=sub[4:]
					print( s.Object.Name, sub, int(nr))
					a=FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython","TripodSketch")
					#Tripod(a,mode='Sketch')
					Tripod(a)
					a.mode="Sketch"
					a.ViewObject.LineWidth = 1
					a.faceNumber=int(nr)
					# a.wireMode=True
					a.source=s.Object
					ViewProvider(a.ViewObject)



	else:
		#a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Tripod")
		a=FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython","TripodSketch")
		#Tripod(a,mode='Sketch')
		Tripod(a)
		a.mode="Sketch"
		a.ViewObject.LineWidth = 2
		a.source=Gui.Selection.getSelection()[0]
		ViewProvider(a.ViewObject)



def createSweep():
	sw=FreeCAD.ActiveDocument.addObject('Part::Sweep','Sweep')
	sw.Spine=(Gui.Selection.getSelection()[-1],["Edge1"])
	sw.Sections=Gui.Selection.getSelection()[0:-1]
	App.activeDocument().recompute()


def createLoft():
	sw=FreeCAD.ActiveDocument.addObject('Part::Loft','Loft')
	sw.Sections=Gui.Selection.getSelection()
	App.activeDocument().recompute()

def createCompound():
	sw=FreeCAD.ActiveDocument.addObject("Part::Compound","Compound001")
	sw.Links=Gui.Selection.getSelection()
	App.activeDocument().recompute()

# createSweep()



'''
# Analyse Raender eines lochs
pts=[]
for s in Gui.Selection.getSelectionEx():

	for so in s.SubObjects:
		nn=so.toNurbs()
		print nn.Edge1.ParameterRange
		[ui,ua]=nn.Edge1.ParameterRange
		c=nn.Edge1.Curve
		c.segment(ui,ua)
		Part.show(c.toShape())
		App.ActiveDocument.ActiveObject.Shape.Vertexes[1].Tolerance = 1e-5
		App.ActiveDocument.ActiveObject.Shape.Vertexes[0].Tolerance = 1e-5

		for v in nn.Vertexes:
			print v.Point
			pts +=[v.Point]
		print

'''


'''

fs=App.ActiveDocument.Thickness.Shape.Faces
print len(fs)
fs += App.ActiveDocument.Surface001.Shape.Faces
print len(fs)
Part.show(Part.makeShell(fs))

'''
