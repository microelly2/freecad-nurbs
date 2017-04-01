
import FreeCADGui as Gui
import FreeCAD,Part

import Draft
import numpy as np
import cv2

from PySide import QtGui
import sys,traceback,random


def showdialog(title="Fehler",text="Schau in den ReportView fuer mehr Details",detail=None):
	msg = QtGui.QMessageBox()
	msg.setIcon(QtGui.QMessageBox.Warning)
	msg.setText(text)
	msg.setWindowTitle(title)
	if detail<>None:   msg.setDetailedText(detail)
	msg.exec_()


def sayexc(title='Fehler',mess=''):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=lls[(l-3):]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))
	showdialog(title,text=mess,detail="--> ".join(l2))



class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

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

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

#------------------

def diag(p,pts,u0,v0):
	pts=np.array([[pts[0],pts[1]],[pts[3],pts[2]]])

	bs=Part.BSplineSurface()
	mv=[2,2]
	mu=[2,2]
	kv=[0,1]
	ku=[0,1]
	bs.buildFromPolesMultsKnots(pts, mu, mv, ku, kv, False,False ,1,1)
	# Part.show(bs.toShape())


	(u,v)=bs.parameter(p)

	if u>1 or u<0 or v>1 or v<0:
		#print "Punkt ausserhalb"
		return [False,p]
	else:
		#print "drin"
		if u<=0.5:
			un=u/0.5*u0
		else:
			un=u0+(u-0.5)/0.5*(1-u0)
		if v<=0.5:
			vn=v/0.5*v0
		else:
			vn=v0+(v-0.5)/0.5*(1-v0)
		pn=bs.value(un,vn)
		return [True,pn]



class Trafo(PartFeature):
	def __init__(self,obj ):
		PartFeature.__init__(self,obj)

		self.Type="Transformation"
		self.TypeId="Transformation"

		obj.addProperty("App::PropertyBool","useCenter","A").useCenter=False
		obj.addProperty("App::PropertyLink","source","A")#.source=App.ActiveDocument.DWire
		obj.addProperty("App::PropertyLink","target","A")#.target=line2
		obj.addProperty("App::PropertyLink","model","A")#.model=App.ActiveDocument.Sketch
		obj.addProperty("App::PropertyLink","center","A")#.center=App.ActiveDocument.Point
		ViewProvider(obj.ViewObject)
		obj.ViewObject.LineColor=(0.5,1.0,0.5)


	def execute(proxy,obj):
		try: 
			if proxy.lock: return
		except:
			print("except proxy lock")
		proxy.lock=True
		proxy.myexecute(obj)
		proxy.lock=False

	def myexecute(self,obj):

		if obj.source<>None:
			pts1= np.float32([(p.x,p.y) for p in obj.source.Points])
		else:
			tpts1=[obj.model.Shape.BoundBox.getPoint(i) for i in range(4)]
			pts1= np.float32([(p.x,p.y) for p in tpts1])
		pts2= np.float32([(p.x,p.y) for p in obj.target.Points])
		pts3= np.float32([(p.x,p.y) for p in obj.model.Shape.Edge1.Curve.getPoles()])


		c=obj.model.Shape.Edge1.Curve.getPoles()
		ks=[1.0/(len(c))*i for i in range(len(c)+1)]
		ms=[1]*(len(c)+1)
		bc=Part.BSplineCurve()
		bc.buildFromPolesMultsKnots(c,ms,ks,True,2)


		try: bb=FreeCAD.ActiveDocument.cc
		except: bb=FreeCAD.activeDocument().addObject("Part::Spline","cc")

		bb.ViewObject.ControlPoints=True
		bb.Label="Source Poles"
		bb.Shape=bc.toShape()


		M = cv2.getPerspectiveTransform(pts1,pts2)

		if not obj.useCenter:
			a = cv2.perspectiveTransform(np.array([pts3]), M)
			ptsa=[FreeCAD.Vector(p[0],p[1],0) for p in a[0]]

		else:
			pts=obj.source.Points
			pts=np.array([[pts[0],pts[1]],[pts[3],pts[2]]])

			bs=Part.BSplineSurface()
			mv=[2,2]
			mu=[2,2]
			kv=[0,1]
			ku=[0,1]
			bs.buildFromPolesMultsKnots(pts, mu, mv, ku, kv, False,False ,1,1)

			if obj.useCenter:
				(u0,v0)=bs.parameter( obj.center.Shape.Vertex1.Point)
			else:
				(u0,v0)=(0.5,0.5)
			#print ("u0,v0",u0,v0)

			lrc=[]
			for pk in obj.model.Shape.Edge1.Curve.getPoles():
				cpn=diag(pk,obj.source.Points,u0,v0)
				lrc.append(cpn)

			pts3= np.float32([(p[1].x,p[1].y) for p in lrc])
			a = cv2.perspectiveTransform(np.array([pts3]), M)
			pas=[]
			for i,p in enumerate(lrc):
				[flag,pt]=p
				if flag: p2=FreeCAD.Vector(a[0][i][0],a[0][i][1],0)
				else: p2=pt
				pas.append(p2)
			ptsa=pas

		# Draft.makeWire(ptsa,closed=False,face=True,support=None)
		poly=Part.makePolygon(ptsa)

		c=ptsa
		ks=[1.0/(len(c))*i for i in range(len(c)+1)]
		ms=[1]*(len(c)+1)
		bc.buildFromPolesMultsKnots(c,ms,ks,True,2)

		obj.Shape=poly
		obj.Shape=bc.toShape()

		try: ee=FreeCAD.ActiveDocument.ee
		except: ee=FreeCAD.activeDocument().addObject("Part::Spline","ee")
		ee.Shape=bc.toShape()
		ee.ViewObject.hide()
		ee.Label="Target Poles"
		ee.ViewObject.ControlPoints=True



def run():

	if len( Gui.Selection.getSelection())==0:
		showdialog('Oops','nothing selected - nothing to do for me','Please select a Bspline Curve')
		raise Exception("nothing selected")

	model=Gui.Selection.getSelection()[0]
	if model.Shape.Edge1.Curve.__class__.__name__ <>'BSplineCurve':
		print model.Label
		print model.Shape.Edge1.Curve.__class__.__name__
		showdialog('Error','edge of the selected curve is not a BSpline','method is only implemented for BSpline Curves')
		raise Exception("not implemented for this curve type")
	
	try: 
		source=Gui.Selection.getSelection()[1]
		points2=source.Points
		# todo: rectangle as source frame
	except:
		print "use bound box as source frame"
		print model.Shape.BoundBox
		points2=[model.Shape.BoundBox.getPoint(i) for i in range(4)]
		source=None

	try: center=Gui.Selection.getSelection()[2]
	except: center=None

	line2 = Draft.makeWire(points2,closed=True,face=False,support=None)
	line2.ViewObject.LineColor = (1.00,0.00,1.00)
	line2.Label="Target Frame"

	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyTransform")
	tt=Trafo(b)

	b.source=source
	b.target=line2
	b.model=model
	b.center=center
	b.useCenter= center <> None

	FreeCAD.activeDocument().recompute()


# run()
