# -*- coding: utf-8 -*-
'''approximate  a point cloud by a bezier curve
#-------------------------------------------------
#-- 
#--
#-- microelly 2018  0.2
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
'''

import numpy as np
import Draft,Points,Part,Sketcher
import nurbswb.say
from nurbswb.say import *
import random
import time

import inspect
reload (nurbswb.say)

from nurbswb.miki_g import createMikiGui2, MikiApp
reload( nurbswb.miki_g)

from pyob import *
import nurbswb.pyob
from nurbswb.pyob import  FeaturePython,ViewProvider

import scipy
from scipy.optimize import minimize
from scipy import signal
from scipy import misc



def getPart(name="hugo"):
	'''objekt bereitstellen bzw. anlegen'''

	obj=FreeCAD.ActiveDocument.getObject(name)
	if obj== None:
		obj=FreeCAD.ActiveDocument.addObject("Part::Feature",name)
	return obj


# diagramm fuer filter nur einmal am anfang zeigen
diagram=False

def runfilt(t,xn,degree=2,lowfilt=0.005):
	'''signale-filter fuer PointCloudApprox'''

	global diagram

	if 0:
		mymin=-5
		mymax=5
		xn2=[]
		for x in xn:
			if x <mymin: xn2 += [mymin]
			elif x>mymax: xn2 += [mymax]
			else: xn2 += [x]
		xn=xn2
	
	b, a = signal.butter(degree, lowfilt)

	zi = signal.lfilter_zi(b, a)
	z, _ = signal.lfilter(b, a, xn, zi=zi*xn[0])
	z2, _ = signal.lfilter(b, a, z, zi=zi*z[0])
	y = signal.filtfilt(b, a, xn)

	if 1 or not diagram:
		if 0: # in midi-bereich
			import Plot
			Plot.figure("Smooth Filter for Points")
		else: # eigenes fenster
			import Plot2 as Plot
			Plot.figureWindow("Smooth Filter for Points")

		Plot.plot(t, xn ,'points')
		Plot.plot( t, y, 'filter')
		Plot.legend(True)
		Plot.grid(True)
		diagram=True

	return (t,y)

#----------------------------------------


# Approximation einer Punktwolke durche ine Kurve
#
#


class PointCloudApprox(FeaturePython):
	def __init__(self, obj,label=None,points=None,start=None):
		FeaturePython.__init__(self, obj)

		obj.addProperty("App::PropertyInteger","count").count=10
		obj.addProperty("App::PropertyInteger","degree").degree=10
		obj.addProperty("App::PropertyFloat","lowfilter").lowfilter=2
		obj.addProperty("App::PropertyFloat","threshold").threshold=5

		obj.addProperty("App::PropertyLink","Points")
		obj.addProperty("App::PropertyLink","Start")
#		obj.addProperty("App::PropertyBool","createBSpline","smooth")
#		obj.addProperty("App::PropertyBool","closeBSpline","smooth")
#		obj.addProperty("App::PropertyInteger","discretizeCount").discretizeCount=30
		obj.addProperty("App::PropertyBool","active","smooth")
		obj.addProperty("App::PropertyBool","closed","smooth")
		obj.Points=points
		obj.Start=start

	def runPountCloudApprox(self,obj,bo=None):

		dd=obj.count
		name=obj.Name
		ao=obj.Start
		a=ao.Shape
		w=obj.Points.Points.Points

		pts=[]
		ptsu=[]
		comps=[]
		for i,bbb in enumerate(w):
			b=Part.Point(bbb).toShape()
			rc=a.distToShape(b)
			if rc[0]>0:
				(pa,pb)=rc[1][0]
				comps += [Part.makePolygon([pb,pa])]

				c=a.Edge1.Curve
				try:
					p=c.parameter(pb)
					n=c.normal(p)
					if abs((pb-pa).dot(n))<obj.threshold:
						pts += [FreeCAD.Vector(p,(pb-pa).dot(n))]

				except:
					print "ignore",i

		hop=getPart(name+"_helper")
		hop.Shape=Part.Compound(comps)
		hop.ViewObject.hide()

		# sortieren
		pts2=sorted(pts,key=lambda x: x[0])
		pts3=pts2

		for l in [0]: # anzahl der durchlaeufe

			pts2=pts3
			ll=len(pts2)

			pts3=[pts2[0]]
			x=[]
			y=[]
			for i in range(ll):
				x+=[pts2[i].x]
				y+=[pts2[i].y]

			if obj.closed: # zyklisch -enden anpassen
				sx=x[0]
				ex=x[-1]
				xx=[v+(ex-sx) for v in x]
				x0=[v-(ex-sx) for v in x]
				ll=len(x)

				(x2,y2)=runfilt(x0+x+xx,y+y+y,obj.degree,0.001*obj.lowfilter)
				pts3=[FreeCAD.Vector(x,y) for (x,y) in zip(x2[ll:2*ll],y2[ll:2*ll])]

			else:
				(x2,y2)=runfilt(x,y,obj.degree,0.001*obj.lowfilter)
				pts3=[FreeCAD.Vector(x,y) for (x,y) in zip(x2,y2)]


			pts4=[]
			pts5=[]
			for p in pts3:
				pts4 += [c.value(p.x)+c.normal(p.x)*p.y]
				pts5 += [c.value(p.x),c.value(p.x)+c.normal(p.x)*p.y,c.value(p.x)]

			hop=getPart(name+"_Wire")
			hop.Shape=Part.makePolygon(pts4)

			import nurbswb.smooth
			reload(nurbswb.smooth)
			smooth=FreeCAD.ActiveDocument.getObject("smooth"+"_"+name)
			if smooth == None:
				nurbswb.smooth.smoothWire(hop,"smooth"+"_"+name)
			else:
				print "setze smooth count ",dd
				smooth.Wire=hop
				smooth.discretizeCount=dd


	def onChanged(self, obj, prop):
		if not hasattr(obj,"active"): return
		if prop in  ['count','degree','lowfilter','threshold']:
			self.runPountCloudApprox(obj)


