import time
# from say import *
# import nurbswb.pyob

#------------------------------
import FreeCAD,Sketcher,Part
import FreeCADGui
App = FreeCAD
Gui = FreeCADGui

import Part
import numpy as np


class FeaturePython:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

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

#-------------------------------


def createGeometryS(obj=None):

	if obj==None:
		sk=App.ActiveDocument.addObject('Sketcher::SketchObject','Sketch')
	else:
		sk=obj

	sk.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(96.450951,236.065002,0),App.Vector(0,0,1),267.931216),-2.497296,-1.226827),False)
	App.ActiveDocument.recompute()

	sk.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(-223.275940,-184.908691,0),App.Vector(0,0,1),280.634057),-0.171680,1.185353),False)
	sk.addConstraint(Sketcher.Constraint('Coincident',0,1,1,1)) 
	App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('Tangent',0,1)) 
	App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('Radius',0,1500.)) 
	App.ActiveDocument.recompute()

	# punkt A bewegen
	sk.movePoint(0,1,App.Vector(-228.741898,243.874924,0),0)

	consAX=sk.addConstraint(Sketcher.Constraint('DistanceX',0,2,-284.619380)) 
	sk.setDatum(consAX,-300)
	sk.renameConstraint(consAX, u'AX')
	consAY=sk.addConstraint(Sketcher.Constraint('DistanceY',0,2,162.125989)) 
	sk.setDatum(consAY,200)
	sk.renameConstraint(consAY, u'AY')
	App.ActiveDocument.recompute()

	# punkt B bewegen
	consBX=sk.addConstraint(Sketcher.Constraint('DistanceX',1,2,-284.619380)) 
	sk.setDatum(consBX,200)
	sk.renameConstraint(consBX, u'BX')
	consBY=sk.addConstraint(Sketcher.Constraint('DistanceY',1,2,162.125989)) 
	sk.setDatum(consBY,-75)
	sk.renameConstraint(consBY, u'BY')
	App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('Radius',1,3000.)) 

	return



def getNamedConstraint(sketch,name):
	'''get the index of a constraint name'''
	for i,c in enumerate (sketch.Constraints):
		if c.Name==name: return i
	print ('Constraint name "'+name+'" not in ' +sketch.Label)
	raise Exception ('Constraint name "'+name+'" not in ' + sketch.Label)




class FeedbackSketch(FeaturePython):
	'''Sketch Object with Python''' 

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		self.aa = None
		ViewProvider(obj.ViewObject)
		# _ViewProvider(obj.ViewObject, icon) 

	##\endcond


#	def onChanged(proxy,obj,prop):
#		'''run myExecute for property prop: relativePosition and vertexNumber'''
#
#		if prop in ["parent"]: 
#			proxy.myExecute(obj)


	def myExecute(proxy,obj):

		print "execute vor try"
		try: 
			if proxy.exflag: pass
		except: proxy.exflag=True

		if  not proxy.exflag: 
			proxy.exflag=True
			return

		proxy.exflag=False
		print ("execute ",obj.Label)


		for subs in obj.bases:
			print "Section ",subs
			g=getattr(obj,"base"+subs)
			if g == None: continue
			print g.Label
			if getattr(obj,"active"+subs):
				for sof in getattr(obj,"setoff"+subs):
					ci=getNamedConstraint(g,sof)
					g.setDriving(ci,False)

				for gets in getattr(obj,"get"+subs):
					print gets
					cgi=getNamedConstraint(g,gets)
					val_cgi=g.Constraints[cgi].Value
					print val_cgi
					# set the own geometry
					ci=getNamedConstraint(obj,gets)
					obj.setDatum(ci,val_cgi)

				# solve the tasks
				obj.solve()

				for sets in getattr(obj,"set"+subs):
					cgi=getNamedConstraint(obj,sets)
					val_cgi=obj.Constraints[cgi].Value
					print "setze",sets,val_cgi
					# set the data back 
					ci=getNamedConstraint(g,sets)

					isdriving=g.getDriving(ci)
					g.setDriving(ci,True)

					g.setDatum(ci,val_cgi)
					g.solve()

					if not isdriving:
						g.setDriving(ci,False)
						g.solve()

				for sof in getattr(obj,"seton"+subs):
					ci=getNamedConstraint(g,sof)
					g.setDriving(ci,True)


			g.solve()

		return

#example read and set geometry 
#			# daten von parent skp zu obj
#			ep=skp.Geometry[0].StartPoint
#			obj.setDatum(3,ep.x)
#			obj.setDatum(4,ep.y)
#
#			ep=skp.Geometry[-1].EndPoint
#			obj.setDatum(5,ep.x)
#			obj.setDatum(6,ep.y)
#
#			obj.recompute()




	def execute(self,obj):
		obj.recompute() 
		try: self.Lock
		except: self.Lock=False
		if not self.Lock:
			self.Lock=True
			try:
				#print "run myexecute"
				self.myExecute(obj)
				#print "myexecute done"
			except Exception as ex:
				print(ex)
				print('myExecute error')
#				sayexc("myExecute Error")
			self.Lock=False


##\cond
	def yexecute(self, obj):
		''' recompute sketch and than run postprocess: myExecute'''
		obj.recompute() 
		self.myExecute(obj)
##\endcond


import Sketcher

def runFBS(name="MyFeedbackSketch"):
	'''runS(name="MyFeedbackSketch"): 
		creates a Demo Feedbacksketch
	'''

	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
#	obj.addProperty("App::PropertyLink", "parent", "Parent", )

	FeedbackSketch(obj)

	return obj

def copySketch(source,target):
	'''Sketch uebernehmen'''
	for g in source.Geometry:
		target.addGeometry(g)
	for c in source.Constraints:
		target.addConstraint(c)



