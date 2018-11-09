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


if __name__ == '__main__':
	createMorpher()




