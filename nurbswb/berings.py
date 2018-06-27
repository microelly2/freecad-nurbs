'''
create curves and faces like Bezier format 
'''

import numpy as np
import Draft,Points,Part
from say import *
import random


class FeaturePython:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

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


def copySketch(sketch,target):
	'''kopiert sketch in sketchobjectpython'''
	sb=sketch
	gs=sb.Geometry
	cs=sb.Constraints

	sk=target
	sk.deleteAllGeometry()

	for g in gs:
		rc=sk.addGeometry(g)
		sk.setConstruction(rc,g.Construction)

	for c in cs:
		rc=sk.addConstraint(c)

	sk.solve()
	sk.recompute()
	App.activeDocument().recompute()


class Bering(FeaturePython):
	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyInteger","level")
		obj.addProperty("App::PropertyLink","source")
		obj.addProperty("App::PropertyInteger","start")
		obj.addProperty("App::PropertyInteger","end")
		obj.addProperty("App::PropertyFloat","scale").scale=1.0
		obj.addProperty("App::PropertyBool","detach").detach


	def onChanged(self, fp, prop):
		#if not hasattr(fp,'onchange') or not fp.onchange : return
#		print "bering ########################## changed ",prop
		if prop == "detach" and  fp.detach:
			print " copy from sketch"
			copySketch(fp.source,fp)


	def execute(self,fp):

		if fp.detach:
			ptsa=[fp.getPoint(g,1) for g  in range(len(fp.Geometry))]
			ptsa +=[fp.getPoint(len(fp.Geometry)-1,2)]
		else:
			try:
				ptsa=fp.source.Shape.Curve.getPoles()
			except:
				ptsa=[v.Point*fp.scale for v in fp.source.Shape.Vertexes]

		# testen ob geschlossenes oder offnes modell
		print ("Lanege test",len(ptsa),len(ptsa)%3)
		if len(ptsa)%3==0:

			pts=ptsa[1:]+[ptsa[0],ptsa[1]]

		else:
			pts=ptsa


		if fp.start==0 and fp.end==0:
			ecken=(len(pts))/3-1

		if fp.end>0:
			ecken=fp.end-fp.start-1
			pts=pts[fp.start*3:fp.start*3+ecken*3+4]
			print(fp.start*3,ecken*3+4)

		ms=[4]+[3]*ecken+[4]

		print ("start,end",fp.start,fp.end)
		print ("ms",ms,"Ecken",ecken,"len pts", len(pts))

		bc=Part.BSplineCurve()
		bc.buildFromPolesMultsKnots(pts, 
			ms,
			range(len(ms)),
			False,3)

		fp.Shape=bc.toShape()



class Beface(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLinkList","berings")
		obj.addProperty("App::PropertyInteger","start")
		obj.addProperty("App::PropertyInteger","end")
		obj.addProperty("App::PropertyBool","showStripes")
		obj.addProperty("App::PropertyBool","generatedBackbone")
		


	def execute(self,fp):

#		assert (len(fp.berings)-1)%3==0
		
		ptsa=[]
		ll=-1
		for r in fp.berings:
			pps=r.Shape.Edge1.Curve.getPoles()
			if ll==-1:ll=len(pps)
			assert ll == len(pps)
			ptsa += [pps]

		print "##"
		print len(ptsa)
		print len(ptsa[0])
		poles=np.array(ptsa)
#		print ptsa
#		print poles
		print poles.shape

		af=Part.BSplineSurface()
		(a,b,c)=poles.shape

		if not fp.generatedBackbone:
			ecken=(a-1)/3

			if fp.end>0:
				ecken=fp.end-fp.start
				poles=poles[3*fp.start:3*fp.end+1]

			ya=[4]+[3]*(ecken-1)+[4]

			(a,b,c)=poles.shape
			print ("poles.shape a,b",a,b)

			# die bezier variante
			yb=fp.berings[0].Shape.Edge1.Curve.getMultiplicities()

			db=min(3,a-1)
			if db==3:
				ya=[4]+[3]*(ecken-1)+[4]
			if db==2:
				ya=[3,3]
			if db==1:
				ya=[2,2]

			print ("a---",a,db,ya)
			print ("b---",b,db,yb)

		else:
			ya=[4]+[1]*(a-4)+[4]
			yb=fp.berings[0].Shape.Edge1.Curve.getMultiplicities()
			db=3

		af.buildFromPolesMultsKnots(poles, 
				ya,yb,
				range(len(ya)),range(len(yb)),
				False,False,db,3)


		for i in range(1,len(ya)-1):
			print (i,ya[i])
			if ya[i]<3:
				af.insertUKnot(i,3,0)





		fp.Shape=af.toShape()

		if fp.showStripes:

			wist=20 # width of the tangent stripes

			# create some extra objects for debugging

			#for j in [2,5]:
			for jj in range((a-1)/3-1):
				j=jj*3+2
				pp=poles[j:j+3]
				#normalize and scale the tangents
				ppy=[]
				for (pa,pb,pc) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					pc=FreeCAD.Vector(pc)
					ppy += [[pb+(pa-pb).normalize()*wist,pb,pb+(pc-pb).normalize()*wist]]

				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,1,2],yb,
						[0,1,2],range(len(yb)),
						False,False,1,3)

				name="rib_tangstrip_"+str(j)

				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)
				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(1.0,0.0,0.0)


			for j in [0]:
				pp=poles[j:j+2]
				ppy=[]

				for (pa,pb) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					ppy += [[pa,pa+(pb-pa).normalize()*2*wist]]

				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,2],yb,
						[0,1],range(len(yb)),
						False,False,1,3)

				name="rib_tangstrip_"+str(j)

				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)

				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(1.0,0.0,0.0)

			for j in [a-2]:
				pp=poles[j:j+2]
				ppy=[]

				for (pa,pb) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					ppy += [[pb+(pa-pb).normalize()*2*wist,pb]]

				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,2],yb,
						[0,1],range(len(yb)),
						False,False,1,3)

				name="rib_tangstrip_"+str(j)

				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)
				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(1.0,0.0,0.0)

			#create the meridians
			poles2=poles.swapaxes(0,1)

			for jj in range((b-1)/3-1):
				j=jj*3+2

	#		for j in [2,5,8]:
				pp=poles2[j:j+3]
				ppy=[]
				for (pa,pb,pc) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					pc=FreeCAD.Vector(pc)
					ppy += [[pb+(pa-pb).normalize()*wist,pb,pb+(pc-pb).normalize()*wist]]
				
				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,1,2],ya,
						[0,1,2],range(len(ya)),
						False,False,1,3)
				name="meridian_tangstrip_"+str(j)
				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)
				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(.0,0.0,1.0)


			for j in [b-2]:
				pp=poles2[j:j+2]

				ppy=[]
				for (pa,pb) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					ppy += [[pb+(pa-pb).normalize()*2*wist,pb]]
				
				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,2],ya,
						[0,1],range(len(ya)),
						False,False,1,3)
				name="meridian_tangstrip_"+str(j)
				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)
				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(.0,0.0,1.0)

			for j in [0]:
				pp=poles2[j:j+2]

				ppy=[]
				for (pa,pb) in pp.swapaxes(0,1):
					pa=FreeCAD.Vector(pa)
					pb=FreeCAD.Vector(pb)
					ppy += [[pa,pa+(pb-pa).normalize()*2*wist]]
				
				pp=np.array(ppy).swapaxes(0,1)

				ag=Part.BSplineSurface()
				ag.buildFromPolesMultsKnots(pp, 
						[2,2],ya,
						[0,1],range(len(ya)),
						False,False,1,3)
				name="meridian_tangstrip_"+str(j)
				tt=App.ActiveDocument.getObject(name)
				if tt==None:
					tt=App.ActiveDocument.addObject('Part::Spline',name)
				tt.Shape=ag.toShape()
				tt.ViewObject.ControlPoints = True
				tt.ViewObject.ShapeColor=(.0,0.0,1.0)

