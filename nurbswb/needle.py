# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create a needle
#--
#-- microelly 2016 v 0.4
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import Part,Mesh,Draft

import numpy as np

def Myarray2NurbsD3(arr,label="MyWall"):

	cylinder=True

	pst=np.array(arr)
	NbVPoles,NbUPoles,_t1 =pst.shape

	ps=[[FreeCAD.Vector(pst[v,u,0],pst[v,u,1],pst[v,u,2]) for u in range(NbUPoles)] for v in range(NbVPoles)]

	kv=[1.0/(NbVPoles-3)*i for i in range(NbVPoles-2)]
	mv=[4] +[1]*(NbVPoles-4) +[4]

	if cylinder:
		ku=[1.0/(NbUPoles-1)*i for i in range(NbUPoles)]
		mu=[2]+[1]*(NbUPoles-2)+[2]
	else:
		ku=[1.0/(NbUPoles-3)*i for i in range(NbUPoles-2)]
		mu=[4]+[1]*(NbUPoles-4)+[4]

	bs=Part.BSplineSurface()
	bs.buildFromPolesMultsKnots(ps, mv, mu, kv, ku, False,cylinder ,3,3)

	fa=bs.uIso(0)
	sha1 = Part.Wire(fa.toShape())
	sha = Part.Face(sha1)

	fb=bs.uIso(1)
	shb1 = Part.Wire(fb.toShape())
	shb = Part.Face(shb1)

	sh=bs.toShape()

	if 0:
		sp=App.ActiveDocument.addObject("Part::Spline",label)
		sp.Shape=sh
		sp.ViewObject.ControlPoints=True
		sp.ViewObject.hide()

	sol=Part.Solid(Part.Shell([sha.Face1,shb.Face1,sh.Face1]))

	return (sol,bs)


def toUVMesh(bs, uf=5, vf=5):
		uc=uf*bs.NbUPoles
		vc=vf*bs.NbVPoles
		ss=[]
		for x in range(uc+1): 
			for y in range(vc+1): 
				ss.append(bs.value(1.0/uc*x,1.0/vc*y))

		mm=np.array(ss)[:,2].max()
		#add closing points
		ss.append(FreeCAD.Vector(0,0,0))
		ss.append(FreeCAD.Vector(0,0,mm))

		topfaces=[]
		x=0
		for y in range(vc): 
			topfaces.append(((vc+1)*x+y,(vc+1)*x+y+1,len(ss)-2))
		x=uc
		for y in range(vc): 
			topfaces.append(((vc+1)*x+y,(vc+1)*x+y+1,len(ss)-1))

#		t=Mesh.Mesh((ss,topfaces))
#		Mesh.show(t)
#		App.ActiveDocument.ActiveObject.ViewObject.Lighting="Two side"



		faces=[]
		for x in range(uc): 
			for y in range(vc): 
				#if max((vc+1)*x+y,(vc+1)*x+y+1,(vc+1)*(x+1)+y,(vc+1)*x+y+1,(vc+1)*(x+1)+y+1,(vc+1)*(x+1)+y)<50000: 
				#if len(faces)<100000:
					faces.append(((vc+1)*x+y,(vc+1)*x+y+1,(vc+1)*(x+1)+y))
					faces.append(((vc+1)*x+y+1,(vc+1)*(x+1)+y+1,(vc+1)*(x+1)+y))

		# print ss
		# print faces
		FreeCAD.Console.PrintMessage(str(("size of the mesh:",uc,vc))+"\n")
		FreeCAD.Console.PrintMessage(str(("number of points" ,len(ss)))+"\n")
		FreeCAD.Console.PrintMessage(str(("faces:",len(faces)))+"\n")



		if len(faces)<100000:
			t=Mesh.Mesh((ss,faces))
			Mesh.show(t)
			App.ActiveDocument.ActiveObject.ViewObject.Lighting="Two side"
			App.ActiveDocument.ActiveObject.ViewObject.DisplayMode = u"Wireframe"
			App.ActiveDocument.ActiveObject.ViewObject.LineColor = (.70,.00,0.00)
			FreeCAD.Console.PrintMessage(str(t))
			return App.ActiveDocument.ActiveObject
		else:
			raise Exception("big mesh not implemented")

			ks=len(faces)//100000
			for i in range(ks+1):
				t=Mesh.Mesh((ss,faces[i*100000:(i+1)*100000]))
				Mesh.show(t)
				App.ActiveDocument.ActiveObject.ViewObject.Lighting="Two side"
				App.ActiveDocument.ActiveObject.ViewObject.DisplayMode = u"Wireframe"
				App.ActiveDocument.ActiveObject.ViewObject.LineColor = (.70,.00,0.00)
				FreeCAD.Console.PrintMessage(str(t))

		return t