# fuer eine pointcloud und einer Startkurve wird eine BSpline-Approximation berechnet
# die stoehrungen werden mit scipy.signal.filtfilt entfernt
# als amplitude wird die abweichung von der vorgeschlagenen kurve genutzt

def createPointCloudApprox():
	'''methode wird vom Dialog smoothPointcloud aufgerufen'''

	[points,start]= Gui.Selection.getSelection()
	name=points.Name+"_from_"+start.Name

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
	PointCloudApprox(a,name,points,start)
	ViewProvider(a.ViewObject)
	return a



def _smoothPointcloudGUI():
	'''smooth the point cloud to a bspline curve'''

##\cond
	layout = '''
	MainWindow:
		QtGui.QLabel:
			setText:"***   D E M O 1  ***"

		HorizontalGroup:
			setTitle: "Mode"
			QtGui.QComboBox:
				id: 'mode'
				addItem: "all"
				#addItem: "none"
				addItem: "vertical"
				addItem: "horizontal"

		HorizontalGroup:
			setTitle: "Tangent Force v"

			QtGui.QDial:
				id: 'tbb'
				setFocusPolicy: QtCore.Qt.StrongFocus
				valueChanged.connect: app.run
				setMinimum: 5
				setValue: 10
				setMaximum: 50

		QtGui.QPushButton:
			setText: "Run Action"
			clicked.connect: app.run

		QtGui.QPushButton:
			setText: "change Image"
			clicked.connect: app.changeImage

		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.myclose

		setSpacer:
		# temp image widget prototype
		PicWidget:
			id: 'image'
			sizeX: 400
			sizeY: 200
			run_display: "/home/thomas/Bilder/bp_841.png"
		'''


	class myApp(MikiApp):

		# temp. testdaten fuer den image widget
		index=0
		images=["/home/thomas/Bilder/bp_842.png",
		"/home/thomas/Bilder/bp_843.png",
		"/home/thomas/Bilder/bp_844.png"
		]

		def myclose(self):
			self.close()

		def changeImage(self):
			'''testmethode fuer image widget'''

			self.root.ids['image'].run_display(self.images[self.index] )
			self.index += 1
			if self.index >=len(self.images): self.index=0

		def run(self):
			modus=self.root.ids['mode'].currentText()
	
			try:
				print "part is ..",self.part
			except: 
				print "noch kein objekt zugewiesen"
				return

			try:
				tb=self.root.ids['tbb'].value()
				self.part.count=int(round(tb))

			except: 
				return

	mikigui = createMikiGui2(layout, myApp)
	mikigui.part=createPointCloudApprox()
	mikigui.run()
	return mikigui

##\endcond

# laden der punkte aus einem bild - das bild muss 
# mit methoden der reconstruction wb nachbearbeitet werden