def genk(start,ende,scale,pos,source):
	# kurven erzeugen
	sk=App.ActiveDocument.addObject('Sketcher::SketchObjectPython','BeringSketch')
	Bering(sk)
	ViewProvider(sk.ViewObject)
	sk.source=source
	sk.start=start
	sk.end=ende
	sk.scale=scale
	sk.Placement.Base=pos
	App.activeDocument().recompute()
	return sk


def genA():

	source=App.ActiveDocument.Sketch002;end=2;start=0
	source=App.ActiveDocument.Sketch003;end=5;start=0

	sks=[]

	sks += [genk(start,end,1,FreeCAD.Vector(),source)]
	sks += [genk(start,end,1.9,FreeCAD.Vector(200,0,0),source)]
	sks += [genk(start,end,0.9,FreeCAD.Vector(400,0,100),source)]


	sf=App.ActiveDocument.addObject('Sketcher::SketchObjectPython','BeringFace')
	Beface(sf)
	sf.berings=sks
	ViewProvider(sf.ViewObject)

	App.activeDocument().recompute()



	# varianten zum testen
def genB():

		#source=App.ActiveDocument.Sketch;end=5:start=1
	source=App.ActiveDocument.Sketch001;end=0;start=0

	sks=[]

	sks += [genk(start,end,1,FreeCAD.Vector(),source)]
	sks += [genk(start,end,0.9,FreeCAD.Vector(0,0,80),source)]

	sks += [genk(start,end,0.5,FreeCAD.Vector(0,0,200),source)]
	sks += [genk(start,end,0.5,FreeCAD.Vector(0,0,240),source)]
	sks += [genk(start,end,0.5,FreeCAD.Vector(0,0,280),source)]

	sks += [genk(start,end,0.6,FreeCAD.Vector(0,0,600),source)]
	sks += [genk(start,end,0.6,FreeCAD.Vector(0,0,650),source)]
	sks += [genk(start,end,0.6,FreeCAD.Vector(0,0,690),source)]

	sks += [genk(start,end,0.64,FreeCAD.Vector(0,0,800),source)]
	sks += [genk(start,end,0.64,FreeCAD.Vector(0,0,850),source)]
	sks += [genk(start,end,0.64,FreeCAD.Vector(0,0,890),source)]

	sks += [genk(start,end,1.1,FreeCAD.Vector(0,0,1340),source)]
	sks += [genk(start,end,1.0,FreeCAD.Vector(0,0,1440),source)]

	sf=App.ActiveDocument.addObject('Sketcher::SketchObjectPython','BeringFace')
	Beface(sf)
	sf.berings=sks
	ViewProvider(sf.ViewObject)

	App.activeDocument().recompute()

def createBering():
		for source in Gui.Selection.getSelection():
			genk(0,0,1,FreeCAD.Vector(),source)


def AA():
	obj=App.ActiveDocument.jj2
	sf=obj.Shape.Face1.Surface
	poles=np.array(sf.getPoles())
	print poles.shape
	u=2
	v=2
	sub=poles[u:u+9,v:v+6]
	t1=1
	t2=1


	sub[:]=(t1*sub[1]+t2*sub[4])/(t1+t2)

	poles[u:u+9,v:v+6]=sub
	af=Part.BSplineSurface()
	af.buildFromPolesMultsKnots(poles, 
				sf.getUMultiplicities(),sf.getVMultiplicities(),
				sf.getUKnots(),sf.getVKnots(),
				False,False,sf.UDegree,sf.VDegree)

	#sk=App.ActiveDocument.getObject(res.Name+"_"+label)
	sk=None
	if sk==None:
		sk=App.ActiveDocument.addObject('Part::Spline',"UUU")
		sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)

	sk.Shape=af.toShape()

def createBeface():

	sks=Gui.Selection.getSelection()
	sf=App.ActiveDocument.addObject('Sketcher::SketchObjectPython','BeringFace')
	Beface(sf)
	sf.berings=sks
	ViewProvider(sf.ViewObject)


def createBeringTest():

	try:
		App.closeDocument("bering_testdaten")
	except:
		pass

	appdat=FreeCAD.ConfigGet('UserAppData')
	fn=appdat+'/FreeCAD_testfiles/bering_testdaten.fcstd'

	FreeCAD.open(fn)
	App.setActiveDocument("bering_testdaten")
	App.ActiveDocument=App.getDocument("bering_testdaten")
	Gui.ActiveDocument=Gui.getDocument("bering_testdaten")

	genA()
	#genB()

	source=App.ActiveDocument.Sketch004;end=5;start=0

	sks=[]

	sks += [genk(start,end,1,FreeCAD.Vector(),source)]
	sks += [genk(start,end,1.9,FreeCAD.Vector(200,0,0),source)]
	sks += [genk(start,end,0.9,FreeCAD.Vector(400,0,100),source)]


	sf=App.ActiveDocument.addObject('Sketcher::SketchObjectPython','BeringFace')
	Beface(sf)
	sf.berings=sks
	ViewProvider(sf.ViewObject)

	App.activeDocument().recompute()
	connectFaces()
	App.activeDocument().recompute()





def connectFacesAA():
	import numpy as np
	# connect
	sfa=App.ActiveDocument.BeringFace.Shape.Face1.Surface
	pa0=sfa.getPoles()

	sfb=App.ActiveDocument.BeringFace001.Shape.Face1.Surface
	pb0=sfb.getPoles()
	
	_connectFaces(App.ActiveDocument.BeringFace,App.ActiveDocument.BeringFace001)


class Corner(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","sourceA")
		obj.addProperty("App::PropertyLink","sourceB")
		obj.addProperty("App::PropertyLink","sourceC")
		obj.addProperty("App::PropertyInteger","modeA","Base")
		obj.addProperty("App::PropertyInteger","modeB","Base")
		obj.addProperty("App::PropertyInteger","modeC","Base")
		ViewProvider(obj.ViewObject)

	def execute(proxy,obj):
		comps=_moveCorner(obj)
		# comps=[obj.sourceA.Shape,obj.sourceB.Shape,obj.sourceC.Shape,]
		obj.Shape=Part.Compound(comps)
		

	def onChanged(self, obj, prop):
		print ("onChanged",prop)
		if prop=="Shape":return
		try:
			comps=[obj.sourceA.Shape,obj.sourceB.Shape,obj.sourceC.Shape,]
		except:
			comps=[]
		if prop in ['modeA','modeB','modeC']:
#			pts= [
#					obj.sourceA.Points[obj.modeA],
#					obj.sourceB.Points[obj.modeB],
#					obj.sourceC.Points[obj.modeC],
#					obj.sourceA.Points[obj.modeA],
#				]
#			ww=Part.makePolygon(pts)
			ss=Part.Sphere()
			ss.Radius=100
			sa=ss.toShape()
			
			sa.Placement.Base=_moveCorner(obj,True)
			comps += [sa]
			obj.Shape=Part.Compound(comps)






def _fixCorner(a,b,c):

	res=App.ActiveDocument.addObject("Part::FeaturePython","Corner")
	res.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	res.ViewObject.Visibility=False
	Corner(res)

	res.sourceA=a
	res.sourceB=b
	res.sourceC=c



	return

def _moveCorner(res,onlypos=False):

	a=res.sourceA
	b=res.sourceB
	c=res.sourceC
	
	modtab=[[0,0],[0,-1],[-1,0],[-1,-1]]
	[ua,va] = modtab[res.modeA%4]
	[ub,vb] = modtab[res.modeB%4]
	[uc,vc] = modtab[res.modeC%4]

	sfa=a.Shape.Face1.Surface
	pa0=np.array(sfa.getPoles())

	sfb=b.Shape.Face1.Surface
	pb0=np.array(sfb.getPoles())

	sfc=c.Shape.Face1.Surface
	pc0=np.array(sfc.getPoles())


	corner=(pa0[ua,va]+pb0[ub,vb]+pc0[uc,vc])/3.
	if onlypos:
		return corner

	cfg=[['A',sfa,ua,va],['B',sfb,ub,vb],['C',sfc,uc,vc]]
	fs=[]
	
	for (label,sf,u,v) in cfg:
		af=Part.BSplineSurface()
		poles=np.array(sf.getPoles())
		poles[u,v]=corner

		af.buildFromPolesMultsKnots(poles, 
				sf.getUMultiplicities(),sf.getVMultiplicities(),
				sf.getUKnots(),sf.getVKnots(),
				False,False,sf.UDegree,sf.VDegree)

		sk=App.ActiveDocument.getObject(res.Name+"_"+label)
		if sk==None:
			sk=App.ActiveDocument.addObject('Part::Spline',res.Name+"_"+label)
			sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)

		sk.Shape=af.toShape()
		fs += [sk.Shape]

	return fs



