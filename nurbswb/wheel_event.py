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
				z == 'PySide.QtCore.QEvent.Type.UpdateRequest'   :
			return QtGui.QWidget.eventFilter(self, o, e)

		if event.type() == QtCore.QEvent.MouseMove:
			if event.buttons() == QtCore.Qt.NoButton:
				pos = event.pos()
				x=pos.x()
				y=pos.y()
				# print ("mous pos ",x,y)


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
						say("stopped------------")

					elif e.key()== QtCore.Qt.Key_F3 :
						say("------------F3-----------------")
						stop()
						say("stopped------------")

					elif e.key()== QtCore.Qt.Key_Enter or e.key()== QtCore.Qt.Key_Return:
						say("------------Enter-----------------")
						self.update()
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
						print "Key up"
						self.mouseWheel += 1
						self.dialog.ef_action("up",self,self.mouseWheel) 
						return True
					elif e.key() == QtCore.Qt.Key_Down :
						self.mouseWheel -= 1 
						self.dialog.ef_action("down",self,self.mouseWheel)
						return True
					elif e.key() == QtCore.Qt.Key_PageUp :
						self.mouseWheel += 10 
						self.dialog.ef_action("up!",self,self.mouseWheel)
						return True
					elif e.key() == QtCore.Qt.Key_PageDown :
						self.mouseWheel -= 10 
						self.dialog.ef_action("down!",self,self.mouseWheel)
						return True
					else: # letter key pressed
						ee=e.text()
						if len(ee)>0: 
							r=ee[0]
							self.key=str(r)
						else: r="key:"+ str(e.key())
						say("-------action for key ----!!------" + r)
						self.lastkey=e.text()
						if r=='+':
							Gui.ActiveDocument.ActiveView.zoomIn()
							return True
						if r=='-':
							Gui.ActiveDocument.ActiveView.zoomOut()
							return True
						if r=='*':
							Gui.ActiveDocument.ActiveView.fitAll()
							return True
 						if r in ['l','r','h','x','y','z','n','t','b']:
							self.mode=str(r)
							self.dialog.ef_action(r,self)
							self.dialog.modelab.setText("Direction: "+ r)
						if r == '0':
							self.mouseWheel = 0
							self.mode='0'

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

				FreeCAD.Console.PrintMessage("wheel: " + str(self.mouseWheel) + " pos: " +str(e.pos())+ "\n")
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




def focus():
	'''get preselected pole sets'''

	try:
		s=FreeCADGui.Selection.getSelectionEx()[0]

		s.Object.Label
		print s.Object.Name
		print s.SubElementNames


		needle=s.Object.InList[0]
		needle.Label

		for sen in s.SubElementNames:
			print sen[4:]
			if s.Object.Name[0:4]=='Ribs':
				return (needle,"rib",int(sen[4:]))
			if s.Object.Name[0:9]=='Meridians':
				return(needle,"meridian",int(sen[4:]))
	except:
		return (None,None,-1)







class MyWidget(QtGui.QWidget):
	'''edit pole mastre dialog'''

	def getNeedle(self): 
		source=self.getsource()
		needle=source.InList[0]
		return needle


	def commit_noclose(self):

		self.update()
		hd=self.helperDok()
		poles=hd.BSpline.Shape.Edge1.Curve.getPoles()
		
		pos=self.dial.value()
		source=self.getsource()
		needle=source.InList[0]
		curve,bb,scaler,twister= needle.Proxy.Model()
		self.twister=twister
		self.scaler=scaler
		if self.source=='Backbone': 
			bb=poles
			print (self.rotx,self.roty,self.rotz)
			(rx,ry,rz)=twister[pos]
			twister[pos]=[rx+self.rotx,ry+self.roty,rz+self.rotz]
			self.dialx.setValue(0)
			self.dialy.setValue(0)
			self.dialz.setValue(0)
		elif self.source=='Rib_template': curve=poles

		needle.Proxy.updateSS(curve,bb,scaler,twister)