def scaleAndExtrude(profile,scaler=None,path=None):
	c=np.array(profile)
	if scaler == None: scaler= [1]*10
	if path == None: path= [[0,0,10*i] for i in range(len(scaler))]

	assert(len(path)==len(scaler))
	#poles=np.array([c*scaler[i]]+path[i] for i in  range(len(path))])
	poles=np.array([c*[scaler[i,0],scaler[i,0],scaler[i,1]]+path[i] for i in  range(len(path))])
	return poles

def twist(profile,twister):
	c=np.array(profile)
	vc,uc,_t=c.shape
	# assert len(twister) == c.shape[0]
	rc=[]
	for v in range(vc):
		cv=[]
		for u in range(uc):
			sp=c[v,u]
			tw=twister[v]*np.pi/180 
			tpp=[np.cos(tw)*sp[0] - np.sin(tw)*sp[1],np.sin(tw)*sp[0] + np.cos(tw)*sp[1],sp[2]]
			cv.append(tpp)
		c[v]=cv
	return c





#---------------------
# daten aus sheet







def cellname(col,row):
	#limit to 26
	if col>90-64:
		raise Exception("not implement")
	char=chr(col+64)
	cn=char+str(row)
	return cn



def npa2ssa(arr,spreadsheet,c1,r1):
	''' write 2s array into spreadsheet '''
	ss=spreadsheet
	arr=np.array(arr)
	try:
		rla,cla=arr.shape
	except:
		rla=arr.shape[0]
		cla=0
	c2=c1+cla
	r2=r1+rla
	if cla==0:
		for r in range(r1,r2):
			cn=cellname(c1,r)
			ss.set(cn,str(arr[r-r1]))
	else:
		for r in range(r1,r2):
			for c in range(c1,c2):
				cn=cellname(c,r)
	#			print (cn,c,r,)
				ss.set(cn,str(arr[r-r1,c-c1]))

def gendata(ss):
	print ("gendata",ss.Label)

	# Form der Nadel als Parameter 

	# profil blatt
	curve=[[0,0,0],[5,-5,10],[30,-10,-0],[20,-5,-10],[0,10,0],[-20,-5,-0],[-30,-10,0],[-5,-5,0]]

	# backbone
	bb= [[0,0,0],[10,5,20],[5,-5,40],[5,-10,170],[-3,20,300]]

	#scaling
	sc=[[1,0],[1.5,1],[1,-5],[0.7,1],[3.05,0]]
	sc=[[1,0],[1,0],[1,0],[1,0],[3,0]]

	#twist along the z-axis
	twister=[0,30,70,-20,20]

	npa2ssa(curve,ss,2,3)
	npa2ssa(bb,ss,7,3)
	npa2ssa(sc,ss,10,3)
	npa2ssa(twister,ss,12,3)
	ss.set('B1',str(len(curve)))
	ss.set('H1',str(len(bb)))
	App.activeDocument().recompute()


def ssa2npa(spreadsheet,c1,r1,c2,r2,default=None):
	''' create array from table'''

	c2 +=1
	r2 +=1

	ss=spreadsheet
	z=[]
	for r in range(r1,r2):
		for c in range(c1,c2):
			cn=cellname(c,r)
			# print cn
			try:
				v=ss.get(cn)
				z.append(ss.get(cn))
			except:
				z.append(default)

	z=np.array(z)
#	print z
	ps=np.array(z).reshape(r2-r1,c2-c1)
	return ps


if 0 and __name__=='__main__':

	App.ActiveDocument=None
	Gui.ActiveDocument=None
	FreeCAD.open(u"/home/thomas/Schreibtisch/nadel_daten.fcstd")
	App.setActiveDocument("nadel_daten")
	App.ActiveDocument=App.getDocument("nadel_daten")
	Gui.ActiveDocument=Gui.getDocument("nadel_daten")





class PartFeature:
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
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj



class Needle(PartFeature):
	def __init__(self, obj,uc=5,vc=5):
		PartFeature.__init__(self, obj)

		self.Type="Needle"
		self.TypeId="Needle"

		for l in ['Mesh','Backbone','Profile','RibCage','RibTemplate','Spreadsheet']:
			obj.addProperty("App::PropertyLink",l,l)
			obj.addProperty("App::PropertyBool","use" + l ,l)
			setattr(obj,"use"+l,False)

		obj.addProperty("App::PropertyBool","noExecute" ,"Base")
		obj.addProperty("App::PropertyLink","Meridians","RibCage")
		obj.addProperty("App::PropertyInteger","RibCount","RibCage").RibCount=10
		obj.addProperty("App::PropertyInteger","MeshUCount","Mesh").MeshUCount=5
		obj.addProperty("App::PropertyInteger","MeshVCount","Mesh").MeshVCount=5

		obj.ViewObject.LineColor=(1.0,0.0,1.0)
		obj.addProperty("App::PropertyLink","ribtemplateSource","Spreadsheet")
		obj.addProperty("App::PropertyLink","backboneSource","Spreadsheet")
		obj.addProperty("App::PropertyBool","externSourcesOff" ,"Spreadsheet")

	def onChanged(self, fp, prop):
		
		if prop == 'useSpreadsheet':
			if fp.useSpreadsheet:
				if fp.Spreadsheet == None:
					fp.Spreadsheet = App.activeDocument().addObject('Spreadsheet::Sheet','Spreadsheet')
			return
		if prop in ["Shape", 'Spreadsheet']: return
		print ("onChanged",prop)


	def execute(proxy,obj):
		print("execute ")
		if obj.noExecute: return
		try: 
			if proxy.lock: return
		except:
			print("except proxy lock")
		proxy.lock=True
		print("myexecute")
		proxy.myexecute(obj)
		proxy.lock=False

	def myexecute(proxy,obj):

		ss=obj.Spreadsheet


		if obj.ribtemplateSource <> None and not obj.externSourcesOff:
			cs=obj.ribtemplateSource.Shape.Edge1.Curve
			curve=cs.getPoles()
			cl=len(curve)
			npa2ssa(curve,ss,2,3)
			print "update curve",curve
		else:
			cl=int(ss.get('B1'))
			curve=ssa2npa(ss,2,3,4,3+cl-1)


		if obj.backboneSource <> None and not obj.externSourcesOff:
			cs=obj.backboneSource.Shape.Edge1.Curve
			bb=cs.getPoles()
			bl=len(bb)
			npa2ssa(bb,ss,7,3)
			print "update backbone",bb

		else:
			bl=int(ss.get('H1'))
			bb=ssa2npa(ss,7,3,9,3+bl-1)


		scaler=ssa2npa(ss,10,3,11,3+bl-1,default=1.0)
		twister=ssa2npa(ss,12,3,12,3+bl-1,default=0.0)

		poles= scaleAndExtrude(curve,scaler,bb)
		poles= twist(poles,twister)

		(nn,bs)=Myarray2NurbsD3(poles,"Nadelhuelle")
		obj.Shape=nn

		if obj.useBackbone: proxy.createBackbone(obj,bb)
		if obj.useRibTemplate: proxy.createRibTemplate(obj,curve)
		if obj.useRibCage: proxy.createRibCage(obj,bs)
		if obj.useMesh: proxy.createMesh(obj,bs)

	def createBackbone(proxy,obj,bb):
		if obj.Backbone == None:
			obj.Backbone=App.ActiveDocument.addObject('Part::Feature','Backbone')
		obj.Backbone.Shape=Part.makePolygon([FreeCAD.Vector(b) for b in bb])

		vob=obj.Backbone.ViewObject
		vob.LineColor=(0.,1.,1.)
		vob.LineWidth = 10.00

	def createRibTemplate(proxy,obj,curve):
		if obj.RibTemplate == None:
			obj.RibTemplate=App.ActiveDocument.addObject('Part::Feature','Rib template')
		obj.RibTemplate.Shape=Part.makePolygon([FreeCAD.Vector(c) for c in curve])

		vob=obj.RibTemplate.ViewObject
		vob.LineColor=(0.,1.,0.)
		vob.LineWidth = 10.00

	def createMesh(proxy,obj,bs):
			if obj.Mesh <> None:
				App.ActiveDocument.removeObject(obj.Mesh.Name)
			obj.Mesh=toUVMesh(bs,obj.MeshUCount,obj.MeshVCount)

	def createRibCage(proxy,obj,bs):
		ribs=[]
		rc=obj.RibCount
		for i in range(rc+1):
			f=bs.uIso(1.0/rc*i)
			ribs.append(f.toShape())
		comp=Part.Compound(ribs)
		if obj.RibCage == None:
			obj.RibCage=App.ActiveDocument.addObject('Part::Feature','Ribs')
		obj.RibCage.Shape=comp
		vob=App.ActiveDocument.ActiveObject.ViewObject
		vob.LineColor=(1.,1.,0.)
		vob.LineWidth = 10.00

		mers=[]
		for i,j in enumerate(bs.getVKnots()):
			f=bs.vIso(j)
			mers.append(f.toShape())
		comp=Part.Compound(mers)
		if obj.Meridians == None:
			obj.Meridians=App.ActiveDocument.addObject('Part::Feature','Meridians')
		obj.Meridians.Shape=comp
		vob=App.ActiveDocument.ActiveObject.ViewObject
		vob.LineColor=(1.,0.,0.4)
		vob.LineWidth = 10.00