class ImagePoints(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyFile","image")
		obj.addProperty("App::PropertyInteger","min").min=150
		obj.addProperty("App::PropertyInteger","max").max=1000
		obj.addProperty("App::PropertyIntegerList","params").params=[1,1,1,1]

	def execute(self,obj):

		face = misc.imread(obj.image)

		face2=obj.params[0]*face[:,:,0]+obj.params[1]*face[:,:,1]+obj.params[2]*face[:,:,2]
		(uc,vc)=face2.shape

		pts=[]
		for u in range(uc):
			for v in range(vc):
				if face2[u,v] >obj.min and face2[u,v] < obj.max:
					pts += [FreeCAD.Vector(v,u,face2[u,v]*obj.params[3])]

		obj.Points=Points.Points(pts)


def _loadPointcloudfromImageGUI():
	''' bild datei laden'''

	fn='/home/thomas/Downloads/Profil-Punktewolke3D.png'
	yy=App.ActiveDocument.addObject("Points::FeaturePython","ImagePoints")
	ImagePoints(yy)
	yy.image=fn
	ViewProvider(yy.ViewObject)


class MinLengthBezier(FeaturePython):
	''' gegeben 7 Punkte Spline, finde optimale Kurve durch Mittelpunkt, durch Endpunkt und Endtangenten'''

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","path","source")
		obj.addProperty("App::PropertyFloat","factor","config")#.factor=30
		obj.addProperty("App::PropertyFloat","alphaStart","config")#.alphaStart=-18
		obj.addProperty("App::PropertyFloat","alphaEnd","config")
		obj.addProperty("App::PropertyFloat","betaStart","config")#.alphaStart=-18
		obj.addProperty("App::PropertyFloat","betaEnd","config")
		obj.addProperty("App::PropertyBool","betaOff","config")

		obj.addProperty("App::PropertyBool","reuseAlphas")
		
		obj.addProperty("App::PropertyFloat","tol","approx").tol=0.1
		obj.addProperty("App::PropertyBool","closed").closed=True
		obj.addProperty("App::PropertyBool","useStart","config").useStart=True
		obj.addProperty("App::PropertyBool","useEnd","config").useEnd=True
		obj.addProperty("App::PropertyEnumeration","method","approx")
		obj.addProperty("App::PropertyEnumeration","tangentModel","approx")
		obj.addProperty("App::PropertyFloatList","factorList").factorList=[100.]*20
		obj.addProperty("App::PropertyFloatList","alphaList","result")
		obj.addProperty("App::PropertyFloatList","extraKnots")
		obj.addProperty("App::PropertyInteger","start","source").start=0
		obj.addProperty("App::PropertyInteger","end","source").end=0
		obj.addProperty("App::PropertyInteger","Wire","source").Wire=-1

		obj.addProperty("App::PropertyEnumeration","mode","approx")
		obj.mode=['minimal Lenght','Length','curvature','myMinA']
		

		obj.addProperty("App::PropertyFloat","length","result")

		obj.addProperty("App::PropertyFloat","_a")._a=10
#		obj.addProperty("App::PropertyFloat","_b")._b=10
#		obj.addProperty("App::PropertyFloat","_c")._c=10
#		obj.addProperty("App::PropertyFloat","_d")._d=3

		obj.tangentModel=['all equal','1/3 distance','circle']
		# obj.tangentModel='1/3 distance'

		obj.method=[ 'Default',
			'simple',
			'Nelder-Mead' ,
			'Powell' ,
			'CG' ,
			'BFGS' ,
#*			'Newton-CG',
			'L-BFGS-B', 
			'TNC',
			'COBYLA',
			'SLSQP',
#			'trust-constr',
#*			'dogleg',
#			'trust-ncg',
#			'trust-exact',
#			'trust-krylov',
		]

		obj.method='Nelder-Mead'
		# obj.method='simple'
		obj.closed=False
		#obj.factor=10
		obj.alphaStart=0
		obj.alphaEnd=0
		obj.tangentModel='1/3 distance'
		obj._debug=True

		obj.mode='myMinA'

		self.restored=False
		self.executed=False

	def runMinLength(self,fp,ptsa,f=0.5):

		if fp.start<>0 or fp.end<>0:
			ptsa=ptsa[fp.start:fp.end]

		if fp.closed:
			ptsa += [ptsa[0]]

		pts=ptsa
		alphas=[1]*(len(ptsa))*2
		alphasKK=[1]*(len(ptsa))*2

		for i in range(1,len(ptsa)-2):
			v=ptsa[i+1]-ptsa[i-1]
			alphas[i]=np.arctan2(v.y,v.x)

#			print i
#			print ptsa[i+1]
#			print ptsa[i-1]
#			print v
#			print (i,alphas[i]*180/np.pi)
			#alphas[i]=np.pi*0.5
			alphasKK[i]=np.arctan2(v.y,v.x)
		
		fp.Proxy.loops=0
		fp.Proxy.time=time.time()

#		# diagramm
#		if 1: # in midi-bereich
#			import Plot
#			Plot.figure("directions of tangents")
#		else: # eigenes fenster
#			import Plot2 as Plot
#			Plot.figureWindow("Smooth Filter for Points")

#		t=range(len(ptsa)*2)
#		Plot.plot(t, alphas ,'points')
#		Plot.plot( t, alphas, 'filter2')
#		Plot.legend(True)
#		Plot.grid(True)



		def lengthMin(alpha,show=True):
			'''function to minimize'''

			la=len(ptsa)
			alphas=[0]*(la)*2

			if fp.betaOff:
				alphas[0:la]=alpha[0:la]
			else:
				alphas[0:2*la]=alpha[0:2*la]

			alpha=alphas

			fp.Proxy.loops += 1

			if alpha <> None:

				if fp.Proxy.loops == 1 :
					if fp.useStart:
						alpha[0]=fp.alphaStart*np.pi/18.0
						alpha[la]=fp.betaStart*np.pi/18.0

					if fp.useEnd:
						alpha[la-1]=fp.alphaEnd*np.pi/18.0
						alpha[2*la-1]=fp.betaEnd*np.pi/18.0

				if fp.closed:
					alpha[la-1]=alpha[0]
					alpha[2*la-1]=alpha[la]


				if fp.tangentModel=='1/3 distance':

					pts=[]
					kk=0.33 # 1/3 distance
					k=fp.factorList[0]*0.01*fp.factor
					k1=min((ptsa[-1]-ptsa[0]).Length*kk,k)

					for i in range(0,len(ptsa)):
						k=fp.factorList[i]*0.01*fp.factor
						k2=k1
						if i==len(ptsa)-1:
							k1=min((ptsa[0]-ptsa[i]).Length*kk,k)
						else:
							k1=min((ptsa[i+1]-ptsa[i]).Length*kk,k)

						if i <> 0:
							pts += [ ptsa[i]-FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k2,
								np.cos(alpha[la+i])*np.sin(alpha[i])*k2,np.sin(alpha[la+i])*k2) ]

						pts += [ptsa[i]]
						if i <>len(ptsa)-1:
							pts += [ ptsa[i]+FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k1,
								np.cos(alpha[la+i])*np.sin(alpha[i])*k1,np.sin(alpha[la+i])*k1) ]

				else:

					pts=[]
					for i in range(0,len(ptsa)):
						k=fp.factorList[i]*0.01*fp.factor
						#k=30
						if i <> 0:
							pts += [ ptsa[i]-FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k,
									np.cos(alpha[la+i])*np.sin(alpha[i])*k,np.sin(alpha[la+i])*k) ]
						pts += [ptsa[i]]
						if i <>len(ptsa)-1:
							pts += [ ptsa[i]+FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k,
									np.cos(alpha[la+i])*np.sin(alpha[i])*k,np.sin(alpha[la+i])*k) ]

			bc=Part.BSplineCurve()
			n=la-2
			ms=[4]+[3]*n+[4]

			bc.buildFromPolesMultsKnots(pts, ms, range(len(ms)), False,3)
			if show:
				fp.Shape=bc.toShape()
				if fp._showaux:
					fp.Shape=Part.Compound([bc.toShape(),Part.makePolygon(pts)])
				if fp._debug:
					Gui.updateGui()

			err=sum([abs(a+b) for a,b in zip(alphas,alphasKK)])