# geht nicht #+# warumn?
#		App.getDocument("Unnamed").Spreadsheet.touch()
#		App.getDocument("Unnamed").recompute()

		dokname=FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetString("Document","Needle")
		App.ActiveDocument=App.getDocument(dokname)
		Gui.ActiveDocument=Gui.getDocument(dokname)
		App.ActiveDocument.Spreadsheet.touch()
		App.ActiveDocument.recompute()
		self.setSelection(pos)

	def commit(self):
		''' commit data and close dialog '''
		self.commit_noclose()
		self.closeHelperDok()
		stop()

	def cancel(self):
		self.closeHelperDok()
		stop()

	def getsource(self):
		dokname=FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetString("Document","Needle")
		return App.getDocument(dokname).getObject(self.source)

	def update(self):
		mode=self.imode
		print ("focus",focus())
		ef=self.ef
		print ("val,x,y,k",ef.mouseWheel,ef.posx,ef.posy,ef.key)
		#hilfsfenster 
		hd=self.helperDok()


		# move-mode
		if mode==0 or mode==-1:
			try: 
				bb=App.ActiveDocument.BSpline
				pos=self.dial.value()

				try:
					t=hd.Target.Shape.Point
				except:
					t=FreeCAD.Vector()

				pp=bb.Shape.Edge1.Curve.getPoles()
				points=pp
				if pos>0:
					pp2=pp[:pos]+[t]+pp[pos+1:]
				else:
					pp2=[t]+pp[pos+1:]

				bs=bb.Shape.Edge1.Curve.copy()
				bs.setPole(pos+1,FreeCAD.Vector(t))
				bb.Shape=bs.toShape()
				points=pp2

			except:
				print "ExCEPT - need to create helper BSpline"
				src=self.getsource()
				points=src.Shape.Edge1.Curve.getPoles()
				mybsc=App.ActiveDocument.addObject('Part::Feature','BSpline')
				mybsc.Shape=src.Shape

				Gui.activeDocument().activeView().viewAxonometric()
				Gui.SendMsgToActiveView("ViewFit")
				bb=App.ActiveDocument.ActiveObject

			Gui.Selection.addSelection(bb)

			self.points=points
			self.setcursor()
			#reset diff
			self.ef.mouseWheel=0
			self.settarget()
			return

		# "sharpening mode"
		elif mode==2:
			try: 
				bb=App.ActiveDocument.BSpline
				pos=self.dial.value()

				pp=bb.Shape.Edge1.Curve.getPoles()
				pc=len(pp)

				prep=FreeCAD.Vector(pp[pos-1])
				if pos>=len(pp)-1:px=0
				else: px=pos+1
				posp=FreeCAD.Vector(pp[px])

				faktor=0.05
				t=pp[pos]

				t0=prep - t
				t0 *= faktor
				t0  += t

				t2=posp - t
				t2 *= faktor
				t2 += t

				points=pp

				pp2=pp

				bs=bb.Shape.Edge1.Curve.copy()

				# hack !!
				bs.setPole(pos+1,t)

				if pos==0: px0=pc
				else: px0=pos
				bs.setPole(px0,t0)

				if pos==pc-1: px2=1
				else: px2=pos+2
				bs.setPole(px2,t2)

				if pos==0:
					pp2=[t,t2]+pp[2:-1]+[t0]
				elif pos==1:
					pp2=[t,t2]+pp[2:-1]+[t0]
				elif pos==pc-1:
					pp2=[t2]+pp[1:-2]+[t0,t]
				else:
					pp2=pp[:pos-2]+[t0,t,t2]+pp2[pos+1:]

				bb.Shape=bs.toShape()

				points=pp2
			except:
				print "ExCEPT 2 not possible"""
				return

			Gui.Selection.addSelection(bb)

			self.points=points
			self.setcursor()
			#reset diff
			self.ef.mouseWheel=0
			self.settarget()
			return



		else:
			print "!!!!!!!!!!!!!! no imp for this mode!!"



	def ef_action(self,*args):
		# aufruf durch ef.dialog.ef_action()
		self.settarget()


	def helperDok(self):
		'''get or create helper document'''
		try: hd=App.getDocument("Aux")
		except:
			App.newDocument("Aux")
			hd=App.getDocument("Aux")

		App.setActiveDocument("Aux")
		App.ActiveDocument=App.getDocument("Aux")
		Gui.ActiveDocument=Gui.getDocument("Aux")
		return hd

	def closeHelperDok(self):
		'''close helper document'''
		try: App.closeDocument("Aux")
		except: pass

	def cursor(self,dok,cords=(0,0,0)):
		'''pointer to the selected pole/coords as a red quad'''
		v=Part.Point(FreeCAD.Vector(cords)).toShape()
		try: curs=dok.Cursor
		except: curs=dok.addObject('Part::Feature','Cursor')
		curs.Shape=v
		dok.recompute()
		curs.ViewObject.PointSize=8
		curs.ViewObject.PointColor=(1.0,0.,0.)
		self.settarget()

	def setcursor(self):
		''' set cursor to the dialer selecterd pole'''
		hd=self.helperDok()
		pl=len(self.points)
		self.cursor(hd,self.points[self.dial.value()%pl])
		self.dial.setMaximum(pl-1)

	def setcursor2(self,p):
		''' set cursor as dialer backcall'''
		hd=self.helperDok()
		self.cursor(hd,self.points[p])
		self.setSelection(p)

	def setSelection(self,pos):
		obj=self.getNeedle()
		print obj, obj.Label
		if self.source=='Backbone':
			obj.Proxy.showRib(pos)
		else:
			obj.Proxy.showMeridian(pos)

	def setrotx(self,rx):
		self.rotx=rx
		self.settarget()

	def setroty(self,r):
		self.roty=r
		self.settarget()

	def setrotz(self,r):
		self.rotz=r
		self.settarget()


	def target(self,dok,cords=(0,0,0)):
		''' set changed pole to '''
		v=Part.Point(FreeCAD.Vector(cords)).toShape()
		try: curs=dok.Target
		except: curs=dok.addObject('Part::Feature','Target')
		curs.Shape=v
		dok.recompute()
		curs.ViewObject.PointSize=10
		curs.ViewObject.PointColor=(.0,0.,1.)

	def settarget(self):
		'''set the target depending on the mouse wheel roll and mode key'''

		print (self.rotx,self.roty,self.rotz)

		dok=self.helperDok()
		pl=len(self.points)
		self.dial.setMaximum(pl-1)
		pos=self.dial.value()

		if pos==0: lpos=pl-1
		else: lpos=pos-1

		if pos==pl-1: rpos=0
		else: rpos=pos+1
		print ('pl,pos,lpos,rpos',pl,pos,lpos,rpos)


		ef=self.ef
		if ef.key in  ['x','y','z']:
			kx,ky,kz=0,0,0
			if ef.key=='x': kx=ef.mouseWheel
			if ef.key=='y': ky=ef.mouseWheel
			if ef.key=='z': kz=ef.mouseWheel

			#changed point 
			diff=FreeCAD.Vector(kx,ky,kz)
			t=self.points[pos] + diff
		elif  ef.key=='t':
			a=FreeCAD.Vector(self.points[lpos])-FreeCAD.Vector(self.points[rpos])
			a.normalize()
			diff=a.multiply(ef.mouseWheel)
			t=self.points[pos] + diff 
		elif  ef.key=='n' or  ef.key=='b':
			a=FreeCAD.Vector(self.points[lpos])-FreeCAD.Vector(self.points[rpos])
			b=FreeCAD.Vector(self.points[lpos])-FreeCAD.Vector(self.points[pos])
			c=a.cross(b)
			if  ef.key=='n': d=c.cross(a)
			else: d=c
			d.normalize()
			diff=d.multiply(ef.mouseWheel)
			t=self.points[pos] + diff 
		elif  ef.key=='r':
			d=FreeCAD.Vector(self.points[pos][0],self.points[pos][1],0).normalize()
			diff=d.multiply(ef.mouseWheel)
			t=self.points[pos] + diff 
		else:
			print ("mode not implemented ",ef.key)
			t=self.points[pos]

		self.target(dok, t)

		# create or get traget curve
		try: bb=dok.TargetCurve
		except: bb=dok.addObject('Part::Feature','TargetCurve')

		pp=self.points

		if pos>0: pp2=pp[:pos]+[t]+pp[pos+1:]
		else: pp2=[t]+pp[pos+1:]

		# bspline curve
		bs=dok.BSpline.Shape.Edge1.Curve.copy()
		bs.setPole(pos+1,FreeCAD.Vector(t))
		bb.Shape=bs.toShape()

		# pole polygon
		pol=Part.makePolygon(pp2 + [pp2[0]])