def importCurves(obj):
	ss=obj.Spreadsheet
	print ss.Label
	if obj.ribtemplateSource <> None and not obj.externSourcesOff:
		cs=obj.ribtemplateSource.Shape.Edge1.Curve
		curve=cs.getPoles()
		cl=len(curve)
		npa2ssa(curve,ss,2,3)
		print "update curve",curve


	if obj.backboneSource <> None and not obj.externSourcesOff:
		cs=obj.backboneSource.Shape.Edge1.Curve
		bb=cs.getPoles()
		bl=len(bb)
		npa2ssa(bb,ss,7,3)
		print "update backbone",bb


#-----------------------------------------
# TEST CASE
#-----------------------------------------

if  __name__=='__main__':

	# test aus parametern
	import Draft
	import nurbswb
	import nurbswb.needle as needle
	reload( nurbswb.needle)

	try: App.closeDocument("Unnamed")
	except: pass

	App.newDocument("Unnamed")
	App.setActiveDocument("Unnamed")
	App.ActiveDocument=App.getDocument("Unnamed")
	Gui.ActiveDocument=Gui.getDocument("Unnamed")

	points=[FreeCAD.Vector(192.694291746,-129.634476444,0.0),FreeCAD.Vector(130.429397583,-0.657173752785,0.0),FreeCAD.Vector(-52.807308197,-112.73400116,0.0),FreeCAD.Vector(-127.525184631,-71.8170700073,0.0),FreeCAD.Vector(-205.801071167,-274.622741699,0.0),FreeCAD.Vector(28.1370697021,-262.169769287,0.0),FreeCAD.Vector(125.981895447,-187.451873779,0.0)]
	Draft.makeBSpline(points,closed=True,face=True,support=None)
	# BSpline

	points=[FreeCAD.Vector(-37.2293014526,1.68375661825e-08,0.28248746792),FreeCAD.Vector(132.959136963,6.57217134591e-06,110.262731687),FreeCAD.Vector(149.817367554,1.45151301104e-05,243.523458616),FreeCAD.Vector(-69.3403015137,2.18838984602e-05,367.150869505),FreeCAD.Vector(-182.531646729,2.7960740423e-05,469.103353635),FreeCAD.Vector(-256.549041748,5.67015768864e-05,951.294546262)]
	Draft.makeBSpline(points,closed=False,face=True,support=None)
	# Bspline001


	points=[FreeCAD.Vector(-73.5499812578,-192.458589192,0.0),FreeCAD.Vector(-35.2118430692,-245.401746512,0.0),FreeCAD.Vector(-148.400562353,-232.622317741,0.0),FreeCAD.Vector(-115.539281652,-172.376687886,0.0)]
	Draft.makeBSpline(points,closed=True,face=True,support=FreeCAD.ActiveDocument.getObject("BSpline"))
	# Bspline002

	points=[FreeCAD.Vector(-37.2293014526,1.68375661825e-08,-10),FreeCAD.Vector(132.959136963,6.57217134591e-06,110.262731687),FreeCAD.Vector(149.817367554,1.45151301104e-05,243.523458616),FreeCAD.Vector(-69.3403015137,2.18838984602e-05,367.150869505),FreeCAD.Vector(-182.531646729,2.7960740423e-05,469.103353635),FreeCAD.Vector(-256.549041748,5.67015768864e-05,1200)]
	Draft.makeBSpline(points,closed=False,face=True,support=None)
	# Bspline003

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","MyNeedle")
	n=needle.Needle(a)

	'''
	a.useBackbone=True
	a.useRibTemplate=True
	a.useRibCage=True
	a.useMesh=True
	'''
	a.useSpreadsheet=True


	ss=a.Spreadsheet
	needle.gendata(ss)

	a.ribtemplateSource=App.ActiveDocument.BSpline
	a.backboneSource=App.ActiveDocument.BSpline001

	App.activeDocument().recompute()

	vp=needle.ViewProvider(a.ViewObject)
	App.activeDocument().recompute()



	# zweiter koerper

	b=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","MyNeedle")
	bn=needle.Needle(b)


	'''
	b.useBackbone=True
	b.useRibTemplate=True
	b.useRibCage=True
	b.useMesh=True
	'''
	b.useSpreadsheet=True


	# b.Spreeadsheet=App.activeDocument().addObject('Spreadsheet::Sheet','huhu')
	bss=b.Spreadsheet
	needle.gendata(bss)

	b.ribtemplateSource=App.ActiveDocument.BSpline002
	b.backboneSource=App.ActiveDocument.BSpline003
	App.activeDocument().recompute()


	vp=needle.ViewProvider(b.ViewObject)


	Gui.SendMsgToActiveView("ViewFit")
	print "fertig"
	 


	needle.importCurves(a)
	needle.importCurves(b)
	
	App.activeDocument().recompute()
	App.activeDocument().recompute()