#			if fp.Proxy.loops %100 ==0 :
#				Plot.removeSerie(1)
#				Plot.plot(range(la*2), alpha ,'results')
	
			return bc.length()

		# main method 

		if fp.method=='Default':
			rc=minimize(lengthMin,alphas,tol=1.)
		elif fp.method=='simple':
			print "simple structure - no optimize"
			_ = lengthMin(alphas)
			
			return
		else:
			rc=minimize(lengthMin,alphas,method=fp.method,tol=fp.tol)

		print (fp.method,rc.success,rc.message,fp.Proxy.loops)
		print "Length ",round(fp.Shape.Edge1.Length,1)
		fp.length=fp.Shape.Edge1.Length
		fp.alphaList=list(rc.x)
		e=fp.Shape.Edge1
		bc=fp.Shape.Edge1.Curve

		size=bc.NbKnots+1
		anz=1000
		cc=np.array([bc.curvature(size*u/anz)**2 for u in range(anz+1)])

		print "Curvature mean ",round(cc.mean()*10**6,1)
		print "Curvature max ",round(cc.max()*10**6,1)
		
		print ("Radius",round(1/cc.mean(),1),round(1/cc.max(),1),round(1/cc.min(),1))


	def addExtraKnots(self,fp):

		bc=fp.Shape.Edge1.Curve
		for i in fp.extraKnots:
				print "extra knot ",i
				bc.insertKnot(i,3)

		af=Part.BSplineCurve()
		poles=bc.getPoles()
		ya=bc.getMultiplicities()
		af.buildFromPolesMultsKnots(poles,ya,range(len(ya)),False,3)
		fp.Shape=af.toShape()

	def onChanged(self,fp,prop):

		try: self.restored
		except: return
		if fp._noExecute: return
		oldpm=fp.Placement

		if prop in ["factor",'method','alphaStart','alphaEnd','betaEnd','betaStart','factorList','tangentModel'] or prop.startswith('_'):

			if fp.Shape == None or fp.path== None:
				return
			try:
				pts=fp.path.Points
			except:
				pts=[v.Point for v in fp.path.Shape.Vertexes]
			
			
			if fp.Wire> -1:
				pts=[v.Point for v in fp.path.Shape.Wires[fp.Wire].Vertexes]
			
			if fp.factor == 0:
				try:
					fp.factor=fp.path.Shape.BoundBox.DiagonalLength/len(pts)/4
				except:
					fp.factor=100

			if fp.mode=='myMinA':
				runMyMinA(fp,pts)
			else:
				self.runMinLength(fp,pts,fp.factor)

			self.addExtraKnots(fp)
			self.executed=True
			fp.Placement=oldpm

	def execute(self,fp):
		try:
			if self.executed:
				self.executed=False
				return
		except:
			pass
		if fp._noExecute: return
		self.onChanged(fp,'method')
		self.executed=False