#		bb.Shape=pol



		pp3=[]

		if self.source=='Backbone':
			xV=FreeCAD.Vector(100,0,0)
			yV=FreeCAD.Vector(0,100,0)

			source=self.getsource()
			needle=source.InList[0]
			curvea,bba,scaler,twister= needle.Proxy.Model()


			for i,p in enumerate(pp2):
				# print (i,twister[i],scaler[i])
				[xa,ya,za]=twister[i]

				if pos  == i :
					xa += self.rotx
					ya += self.roty
					za += self.rotz

				p2=FreeCAD.Placement()
				p2.Rotation=FreeCAD.Rotation(FreeCAD.Vector(0,0,1),za).multiply(FreeCAD.Rotation(FreeCAD.Vector(0,1,0),ya).multiply(FreeCAD.Rotation(FreeCAD.Vector(1,0,0),xa)))

				ph=FreeCAD.Placement()
				ph.Base=xV
				xR=p2.multiply(ph).Base
				ph=FreeCAD.Placement()
				ph.Base=yV
				yR=p2.multiply(ph).Base


				pp3.append(Part.makePolygon([p+xR,p,p+yR]))


		# all together 
		bb.Shape=Part.Compound(pp3+ [pol,bs.toShape()])

		dok.recompute()

		bb.ViewObject.LineColor=(1.0,0.6,.0)
		bb.ViewObject.LineWidth=1
		bb.ViewObject.PointColor=(.8,0.4,.0)
		bb.ViewObject.PointSize=3


	def settarget2(self,p):
		'''set target as dialer callback'''
		dok=self.helperDok()
		self.target(dok,self.points[p])

	def setmode(self,index):
		'''callback from list'''
		self.imode=index

