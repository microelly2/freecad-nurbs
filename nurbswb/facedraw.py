# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- event filter for nurbs-needle editor 
#--
#-- microelly 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from PySide import QtGui,QtCore
from nurbswb.say import *

import FreeCAD
import sys,time

'''
# parameter
FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MoveWheelStep",1)
FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MovePageStep",50)
FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MoveCursorStep",10)

'''



class EventFilter(QtCore.QObject):

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.mouseWheel=0
		self.enterleave=False
		self.enterleave=True
		self.keyPressed2=False
		self.editmode=False
		self.key='x'
		self.posx=-1
		self.posy=-1
		self.lasttime=time.time()
		self.lastkey='#'


	def eventFilter(self, o, e):

		z=str(e.type())

		event=e

		if event.type() == QtCore.QEvent.ContextMenu : return True

		# not used events
		if z == 'PySide.QtCore.QEvent.Type.ChildAdded' or \
				z == 'PySide.QtCore.QEvent.Type.ChildRemoved'or \
				z == 'PySide.QtCore.QEvent.Type.User'  or \
				z == 'PySide.QtCore.QEvent.Type.Paint' or \
				z == 'PySide.QtCore.QEvent.Type.LayoutRequest' or\
				z == 'PySide.QtCore.QEvent.Type.UpdateRequest'  : 
			return QtGui.QWidget.eventFilter(self, o, e)

		if event.type() == QtCore.QEvent.MouseMove:
			#if event.buttons() == QtCore.Qt.NoButton:
				#print ("vetnbuttons",event.buttons() )
				pos = event.pos()
				x=pos.x()
				y=pos.y()
#				print ("mouse pos ",x,y)
				(x,y)=Gui.ActiveDocument.ActiveView.getCursorPos()
#				print ("cursor pos",x,y)
				t=Gui.ActiveDocument.ActiveView.getObjectsInfo((x,y))
				if t<>None:
					for tt in t:
#						if tt['Object']=='Sphere' and tt['Component']=='Face1':
						if tt['Object']==self.objname and tt['Component']==self.subelement:

							#print ("!",tt['x'],tt['y'],tt['z'])
							#print ("event buttons",event.buttons())
							self.x,self.y,self.z=tt['x'],tt['y'],tt['z']
							break
					if event.buttons()==QtCore.Qt.LeftButton:
						print "LEFT AA"
						vf=FreeCAD.Vector(self.x,self.y,self.z)
						bs=self.subobj.Surface
						#print bs
						(u,v)=bs.parameter(vf)
						print (u,v)
						lu=0.5
						lv=0.5

						ba=bs.vIso(u)
						ky=ba.length(v,lv)
						if v<0.5: ky =-ky

						bbc=bs.vIso(v)
						kx=bbc.length(lu,u)
						if u<0.5: kx =-kx
						
						
						
						mf=FreeCAD.Vector(self.x,self.y,0)
						mf=FreeCAD.Vector(-1*ky,-1*kx,0)
						
						try:
							self.pts += [vf]
							self.ptsm += [mf]
						except:
							self.pts = [vf]
							self.ptsm = [mf]



						if len(self.pts)>1:

							self.wire.Shape=Part.makePolygon(self.pts)
							self.wirem.Shape=Part.makePolygon(self.ptsm)
							self.wire.ViewObject.PointSize=int(self.dialog.dial.value()+1)
							self.wire.ViewObject.LineWidth=int(self.dialog.dial.value()+1)




		if z == 'PySide.QtCore.QEvent.Type.KeyPress':
			# http://doc.qt.io/qt-4.8/qkeyevent.html

			# ignore editors
			try:
				if self.editmode:
					return QtGui.QWidget.eventFilter(self, o, e)
			except: pass

			# only first time key pressed
			if not self.keyPressed2:
				self.keyPressed2=True
				time2=time.time()
				ee=e.text()

				if time2-self.lasttime<0.01 and len(ee)>0 and ee[0]==self.lastkey:
					self.lasttime=time2
					return False

				try:
					# only two function keys implemented, no modifieres
					if e.key()== QtCore.Qt.Key_F2:
						say("------------F2-- show mode and moddata---------------")
						print self.mode
						return False
					elif e.key()== QtCore.Qt.Key_Escape:
						say("------------Escape-----------------")
						stop()

					elif e.key()== QtCore.Qt.Key_F3 :
						say("------------F3-----------------")
						stop()