def _minimumLengthBezierGUI():
	''' optimale kurve mit zwei Segmenten durch einen Punkt finden'''

	for s in Gui.Selection.getSelection():
		yy=App.ActiveDocument.addObject("Part::FeaturePython","MinLenBezier")
		MinLengthBezier(yy)
		ViewProvider(yy.ViewObject)

		yy.path=s
		# yy._noExecute=True
		yy._debug=False
		yy.alphaStart=15
		yy.alphaEnd=14
		yy.factor=50

		yy.ViewObject.LineColor=(.3,1.,0.0)


def _createMyMinAGUI():
	''' myMinA-Object erzeugen'''

	s=App.ActiveDocument.addObject('Sketcher::SketchObject','Sketch_forMyMinA')
	s.addGeometry(Part.LineSegment(App.Vector(-20,0,0),App.Vector(-10,10,0)),False)
	s.addGeometry(Part.LineSegment(App.Vector(-10,10,0),App.Vector(10,10,0)),False)
	s.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1)) 
	s.addGeometry(Part.LineSegment(App.Vector(10,10,0),App.Vector(20,-10,0)),False)
	s.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1)) 
	App.ActiveDocument.recompute()
	
	yy=App.ActiveDocument.addObject("Part::FeaturePython","MyMinA")
	MinLengthBezier(yy)
	ViewProvider(yy.ViewObject)
	yy.path=s
	yy.ViewObject.LineColor=(.3,1.,0.0)




'''
if 1:
	pts=[FreeCAD.Vector(0,0,0),
			FreeCAD.Vector(300,0,0),
			FreeCAD.Vector(500,200,300),
			FreeCAD.Vector(500,400,500),
			FreeCAD.Vector(500,400,800),
			]
	import Draft
	Draft.makeWire(pts)
'''



