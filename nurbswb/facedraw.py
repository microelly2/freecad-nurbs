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
			if event.buttons() == QtCore.Qt.NoButton:
				pos = event.pos()
				x=pos.x()
				y=pos.y()
#				print ("mouse pos ",x,y)
				(x,y)=Gui.ActiveDocument.ActiveView.getCursorPos()
				print ("cursor pos",x,y)
				t=Gui.ActiveDocument.ActiveView.getObjectsInfo((x,y))
				if t<>None:
					for tt in t:
#						if tt['Object']=='Sphere' and tt['Component']=='Face1':
						if tt['Object']==self.objname and tt['Component']==self.subelement:

							print (tt['x'],tt['y'],tt['z'])
							self.x,self.y,self.z=tt['x'],tt['y'],tt['z']
							break

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


					elif e.key()== QtCore.Qt.Key_Enter or e.key()== QtCore.Qt.Key_Return:
#						say("------------Enter-----------------")
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
 						if r in ['l','r']:

							print ("KEY pressed ----------------------",r)
							vf=FreeCAD.Vector(self.x,self.y,self.z)
							try:
								self.pts += [vf]
							except:
								self.pts = [FreeCAD.Vector(),vf]

							self.wire.Shape=Part.makePolygon(self.pts)

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





class MyWidget(QtGui.QWidget):
	'''edit pole mastre dialog'''

	def commit(self):
		stop()

	def cancel(self):
		stop()


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

	btn=QtGui.QPushButton("Cancel")
	btn.clicked.connect(w.cancel)

	cobtn=QtGui.QPushButton("Commit and stop")
#	cobtn.clicked.connect(w.commit)


	cbtn=QtGui.QPushButton("Stop Dialog (preserve Aux)")
	cbtn.clicked.connect(stop)

	poll=QtGui.QLabel("Selected  Pole:")

	dial=QtGui.QDial() 
	dial.setNotchesVisible(True)
	dial.setValue(FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetInt("Cursor",0))
#	dial.valueChanged.connect(w.setcursor2)
	w.dial=dial


	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	
	for ww in [btn,dial] :
		box.addWidget(ww)

	return w


import time
def start(source='Backbone'):
	'''create and initialize the event filter'''



	ef=EventFilter()
	ef.mouseWheel=0
	ef.mode='r'
	try:
			s=Gui.Selection.getSelectionEx()
			ef.objname=s[0].Object.Name
			ef.subelement=s[0].SubElementNames[0]
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


	ef.wire=w

	ef.dialog=dialog(source)
	ef.dialog.ef=ef


	ef.dialog.show()




def delo(label):
	''' delete object by given label'''
	try:
		c=App.activeDocument().getObjectsByLabel(label)[0]
		App.activeDocument().removeObject(c.Name)
	except: pass

def stop():
	''' stop eventserver'''

	mw=QtGui.qApp
	ef=FreeCAD.eventfilter
	mw.removeEventFilter(ef)
	ef.keyPressed2=False
	ef.dialog.hide()



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
