
from say import *
import nurbswb.pyob
import Sketcher


class _ViewProvider(nurbswb.pyob.ViewProvider):
	''' base class view provider '''

	def __init__(self, vobj):
		self.Object = vobj.Object
		vobj.Proxy = self

	def getIcon(self):
		return '/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/sketchdriver.svg'


class SketchClone(nurbswb.pyob.FeaturePython):
	'''Sketch Object with Python''' 

	##\cond
	def __init__(self, obj):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		_ViewProvider(obj.ViewObject) 
	##\endcond


	def onChanged(proxy,obj,prop):
		'''run myExecute for some properties'''

		if prop == 'base':
			print "Changed Base"
			if obj.base == None:
				return

			gs=obj.base.Geometry
			rel=obj.relation
			if rel==[]:
				rel=range(len(obj.base.Geomery))
			for i,i2 in enumerate(rel):
				obj.addGeometry(gs[i2-1])


	def myExecute(proxy,obj):
		''' position to parent'''

		if obj.off:
			print obj.Label + " is deactivated (off)"
			return

		if obj.base == None:
			return
		rel=obj.relation
		if rel==[]:
			rel=range(len(obj.base.Geomery))
		try:
			ts=time.time()
			bsk=obj.base
			gs=obj.base.Geometry
			#for i,g in enumerate(gs):
			for i,i2 in enumerate(rel):
				for j in range(4):
					pos=obj.getPoint(i,j)
					posn=obj.base.getPoint(i2-1,j)
					if pos <>posn:
						obj.movePoint(i,j,posn+obj.offset)
						rc=obj.solve()
						if rc <>0: print ("solve 0 rc=",rc)

			rc=obj.solve()
			if rc <>0: print ("solve 0 rc=",rc)
			obj.recompute()
			# bsk.recompute()
		except:
			sayexc()

		print ("myExecute time",round(time.time()-ts,3))



##\cond
	def execute(self, obj):
		''' recompute sketch and than run postprocess: myExecute'''
		obj.recompute() 
		self.myExecute(obj)
##\endcond



def runSketchClone(name="MySketchClone"):

	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	obj.addProperty("App::PropertyLink", "base", "Base",)
	obj.addProperty("App::PropertyBool", "off", "Base",)
	obj.addProperty("App::PropertyIntegerList", "relation", "Base",)
	obj.addProperty("App::PropertyVector", "offset", "Base",)
	obj.offset=FreeCAD.Vector(1,1,0)
	SketchClone(obj)

	obj.ViewObject.DrawStyle = u"Dashdot"
	obj.ViewObject.LineColor= (1.000,0.000,0.498)
	obj.ViewObject.LineWidth = 6

	return obj



def runtest():
	pass

	obj=runDriver()
	obj.relation=[1,3,5,6,7]
	obj.base=App.ActiveDocument.Sketch

	App.activeDocument().recompute()