class ConstantCurvatureBezier(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","path")
#		obj.addProperty("App::PropertyInteger","factor").factor=30
#		obj.addProperty("App::PropertyFloat","alphaStart").alphaStart=-18
#		obj.addProperty("App::PropertyFloat","alphaEnd")
		obj.addProperty("App::PropertyFloat","tol").tol=0.1
#		obj.addProperty("App::PropertyBool","closed").closed=True
#		obj.addProperty("App::PropertyBool","useStart").useStart=True
#		obj.addProperty("App::PropertyBool","useEnd").useEnd=True
		obj.addProperty("App::PropertyEnumeration","method")
#		obj.addProperty("App::PropertyEnumeration","tangentModel")
#		obj.addProperty("App::PropertyFloatList","factorList").factorList=[100.]*20
		obj.addProperty("App::PropertyFloatList","alphaList","~calculated")
		obj.addProperty("App::PropertyInteger","start").start=0
		obj.addProperty("App::PropertyInteger","end").end=0

#		obj.addProperty("App::PropertyEnumeration","mode")
#		obj.mode=['minimal Lenght','Length','curvature']
		obj.addProperty("App::PropertyFloat","length","~calculated")
		
#		obj.addProperty("App::PropertyFloat","_a")._a=10
#		obj.addProperty("App::PropertyFloat","_b")._b=10
#		obj.addProperty("App::PropertyFloat","_c")._c=10
#		obj.addProperty("App::PropertyFloat","_d")._d=3

#		obj.addProperty("App::PropertyInteger","segment").segment=0
#		obj.tangentModel=['all equal','1/3 distance','circle']
		# obj.tangentModel='1/3 distance'
		obj.method=[ 'Default',
			'Nelder-Mead' ,
			'Powell' ,
			'CG' ,
			'BFGS' ,
#*			'Newton-CG',
			'L-BFGS-B', 
			'TNC',
			'COBYLA',
			'SLSQP',
#			'trust-constr',
#*			'dogleg',
#			'trust-ncg',
#			'trust-exact',
#			'trust-krylov',
		]
		obj.method='Nelder-Mead'
		obj._debug=True
		self.restored=False

	def runMinCurv(self,fp,ptsv):

		ptsa=ptsv
		fp.Proxy.loops=0
		fp.Proxy.time=time.time()

		def curvatureMinMax(alpha,show=True):

			a=alpha[0]
			b=alpha[1]
			pts=[	ptsa[0],
					ptsa[0]+(ptsa[1]-ptsa[0]).normalize()*(0.0001+abs(a)),
					ptsa[3]+(ptsa[2]-ptsa[3]).normalize()*(0.0001+abs(b)),
					ptsa[3]
				]
			fp.Proxy.loops += 1

			bc=Part.BSplineCurve()
			ms=[4]+[4]

			bc.buildFromPolesMultsKnots(pts, ms, range(len(ms)), False,3)
			if show:
				fp.Shape=bc.toShape()

			if fp._debug:
				Gui.updateGui()

			size=1.0
			anz=1000
			cc2=np.array([bc.curvature(size*u/anz) for u in range(anz+1)])
			fp.Proxy.cc2=cc2

			fp.alphaList=list(alpha)
#			print "!"
#			print (cc2.max(),cc2.min())
#			print (abs(cc2.max()-cc2.min()),cc2.mean())
#			print bc.length()
#			
#
#			
#			rc=abs(cc2.max()-cc2.min())*(1+cc2.mean())**np.pi#*bc.length()
#			print rc

			rc=abs(cc2.max()-cc2.min())*(1+cc2.mean())**np.pi*bc.length()

#			print rc
#			if fp.Proxy.loops>3000: 	
#				print "loops ende"
#				return 0 

			return rc *10**4

		#main method

		alphas=[0,0]
		if fp.method=='Default':
			rc=minimize(curvatureMinMax,alphas,tol=fp.tol)
		else:
			rc=minimize(curvatureMinMax,alphas,method=fp.method,tol=fp.tol)

		print (fp.method,fp.Proxy.loops,rc.success,rc.message)
		print (fp.Proxy.cc2.max(),fp.Proxy.cc2.min())

		curvatureMinMax(fp.alphaList)
		return fp.Shape


	def onChanged(self,fp,prop):
		try: self.restored
		except: return
		if fp._noExecute: return
		oldpm=fp.Placement

		if prop in ["_execute","factor",'method','alphaStart','alphaEnd','factorList','tangentModel','segment'] or prop.startswith('_'):
			if fp.Shape == None or fp.path== None:
				return

			try: # Draft Wire oder Draft BSpline
				pts=fp.path.Points
			except:
				pts=[v.Point for v in fp.path.Shape.Vertexes]

			try: # wenn es eine kurve ist
				pts=fp.path.Shape.Edge1.Curve.getPoles()
			except:
				pass

			if fp.start<>0 or fp.end<>0:
				pts=pts[3*fp.start:3*fp.end+1]

			ll=len(pts)/3
			shapes=[]
			lenn=0.0
			for li in range(ll):
				ptsa=pts[li*3:li*3+4]
				rc=self.runMinCurv(fp,ptsa)
				print ("runArc",li,rc)
				shapes +=[rc]
				lenn += rc.Length

			poles=[]
			for i,s in enumerate(shapes):
				if i==0: 
					poles= s.Edge1.Curve.getPoles()
				else:
					poles += s.Edge1.Curve.getPoles()[1:4]

#			fp.Shape=Part.makePolygon(poles)

			abc=Part.BSplineCurve()
			ms=[4]+[3]*i+[4]

			abc.buildFromPolesMultsKnots(poles, ms, range(len(ms)), False,3)
			fp.Shape=abc.toShape()
			fp.Placement=oldpm

			fp.length=lenn


	def execute(self,fp):
		try:
			if self.executed:
				self.executed=False
				return
		except:
			pass

		if fp._noExecute: return
		self.onChanged(fp,"_execute")

def _nearconstantCurvatureBezierGUI():
	''' optimale kurve mit minimaler kruemmungs aenderung'''

	for s in Gui.Selection.getSelection():
		yy=App.ActiveDocument.addObject("Part::FeaturePython","nearConstantCurvatureBezier")
		ConstantCurvatureBezier(yy)
		ViewProvider(yy.ViewObject)
		yy
	#	yy.start=3
	#	yy.end=4
		yy._debug=False
		yy.path=s
		yy.ViewObject.LineColor=(1.0,0.3,1.0)



def deactivateExecution():
	''' the execute method for the selection is deactivated'''
	for s in Gui.Selection.getSelection():
		try:
			s._noExecute=True
		except:
			pass

def  activateExecution():
	''' the execute method for the selection is activated'''
	for s in Gui.Selection.getSelection():
		try:
			s._noExecute=False
		except:
			pass

#------------------


def myMinA(pts):
	'''meine midimal-Methdoe A'''
#	a=FreeCAD.Vector(0,0,0)
#	b=FreeCAD.Vector(50,100,0)
#	c=FreeCAD.Vector(200,0,0)

	[a,b,c]=pts
	#Part.show(Part.makePolygon([a,b,c]))

	ptr=[]
	n=10
	ta=range(0,n+1)
	tb=range(0,n+1)
	for ia in ta:
		for ib in tb:
			iar=1.0*ia/(n+1)
			ibr=1.0*ib/(n+1)
			a1=a*iar+b*(1-iar)
			b1=c*ibr+b*(1-ibr)
			pts=[a,a1,b1,c]
			cu=Part.BSplineCurve()
			cu.buildFromPolesMultsKnots(pts,[4,4],[0,1],False,3)
			#print cu.length()
			s=[]
			for i in range(n+1):
				s += [cu.curvature(1.0*i/(n+1))]
			ss=(np.max(s)-np.min(s))/np.mean(s)**1.0
			ptr += [FreeCAD.Vector(iar,ibr,ss)]

	#Points.show(Points.Points(ptr))

	ptra=np.array(ptr)
	mm=np.min(ptra[:,2])
	mins=np.where(ptra[:,2] <= mm + 0.0)

	#for (ix,iy) in zip(mins[0],mins[1]):
	#	if iy==2:
	#		print (ix,iy,ptra[ix])

#	for ix in mins[0]:
#			print (ix,ptra[ix])

	ix=mins[0][0]

	iar,ibr,_= ptra[ix]
	a1=a*iar+b*(1-iar)
	b1=c*ibr+b*(1-ibr)
	pts=[a,a1,b1,c]
	cu=Part.BSplineCurve()
	cu.buildFromPolesMultsKnots(pts,[4,4],[0,1],False,3)
	#Part.show(cu.toShape())

	return pts


def runMyMinA(fp, pts):

		
#	for s in Gui.Selection.getSelection():
#		pts=[v.Point for v in s.Shape.Wires[0].Vertexes]
		s=fp

		label=s.Label+"_curve"

		debug=0

		import numpy as np

		def schnittpunkt(pts):

			a = np.array ( ( (pts[0].x-pts[1].x, pts[3].x-pts[2].x), 
								(pts[0].y-pts[1].y, pts[3].y-pts[2].y))) 
								
			b = np.array ( (pts[3].x-pts[1].x, pts[3].y-pts[1].y) )
			t, s = np.linalg.solve(a,b)
		#	print pts
		#	print (t,s)
		#	print pts[0]*t+pts[1]*(1-t)
		#	print pts[2]*s+pts[3]*(1-s)
			return pts[0]*t+pts[1]*(1-t)



		def makeSimpleCurve(pts):
			
#			print "makeSimpleCurve"
#			print pts

			pr=[]
			#print len(pts)
			if len(pts)<=3:
				pr=pts
				#Draft.makeWire(pr)
				return []
			for i in range(len(pts)-3):
		#		print i
				sp=schnittpunkt([pts[i+1],pts[i+1]+pts[i]-pts[i+2],pts[i+2],pts[i+2]+pts[i+3]-pts[i+1]])
				k=0.9
				k=0.5
				pr += myMinA([pts[i+1],sp,pts[i+2]])[0:3]
	#			pr += pts[i+1],k*sp+(1-k)*pts[i+1],k*sp+(1-k)*pts[i+2]

			pr += [pts[i+2]]


			a=len(pr)
			af=Part.BSplineCurve()
			ya=[4]+[3]*((a-4)/3)+[4]
			af.buildFromPolesMultsKnots(pr,ya,range(len(ya)),False,3)
			if debug:
				Part.show(af.toShape())
			# Draft.makeWire(pr)
			return pr

		def makeLineCurve(pts,mode='' ):
			
#			print ("Make Line",mode)
#			print pts

			ff=0.2
			if mode=='start':
				k=(pts[1]-pts[0]).Length *ff
				pr=[pts[0],pts[0]+(pts[1]-pts[0]).normalize()*k,pts[1]+(pts[0]-pts[2]).normalize()*k,pts[1]]

			elif mode=='end':
				k=(pts[1]-pts[2]).Length *ff
				pr=[pts[1],pts[1]+(pts[2]-pts[0]).normalize()*k,pts[2]+(pts[1]-pts[2]).normalize()*k,pts[2]]

			else:
				k=(pts[2]-pts[1]).Length *ff
				pr=[pts[1],pts[1]+(pts[2]-pts[0]).normalize()*k,pts[2]+(pts[1]-pts[3]).normalize()*k,pts[2]]

			a=len(pr)
			af=Part.BSplineCurve()
			ya=[4]+[3]*((a-4)/3)+[4]
			af.buildFromPolesMultsKnots(pr,ya,range(len(ya)),False,3)
			if debug:
				Part.show(af.toShape())
			return pr


		print "Loop---------------------------"
		ll=len(pts)
		if ll<3:
			print "brauche wenigstens 3 punkte"
			print "ABBRuch"
			return

		j=0
		d=pts[j+1]-pts[j]
		direct=np.arctan2(d.x,d.y)
		d2=pts[j+2]-pts[j+1]
		direct2=np.arctan2(d2.x,d2.y)
		

		start= -1 if  direct-direct2>0 else  1
		anfang=0

		pr=[]
		rc=makeLineCurve(pts[0:3],mode='start')
		pr += rc

		j=1
		while j<ll-2:
			d=pts[j+1]-pts[j]
			direct=np.arctan2(d.x,d.y)
			d2=pts[j+2]-pts[j+1]
			direct2=np.arctan2(d2.x,d2.y)
			dd=direct-direct2
#			print ("Richtung Punkt           ",pts[j+1]) 
#			print "start ",start
			if direct>0:
				if direct2<direct and direct2>direct-np.pi: 
					dd=-1
#					print ("A",j,direct,direct2,dd)
				else: 
					dd=1
#					print ("B",j,direct,direct2,dd)
			else:
				if (direct2>direct and direct2<np.pi+direct) :
					dd=1
#					print ("C",j,direct,direct2,dd)
				else: 
					dd=-1
#					print ("D",j,direct,direct2,dd)

			if  dd*start < 0:
				print ("Ende",j)
				start=dd
				rc=makeSimpleCurve(pts[anfang:j+2])
				pr += rc[1:]
				anfang=j
				rc=makeLineCurve(pts[j-1:j+3])
				pr += rc[1:]
			else:
				j += 1
				# start=direct

		rc=makeSimpleCurve(pts[anfang:j+2])
		pr += rc[1:]
		rc=makeLineCurve(pts[-3:],mode='end')
		pr += rc[1:]


		a=len(pr)
		af=Part.BSplineCurve()
		ya=[4]+[3]*((a-4)/3)+[4]
		af.buildFromPolesMultsKnots(pr,ya,range(len(ya)),False,3)
		fp.Shape=af.toShape()
		#App.ActiveDocument.ActiveObject.Label=label






#---------------------
def A():
	''' polefeld in andrere richtung aufziehen'''
	polar=[]
	for s in Gui.Selection.getSelection():
		polar +=[s.Shape.Edge1.Curve.getPoles()]
	polar=np.array(polar).swapaxes(0,1)
	for pts in polar:
		ptsa=[FreeCAD.Vector(p[0],p[1],p[2])  for p in pts]
		Part.show(Part.makePolygon(ptsa))



def B():
	'''flaeche aus polefeld selbst berechenn'''
	polsarr=[]
	cc=Gui.Selection.getSelection()[0]
	for l in cc .Links:
		pols=l.Shape.Edge1.Curve.getPoles()
		polsarr += [pols]
	
	poles=np.array(polsarr)
	print poles.shape
	b,a,_=poles.shape
	af=Part.BSplineSurface()
	ya=[4]+[3]*((a-4)/3)+[4]
	yb=[4]+[3]*((b-4)/3)+[4]
	db=3
	print ya
	print yb
	af.buildFromPolesMultsKnots(poles, 
				yb,ya,
				range(len(yb)),range(len(ya)),
				False,False,db,3)
	Part.show(af.toShape())