def dialog(source):
	''' create dialog widget'''

	
	w=MyWidget()
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	w.source=source
	w.imode=-1
	w.ef="no eventfilter defined"


	try:
		n=w.getNeedle()
		n.RibTemplate.ViewObject.hide()
		n.Backbone.ViewObject.hide()
	except:
		pass

	mode=QtGui.QComboBox()
	mode.addItem("move pole") #0
	mode.addItem("move pole and its eighbors") #1
	mode.addItem("sharpening edge") #2
	mode.addItem("smoothing edge") #3
	mode.currentIndexChanged.connect(w.setmode)
	w.mode=mode

	lab=QtGui.QLabel("Direction: x")
	w.modelab=lab

	btn=QtGui.QPushButton("Cancel")
	btn.clicked.connect(w.cancel)

	cobtn=QtGui.QPushButton("Commit and stop")
	cobtn.clicked.connect(w.commit)

	conbtn=QtGui.QPushButton("Commit and continue")
	conbtn.clicked.connect(w.commit_noclose)

	cbtn=QtGui.QPushButton("Stop Dialog")
	cbtn.clicked.connect(stop)

	poll=QtGui.QLabel("Selected  Pole:")

	dial=QtGui.QDial() 
	dial.setNotchesVisible(True)
	dial.valueChanged.connect(w.setcursor2)
	w.dial=dial

	if source == 'Backbone':
		rotxl=QtGui.QLabel("Rotation X:")

		dialx=QtGui.QDial() 
		dialx.setNotchesVisible(True)
		dialx.setMinimum(-90)
		dialx.setMaximum(90)
		dialx.setValue(0)
		dialx.setSingleStep(15)
		dialx.valueChanged.connect(w.setrotx)
		w.dialx=dialx

		rotyl=QtGui.QLabel("Rotation Y:")

		dialy=QtGui.QDial() 
		dialy.setNotchesVisible(True)
		dialy.setMinimum(-90)
		dialy.setMaximum(90)
		dialy.setValue(0)
		dialy.setSingleStep(15)

		dialy.valueChanged.connect(w.setroty)
		w.dialy=dialy

		rotzl=QtGui.QLabel("Rotation Z:")

		dialz=QtGui.QDial() 
		dialz.setNotchesVisible(True)
		dialz.setMinimum(-90)
		dialz.setMaximum(90)
		dialz.setValue(0)
		dialz.setSingleStep(15)

		dialz.valueChanged.connect(w.setrotz)
		w.dialz=dialz
		
		rots=[rotxl,dialx,rotyl,dialy,rotzl,dialz]
	else:
		rots=[]

	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	
	for ww in [mode,lab,btn,cobtn,conbtn,cbtn,poll,dial] + rots:
		box.addWidget(ww)

	return w



