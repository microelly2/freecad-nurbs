import numpy as np
import random


import nurbswb
from nurbswb.pyob import  FeaturePython,ViewProvider
from nurbswb.say import *
reload (nurbswb.pyob)

class Morpher(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","A")
		obj.addProperty("App::PropertyLink","B")
		obj.addProperty("App::PropertyFloat","factorA").factorA=10

	def myOnChanged(self,obj,prop):

		if prop in ["Shape"]:
			return

		try:
			obj.A.Shape,obj.B.Shape,obj.factorA
		except:
			return

		sfa=obj.A.Shape.Face1.Surface
		sfb=obj.B.Shape.Face1.Surface

		umsa,vmsa=sfa.getUMultiplicities(),sfa.getVMultiplicities()
		umsb,vmsb=sfb.getUMultiplicities(),sfb.getVMultiplicities()
		uksa,vksa=sfa.getUKnots(),sfa.getVKnots()
		uksb,vksb=sfb.getUKnots(),sfb.getVKnots()


		kbb=uksb[-1]
		kaa=uksa[-1]
		kbbv=vksb[-1]
		kaav=vksa[-1]

		# beide flaechen auf gleiche polanzahl bringen
		for (k,m) in zip(uksa,umsa)[1:-1]:
			kb=k*kbb/kaa
			sfb.insertUKnot(kb,m,0)

		for (k,m) in zip(vksa,vmsa)[1:-1]:
			kb=k*kbbv/kaav
			sfb.insertVKnot(kb,m,0)

		for (k,m) in zip(uksb,umsb)[1:-1]:
			kb=k*kaa/kbb
			sfa.insertUKnot(kb,m,0)

		for (k,m) in zip(vksb,vmsb)[1:-1]:
			kb=k*kaav/kbbv
			sfa.insertVKnot(kb,m,0)


		pa=np.array(sfa.getPoles())
		pb=np.array(sfb.getPoles())

		print pa.shape
		print pb.shape
		pb2=npb.copy()
		a,b=pb.shape[0:1]

		if 0:
			ppa=pa.swapaxes(0,1)
			ppa=ppa[::-1]
			pa=ppa.swapaxes(0,1)
			pb=pb[::-1] 
			print pa.shape
			print pb.shape
			print "Ecken 0 0"
			print pa[0,0]
			print pb[0,0]
			print "Eckebn -1 -1 "
			print pa[-1,-1]
			print pb[-1,-1]

			print "Eckebn 0 1"
			print pa[0,-1]
			print pb[0,-1]
			print "Eckebn 1 0"
			print pa[-1,0]
			print pb[-1,0]


		# pole morphen
		ka=obj.factorA
		kb=20-ka
		pc=(pa*ka+pb*kb)/20

		# spezielles addieren
		# pc[:,:,1] *= 2

		mu,mv=sfa.getUMultiplicities(),sfa.getVMultiplicities()
		bs=Part.BSplineSurface()

		bs.buildFromPolesMultsKnots(
					pc,
					mu,mv,range(len(mu)),range(len(mv)),
					False,False,3,3)

		obj.Shape=bs.toShape()

	def myExecute(self,obj):
		print obj.Label," executed"


def createMorpher():
	'''create a moprhing between two bezier faces'''


	yy=App.ActiveDocument.addObject("Part::FeaturePython","Morpher")
	Morpher(yy)
	[yy.A,yy.B]=Gui.Selection.getSelection()
	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.6,.6,1.)
	yy.factorA=10
	return yy

# -----------curve morphed Face

class CurveMorpher(FeaturePython):

	def __init__(self, obj):
		FeaturePython.__init__(self, obj)
		obj.addProperty("App::PropertyLink","N","borders")
		obj.addProperty("App::PropertyLink","S","borders")
		obj.addProperty("App::PropertyLink","W","borders")
		obj.addProperty("App::PropertyLink","E","borders")
		obj.addProperty("App::PropertyBool","_showborders","borders")
		obj.addProperty("App::PropertyFloat","factorForce","config").factorForce=0
		obj.addProperty("App::PropertyInteger","count","config").count=9
		obj.addProperty("App::PropertyBool","curvesNS")
		obj.addProperty("App::PropertyBool","curvesWE")
		obj.addProperty("App::PropertyBool","faceNS")
		obj.addProperty("App::PropertyBool","faceWE")
		obj.addProperty("App::PropertyBool","flipA","config details")
		obj.addProperty("App::PropertyBool","flipB","config details")
		obj.addProperty("App::PropertyBool","flipAA","config details")
		obj.addProperty("App::PropertyBool","flipAB","config details")
		obj.addProperty("App::PropertyBool","flipBA","config details")
		obj.addProperty("App::PropertyBool","flipBB","config details")
		obj.addProperty("App::PropertyBool","_showconfigdetails","config details")
		obj.addProperty("App::PropertyBool","curveOnlyB","special")
		obj.addProperty("App::PropertyBool","curveOnlyA","special")
		obj.addProperty("App::PropertyFloat","curveAPosition","special").curveAPosition=50
		obj.addProperty("App::PropertyFloat","curveBPosition","special").curveBPosition=50
		obj.curvesNS=1
		obj.curvesWE=0
		obj.faceWE=0
		obj.curveOnlyA=0

		obj.addProperty("App::PropertyBool","_showspecial","special")
		obj._showspecial=False
		obj._showconfigdetails=False
		obj._showaux=False
		obj._showborders=False

	def myOnChanged(self,obj,prop):

		# print "change morpehr prop",prop
		if prop in ["Shape"]:
			return

		self.showprops(obj,prop)

		try:
			obj.factorForce,obj.curvesNS,obj.curvesWE,obj.faceNS,obj.faceWE
			obj.N.Shape,obj.S.Shape,obj.W.Shape,obj.E.Shape
			obj.curveAPosition,obj.curveBPosition
		except:
			return