#					elif  e.key()== QtCore.Qt.Key_Return:
#						say("------------Enter-----------------")
#						self.update()
					elif e.key() == QtCore.Qt.Key_Right :
						if self.dialog.dial.value()==self.dialog.dial.maximum(): val=0
						else: val=self.dialog.dial.value()+1
						self.dialog.dial.setValue(val)
						return True
					elif e.key() == QtCore.Qt.Key_Left :
						if self.dialog.dial.value()== 0: val=self.dialog.dial.maximum()
						else: val=self.dialog.dial.value()-1
						self.dialog.dial.setValue(val)
						return True
					elif e.key() == QtCore.Qt.Key_Up :
						self.mouseWheel += FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MoveCursorStep",10)
						self.dialog.ef_action("up",self,self.mouseWheel) 
						return True
					elif e.key() == QtCore.Qt.Key_Down :
						self.mouseWheel -= FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MoveCursorStep",10) 
						self.dialog.ef_action("down",self,self.mouseWheel)
						return True
					elif e.key() == QtCore.Qt.Key_PageUp :
						self.mouseWheel += FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MovePageStep",50)
						self.dialog.ef_action("up!",self,self.mouseWheel)
						return True
					elif e.key() == QtCore.Qt.Key_PageDown :
						self.mouseWheel -= FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetFloat("MovePageStep",50)
						self.dialog.ef_action("down!",self,self.mouseWheel)
						return True
					if e.key()== QtCore.Qt.Key_Enter or e.key()== QtCore.Qt.Key_Return:
							vf=FreeCAD.Vector(self.x,self.y,self.z)
							try:
								self.pts += [vf]
							except:
								self.pts = [vf]
							if len(self.pts)>1:
								self.wire.Shape=Part.makePolygon(self.pts)
								self.wire.ViewObject.PointSize=int(self.dialog.dial.value()+1)

					else: # letter key pressed
						ee=e.text()
						if len(ee)>0: 
							r=ee[0]
							
						else: r="key:"+ str(e.key())
						#say("-------action for key ----!!------" + r)
						self.lastkey=e.text()
						if r=='+':
							Gui.activeDocument().ActiveView.zoomIn()
							return True
						if r=='-':
							Gui.activeDocument().ActiveView.zoomOut()
							return True
						if r=='*':
							Gui.activeDocument().ActiveView.fitAll()
							return True
 						if r in ['a']:

								print ("KEY pressed ----------------------",r)

						vf=FreeCAD.Vector(self.x,self.y,self.z)
						mf=FreeCAD.Vector(self.x,self.y,0)

						try:
							self.pts += [vf]
							self.ptsm += [mf]
						except:
							self.pts = [vf]
							self.ptsm = [mf]

						if len(self.pts)>1:
							self.wire.Shape=Part.makePolygon(self.pts)
							self.wire.ViewObject.PointSize=int(self.dialog.dial.value()+1)
							self.wire.ViewObject.LineWidth=int(self.dialog.dial.value()+1)
							self.wirem.Shape=Part.makePolygon(self.ptsm)
							self.wirem.ViewObject.PointSize=int(self.dialog.dial.value()+1)
							self.wirem.ViewObject.LineWidth=int(self.dialog.dial.value()+1)



				except:
					sayexc()

		# end of a single key pressed
		if z == 'PySide.QtCore.QEvent.Type.KeyRelease':
			self.lasttime=time.time()
			self.keyPressed2=False

		# enter and leave a widget - editor widgets
		if z == 'PySide.QtCore.QEvent.Type.Enter' or z == 'PySide.QtCore.QEvent.Type.Leave':
			pass

		# deactive keys in editors context
		if z == 'PySide.QtCore.QEvent.Type.Enter' and \
			(o.__class__ == QtGui.QPlainTextEdit or o.__class__ == QtGui.QTextEdit):
			self.editmode=True
		elif z == 'PySide.QtCore.QEvent.Type.Leave' and \
			(o.__class__ == QtGui.QPlainTextEdit or o.__class__ == QtGui.QTextEdit):
			self.editmode=False

		# mouse movement only leaves and enters
		if z == 'PySide.QtCore.QEvent.Type.HoverMove' :
			pass



		event=e
		try:

			if event.type() == QtCore.QEvent.ContextMenu : #and o.__class__ == QtGui.QWidget:
					# hier contextmenue rechte maus auschalten
					FreeCAD.Console.PrintMessage('!! cancel -------------------------------------context-----------\n')
					return False
					pass

			# wheel rotation
			if event.type()== QtCore.QEvent.Type.Wheel:

				self.mouseWheel += e.delta()/120
				pos=e.pos()
				self.posx=pos.x()
				self.posy=pos.y()

				##FreeCAD.Console.PrintMessage("wheel: " + str(self.mouseWheel) + " pos: " +str(e.pos())+ "\n")
				#self.modedat[self.mode]=self.mouseWheel
				self.dialog.ef_action("wheel",self,self.mouseWheel)

				noDefaultWheel = self.mode<>'n'
				
				if noDefaultWheel:
					return True 
				else:
					return False

			# mouse clicks
			if event.type() == QtCore.QEvent.MouseButtonPress or \
					event.type() == QtCore.QEvent.MouseButtonRelease or\
					event.type() == QtCore.QEvent.MouseButtonDblClick:

#				FreeCAD.Console.PrintMessage(str(event.type())+ " " + str(o) +'!!\n')

				if event.button() == QtCore.Qt.MidButton or  event.button() == QtCore.Qt.MiddleButton:
#					FreeCAD.Console.PrintMessage('!-------------------------------------!!  X middle \n')
					return False

				if event.button() == QtCore.Qt.LeftButton:
#					FreeCAD.Console.PrintMessage('!! X one left\n')



					return False

				elif event.button() == QtCore.Qt.RightButton:
#					FreeCAD.Console.PrintMessage('!! X one right\n')
					return False

		except:
			sayexc()

		return QtGui.QWidget.eventFilter(self, o, e)


	def update(self):
		self.dialog.commit_noclose()




def drawcurve(wire,face):
	print "drawcurve"

	#w=App.ActiveDocument.Drawing_on_MyShoe__Face2.Shape
	#t=App.ActiveDocument.MyShoe.Shape.Face2

	w=wire.Shape
	t=face


	pts=[p.Point for p in w.Vertexes]
	sf=t.Surface

	pts2da=[sf.parameter(p) for p in pts[1:]]
	pts2d=[FreeCAD.Base.Vector2d(p[0],p[1]) for p in pts2da]
	FreeCAD.pts2d=pts2d

	bs2d = Part.Geom2d.BSplineCurve2d()
	bs2d.setPeriodic()
	bs2d.interpolate(pts2d)
	bs2d.setPeriodic()

	e1 = bs2d.toShape(t)
#	Part.show(e1)
	sp=App.ActiveDocument.addObject("Part::Spline",wire.Label+" Spline")
	sp.Shape=e1
	sp.ViewObject.LineColor=wire.ViewObject.LineColor
	wire.ViewObject.hide()

	# flaeche erzeugen


	face=App.ActiveDocument.Poles.Shape.Face1
	edges=e1.Edges


	ee=edges[0]
	splita=[(ee,face)]
	r=Part.makeSplitShape(face, splita)
#	Part.show(r[0][0])

	ee.reverse()
	splitb=[(ee,face)]
	r2=Part.makeSplitShape(face, splitb)
#	Part.show(r2[0][0])

	#r=Part.makeSplitShape(face, splita)
	#Part.show(r[0][0])
	sp=App.ActiveDocument.addObject("Part::Spline",wire.Label+" SplineFaceA")
	sp.Shape=r[0][0]
	sp.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
	sp.ViewObject.LineColor=sp.ViewObject.ShapeColor

	sp=App.ActiveDocument.addObject("Part::Spline",wire.Label+" SplineFaceB")
	sp.Shape=r2[0][0]
	sp.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
	sp.ViewObject.LineColor=sp.ViewObject.ShapeColor




import random

def createnewwire(widget):

	print "new wire"
	ef=widget.ef
	w=App.ActiveDocument.addObject("Part::Feature","A Drawing on " + ef.objname + ": "+ ef.subelement +"#")
	w.Shape=Part.Shape()
	wam=App.ActiveDocument.addObject("Part::Feature","YY Drawing on " + ef.objname + ": "+ ef.subelement +"#")
	wam.Shape=Part.Shape()

	if 0:
		c=PySide.QtGui.QColorDialog.getColor(QtGui.QColor(random.randint(10,255),random.randint(10,255),random.randint(10,255)))
		print (c.red(),c.green(),c.blue())

		w.ViewObject.LineColor=(1.0/255*c.red(),1.0/255*c.green(),1.0/255*c.blue())
		w.ViewObject.LineWidth=int(widget.dial.value()+1)
		w.ViewObject.PointColor=(1.0/255*c.red(),1.0/255*c.green(),1.0/255*c.blue())
		w.ViewObject.PointSize=int(widget.dial.value()+1)
	# w.Label=str(w.ViewObject.LineColor)

	w.ViewObject.LineColor=(random.random(),random.random(),random.random())

	ef.wire=w
	ef.wirem=wam
	ef.pts=[]




class MyWidget(QtGui.QWidget):
	'''edit pole mastre dialog'''

	def commit(self):
		stop()

	def apply(self):
		try:
			drawcurve(self.ef.wire,self.ef.subobj)
		except:
			sayexc()
		stop()

	def applyandnew(self):
		try:
			drawcurve(self.ef.wire,self.ef.subobj)
		except:
			sayexc()
		createnewwire(self)



	def update(self):
		mode=self.imode
		print ("focus",focus())
		ef=self.ef
		print ("val,x,y,k",ef.mouseWheel,ef.posx,ef.posy,ef.key)
		return 

	def ef_action(self,*args):
		return