class Product(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","uSource")
		obj.addProperty("App::PropertyLink","vSource")
		obj.addProperty("App::PropertyLink","uSource2")
		obj.addProperty("App::PropertyLink","vSource2")

		obj.addProperty("App::PropertyVector","Offset")
		obj.addProperty("App::PropertyVector","uOffset")
		obj.addProperty("App::PropertyVector","vOffset")
#		obj.addProperty("App::PropertyVector","vOffset")
#		obj.addProperty("App::PropertyInteger","start")
#		obj.addProperty("App::PropertyInteger","end")
		obj.addProperty("App::PropertyBool","borderMode")
		obj.addProperty("App::PropertyBool","onlyu")
		obj.addProperty("App::PropertyBool","onlyv")
		

	def execute(self,fp):
		self.createP(fp)

	def createP(self,fp):

		sourceA=fp.uSource
		sourceB=fp.vSource

		ptsa=[p.Point for p in sourceA.Shape.Vertexes]
		sa=len(ptsa)
		ptsa=np.array(ptsa).reshape(sa,1,3)

		ptsb=[p.Point for p in sourceB.Shape.Vertexes]
		sb=len(ptsb)
		
		ptsb=np.array(ptsb)
		
		print ptsb[0]
		print ptsa[0]

		if 1: # startpunkte zusammenlagen auf anfang von a
			ptsb += -ptsb[0] # + ptsa[0]

		print ptsb[0]
		endeb=ptsb[-1]
		startb=ptsb[0]

		ptsb=ptsb.reshape(1,sb,3)


		if fp.uSource2<>None:
#			ptsbj=[p.Point for p in sourceB.Shape.Vertexes]
			ptsa=np.array([p.Point for p in sourceA.Shape.Vertexes])


			ptsa2=np.array([p.Point+ fp.uOffset  for p in fp.uSource2.Shape.Vertexes])

			if 1: # startpunkte zusammenlagen auf anfang von a
				ptsa2 -= ptsa2[0] -ptsa[0]
				ptsa2  += -startb
			
			print "!! ",endeb-startb


			ll=1.0*sb-1
			ptsaa=[ptsa*(ll-i)/ll+ptsa2*i/ll for i in range(sb)]

			print "shape ptsa ",ptsa.shape

			ptsa=np.array(ptsaa)
			print "shape ptsaa ",ptsa.shape


##		ptsa[:,0] += fp.Offset

			ptsa=ptsa.swapaxes(0,1)

			if fp.borderMode:
				ptsa *= 0.5
				#ptsb[:,:,0:1] *= 0.5


		if fp.vSource2<>None:
			ptsb=[p.Point  for p in sourceB.Shape.Vertexes]
			sb=len(ptsb)
			ptsb=np.array(ptsb)
			
			ptsb2=[p.Point + fp.vOffset for p in fp.vSource2.Shape.Vertexes]
			ptsb2=np.array(ptsb2)

			print ("sa sb",sa,sb)
			ll=1.0*sa-1

			ptsbb=[ptsb*(ll-i)/ll+ptsb2*i/ll for i in range(sa)]

			ptsb=np.array(ptsbb)
			print "shape ptsbxx",ptsb.shape

			if fp.borderMode:
				ptsb *= 0.5
				#ptsb[:,:,0:1] *= 0.5



		#poles=ptsa+ptsb
		print "shape X ptsa",ptsa.shape
		print "shape X ptsb",ptsb.shape
		
		poles=ptsa+ptsb
		if fp.onlyu:
			poles=ptsa
		if fp.onlyv:
			poles=ptsb

		

		(a,b,c)=poles.shape
		print ("poles.shape a,b",a,b)

		aecken=(a-1)/3
		ya=[4]+[3]*(aecken-1)+[4]
		becken=(b-1)/3
		yb=[4]+[3]*(becken-1)+[4]

		db=min(3,a-1)
		if db==3:
			ya=[4]+[3]*(aecken-1)+[4]
		if db==2:
			ya=[3,3]
		if db==1:
			ya=[2,2]

		print ("a---",a,db,ya)
		af=Part.BSplineSurface()
		af.buildFromPolesMultsKnots(poles, 
				ya,yb,
				range(len(ya)),range(len(yb)),
				False,False,db,3)

		fp.Shape=af.toShape()
		#Part.show(af.toShape())





def createProduct():
	if 0:
		try:
			App.closeDocument("bering_testdaten")
		except:
			pass

		appdat=FreeCAD.ConfigGet('UserAppData')
		fn=appdat+'/FreeCAD_testfiles/bering_testdaten.fcstd'

		FreeCAD.open(fn)
		App.setActiveDocument("bering_testdaten")
		App.ActiveDocument=App.getDocument("bering_testdaten")
		Gui.ActiveDocument=Gui.getDocument("bering_testdaten")


	sf=App.ActiveDocument.addObject('Part::FeaturePython','ProductFace')
	Product(sf)
	ViewProvider(sf.ViewObject)
	sel=Gui.Selection.getSelection()
	sf.uSource=sel[0]
	sf.vSource=sel[1]
	if len(sel)==3:	
		sf.uSource2=sel[2]


'''
	# alte Testfaelle
	sourceA=App.ActiveDocument.Sketch005
	sourceB=App.ActiveDocument.Sketch006
	_createP(sourceA,sourceB)
	r=App.ActiveDocument.ActiveObject

	sourceA=App.ActiveDocument.Sketch006
	sourceB=App.ActiveDocument.Sketch007
	_createP(sourceA,sourceB)
	r2=App.ActiveDocument.ActiveObject

	sourceA=App.ActiveDocument.Sketch007
	sourceB=App.ActiveDocument.Sketch005
	_createP(sourceA,sourceB)
	r3=App.ActiveDocument.ActiveObject
'''


def debugP(pts,label):


	print "debugP deaktiviert";return

	pts=[FreeCAD.Vector(p) for p in pts]
	obj=App.ActiveDocument.getObject(label)
	if obj == None:
		obj=App.ActiveDocument.addObject('Part::Feature',label)

	obj.Shape=Part.makePolygon([FreeCAD.Vector()]+pts)



class FaceConnection(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","aSource")
		obj.addProperty("App::PropertyLink","bSource")
		
#		obj.addProperty("App::PropertyVector","Offset")
#		obj.addProperty("App::PropertyVector","vOffset")
#		obj.addProperty("App::PropertyInteger","start")
#		obj.addProperty("App::PropertyInteger","end")
		obj.addProperty("App::PropertyBool","swapA")
		obj.addProperty("App::PropertyBool","swapB")
		obj.addProperty("App::PropertyBool","reverseA")
		obj.addProperty("App::PropertyBool","reverseB")
		obj.addProperty("App::PropertyBool","close")
		obj.addProperty("App::PropertyBool","mergeEdge")
		obj.addProperty("App::PropertyBool","displayConnect")
		obj.addProperty("App::PropertyEnumeration","mode").mode=['Connect','Seam']
		obj.addProperty("App::PropertyFloat","tangfacA").tangfacA=1
		obj.addProperty("App::PropertyFloat","tangfacB").tangfacB=1

	def execute(self,fp):
		if fp.mode=='Seam':
			self.createSeam(fp)
		else:
			self.connect(fp)

	def createSeam(self,fp):
		print "in create seam ..."

		try:
			a=fp.aSource
			b=fp.bSource
		except:
			return
		sfa=a.Shape.Face1.Surface
		pa0=sfa.getPoles()

		sfb=b.Shape.Face1.Surface
		pb0=sfb.getPoles()

		print "shapes ..."
		print np.array(pa0).shape
		print np.array(pb0).shape

		if 1:

			if fp.swapA:
				pa=np.array(pa0).swapaxes(0,1)
			else:
				pa=np.array(pa0)
			if fp.swapB:
				pb=np.array(pb0).swapaxes(0,1)
			else:
				pb=np.array(pb0)

			if fp.reverseA:
				pa=pa[::-1]
			if fp.reverseB:
				pb=pb[::-1]

			debugP(pa[0],"pa_0")
			debugP(pb[1],"pb_1_x")
			debugP(pa[1],"pa_1_x")

			poles=np.array([pa[0],pa[0]+fp.tangfacA*(pa[0]-pa[1]),pb[0]+fp.tangfacB*(pb[0]-pb[1]),pb[0]]).swapaxes(0,1)

			af=Part.BSplineSurface()
			af.buildFromPolesMultsKnots(poles, 
				sfa.getUMultiplicities(),[4,4],
				sfa.getUKnots(),[0,1],
				False,False,sfa.UDegree,3)
			fp.Shape=af.toShape()

			if 0:
				sk=App.ActiveDocument.getObject(fp.Name+"_"+a.Name)
				if sk==None:
					sk=App.ActiveDocument.addObject('Part::Spline',fp.Name+"_"+a.Name)
					sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
				sk.Shape=af.toShape()
				sk.ViewObject.ControlPoints = True


			poles=np.concatenate([pa[::-1],[pa[0]+fp.tangfacA*(pa[0]-pa[1]),pb[0]+fp.tangfacB*(pb[0]-pb[1])],pb]).swapaxes(0,1)
			print "Concatt shape ",poles.shape
			(_a,_b,_c)=poles.shape

			ecken=(_b-4)/3
			ms=[4]+[3]*ecken+[4]

			af=Part.BSplineSurface()
			sfa.getUMultiplicities()
			af.buildFromPolesMultsKnots(poles, 
				sfa.getUMultiplicities(),ms,
				sfa.getUKnots(),range(len(ms)),
				False,False,sfa.UDegree,3)

			# return

			if fp.displayConnect:
				nn=fp.Name+"_"+a.Name+"_"+b.Name
				sk=App.ActiveDocument.getObject(nn)
				if sk==None:
					sk=App.ActiveDocument.addObject('Part::Spline',nn)
					sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
				sk.Shape=af.toShape()
				sk.ViewObject.ControlPoints = True







	def connect(self,fp):

		print "in connect ...."
		try:
			a=fp.aSource
			b=fp.bSource
		except:
			return
		mode='u0v0'
		sfa=a.Shape.Face1.Surface
		pa0=sfa.getPoles()

		sfb=b.Shape.Face1.Surface
		pb0=sfb.getPoles()

		print "shapes ..."
		print np.array(pa0).shape
		print np.array(pb0).shape

		tt=0.8
	#	tt=0.6
		tt=0.3

		shapes=[]

		mergeEdge=False
		mergeEdge=0


		if 1:

			if fp.swapA:
				pa=np.array(pa0).swapaxes(0,1)
			else:
				pa=np.array(pa0)
			if fp.swapB:
				pb=np.array(pb0).swapaxes(0,1)
			else:
				pb=np.array(pb0)

			if fp.reverseA:
				pa=pa[::-1]
			if fp.reverseB:
				pb=pb[::-1]

			debugP(pa[0],"pa_0")
			debugP(pb[1],"pb_1_x")
			debugP(pa[1],"pa_1_x")


			if fp.mergeEdge:
				pa[0]=pa[1]*tt+pb[1]*(1-tt)
			else:
				tb=pb[1]-pb[0]
				ta=pa[1]-pa[0]
				pa[1] = pa[0]+(ta-tb)

			debugP(pa[0],"pa_0_neu")
			debugP(pa[1],"pa_1_neu")


			if fp.close:

				#if mergeEdge:
#					pb[-1]=(pa[-2]+pb[-2])*0.5
				pa[-1]=(pa[-2]+pb[-2])*0.5
				#else:
				#	tb=pb[-2]-pb[-1]
				#	ta=pa[-2]-pa[-1]
				#	pa[-2] = pa[-1]+(ta-tb)



			if fp.swapA:
				poles=pa.swapaxes(0,1)
			else:
				poles=pa



		af=Part.BSplineSurface()
		af.buildFromPolesMultsKnots(poles, 
				sfa.getUMultiplicities(),sfa.getVMultiplicities(),
				sfa.getUKnots(),sfa.getVKnots(),
				False,False,sfa.UDegree,sfa.VDegree)

		sk=App.ActiveDocument.getObject(fp.Name+"_"+a.Name)
		if sk==None:
			sk=App.ActiveDocument.addObject('Part::Spline',fp.Name+"_"+a.Name)
			sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
		sk.Shape=af.toShape()
		# sk.ViewObject.ControlPoints = True
		sk.ViewObject.Visibility=False
		shapes += [af.toShape()]


		if 1:

			if fp.swapA:
				pa=np.array(pa0).swapaxes(0,1)
			else:
				pa=np.array(pa0)
			if fp.swapB:
				pb=np.array(pb0).swapaxes(0,1)
			else:
				pb=np.array(pb0)

			if fp.reverseA:
				pa=pa[::-1]
			if fp.reverseB:
				pb=pb[::-1]

			debugP(pb[0],"pb_0")
			debugP(pb[1],"pb_1")
			debugP(pa[1],"pa_1")

			if fp.mergeEdge:
				pb[0]=pa[1]*tt+pb[1]*(1-tt)

			else:
				tb=pb[1]-pb[0]
				ta=pa[1]-pa[0]
				pb[1] = pb[0]+(tb-ta)



			if fp.close:
				#if mergeEdge:
				pb[-1]=(pa[-2]+pb[-2])*0.5
				#else:
				#	tb=pb[-2]-pb[-1]
				#	ta=pa[-2]-pa[-1]
				#	pb[-2] = pb[-1]+(tb-ta)

			debugP(pb[0],"pb_0_neu")
			debugP(pb[1],"pb_1_neu")


			if fp.swapB:
				poles=pb.swapaxes(0,1)
			else:
				poles=pb



		af=Part.BSplineSurface()
		af.buildFromPolesMultsKnots(poles, 
				sfb.getUMultiplicities(),sfb.getVMultiplicities(),
				sfb.getUKnots(),sfb.getVKnots(),
				False,False,sfb.UDegree,sfb.VDegree)

		sk=App.ActiveDocument.getObject(fp.Name+"_"+b.Name)
		if sk==None:
			sk=App.ActiveDocument.addObject('Part::Spline',fp.Name+"_"+b.Name)
			sk.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)

		sk.Shape=af.toShape()
		# sk.ViewObject.ControlPoints = True
		sk.ViewObject.Visibility=False
		
		shapes += [af.toShape()]

		fp.Shape=Part.Compound(shapes)


def createSeam():
	(fa,fb)=Gui.Selection.getSelection()

	sf=App.ActiveDocument.addObject('Part::FeaturePython','Seam')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	FaceConnection(sf)
	ViewProvider(sf.ViewObject)
	(us,vs)=Gui.Selection.getSelection()
	sf.aSource=fa
	sf.bSource=fb
	sf.mode='Seam'

	App.activeDocument().recompute()


def createDatumPlane():
	App.activeDocument().addObject('PartDesign::Plane','DatumPlane')

def createDatumLine():
	App.activeDocument().addObject('PartDesign::Line','DatumLine')

def begrid(bs,showTangents=True,showKnotCurves=True):

		comps=[]
		if showTangents:
			uks=bs.getUKnots()
			for i,k in enumerate(uks):
				comps  +=  [bs.uIso(k).toShape()] 

			vks=bs.getVKnots()
			for i,k in enumerate(vks):
				comps  +=  [bs.vIso(k).toShape()] 

		if showKnotCurves:
			poles=np.array(bs.getPoles())
			(uc,vc,_)=poles.shape
			nu=(uc-1)/3
			nv=(vc-1)/3
			tl=10
			for u in range(nu):
				for v in range(nv):
					try:
						comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u,3*v]),FreeCAD.Vector(poles[3*u,3*v+1])])]
						comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u,3*v]),FreeCAD.Vector(poles[3*u+1,3*v])])]
						if u>0:
							comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u-1,3*v]),FreeCAD.Vector(poles[3*u,3*v])])]
						if v>0:
							comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u,3*v-1]),FreeCAD.Vector(poles[3*u,3*v])])]
					except: pass
			for u in range(nu):
				try:
					v=vc-1
					comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u,v]),FreeCAD.Vector(poles[3*u+1,v])])]
					comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u,v-1]),FreeCAD.Vector(poles[3*u,v])])]
					if u>0:
						comps += [Part.makePolygon([FreeCAD.Vector(poles[3*u-1,v]),FreeCAD.Vector(poles[3*u,v])])]
				except:
					pass
			for v in range(nv):
				try:
					u=uc-1
					comps += [Part.makePolygon([FreeCAD.Vector(poles[u,3*v]),FreeCAD.Vector(poles[u,3*v+1])])]
					comps += [Part.makePolygon([FreeCAD.Vector(poles[u,3*v]),FreeCAD.Vector(poles[u-1,3*v])])]
					if v>0:
						comps += [Part.makePolygon([FreeCAD.Vector(poles[u,3*v]),FreeCAD.Vector(poles[u,3*v-1])])]
				except:
					pass
			try:
				u=uc-1
				v=vc-1
				comps += [Part.makePolygon([FreeCAD.Vector(poles[u,v]),FreeCAD.Vector(poles[u,v-1])])]
				comps += [Part.makePolygon([FreeCAD.Vector(poles[u,v]),FreeCAD.Vector(poles[u-1,v])])]
			except:
				pass

		return comps