#		self.showprops(obj,prop)

		compsA=[]

		if 0:
			ca=App.ActiveDocument.BeringSketch.Shape.Curve
			cb=App.ActiveDocument.BeringSketch002.Shape.Curve
			cc=App.ActiveDocument.BeringSketch003.Shape.Curve
			cd=App.ActiveDocument.BeringSketch005.Shape.Curve
		else:
#			a,b,c,d=Gui.Selection.getSelection()
			a=obj.S
			b=obj.N
			c=obj.W
			d=obj.E
			ca=a.Shape.Curve
			cb=b.Shape.Curve
			cc=c.Shape.Curve
			cd=d.Shape.Curve

		anz=obj.count

		flip=0
		if flip:
			ca,cb,cc,cd=cc,cd,ca,cb

		import Draft
		def getmorph(A,B,ptsa,ptsb,u=0.5,ff=1.):

			ptsa=np.array(ptsa)
			ptsb=np.array(ptsb)
			assert ptsa.shape == ptsb.shape	
			l=ptsa.shape[0]
			pts=u*ptsa+(ff-u)*ptsb
			pts *= 1.0/ff
			AA=pts[0].copy()
			BB=pts[-1].copy()
			ptsA=pts.copy()
		#	Draft.makeWire([FreeCAD.Vector(AA),FreeCAD.Vector(BB)])
		#	Draft.makeWire([FreeCAD.Vector(A),FreeCAD.Vector(B)])
		#	Draft.makeWire([FreeCAD.Vector(A),FreeCAD.Vector(AA)])
		#	Draft.makeWire([FreeCAD.Vector(B),FreeCAD.Vector(BB)])
		#	A,B=B,A
		#	Draft.makeWire([FreeCAD.Vector(p) for p in pts])
			h=(obj.factorForce+10)*0.1
			for il in range(l):
					fa=((l-il-1.)/(l-1))**h if il!=l-1 else 0
					fb=((il+0.)/(l-1))**h if il!=0 else 0
					pts[il] -= (fa*(AA-A)  +fb*(BB-B))

			return pts

		flipA=False
		flipB=True
		#flipA=True
		flipB=False
		flipA=obj.flipAA
		flipB=obj.flipAB


		if obj.curveOnlyA:
			Arange=[0.01*obj.curveAPosition*anz]
		else:
			Arange=range(anz+1)

		for V in Arange:
			#break

			v=V/(anz+0.0)
			u=1-v

			ptsa=np.array(ca.getPoles())
			ptsb=np.array(cb.getPoles())
		#	ptsb=ptsb[::-1]


			if flipA:
				A=np.array(cc.value(1-v))
			else:
				A=np.array(cc.value(v))
			if flipB:
				B=np.array(cd.value(1-v))	
			else:
				B=np.array(cd.value(v))	

			if obj.flipA:
				A,B=B,A

			pts=getmorph(A,B,ptsa,ptsb,u,)

			bc=Part.BSplineCurve()
			bc.buildFromPolesMultsKnots(pts,ca.getMultiplicities(),ca.getKnots(),False,3)
			compsA += [bc.toShape()]

		ca,cb,cc,cd=cc,cd,ca,cb

		flipA=False
		flipB=False

		compsB=[]

		if obj.curveOnlyB:
			Brange=[0.01*obj.curveBPosition*anz]
		else:
			Brange=range(anz+1)

		flipA=obj.flipBA
		flipB=obj.flipBB


		for V in Brange:
			#break

			ff=cc.getKnots()[-1]
			ff=2.
			v=ff*V/(anz+0.0)
			u=ff-v

			ptsa=np.array(ca.getPoles())
			ptsb=np.array(cb.getPoles())

		#	ptsb=ptsb[::-1]
		#	ptsa=ptsa[::-1]


			if flipA:
				A=np.array(cc.value(1-v))
			else:
				A=np.array(cc.value(v))
			if flipB:
				B=np.array(cd.value(1-v))	
			else:
				B=np.array(cd.value(v))	

			#Draft.makeWire([FreeCAD.Vector(A),FreeCAD.Vector(B)])

			if obj.flipB:
				A,B=B,A
			pts=getmorph(A,B,ptsa,ptsb,u,ff)

			bc=Part.BSplineCurve()
			bc.buildFromPolesMultsKnots(pts,ca.getMultiplicities(),ca.getKnots(),False,3)
			#Part.show(bc.toShape())
			compsB += [bc.toShape()]
			#App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,0.,1.)


		#makeLoft(li
		if not obj.curveOnlyA:
			la=Part.makeLoft(compsA)
		if not obj.curveOnlyB:
			lb=Part.makeLoft(compsB)

		comps=[]
		if obj.curvesNS:
			comps  += compsA
		if obj.curvesWE:
			comps  += compsB
		if obj.faceNS:
			comps += [la]
		if obj.faceWE or len(comps)==0:
			comps += [lb]


		obj.Shape=Part.Compound(comps)







	def myExecute(self,obj):
		if not obj._noExecute:
			self.onChanged(obj,"__execute__")
		print obj.Label," executed"

def curvemorphedFace():
	'''create a face by morphing boder curves'''
	yy=App.ActiveDocument.addObject("Part::FeaturePython","CurveMorpher")
	CurveMorpher(yy)
	[yy.N,yy.S,yy.W,yy.E]=Gui.Selection.getSelection()
	ViewProvider(yy.ViewObject)
	yy.ViewObject.ShapeColor=(.6,.6,1.)
	return yy


if __name__ == '__main__':
	#createMorpher()
	curvemorphedFace()





