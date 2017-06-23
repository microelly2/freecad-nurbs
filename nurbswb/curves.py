'''
SketcherObjectPython example oo
for Offset curve generation
<A HREF="http://www.freecadbuch.de/doku.php?id=blog">FreeCAD Buch</A>

''' 
## <A HREF="http://www.freecadbuch.de/doku.php?id=blog">FreeCAD Buch 2</A> 
# Author  microelly
# Warning huhuwas
# weiter


#http://free-cad.sourceforge.net/SrcDocu/dc/d77/classSketcher_1_1SketchObjectPy.html
#https://forum.freecadweb.org/viewtopic.php?t=6121
#https://forum.freecadweb.org/viewtopic.php?t=12829



#pylint: disable=W0312,W0232,R0903

from say import *
import nurbswb.pyob

##\cond


class _ViewProvider(nurbswb.pyob.ViewProvider):
	''' base class view provider '''

	def __init__(self, vobj, icon='/icons/mover.png'):
		self.Object = vobj.Object
		self.iconpath =  icon
		vobj.Proxy = self

	def getIcon(self):
		return '/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'

##\endcond

## more docu with 
## for _Sketch (hier ist gelich ein Link auf _Sketch und run)

class OffsetSpline(nurbswb.pyob.FeaturePython):
	'''Sketch Object with Python''' 

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		self.aa = None
		_ViewProvider(obj.ViewObject, icon) 

	##\endcond

	def onChanged(proxy,obj,prop):
		'''run myExecute for property prop: "ofin" and "ofout"'''
		if prop not in ["ofin","ofout"]: return 
		proxy.myExecute(obj)



	def myExecute(proxy,obj):
		''' creates a closed BSpline that interpolates the vertexes chain of the sketch
		and two offset curves in- and outside'''
		vs=obj.Shape.Vertexes
		if len(vs)==0: return

		pts=[p.Point for p in vs]
		pts.append(pts[0])

		bc=Part.BSplineCurve()
		bc.interpolate(pts)
		bc.setPeriodic()
		
		name=obj.Name

		fa=App.ActiveDocument.getObject(name+"_spline")
		if fa==None:
			fa=App.ActiveDocument.addObject('Part::Spline',name+"_spline")
		
		fa.Shape=bc.toShape()
		fa.ViewObject.LineColor=(.0,1.0,.0)

		ofs=App.ActiveDocument.getObject(name+"_offOut")
		if ofs==None: ofs=App.ActiveDocument.addObject("Part::Offset2D",name+"_offOut")
		ofs.Source = fa
		ofs.ViewObject.LineColor=(.0,0.0,1.0)
		ofs.Value = obj.ofout
		ofs.recompute()

		ofsi=App.ActiveDocument.getObject(name+"_offIn")
		if ofsi==None: ofsi=App.ActiveDocument.addObject("Part::Offset2D",name+"_offIn")
		ofsi.Source = fa
		ofsi.ViewObject.LineColor=(1.0,0.0,.0)
		ofsi.Value = -obj.ofin
		ofsi.recompute()


##\cond
	def execute(self, obj):
		''' recompuute sketch and than run postprocess: myExecute'''
		obj.recompute() 
		self.myExecute(obj)
##\endcond




def runOffsetSpline(name="MyOffSp"):
	'''run(name="Sole with borders"): a demo skript
		the demo script creates an empty  Sketch Python Object and sets
		the border distances for the offset curves to 10
		@ Author anton
	'''



	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	obj.addProperty("App::PropertyInteger", "ofin", "Base", "end").ofin=10
	obj.addProperty("App::PropertyInteger", "ofout", "Base", "end").ofout=10

	OffsetSpline(obj)

	obj.ofin=10
	obj.ofout=10

	App.activeDocument().recompute()


#
#
# 
#

class Star(nurbswb.pyob.FeaturePython):
	'''Sketch Object with Python''' 

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		self.aa = None
		_ViewProvider(obj.ViewObject, icon) 

	##\endcond

	def onChanged(proxy,obj,prop):
		'''run myExecute for property prop: relativePosition and vertexNumber'''

		if prop in ["relativePosition","vertexNumber"]: 
			proxy.myExecute(obj)


	def myExecute(proxy,obj):
		''' positon to parent'''

		print obj.parent
		print obj.relativePosition
		if obj.parent == None: return
		if obj.VertexNumber==0:
			pos=obj.parent.Placement
		else:
			pos=FreeCAD.Placement(obj.parent.Shape.Vertexes[obj.VertexNumber-1].Point,FreeCAD.Rotation())
		obj.Placement=obj.relativePosition.multiply(pos)
		obj.Placement=pos.multiply(obj.relativePosition)
		print "replaced"


##\cond
	def execute(self, obj):
		''' recompuute sketch and than run postprocess: myExecute'''
		obj.recompute() 
		self.myExecute(obj)
##\endcond


import Sketcher

def runStar(name="MyStar"):
	'''runStar(name="Sole with borders"): 
		creates a Star/Tree with 5 lines (3 leafs)
	'''


	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	obj.addProperty("App::PropertyInteger", "VertexNumber", "Base", "end").VertexNumber=0
	obj.addProperty("App::PropertyLink", "parent", "Base", "end")
	obj.addProperty("App::PropertyPlacement", "relativePosition", "Base", "end")

	# add some data
	obj.addGeometry(Part.LineSegment(App.Vector(0.000000,0.000000,0),App.Vector(100.,150.,0)),False)
	obj.addConstraint(Sketcher.Constraint('Coincident',-1,1,0,1)) 
	App.ActiveDocument.recompute()
	App.ActiveDocument.recompute()

	obj.addGeometry(Part.LineSegment(App.Vector(100.,150,0),App.Vector(50.,256.,0)),False)
	obj.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1)) 
	App.ActiveDocument.recompute()
	App.ActiveDocument.recompute()

	obj.addGeometry(Part.LineSegment(App.Vector(50.,256.,0),App.Vector(134.,334.,0)),False)
	obj.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1)) 
	App.ActiveDocument.recompute()
	App.ActiveDocument.recompute()


	obj.addGeometry(Part.LineSegment(App.Vector(100.,150,0),App.Vector(250.,-256.,0)),False)
	obj.addConstraint(Sketcher.Constraint('Coincident',0,2,3,1)) 
	App.ActiveDocument.recompute()
	App.ActiveDocument.recompute()

	obj.addGeometry(Part.LineSegment(App.Vector(250.,-256.,0),App.Vector(434.,-234.,0)),False)
	obj.addConstraint(Sketcher.Constraint('Coincident',3,2,4,1)) 
	App.ActiveDocument.recompute()
	App.ActiveDocument.recompute()

	Star(obj)
	obj.ViewObject.LineColor=(random.random(),random.random(),random.random())
	App.activeDocument().recompute()
	

	return obj


if __name__=='__main__':
	star=runStar()
	star2=runStar()
	star2.parent=star
	star2.VertexNumber=2
	star2.relativePosition.Rotation.Angle=-1.2
	App.activeDocument().recompute()