def start(source):
	'''create and initialize the event filter'''

	ef=EventFilter()
	ef.mouseWheel=0
	ef.mode='r'

	FreeCAD.eventfilter=ef

	mw=QtGui.qApp
	mw.installEventFilter(ef)
	ef.keyPressed2=False

	ef.dialog=dialog(source)
	#ef.dialog.source=source
	ef.dialog.ef=ef
	ef.dialog.rotx=0
	ef.dialog.roty=0
	ef.dialog.rotz=0
	ef.dialog.update()
	ef.dialog.show()
	tt=Gui.ActiveDocument.activeView()
	tt.stopAnimating()

	mw=FreeCADGui.getMainWindow()
	mdiarea=mw.findChild(QtGui.QMdiArea)
	mdiarea.tileSubWindows()



def delo(label):
	''' delete object by given label'''
	try:
		c=App.ActiveDocument.getObjectsByLabel(label)[0]
		App.ActiveDocument.removeObject(c.Name)
	except: pass

def stop():
	''' stop eventserver'''

	mw=QtGui.qApp
	ef=FreeCAD.eventfilter
	mw.removeEventFilter(ef)
	ef.keyPressed2=False
	ef.dialog.hide()

	for l in ("Cursor","Target","TargetCurve"):
		delo(l)
		pass

	print "stopped "


def undock(label='Spreadsheet'):
	''' open the data spreadsheet as top level window'''

	#activate eventmanager for ss
	a=App.ActiveDocument.MyNeedle
	a.Proxy.startssevents()

	mw=FreeCADGui.getMainWindow()
	mdiarea=mw.findChild(QtGui.QMdiArea)

	sws=mdiarea.subWindowList()
	print "windows ..."
	for w2 in sws:
		print str(w2.windowTitle())
		if str(w2.windowTitle()).startswith(label):
			sw=w2
			bl=w2.children()[3]
			blcc=bl.children()[2].children()

			w=QtGui.QWidget()
			w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

			box = QtGui.QVBoxLayout()
			w.setLayout(box)
			ss=blcc[3]
			box.addWidget(ss)
			# ss.setParent(w)
			w.setGeometry(50, 30, 1650, 350)
			w.show()
			sw.close()
			return w


try: stop()
except: pass

'''


'''