class BeGrid(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		
		obj.addProperty("App::PropertyLink","Source")
		obj.addProperty("App::PropertyBool","showTangents")
		obj.addProperty("App::PropertyBool","showKnotCurves")
		
		
		obj.showKnotCurves=True

	def execute(self,fp):
		bs=fp.Source.Shape.Face1.Surface
		showTangents=fp.showTangents
		showKnotCurves=fp.showKnotCurves
		comps=begrid(bs,showTangents,showKnotCurves)
		fp.ViewObject.LineColor=fp.Source.ViewObject.ShapeColor
		fp.ViewObject.PointColor=fp.Source.ViewObject.ShapeColor
		fp.Shape=Part.Compound(comps)

def createBeGrid():
	fa=Gui.Selection.getSelection()[0]
	#fa=App.ActiveDocument.Seam_ProductFace001

	sf=App.ActiveDocument.addObject('Part::FeaturePython','BeGrid')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	BeGrid(sf)

	ViewProvider(sf.ViewObject)
	#(us,vs)=Gui.Selection.getSelection()
	sf.Source=fa

	App.activeDocument().recompute()



def BSplineToBezierCurve():
	bc=App.ActiveDocument.Sketch.Shape.Edge1.Curve

	mults=bc.getMultiplicities()
	knots=range(len(mults))

	bc2=Part.BSplineCurve()
	bc2.buildFromPolesMultsKnots(

		bc.getPoles(),
		mults,
		knots,
		False,3
	)

	#t=App.ActiveDocument.addObject('Part::Spline','jj')
	#t.Shape=bc2.toShape()
	#t.ViewObject.ControlPoints=True

	for i in range(1,len(mults)-1):
		print (i,mults[i])
		if mults[i]<3:
			bc2.insertKnot(i,3)

	t=App.ActiveDocument.addObject('Part::Spline','jj2')
	t.Shape=bc2.toShape()
	t.ViewObject.ControlPoints=True

def BSplineToBezierSurface():
#	bc=App.ActiveDocument.Nurbs.
	s=Gui.Selection.getSelection()[0]
	bc=s.Shape.Face1.Surface
	

	umults=bc.getUMultiplicities()
	uknots=range(len(umults))

	vmults=bc.getVMultiplicities()
	vknots=range(len(vmults))

	bc2=Part.BSplineSurface()
	bc2.buildFromPolesMultsKnots(

		bc.getPoles(),
		umults,
		vmults,
		uknots,
		vknots,
		False,False,3,3
	)

	#t=App.ActiveDocument.addObject('Part::Spline','jj')
	#t.Shape=bc2.toShape()
	#t.ViewObject.ControlPoints=True

	for i in range(1,len(umults)-1):
		print (i,umults[i])
		if umults[i]<3:
			bc2.insertUKnot(i,3,0)

	for i in range(1,len(vmults)-1):
		print (i,umults[i])
		if vmults[i]<3:
			bc2.insertVKnot(i,3,0)

	t=App.ActiveDocument.addObject('Part::Spline','jj2')
	t.Shape=bc2.toShape()
	t.ViewObject.ControlPoints=True



def BB():
	mode='DockWidget'
	if mode == 'VerticalLayoutTab':
		layout = layoutVT
	elif mode == 'MainWindow':
		layout = layoutMW
	elif mode == 'DockWidget':
		layout = layoutDW

	mikigui = createMikiGui(layout, MikiApp)
	return mikigui



def SurfaceEditor():

	print "--------------"
	from nurbswb.miki_g import createMikiGui2, MikiApp

	layout = '''
	MainWindow:
		QtGui.QLabel:
			setText:"***   Poles Editor   D E M O   ***"
		HorizontalGroup:
			setTitle: "Pole u v"
			QtGui.QLineEdit:
				id: 'ux'
				setText:"1"
				textChanged.connect: app.relativeMode
			QtGui.QLineEdit:
				id: 'vx'
				setText:"1"
				textChanged.connect: app.relativeMode

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
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.relativeMode
			QtGui.QDial:
				id: 'ydial'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.relativeMode
			QtGui.QDial:
				id: 'zdial'
				setMinimum: -100.
				setMaximum: 100.
				valueChanged.connect: app.relativeMode

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
				valueChanged.connect: app.relativeMode

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



		HorizontalGroup:
			setTitle: "Mode"
			QtGui.QComboBox:
				id: 'mode'
				addItem: "u"
				addItem: "v"
#		QtGui.QPushButton:
#			setText: "Run Action"
#			clicked.connect: app.run

		QtGui.QPushButton:
			setText: "connect to selected point"
			clicked.connect: app.connectSelection


		QtGui.QPushButton:
			setText: "apply"
			clicked.connect: app.apply

		QtGui.QPushButton:
			setText: "apply and close"
			clicked.connect: app.applyandclose

		QtGui.QPushButton:
			setText: "cancel and close"
			clicked.connect: app.myclose

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

		def connectSelection(self):

			fp=self.obj
			obj=App.ActiveDocument.getObject('temp_YY1')
			if obj == None:
				obj=App.ActiveDocument.addObject('Part::Spline','temp_YY1')
			bs=fp.Shape.Face1.Surface
			vec=Gui.Selection.getSelectionEx()[0].PickedPoints[0]

			upn=int(self.root.ids['ux'].text())
			vpn=int(self.root.ids['vx'].text())
			poles=bs.getPoles()

			center=poles[upn*3][vpn*3]
			poles=np.array(poles)

			ttp=poles[upn*3-1:upn*3+2,vpn*3-1:vpn*3+2] - center
			ttp += vec 
			poles[upn*3-1:upn*3+2,vpn*3-1:vpn*3+2]=ttp

			ss=Part.Sphere()
			ss.Radius=100
			s=ss.toShape()
			s.Placement.Base=poles[upn*3][vpn*3]

			bs2=Part.BSplineSurface()
			bs2.buildFromPolesMultsKnots(poles, 
				bs.getUMultiplicities(),
				bs.getVMultiplicities(),
				bs.getUKnots(),
				bs.getVKnots(),
				False,False,3,3)

			comps=begrid(bs2,
				self.root.ids['showcurves'].isChecked(),
				self.root.ids['showtangents'].isChecked()
				)



			if self.root.ids['showface'].isChecked():
				comps += [bs2.toShape()]
			self.Shape=bs2.toShape()
			# comps += [s]
			obj.Shape=Part.Compound(comps)
			#obj.Shape=Part.Compound(comps+ [s])

			#obj=App.ActiveDocument.addObject('Part::Spline','YY_'+fp.Name)
#			obj.Shape=bs.toShape()

			obj2=App.ActiveDocument.getObject('temp_YY2')
			
			if obj2 == None:
				obj2=App.ActiveDocument.addObject('Part::Spline','temp_YY2')
				obj2.ViewObject.ShapeColor=(1.0,0.,0.)
				obj2.ViewObject.LineColor=(0.3,0.3,1.)
				obj2.ViewObject.LineWidth=10

			self.NameObj2=obj2.Name

			comps=begrid(bs2,False,True)
			bs3=bs2.copy()
			bs3.segment(upn-1,upn+1,vpn-1,vpn+1)

			obj2.Shape=Part.Compound(comps+[s] + [bs3.toShape()])


			App.activeDocument().recompute()

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
	#		obj=App.ActiveDocument.getObject('YY_'+fp.Name)
			try:
				App.ActiveDocument.removeObject(self.NameObj2)
				App.ActiveDocument.removeObject(self.NameObj)
			except:
				pass
			self.close()


		def myclose(self):
			fp=self.obj
	#		self.save()
	#		obj=App.ActiveDocument.getObject('YY_'+fp.Name)
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
#			print "relative mode called"
			self.apply(False)

		def apply(self,save=True):
#			print "apply  implemented"
			st=time.time()
			try:
				fp=self.obj
			except: # not yet ready
				return
			print ("applay auf ",fp.Label)


			obj=App.ActiveDocument.getObject('temp_YY1')
			if obj == None:
				obj=App.ActiveDocument.addObject('Part::Spline','temp_YY1')
			bs=fp.Shape.Face1.Surface
			vec=FreeCAD.Vector(
						self.root.ids['xdial'].value()*self.root.ids['scale'].value(),
						self.root.ids['ydial'].value()*self.root.ids['scale'].value(),
						self.root.ids['zdial'].value()*self.root.ids['scale'].value()
						)

			upn=int(self.root.ids['ux'].text())
			vpn=int(self.root.ids['vx'].text())
			poles=bs.getPoles()


			print "shape ",np.array(poles).shape
			print ("vec",vec)
			print(upn,vpn)


			center=poles[upn*3][vpn*3]
			poles=np.array(poles)

			ttp=poles[upn*3-1:upn*3+2,vpn*3-1:vpn*3+2] - center
			rot=FreeCAD.Rotation(self.root.ids['xrot'].value(),self.root.ids['yrot'].value(),self.root.ids['zrot'].value())

			for u in 0,1,2:
				for v in 0,1,2:
					ttp[u,v]=rot.multVec(FreeCAD.Vector(ttp[u,v]))

			(t1,t2)=bs.tangent(upn,vpn)
			n=bs.normal(upn,vpn)
			vectn=t1*self.root.ids['udial'].value()*self.root.ids['scale'].value()+\
						t2*self.root.ids['vdial'].value()*self.root.ids['scale'].value()+\
						n*self.root.ids['ndial'].value()*self.root.ids['scale'].value()


			ttp += vec + center +vectn
			poles[upn*3-1:upn*3+2,vpn*3-1:vpn*3+2]=ttp

			ss=Part.Sphere()
			ss.Radius=100
			s=ss.toShape()
			s.Placement.Base=poles[upn*3][vpn*3]

			print "Time A",time.time()-st
			
			bs2=Part.BSplineSurface()
			bs2.buildFromPolesMultsKnots(poles, 
				bs.getUMultiplicities(),
				bs.getVMultiplicities(),
				bs.getUKnots(),
				bs.getVKnots(),
				False,False,3,3)

			comps=begrid(bs2,
				self.root.ids['showcurves'].isChecked(),
				self.root.ids['showtangents'].isChecked()
				)


			print "Time B1 ",time.time()-st
			if self.root.ids['showface'].isChecked():
				comps += [bs2.toShape()]


			self.Shape=bs2.toShape()
			if not save:
				print "Time B2 ",time.time()-st
				# comps += [s]
				obj.Shape=Part.Compound(comps)
				#obj.Shape=Part.Compound(comps+ [s])
				print "Time B2a ",time.time()-st
				#obj=App.ActiveDocument.addObject('Part::Spline','YY_'+fp.Name)
	#			obj.Shape=bs.toShape()

				obj2=App.ActiveDocument.getObject('temp_YY2')
				
				if obj2 == None:
					obj2=App.ActiveDocument.addObject('Part::Spline','temp_YY2')
					obj2.ViewObject.ShapeColor=(1.0,0.,0.)
					obj2.ViewObject.LineColor=(0.3,0.3,1.)
					obj2.ViewObject.LineWidth=10

				self.NameObj2=obj2.Name

				print "Time B3 ",time.time()-st
				comps=begrid(bs2,False,True)
				bs3=bs2.copy()
				bs3.segment(upn-1,upn+1,vpn-1,vpn+1)
				print "Time B4 ",time.time()-st
				obj2.Shape=Part.Compound(comps+[s] + [bs3.toShape()])
				print "Time B ",time.time()-st

			if save:
				print "SAVE"
				sts=time.time()
				self.save()
				print "Time SCA ",time.time()-sts
				sts=time.time()
				self.apply(False)
				print "Time SCB ",time.time()-sts
				sts=time.time()
				self.resetDialog()
				print "Time SCC ",time.time()-sts

			App.activeDocument().recompute()
			print "Time C ",time.time()-st



	fp=Gui.Selection.getSelection()[0]
	obj=App.ActiveDocument.getObject('YY_'+fp.Name)
	if obj == None:
		obj=App.ActiveDocument.addObject('Part::Spline','temp_YY1')
	
	obj.Shape=fp.Shape


	mikigui = createMikiGui2(layout, EditorApp)
	print mikigui
	mikigui.obj=fp
	mikigui.NameObj=obj.Name
	mikigui.relativeMode()





def addKnot():

	from nurbswb.miki_g import createMikiGui2, MikiApp

	layout = '''
	MainWindow:
		QtGui.QLabel:
			setText:"***   Dock Widget    D E M O   ***"

		HorizontalGroup:
			setTitle: "Position UV-tangential Normal"
			QtGui.QDial:
				id: 'udial'
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.displayKnot
				setMinimum: -100
				setMaximum: 100
			QtGui.QDial:
				id: 'vdial'
				setMinimum: -100
				setMaximum: 100
				valueChanged.connect: app.displayKnot

		HorizontalGroup:
			setTitle: "Direction"
			QtGui.QComboBox:
				id: 'mode'
				addItem: "u"
				addItem: "v"
#		QtGui.QPushButton:
#			setText: "Run Action"
#			clicked.connect: app.run
		QtGui.QPushButton:
			setText: "add Knot"
			clicked.connect: app.addKnot

		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.myclose
		setSpacer:
		'''





	class BeKnotApp(MikiApp):

		def run(self):
			print "run"
			insertKnot(
				self.root.ids['pos'].text(),
				self.root.ids['mode'].currentText(),
			)

		def myclose(self):
			try:
				App.ActiveDocument.removeObject(self.NameObj)
			except: 
				pass
			self.close()



		def displayKnot(self):
			mode=str(self.root.ids['mode'].currentText())
			uval=self.root.ids['udial'].value()
			vval=self.root.ids['vdial'].value()

			fp=Gui.Selection.getSelection()[0]
			bs=fp.Shape.Face1.Surface
#			print ("Mode",mode)
			if mode=='u':
				knots=bs.getUKnots()
#				print knots
				c1=bs.uIso((knots[-1]-knots[0])*((uval-0.5)+100.)/200.)
				c2=bs.uIso((knots[-1]-knots[0])*((uval+0.5)+100.)/200.)
			if mode=='v':
				knots=bs.getVKnots()
#				print knots
				c1=bs.vIso((knots[-1]-knots[0])*((vval-0.5)+100.)/200.)
				c2=bs.vIso((knots[-1]-knots[0])*((vval+0.5)+100.)/200.)


			comps=begrid(bs,True,False)

			self.NameObj='Kp_'+fp.Name
			obj=App.ActiveDocument.getObject(self.NameObj)
			if obj == None:
				obj=App.ActiveDocument.addObject('Part::Spline',self.NameObj)

			obj.Shape=Part.Compound(comps+[c1.toShape(),c2.toShape()])

		def addKnot(self):
			mode=str(self.root.ids['mode'].currentText())
			uval=self.root.ids['udial'].value()
			vval=self.root.ids['vdial'].value()
			
			fp=Gui.Selection.getSelection()[0]
			bs=fp.Shape.Face1.Surface
#			print ("Mode",mode)
			if mode=='u':
				knots=bs.getUKnots()
#				print knots
				pos=(knots[-1]-knots[0])*(uval+100.)/200.
				bs.insertUKnot(pos,3,0)
			if mode=='v':
				knots=bs.getVKnots()
#				print knots
				pos=(knots[-1]-knots[0])*(vval+100.)/200.
				bs.insertVKnot(pos,3,0)

			obj=App.ActiveDocument.addObject('Part::Spline','result')
			
			umults=bs.getUMultiplicities()
			uknots=range(len(umults))

			vmults=bs.getVMultiplicities()
			vknots=range(len(vmults))

			bs2=Part.BSplineSurface()
			bs2.buildFromPolesMultsKnots(

				bs.getPoles(),
				umults,
				vmults,
				uknots,
				vknots,
				False,False,3,3
			)


			
			
			obj.Shape=bs2.toShape()
			App.activeDocument().recompute()

			App.ActiveDocument.removeObject(self.NameObj)

			fp.ViewObject.hide()
			Gui.Selection.clearSelection()
			Gui.Selection.addSelection(obj)
			
			self.displayKnot()
#			obj=App.ActiveDocument.getObject('Kp_'+fp.Name)
#			if obj == None:
#				obj=App.ActiveDocument.addObject('Part::Spline','Kp_'+fp.Name)
#			obj.Shape=c.toShape()





	mikigui = createMikiGui2(layout, BeKnotApp)
	mikigui.displayKnot()
	




def connectFaces():
	(fa,fb)=Gui.Selection.getSelection()
#	(b2,b3)=_connectFaces(b,r3,mode='v0v0')

	sf=App.ActiveDocument.addObject('Part::FeaturePython','FaceConnection')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	FaceConnection(sf)
	ViewProvider(sf.ViewObject)
	(us,vs)=Gui.Selection.getSelection()
	sf.aSource=fa
	sf.bSource=fb
	#sf.swapB=True
	#sf.close=True

	App.activeDocument().recompute()

	return



	(b,b1)=_connectFaces(r,r2,mode='u0v0')
	#_connectFaces(r3,rr,mode='v0v0')
	(b2,b3)=_connectFaces(b,r3,mode='v0v0')
	(b4,b5)=_connectFaces(b3,b1,mode='v0v0')
#	_connectFaces(



def fixCorner():


	(a,b,c)=Gui.Selection.getSelection()
	_fixCorner(a,b,c)
	App.activeDocument().recompute()






class BePlane(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyInteger","uSegments")
		obj.addProperty("App::PropertyInteger","vSegments")
		obj.addProperty("App::PropertyBool","swap")
		obj.addProperty("App::PropertyBool","reverse")
		obj.addProperty("App::PropertyFloat","uSize")
		obj.addProperty("App::PropertyFloat","vSize")
		obj.addProperty("App::PropertyFloat","zSize")
		obj.addProperty("App::PropertyFloat","noise")

		obj.uSegments=4
		obj.vSegments=3
		obj.uSize=1000
		obj.vSize=800
		obj.zSize=500

	def execute(self,fp):
		uc=fp.uSegments*3+1
		vc=fp.vSegments*3+1
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)*fp.noise
		poles *= fp.zSize
		for u in range(uc):
			poles[u,:,0]=fp.uSize*u
		for v in range(vc):
			poles[:,v,1]=fp.vSize*v
		
		um=[4]+[3]*(fp.uSegments-1)+[4]
		vm=[4]+[3]*(fp.vSegments-1)+[4]
		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(
			poles,
			um,vm,
			range(len(um)),range(len(vm)),
			False,False,3,3)
		fp.Shape=bs.toShape()

		sf=bs
		print (sf.getUMultiplicities(),sf.getVMultiplicities(),sf.getUKnots(),sf.getVKnots(),)
		print poles.shape


	def execute(self,fp):
		uc=3+fp.uSegments
		vc=3+fp.vSegments
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)*fp.noise
		poles *= fp.zSize
		for u in range(uc):
			poles[u,:,0]=fp.uSize*u
		for v in range(vc):
			poles[:,v,1]=fp.vSize*v
		
		um=[4]+[1]*(fp.uSegments-1)+[4]
		vm=[4]+[1]*(fp.vSegments-1)+[4]
		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(
			poles,
			um,vm,
			range(len(um)),range(len(vm)),
			False,False,3,3)
		fp.Shape=bs.toShape()

		for i in range(1,fp.uSegments):
			bs.insertUKnot(i,3,0)
		for i in range(1,fp.vSegments):
			bs.insertVKnot(i,3,0)

		sf=bs
		print (sf.getUMultiplicities(),sf.getVMultiplicities(),sf.getUKnots(),sf.getVKnots(),)
		print poles.shape





def createBePlane():
	sf=App.ActiveDocument.addObject('Part::FeaturePython','BePlane')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	BePlane(sf)
	ViewProvider(sf.ViewObject)


class BeTube(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyInteger","uSegments")
		obj.addProperty("App::PropertyInteger","vSegments")
		obj.addProperty("App::PropertyInteger","offset")
		obj.addProperty("App::PropertyBool","swap")
		obj.addProperty("App::PropertyBool","reverse")
		obj.addProperty("App::PropertyFloat","uSize")
		obj.addProperty("App::PropertyFloat","vSize")
		obj.addProperty("App::PropertyFloat","noise")

		obj.uSegments=5
		obj.vSegments=3
		obj.uSize=1000
		obj.vSize=200


	# offen form
	def XXexecute(self,fp):
		uc=fp.uSegments*3+1
		vc=fp.vSegments*3+1
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)
		poles *=200 +500
		for u in range(uc):
			poles[u,:,0]=fp.uSize*np.cos(2*u*np.pi/uc)
			poles[u,:,1]=fp.uSize*np.sin(2*u*np.pi/uc)
		for v in range(vc):
			poles[:,v,2]=fp.vSize*v

		print poles

		um=[4]+[3]*(fp.uSegments-1)+[4]
		vm=[4]+[3]*(fp.vSegments-1)+[4]
		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(
			poles,
			um,vm,
			range(len(um)),range(len(vm)),
			False,False,3,3)

		fp.Shape=bs.toShape()

	def execute(self,fp): # gehts
		uc=fp.uSegments*3+3
		vc=fp.vSegments*3+1
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)
		poles *=200 +500
		for u in range(uc):
			poles[u,:,0]=fp.uSize*np.cos(2*u*np.pi/uc)
			poles[u,:,1]=fp.uSize*np.sin(2*u*np.pi/uc)
		for v in range(vc):
			poles[:,v,2]=fp.vSize*v

		um=[3]+[3]*(fp.uSegments)+[3]
		vm=[4]+[3]*(fp.vSegments-1)+[4]
		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(
			poles,
			um,vm,
			range(len(um)),range(len(vm)),
			True,False,3,3)


		fp.Shape=bs.toShape()

	def execute(self,fp):
		uc=fp.uSegments+3
		vc=fp.vSegments+3
		poles=np.random.random(uc*vc*3).reshape(uc,vc,3)
		poles *= fp.noise
		for u in range(uc):
			poles[u,:,0] += fp.uSize*np.cos(2*u*np.pi/uc)
			poles[u,:,1] += fp.uSize*np.sin(2*u*np.pi/uc)
		for v in range(vc):
			poles[:,v,2] += fp.vSize*v


		um=[1]*(fp.uSegments+4)
		vm=[4]+[1]*(fp.vSegments-1)+[4]
		print poles.shape
		print um
		print vm
		bs=Part.BSplineSurface()
		bs.buildFromPolesMultsKnots(
			poles,
			um,vm,
			range(len(um)),range(len(vm)),
			True,False,3,3)

		for i in range(0,fp.uSegments+3):
			bs.insertUKnot(i,3,0)
		for i in range(1,fp.vSegments):
			bs.insertVKnot(i,3,0)

		fp.Shape=bs.toShape()


		sf=bs
		print (sf.getUMultiplicities(),sf.getVMultiplicities(),sf.getUKnots(),sf.getVKnots(),)
		print poles.shape



def createBeTube():
	sf=App.ActiveDocument.addObject('Part::FeaturePython','BeTube')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	BeTube(sf)
	ViewProvider(sf.ViewObject)


class BePlaneTubeConnector(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
#		obj.addProperty("App::PropertyInteger","uSegments")
#		obj.addProperty("App::PropertyInteger","vSegments")
		obj.addProperty("App::PropertyLink","plane")
		obj.addProperty("App::PropertyLink","tube")

		obj.addProperty("App::PropertyInteger","offset")
		obj.addProperty("App::PropertyInteger","level")
		obj.addProperty("App::PropertyBool","swap")
		obj.addProperty("App::PropertyBool","reverse")
		obj.addProperty("App::PropertyFloat","tangentFactor")
#		obj.addProperty("App::PropertyFloat","vSize")
		obj.tangentFactor=1
#		obj.plane=App.ActiveDocument.BePlane
#		obj.tube=App.ActiveDocument.BeTube




	def execute(self,fp):
		sf=fp.plane.Shape.Face1.Surface
		poles=np.array(sf.getPoles())
		sfr=fp.tube.Shape.Face1.Surface
		polesr=np.array(sfr.getPoles())
		polesr=np.concatenate([polesr,polesr])
		a=poles.shape[0]

		print polesr.shape
		k2=fp.tangentFactor
		level=fp.level*3
		offset=fp.offset*3
		if fp.swap:
			if fp.reverse:
				poles[0:a,-1] =polesr[0+offset:a+offset,level]
				poles[0:a,-2] = (1+k2)*polesr[0+offset:a+offset,level]-k2*polesr[0+offset:a+offset,level+1]
			else:
				poles[0:a,-1] =polesr[0+offset:a+offset,level][::-1]
				poles[0:a,-2] = (1+k2)*polesr[0+offset:a+offset,level][::-1]-k2*polesr[0+offset:a+offset,level+1][::-1]
		else:
			if fp.reverse:
				poles[0:a,0] =polesr[0+offset:a+offset,level]
				poles[0:a,1] = (1+k2)*polesr[0+offset:a+offset,level]-k2*polesr[0+offset:a+offset,level+1]
			else:
				poles[0:a,0] =polesr[0+offset:a+offset,level][::-1]
				poles[0:a,1] = (1+k2)*polesr[0+offset:a+offset,level][::-1]-k2*polesr[0+offset:a+offset,level+1][::-1]


		bs=Part.BSplineSurface()

		um=sf.getUMultiplicities()
		vm=sf.getVMultiplicities()
		bs.buildFromPolesMultsKnots(
				poles,
				um,vm,
				range(len(um)),range(len(vm)),
				False,False,3,3)
		fp.Shape=bs.toShape()



def createPlaneTubeConnector():
	sf=App.ActiveDocument.addObject('Part::FeaturePython','BeConnector')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	BePlaneTubeConnector(sf)
	(sf.plane,sf.tube)=Gui.Selection.getSelection()
	ViewProvider(sf.ViewObject)


	
def connectPlaneToTube():
	pass

def AA():
	createPlaneTubeConnector()

def BB():
	print "AA-neu"




class HelmetTubeConnector(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
#		obj.addProperty("App::PropertyInteger","uSegments")
#		obj.addProperty("App::PropertyInteger","vSegments")
		obj.addProperty("App::PropertyLink","helmet")
		obj.addProperty("App::PropertyLink","tube")

		obj.addProperty("App::PropertyInteger","offset")
		obj.addProperty("App::PropertyInteger","level")
		obj.addProperty("App::PropertyBool","swap")
		obj.addProperty("App::PropertyBool","reverse")
		obj.addProperty("App::PropertyFloat","tangentFactorTube")
		obj.addProperty("App::PropertyFloat","tangentFactorHelmet")

		obj.tangentFactorTube=1
		obj.tangentFactorHelmet=1



	def execute(self,fp):

		import numpy as np
		import Draft

		sf=fp.helmet.Shape.Face1.Surface
		#sf=App.ActiveDocument.helmet.Shape.Face1.Surface
		poles=np.array(sf.getPoles())
		print "!###",poles.shape
		a=poles

		print 

		ring=np.concatenate([
			a[:-1,0],
			a[-1,:-1],
			a[1:,-1][::-1],
			a[0,1:][::-1]
			])
		print "!",len(ring)

		ring2=np.concatenate([
			[a[1,1]],
			a[1:-2,1],
			[a[-2,1]],[a[-2,1]],
			a[-2,1:-2],
			[a[-2,-2]],[a[-2,-2]],
			a[2:-1,-2][::-1],
			[a[1,-2]],[a[1,-2]],
			a[1,2:-1][::-1],
			[a[1,1]]
			
			])


		print "!",len(ring)
		print "!",len(ring2)

#		ring2[::,2]+= -400

		k1=fp.tangentFactorHelmet
		ring2a=(1+k1)*ring-k1*ring2
		ring2=ring2a


		ring3=ring2.copy()
		ring3[::,2] += -300
		#ring3 *=1.3

		ring3=[FreeCAD.Vector(p) for p in ring3]

		ring4=ring2.copy()
		ring4[::,2] += -500
		ring4 *=1.2


		# daten von woanders
		tube=App.ActiveDocument.BeTube
		tube=fp.tube
		tsf=tube.Shape.Face1.Surface
		tps=np.array(tsf.getPoles()).swapaxes(0,1)
		k2=fp.tangentFactorTube
		print "tps"
		
		print tps.shape
		if fp.swap:
			ring4=tps[fp.level]
			ring3=(1+k2)*tps[fp.level]-k2*tps[1+fp.level]
		else:
			ring4=tps[-1-fp.level]
			ring3=(1+k2)*tps[-1-fp.level]-k2*tps[-2-fp.level]

		if fp.reverse:
			offset=fp.offset*3+1
		else:
			offset=fp.offset*3

		ring3a=np.concatenate([ring3[offset:],ring3[:offset]])
		ring4a=np.concatenate([ring4[offset:],ring4[:offset]])
		if fp.reverse:
			ring3,ring4=ring3a[::-1],ring4a[::-1]
		else:
			ring3,ring4=ring3a,ring4a


		if 0:
			Draft.makeWire([FreeCAD.Vector(p) for p in ring])
			Draft.makeWire([FreeCAD.Vector(p) for p in ring2])
			Draft.makeWire([FreeCAD.Vector(p) for p in ring3])
			Draft.makeWire([FreeCAD.Vector(p) for p in ring4])

		bs=Part.BSplineSurface()
		print np.array([ring,ring2,ring3,ring4]).shape
		
		bs.buildFromPolesMultsKnots([ring,ring2,ring3,ring4],
			[4,4],[3,3,3,3,3,3,3,3,3],
			[0,1],range(9),
			False,True,3,3)

#		sk=App.ActiveDocument.addObject('Part::Spline','adapter')
#		sk.Shape=bs.toShape()


		fp.Shape=bs.toShape()



def createHelmet():
	import nurbswb.helmet
	reload(nurbswb.helmet)
	nurbswb.helmet.createHelmet()

def createHelmetTubeConnector():
	sf=App.ActiveDocument.addObject('Part::FeaturePython','BeConnector')
	sf.ViewObject.ShapeColor=(0.5+random.random(),random.random(),random.random(),)
	HelmetTubeConnector(sf)
	(sf.helmet,sf.tube)=Gui.Selection.getSelection()
	ViewProvider(sf.ViewObject)
