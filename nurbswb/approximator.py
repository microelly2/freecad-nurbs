# -*- coding: utf-8 -*-
'''approximate  a point cloud by a bezier curve
#-------------------------------------------------
#-- 
#--
#-- microelly 2018  0.1
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

from scipy import signal


def AA():
	'''dummy method for testing'''
	print "AA-nip"

def BB():
	'''dummy method for testing'''
	print "BB-nip"

def getPart(name="hugo"):
	'''objekt bereitstellen bzw. anlegen'''

	obj=FreeCAD.ActiveDocument.getObject(name)
	if obj== None:
		obj=FreeCAD.ActiveDocument.addObject("Part::Feature",name)
	return obj


# diagramm fuer filter nur einmal am anfang zeigen
diagram=False

def runfilt(t,xn,degree=2,lowfilt=0.005):

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

def runY(obj,bo=None):

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



class Apo2(FeaturePython):
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


	def onChanged(self, obj, prop):
		if not hasattr(obj,"active"): return
		if prop in  ['count','degree','lowfilter','threshold']:
			runY(obj)


# fuer eine pointcloud und einer Startkurve wird eine BSpline-Approximation berechnet
# die stoehrungen werden mit scipy.signal.filtfilt entfernt
# als amplitude wird die abweichung von der vorgeschlagenen kurve genutzt

def createApo():
#	points=App.ActiveDocument.Points
#	start=App.ActiveDocument.Sketch

	[points,start]= Gui.Selection.getSelection()
	name=points.Name+"_from_"+start.Name

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
	Apo2(a,name,points,start)
	ViewProvider(a.ViewObject)
	return a



def smoothPointcloud():
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
	mikigui.part=createApo()
	mikigui.run()
	return mikigui

##\endcond


# laden der punkte aus einem bild - das bild muss 
# mit methoden der reconstruction wb nachbearbeitet werden



import nurbswb.pyob
from nurbswb.pyob import  FeaturePython,ViewProvider

class ImagePoints(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyFile","image")
		obj.addProperty("App::PropertyInteger","min").min=150
		obj.addProperty("App::PropertyInteger","max").max=1000
		obj.addProperty("App::PropertyIntegerList","params").params=[1,1,1,1]

	def execute(self,obj):
		import Points
		from scipy import misc

		face = misc.imread(obj.image)

		face2=obj.params[0]*face[:,:,0]+obj.params[1]*face[:,:,1]+obj.params[2]*face[:,:,2]
		(uc,vc)=face2.shape

		pts=[]
		for u in range(uc):
			for v in range(vc):
				if face2[u,v] >obj.min and face2[u,v] < obj.max:
					pts += [FreeCAD.Vector(v,u,face2[u,v]*obj.params[3])]

		obj.Points=Points.Points(pts)


def loadPointcloudfromImage():
	''' bild datei laden'''

	fn='/home/thomas/Downloads/Profil-Punktewolke3D.png'
	yy=App.ActiveDocument.addObject("Points::FeaturePython","ImagePoints")
	ImagePoints(yy)
	yy.image=fn
	ViewProvider(yy.ViewObject)


#

import scipy
from scipy.optimize import minimize
import numpy as np


class Approx2seg(FeaturePython):
	''' gegeben 7 Punkte Spline, finde optimale Kurve durch Mittelpunkt, durch Endpunkt und Endtangenten'''

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","path","source")
		obj.addProperty("App::PropertyInteger","factor","config").factor=30
		obj.addProperty("App::PropertyFloat","alphaStart","config")#.alphaStart=-18
		obj.addProperty("App::PropertyFloat","alphaEnd","config")
		obj.addProperty("App::PropertyFloat","betaStart","config")#.alphaStart=-18
		obj.addProperty("App::PropertyFloat","betaEnd","config")

		
		obj.addProperty("App::PropertyFloat","tol","approx").tol=0.1
		obj.addProperty("App::PropertyBool","closed").closed=True
		obj.addProperty("App::PropertyBool","useStart","config").useStart=True
		obj.addProperty("App::PropertyBool","useEnd","config").useEnd=True
		obj.addProperty("App::PropertyEnumeration","method","approx")
		obj.addProperty("App::PropertyEnumeration","tangentModel","approx")
		obj.addProperty("App::PropertyFloatList","factorList").factorList=[100.]*20
		obj.addProperty("App::PropertyFloatList","alphaList","result")
		obj.addProperty("App::PropertyInteger","start","source").start=0
		obj.addProperty("App::PropertyInteger","end","source").end=0

		obj.addProperty("App::PropertyEnumeration","mode","approx")
		obj.mode=['minimal Lenght','Length','curvature']

		obj.addProperty("App::PropertyFloat","length","result")

#		obj.addProperty("App::PropertyFloat","_a")._a=10
#		obj.addProperty("App::PropertyFloat","_b")._b=10
#		obj.addProperty("App::PropertyFloat","_c")._c=10
#		obj.addProperty("App::PropertyFloat","_d")._d=3

		obj.tangentModel=['all equal','1/3 distance','circle']
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
		obj.closed=False
		obj.factor=200

	def execute(self,obj):
		pass


	def runTT(self,fp,ptsa,f=0.5):

		if fp.start<>0 or fp.end<>0:
			ptsa=ptsa[fp.start:fp.end]

		if fp.closed:
			ptsa += [ptsa[0]]

		pts=ptsa
		alphas=[1]*(len(ptsa))*2

		for i in range(1,len(ptsa)-2):
			v=ptsa[i+1]-ptsa[i-1]
			alphas[i]=np.arctan2(v.y,v.x)
		
		fp.Proxy.loops=0
		fp.Proxy.time=time.time()


		def ff(alpha,show=True):
			'''function to minimize'''

			la=len(ptsa)
			alphas=[0]*(la)*2

			alphas[0:2*la]=alpha[0:2*la]
			alpha=alphas
			fp.Proxy.loops += 1

			if alpha <> None:

				if fp.useStart:
					alpha[0]=fp.alphaStart*np.pi/18.0

				if fp.useEnd:
					alpha[la-1]=fp.alphaEnd*np.pi/18.0

				if fp.closed:
					alpha[la-1]=alpha[0]

				pts=[]
				for i in range(0,len(ptsa)):
					k=fp.factorList[i]*0.01*fp.factor
					if i <> 0:
						pts += [ ptsa[i]-FreeCAD.Vector(np.cos(alpha[i])*k,np.sin(alpha[i])*k) ]
					pts += [ptsa[i]]
					if i <>len(ptsa)-1:
						pts += [ptsa[i]+FreeCAD.Vector(np.cos(alpha[i])*k,np.sin(alpha[i])*k)]

				if fp.tangentModel=='1/3 distance':

					pts=[]
					kk=0.33 # 1/3 distance
					k=fp.factorList[i]*0.01*fp.factor
					k1=min((ptsa[-1]-ptsa[0]).Length*kk,k)

					for i in range(0,len(ptsa)):
						k=fp.factorList[i]*0.01*fp.factor
						k2=k1
						if i==len(ptsa)-1:
							k1=min((ptsa[0]-ptsa[i]).Length*kk,k)
						else:
							k1=min((ptsa[i+1]-ptsa[i]).Length*kk,k)

						if i <> 0:
							pts += [ ptsa[i]+FreeCAD.Vector(np.cos(alpha[i])*k2,np.sin(alpha[i])*k2) ]
						pts += [ptsa[i]]
						if i <>len(ptsa)-1:
							pts += [ptsa[i]-FreeCAD.Vector(np.cos(alpha[i])*k1,np.sin(alpha[i])*k1)]

			bc=Part.BSplineCurve()
			n=la-2
			ms=[4]+[3]*n+[4]

			bc.buildFromPolesMultsKnots(pts, ms, range(len(ms)), False,3)
			if show:
				fp.Shape=bc.toShape()
				if fp._showaux:
					fp.Shape=Part.Compound([bc.toShape(),Part.makePolygon(pts)])

			return bc.length()


		if fp.method=='Default':
			rc=minimize(ff,alphas,tol=1.)
		else:
			rc=minimize(ff,alphas,method=fp.method,tol=fp.tol)

		print (fp.method,rc.success,rc.message)
		print "Length ",round(fp.Shape.Edge1.Length,1)
		fp.length=fp.Shape.Edge1.Length
		e=fp.Shape.Edge1
		bc=fp.Shape.Edge1.Curve

		size=bc.NbKnots
		size=4.0
		anz=10
		cc=np.array([bc.curvature(size*u/anz)**2 for u in range(anz+1)])

		print "Curvature ",round(cc.mean()*10**6,1)
		fp.alphaList=list(rc.x)


	def runTT3D(self,fp,ptsa,f=0.5):

		if fp.start<>0 or fp.end<>0:
			ptsa=ptsa[fp.start:fp.end]

		if fp.closed:
			ptsa += [ptsa[0]]

		pts=ptsa
		alphas=[1]*(len(ptsa))*2

		for i in range(1,len(ptsa)-2):
			v=ptsa[i+1]-ptsa[i-1]
			alphas[i]=np.arctan2(v.y,v.x)
		
		fp.Proxy.loops=0
		fp.Proxy.time=time.time()


		def ff(alpha,show=True):
			'''function to minimize'''

			la=len(ptsa)
			alphas=[0]*(la)*2
			alphas=[1]*(la)*2

			alphas[0:2*la]=alpha[0:2*la]
			#alphas[0:la]=alpha[0:la]
			
			alpha=alphas
			fp.Proxy.loops += 1

			if alpha <> None:

				if fp.useStart:
					alpha[0]=fp.alphaStart*np.pi/18.0
					alpha[la]=fp.betaStart*np.pi/18.0

				if fp.useEnd:
					alpha[la-1]=fp.alphaEnd*np.pi/18.0
					alpha[2*la-1]=fp.betaEnd*np.pi/18.0

				if fp.closed:
					alpha[la-1]=alpha[0]
					alpha[2*la-1]=alpha[la]

				pts=[]
				for i in range(0,len(ptsa)):
					k=fp.factorList[i]*0.01*fp.factor
					if i <> 0:
						pts += [ ptsa[i]-FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k,
								np.cos(alpha[la+i])*np.sin(alpha[i])*k,np.sin(alpha[la+i])*k) ]
					pts += [ptsa[i]]
					if i <>len(ptsa)-1:
						pts += [ ptsa[i]+FreeCAD.Vector(np.cos(alpha[la+i])*np.cos(alpha[i])*k,
								np.cos(alpha[la+i])*np.sin(alpha[i])*k,np.sin(alpha[la+i])*k) ]

				if fp.tangentModel=='1/3 distance':

					pts=[]
					kk=0.33 # 1/3 distance
					k=fp.factorList[i]*0.01*fp.factor
					k1=min((ptsa[-1]-ptsa[0]).Length*kk,k)

					for i in range(0,len(ptsa)):
						k=fp.factorList[i]*0.01*fp.factor
						k2=k1
						if i==len(ptsa)-1:
							k1=min((ptsa[0]-ptsa[i]).Length*kk,k)
						else:
							k1=min((ptsa[i+1]-ptsa[i]).Length*kk,k)

						if i <> 0:
							pts += [ ptsa[i]+FreeCAD.Vector(np.cos(alpha[i])*k2,np.sin(alpha[i])*k2) ]
						pts += [ptsa[i]]
						if i <>len(ptsa)-1:
							pts += [ptsa[i]-FreeCAD.Vector(np.cos(alpha[i])*k1,np.sin(alpha[i])*k1)]

			bc=Part.BSplineCurve()
			n=la-2
			ms=[4]+[3]*n+[4]

			bc.buildFromPolesMultsKnots(pts, ms, range(len(ms)), False,3)
			if show:
				fp.Shape=bc.toShape()
				if fp._showaux:
					fp.Shape=Part.Compound([bc.toShape(),Part.makePolygon(pts)])

			return bc.length()


		if fp.method=='Default':
			rc=minimize(ff,alphas,tol=1.)
		else:
			rc=minimize(ff,alphas,method=fp.method,tol=fp.tol)

		print (fp.method,rc.success,rc.message)
		print "Length ",round(fp.Shape.Edge1.Length,1)
		fp.length=fp.Shape.Edge1.Length
		e=fp.Shape.Edge1
		bc=fp.Shape.Edge1.Curve

		size=bc.NbKnots
		size=5.0
		anz=1000
		cc=np.array([bc.curvature(size*u/anz)**2 for u in range(anz+1)])

		print "Curvature mean ",round(cc.mean()*10**6,1)
		print "Curvature max ",round(cc.max()*10**6,1)
		fp.alphaList=list(rc.x)


	def onChanged(self,fp,prop):
		if fp.Shape==None: return
		if prop in ["factor",'method','alphaStart','alphaEnd','betaEnd','betaStart','factorList','tangentModel'] or prop.startswith('_'):
			if fp.Shape == None or fp.path== None:
				return

			try:
				pts=fp.path.Points
			except:
				pts=[v.Point for v in fp.path.Shape.Vertexes]

			if 0:
				pts=[FreeCAD.Vector(0,0,0),
				FreeCAD.Vector(100,0,0),
				FreeCAD.Vector(200,100,100),
				FreeCAD.Vector(200,200,100),
				FreeCAD.Vector(200,400,200),
				]

			#self.runTT(fp,pts,fp.factor)
			self.runTT3D(fp,pts,fp.factor)

	def execute(self,fp):
		self.onChanged(fp,'method')

def minimumLengthBezier():
	''' optimale kurve mit zwei Segmenten durch einen Punkt finden'''

	yy=App.ActiveDocument.addObject("Part::FeaturePython","MinLenBezier")
	Approx2seg(yy)
	
	ViewProvider(yy.ViewObject)
	yy.path=Gui.Selection.getSelection()[0]
	yy.Proxy.onChanged(yy,"factor")
	yy.ViewObject.LineColor=(1.0,0.3,0.0)

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



class CCB(FeaturePython):

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
		obj.addProperty("App::PropertyFloatList","alphaList")
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

	def runArc(self,fp,ptsv):

		ptsa=ptsv
		fp.Proxy.loops=0
		fp.Proxy.time=time.time()

		def ff(alpha,show=True):

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
			size=1.0
			anz=1000
			cc2=np.array([bc.curvature(size*u/anz) for u in range(anz+1)])
			fp.Proxy.cc2=cc2

			fp.alphaList=list(alpha)
			rc=abs(cc2.max()-cc2.min())*bc.length()
			# rc=abs(cc2.std())*bc.length()**(fp._a*0.1)
			return rc *10**4

		#main method

		alphas=[0,0]
		if fp.method=='Default':
			rc=minimize(ff,alphas,tol=fp.tol)
		else:
			rc=minimize(ff,alphas,method=fp.method,tol=fp.tol)

		print (fp.method,fp.Proxy.loops,rc.success,rc.message)
		print (fp.Proxy.cc2.max(),fp.Proxy.cc2.min())
		return fp.Shape



	def onChanged(self,fp,prop):
		if prop in ["factor",'method','alphaStart','alphaEnd','factorList','tangentModel','segment'] or prop.startswith('_'):
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
				rc=self.runArc(fp,ptsa)
				print ("runArc",li,rc)
				shapes +=[rc]
				lenn += rc.Length

			fp.Shape=Part.Compound(shapes)
			fp.length=lenn


	def execute(self,fp):
		self.onChanged(fp,'method')


def nearconstantCurvatureBezier():
	''' optimale kurve mit minimaler kruemmung aenderung'''

	yy=App.ActiveDocument.addObject("Part::FeaturePython","nearConstantCurvatureBezier")
	CCB(yy)
	
	ViewProvider(yy.ViewObject)
	yy.path=Gui.Selection.getSelection()[0]
	yy.Proxy.onChanged(yy,"factor")
	yy.ViewObject.LineColor=(1.0,0.3,1.0)