def dialog(source):
	''' create dialog widget'''


	w=MyWidget()
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	w.source=source
	w.imode=-1
	w.ef="no eventfilter defined"


	mode=QtGui.QComboBox()
	mode.addItem("move pole") #0
	mode.addItem("move pole and neighbors") #1
	mode.addItem("sharpen/smooth edge") #2
	mode.addItem("colinear neighbors") #3
	mode.addItem("rotate neighbors") #4

	w.mode=mode

	editorkey=FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetString("editorKey","h")
	lab=QtGui.QLabel("Direction: " + editorkey)
	w.key=editorkey
	w.modelab=lab

	btn=QtGui.QPushButton("Apply and close")
	btn.clicked.connect(w.apply)

	cobtn=QtGui.QPushButton("Apply and new")
	cobtn.clicked.connect(w.applyandnew)


	cbtn=QtGui.QPushButton("Stop Dialog (preserve Aux)")
	cbtn.clicked.connect(stop)

	poll=QtGui.QLabel("Selected  Pole:")

	dial=QtGui.QDial() 
	dial.setMaximum(10)
	dial.setNotchesVisible(True)
	dial.setValue(FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetInt("Cursor",0))
#	dial.valueChanged.connect(w.setcursor2)
	w.dial=dial


	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	
	for ww in [btn,cobtn,dial] :
		box.addWidget(ww)

	return w



def createRibCage(bs):

		rc=100
		ribs=[]
		for i in range(rc+1):
			f=bs.uIso(1.0/rc*i)
			ribs.append(f.toShape())

		comp=Part.Compound(ribs)
		RibCage=App.activeDocument().addObject('Part::Feature','Ribs')
		RibCage.Shape=comp

		mers=[]
		for i in range(rc+1):
			f=bs.vIso(1.0/rc*i)
			mers.append(f.toShape())
		comp=Part.Compound(mers)
		Meridians=App.activeDocument().addObject('Part::Feature','Meridians')
		Meridians.Shape=comp
		return (RibCage,Meridians)





def start(source='Backbone'):
	'''create and initialize the event filter'''



	ef=EventFilter()
	ef.mouseWheel=0
	ef.mode='r'
	try:
			s=Gui.Selection.getSelectionEx()
			ef.subobj=s[0].SubObjects[0]
			ef.objname=s[0].Object.Name
			ef.subelement=s[0].SubElementNames[0]
			s[0].Object.ViewObject.Transparency=70
			if ef.subobj.Surface.__class__.__name__ == 'BSplineSurface':
				rc=createRibCage(ef.subobj.Surface)
				ef.rc=rc

	except:
		sayexc("no surface selected")
		return

	FreeCAD.eventfilter=ef

	mw=QtGui.qApp
	mw.installEventFilter(ef)
	ef.keyPressed2=False

	w=App.ActiveDocument.addObject("Part::Feature","Drawing on " + ef.objname + ": "+ ef.subelement)
	w.Shape=Part.Shape()

	w.ViewObject.LineColor=(1.0,0.0,0.0)
	w.ViewObject.LineWidth=10

	wam=App.ActiveDocument.addObject("Part::Feature","Drawing on " + ef.objname + ": "+ ef.subelement)
	wam.Shape=Part.Shape()

	wam.ViewObject.LineColor=(1.0,0.0,1.0)
	wam.ViewObject.LineWidth=10

	ef.wire=w
	ef.wirem=wam

	ef.dialog=dialog(source)
	ef.dialog.ef=ef

	# beispiel - erzeuge hilfsobjekte
	import nurbswb.isodraw
	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyDrawGrid")

	nurbswb.isodraw.Drawgrid(b)
	b.faceObject=App.ActiveDocument.Poles

	b.ViewObject.Transparency=60
	App.activeDocument().recompute()

	b=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyGrid")
	nurbswb.isodraw.Draw3Dgrid(b)
	b.drawgrid=App.ActiveDocument.MyDrawGrid



	ef.dialog.show()



def stop():
	''' stop eventserver'''

	mw=QtGui.qApp
	ef=FreeCAD.eventfilter
	mw.removeEventFilter(ef)
	ef.keyPressed2=False
	
	ef.dialog.hide()
	try:
		App.ActiveDocument.removeObject(ef.rc[0].Name)
		App.ActiveDocument.removeObject(ef.rc[1].Name) 
	except:
		pass



def run():
	tts=time.time()

	try: stop()
	except: pass

	print time.time()-tts

	tts=time.time()

	start()

	print time.time()-tts

	tts=time.time()


'''


'''
