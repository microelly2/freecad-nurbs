
import FreeCADGui as Gui
import FreeCAD,Part,Sketcher
App=FreeCAD

import Draft
import numpy as np


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


import numpy as np

def run(name='ribbow',moves=[],box=[40,0,-40,30]):
	

	label=name
	try: body=App.activeDocument().Body
	except:	body=App.activeDocument().addObject('PartDesign::Body','Body')

	sk=App.activeDocument().addObject('Sketcher::SketchObject',name)
	sk.Label=label
	sk.MapMode = 'FlatFace'

	App.activeDocument().recompute()

	pts=None

	if pts==None: # some test data
		anz=16
		r=50
		pts= [FreeCAD.Vector(r*np.sin(2*np.pi/anz*i),r*np.cos(2*np.pi/anz*i)+50,0) for i in range(anz)]

	for i,p in enumerate(pts):
		sk.addGeometry(Part.Circle(App.Vector(int(round(p.x)),int(round(p.y)),0),App.Vector(0,0,1),10),True)
		if 0:
			#if i == 1: sk.addConstraint(Sketcher.Constraint('Radius',0,10.000000)) 
			if i>0: sk.addConstraint(Sketcher.Constraint('Equal',0,i)) 
		else:
			radius=2.0
			sk.addConstraint(Sketcher.Constraint('Radius',i,radius)) 
			sk.renameConstraint(i, 'Weight ' +str(i+1))


	k=i+1

	l=[App.Vector(int(round(p.x)),int(round(p.y))) for p in pts]

	if 0:
		# open spline
		sk.addGeometry(Part.BSplineCurve(l,False),False)
	else:
		# periodic spline
		sk.addGeometry(Part.BSplineCurve(l,True),False)

	conList = []
	for i,p in enumerate(pts):
		conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',i,3,k,i))
	sk.addConstraint(conList)
	App.activeDocument().recompute()

	for p in range (0,anz):
		ll=sk.addGeometry(Part.LineSegment(App.Vector(100+10*p,100+10*p,0),App.Vector(-100,-100,0)),False)
		sk.toggleConstruction(ll) 
		sk.addConstraint(Sketcher.Constraint('Coincident',p,3,ll,1)) 
		App.ActiveDocument.recompute()
		if p==anz-1: p=-1
		sk.addConstraint(Sketcher.Constraint('Coincident',p+1,3,ll,2)) 
		App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('Parallel',32,17)) 

	sk.addConstraint(Sketcher.Constraint('Parallel',20,21)) 

	sk.addConstraint(Sketcher.Constraint('Parallel',23,24)) 
	sk.addConstraint(Sketcher.Constraint('Parallel',24,25)) 
	sk.addConstraint(Sketcher.Constraint('Parallel',25,26)) 

	sk.addConstraint(Sketcher.Constraint('Parallel',28,29)) 

	sk.addConstraint(Sketcher.Constraint('Horizontal',17)) 
	sk.addConstraint(Sketcher.Constraint('Horizontal',23)) 

	sk.addConstraint(Sketcher.Constraint('Vertical',20)) 
	sk.addConstraint(Sketcher.Constraint('Vertical',28)) 


	sk.addConstraint(Sketcher.Constraint('Equal',20,21)) 
	sk.addConstraint(Sketcher.Constraint('Equal',28,29)) 
	sk.addConstraint(Sketcher.Constraint('Equal',32,17)) 

	sk.addConstraint(Sketcher.Constraint('Equal',23,26)) 
	sk.addConstraint(Sketcher.Constraint('Symmetric',25,2,24,1,24,2))

	App.activeDocument().recompute()
	Gui.SendMsgToActiveView("ViewFit")

	dd=2
	d=sk.addConstraint(Sketcher.Constraint('Distance',20,dd)) 
	print ("datum",d) 
	sk.addConstraint(Sketcher.Constraint('Distance',23,dd)) 

	sk.addConstraint(Sketcher.Constraint('Distance',25,dd)) 
	sk.addConstraint(Sketcher.Constraint('Distance',28,dd)) 
	sk.addConstraint(Sketcher.Constraint('Distance',32,dd)) 
	
	


	[r,b,l,t]=box
	print (r,l,t,b)
	
	sk.movePoint(0,0,App.Vector(0,t,0),0)
	App.activeDocument().recompute()

	sk.movePoint(2,0,App.Vector(r,t,0),0)
	App.activeDocument().recompute()
	sk.movePoint(14,0,App.Vector(l,t,0),0)
	App.activeDocument().recompute()
	sk.movePoint(4,0,App.Vector(r,b+dd,0),0)
	App.activeDocument().recompute()

	sk.movePoint(12,0,App.Vector(l,b+dd,0),0)
	App.activeDocument().recompute()

	sk.movePoint(8,0,App.Vector(0,b,0),0)
	App.activeDocument().recompute()

	print (name,"moves ...")
	for [k,x,y] in moves:
		print (k,x,y)
		sk.movePoint(k,3,App.Vector(x,y,0),0)
		App.activeDocument().recompute()

	return sk





if 0:
	sk1=run("rib1",[[8,0,0],[0,0,120],[4,120,-10],[12,-130,0]])
	sk2=run("rib2",[[8,0,0],[0,0,150],[4,70,10],[12,-90,10]])


# sk3=run("rib3",[[8,0,0]],[40,-10,-40,30])