## \cond
if __name__=='__main__':
	fbs=runFBS()
	fbs.parent=App.ActiveDocument.Sketch
	fbs.addProperty("App::PropertyLink", "grand", "Parent", )
	fbs.grand=App.ActiveDocument.Sketch001
	copySketch(App.ActiveDocument.Sketch002,fbs)
	App.activeDocument().recompute()
#\endcond



#----------------------


def run(): 
	import FreeCAD
	FreeCAD.open(u"/home/thomas/freecad_buch/b248_stassenbau/beuger.fcstd")
	App.setActiveDocument("beuger")
	App.ActiveDocument=App.getDocument("beuger")
	Gui.ActiveDocument=Gui.getDocument("beuger")

	fbs=runFBS()
	fbs.parent=App.ActiveDocument.Sketch
#	fbs.addProperty("App::PropertyLink", "grand", "Parent", )
	fbs.grand=App.ActiveDocument.Sketch001
	copySketch(App.ActiveDocument.Sketch002,fbs)
	App.activeDocument().recompute()


def addgrp(fbs,grpname):
	if hasattr(fbs,'active'+grpname): return

	fbs.addProperty("App::PropertyBool",'active'+grpname, grpname, )
	fbs.addProperty("App::PropertyLink",'base'+grpname, grpname, )
	fbs.addProperty("App::PropertyStringList",'get'+grpname, grpname, )
	fbs.addProperty("App::PropertyStringList",'set'+grpname, grpname, )
	fbs.addProperty("App::PropertyStringList",'seton'+grpname, grpname, )
	fbs.addProperty("App::PropertyStringList",'setoff'+grpname, grpname, )

def runA():
	fbs=runFBS(name="MultiFB")
	copySketch(App.ActiveDocument.Sketch002,fbs)

	fbs.addProperty("App::PropertyBool",'active', 'Base', )
	fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
	fbs.active=True
	fbs.bases=['TAA','TBB']

	addgrp(fbs,"TAA")
	fbs.baseTAA=App.ActiveDocument.Sketch
	fbs.getTAA=['in_p']
	fbs.setTAA=['result_p']
	fbs.activeTAA=True

	addgrp(fbs,"TBB")
	fbs.activeTBB=True
	fbs.baseTBB=App.ActiveDocument.Sketch001
	fbs.getTBB=['in_g']
	fbs.setTBB=['result_g']


def runA():
	'''reorder the constraints'''
	targ=App.ActiveDocument.Sketch002
	csts=targ.Constraints
	yy=targ.ConstraintCount
	for i in range(targ.ConstraintCount):
		targ.delConstraint(yy-1-i)

	copySketch(App.ActiveDocument.Sketch,App.ActiveDocument.Sketch002)
	csts=targ.Constraints
	cx=[]
	cxi=[]
	for i,c in  enumerate(csts):
		print "!",c.Name,"!"
		if c.Name<>'':
			cx.append(c)
			cxi.append(i)
	cxi.reverse()
	for i in cxi:
		targ.delConstraint(i)
	cx.reverse()
	for c in cx:
		targ.addConstraint(c)



def runB():
	fbs=runFBS(name="MultiFB")

 	copySketch(App.ActiveDocument.Sketch,fbs)


	fbs.addProperty("App::PropertyBool",'active', 'Base', )
	fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
	fbs.active=True
	fbs.bases=['ClientA','UFO']
	for b in fbs.bases: addgrp(fbs,b)

	fbs.baseClientA=App.ActiveDocument.Sketch001
	fbs.getClientA=['a','b']
	fbs.setClientA=['c','bm']
#	fbs.setoffTAA=['b']
	#fbs.setonTAA=['b']
	fbs.activeClientA=True



def runC():
	'''copy Sketch'''
	ss=Gui.Selection.getSelection()
	if len(ss)<>2:
		print "select source and target sketch!"
		return
	copySketch(ss[0],ss[1])


def run1C():
	fbs=runFBS(name="SingleClientFeedback")

#	copySketch(App.ActiveDocument.Sketch,fbs)


	fbs.addProperty("App::PropertyBool",'active', 'Base', )
	fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
	fbs.active=True
	fbs.bases=['Client']
	for b in fbs.bases: addgrp(fbs,b)

#	fbs.baseClientA=App.ActiveDocument.Sketch001
#	fbs.getClientA=['a','b']
#	fbs.setClientA=['c','bm']
#	fbs.setoffTAA=['b']
	#fbs.setonTAA=['b']
	fbs.activeClient=True


def run2C():
	fbs=runFBS(name="TwoClientsFeedback")

#	copySketch(App.ActiveDocument.Sketch,fbs)


	fbs.addProperty("App::PropertyBool",'active', 'Base', )
	fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
	fbs.active=True
	fbs.bases=['ClientA','ClientB']
	for b in fbs.bases: addgrp(fbs,b)

#	fbs.baseClientA=App.ActiveDocument.Sketch001
#	fbs.getClientA=['a','b']
#	fbs.setClientA=['c','bm']
#	fbs.setoffTAA=['b']
	#fbs.setonTAA=['b']
	fbs.activeClientA=True
	fbs.activeClientB=True


def run3C():
	fbs=runFBS(name="ThreeClientsFeedback")




	fbs.addProperty("App::PropertyBool",'active', 'Base', )
	fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
	fbs.active=True
	fbs.bases=['ClientA','ClientB','ClientC']
	for b in fbs.bases: addgrp(fbs,b)

#	fbs.baseClientA=App.ActiveDocument.Sketch001
#	fbs.getClientA=['a','b']
#	fbs.setClientA=['c','bm']
#	fbs.setoffTAA=['b']
	#fbs.setonTAA=['b']
	fbs.activeClientA=True
	fbs.activeClientB=True
	fbs.activeClientC=True

