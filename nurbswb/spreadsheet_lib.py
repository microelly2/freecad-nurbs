# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- spreadsheet an dnumpy for nurbs
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
# 
# daten ins spreadsheet und zurueck 
#
#


import FreeCAD,Part,Draft

App=FreeCAD

import numpy as np
import random

def cellname(col,row):
		#still limit to 26
		if col>90-64:
			raise Exception("not implement " + str(col))
		char=chr(col+64)
		cn=char+str(row)
		return cn

assert cellname(1,2)=='A2'
assert cellname(3,4)=='C4'

def createSpreadsheet(label='Spreadsheet'):
	ss=App.ActiveDocument.getObject(label)
	if ss==None:
		ss=App.ActiveDocument.addObject('Spreadsheet::Sheet',label)
		ss.set('A1','UPoles')
		ss.set('A2','VPoles')
		ss.set('A9','Poles or Points')
		ss.set('A10','u/v and z')

		ss.set('B1','0')
		ss.setAlias('B1','NbUPoles')
		ss.set('B2','0')
		ss.setAlias('B2','NbVPoles')

	return ss

def getSpreadsheet(label='Spreadsheet'):
	return createSpreadsheet(label)

def gendata(spreadsheet,spheremode=False):
		# fill sheat
		ss=spreadsheet

		NbUPoles=13
		NbVPoles=17

		if not spheremode:
			# linear model
			x=200.0*np.array(range(NbUPoles))
			y=300.0*np.array(range(NbVPoles))

		else:
			#arc model
			x=360.0/(NbUPoles)*np.array(range(NbUPoles))
			y=180.0/(NbVPoles)*np.array(range(NbVPoles))
			y-= 90
			x += 180.0/(NbUPoles)
			y += 90.0/(NbVPoles)

		z=700.0*np.random.random(NbUPoles*NbVPoles)
		z=z.reshape(NbUPoles,NbVPoles)

		ss.set('A1','UPoles')
		ss.set('A2','VPoles')
		ss.set('A9','Poles or Points')
		ss.set('A10','u/v and z')

		ss.set('B1',str(NbUPoles))
		ss.setAlias('B1','NbUPoles')
		ss.set('B2',str(NbVPoles))
		ss.setAlias('B2','NbVPoles')

		for u in range(NbUPoles):
			cn=cellname(u+2,10)
			ss.set(cn,str(x[u]))

		for v in range(NbVPoles):
			cn=cellname(1,11+v)
			ss.set(cn,str(y[v]))

		for v in range(NbVPoles):
			for u in range(NbUPoles):
				cn=cellname(u+2,10+v+1)
				ss.set(cn,str(z[u,v]))

		App.activeDocument().recompute()


def table2array(spreadsheet):
	''' create array from table'''

	ss=spreadsheet

	NbUPoles = int(ss.NbUPoles)
	NbVPoles = int(ss.NbVPoles)

	x=[]
	for u in range(int(ss.NbUPoles)):
		cn=cellname(u+2,10)
		x.append(ss.get(cn))

	y=[]
	for v in range(int(ss.NbVPoles)):
		cn=cellname(1,11+v)
		y.append(ss.get(cn))

	z=[]
	for v in range(NbVPoles):
		for u in range(NbUPoles):
			cn=cellname(u+2,10+v+1)
			print cn
			z.append(ss.get(cn))

	ps=[]
	for v in range(NbVPoles):
		for u in range(NbUPoles):
			p=[x[u],y[v],z[v*NbUPoles+u]]
			print p
			ps.append(p)

	ps=np.array(ps).reshape(NbVPoles,NbUPoles,3)
	return ps


def tabletop(spreadsheet):
	''' the first dimension data'''

	ss=spreadsheet

	NbUPoles = int(ss.NbUPoles)
	NbVPoles = int(ss.NbVPoles)

	x=[]
	for u in range(int(ss.NbUPoles)):
		cn=cellname(u+2,10)
		x.append(ss.get(cn))

	return np.array(x)


def tableleft(spreadsheet):
	''' the 2nd dimension data'''

	ss=spreadsheet

	NbUPoles = int(ss.NbUPoles)
	NbVPoles = int(ss.NbVPoles)

	y=[]
	for v in range(int(ss.NbVPoles)):
		cn=cellname(1,11+v)
		y.append(ss.get(cn))

	return np.array(y)


def setSpreadsheet(ss,x,y,z):

	NbUPoles=len(x)
	NbVPoles=len(y)

	ss.set('B1',str(len(x)))
	ss.set('B2',str(len(y)))

	for u in range(NbUPoles):
		cn=cellname(u+2,10)
		ss.set(cn,str(x[u]))

	for v in range(NbVPoles):
		cn=cellname(1,11+v)
		ss.set(cn,str(y[v]))

	for v in range(NbVPoles):
		for u in range(NbUPoles):
			cn=cellname(u+2,10+v+1)
			ss.set(cn,str(z[u,v]))

	App.activeDocument().recompute()


def table2Nurbs(ss,label="MyNurbs"):
	''' create nurbs from table'''

	NbUPoles = int(ss.NbUPoles)
	NbVPoles = int(ss.NbVPoles)

	x=[]
	for u in range(int(ss.NbUPoles)):
		cn=cellname(u+2,10)
		x.append(ss.get(cn))

	y=[]
	for v in range(int(ss.NbVPoles)):
		cn=cellname(1,11+v)
		y.append(ss.get(cn))

	z=[]
	for v in range(NbVPoles):
		for u in range(NbUPoles):
			cn=cellname(u+2,10+v+1)
			z.append(ss.get(cn))

	ps=[]
	for v in range(NbVPoles):
		for u in range(NbUPoles):
			p=[x[u],y[v],z[v*NbUPoles+u]]
			ps.append(p)

	ps=np.array(ps).reshape(NbVPoles,NbUPoles,3)

	bs=Part.BSplineSurface()

	kv=[1.0/(NbVPoles-1)*i for i in range(NbVPoles)]
	ku=[1.0/(NbUPoles-1)*i for i in range(NbUPoles)]

	bs.buildFromPolesMultsKnots(ps,
					[3] +[1]*(NbVPoles-2) +[3],
					[3]+[1]*(NbUPoles-2)+[3],
					kv,
					ku,
					False,False
					,3,3)

	sha=bs.toShape()
	sp=App.ActiveDocument.addObject("Part::Spline",label)
	sp.Shape=sha
	sp.ViewObject.ControlPoints = True
	sp.ViewObject.ShapeColor = (random.random(),random.random(),random.random())


def array2Nurbs(arr,a,b,c,d,label="MyArrayNurbs",borderPoles=False):
	''' create nurbs from array'''

	ps=arr[a:a+b,c:c+d]
	NbVPoles,NbUPoles,_t1 =ps.shape

	bs=Part.BSplineSurface()

	if borderPoles:
		kv=[1.0/(NbVPoles-1)*i for i in range(NbVPoles)]
		ku=[1.0/(NbUPoles-1)*i for i in range(NbUPoles)]
		mv=[3] +[1]*(NbVPoles-2) +[3]
		mu=[3]+[1]*(NbUPoles-2)+[3]
	else:
		kv=[1.0/(NbVPoles+3)*i for i in range(NbVPoles+4)]
		ku=[1.0/(NbUPoles+3)*i for i in range(NbUPoles+4)]
		mv=[1]*(NbVPoles+4)
		mu=[1]*(NbUPoles+4)

	print (ps.shape,ku,kv)
	bs.buildFromPolesMultsKnots(ps, mv, mu, kv, ku, False,False ,3,3)

# fehler,wenn tolerance kleiner #+#
#	bs.insertUKnot(0.2,1,0.1)
#	bs.insertVKnot(0.2,1,0.1)

	sha=bs.toShape()
	sp=App.ActiveDocument.addObject("Part::Spline",label)
	sp.Shape=sha
	sp.ViewObject.ControlPoints = True
	sp.ViewObject.ShapeColor = (random.random(),random.random(),random.random())



#-----------------------------------
#
# test cases
#
#

if __name__=='__main__':
	ss1=createSpreadsheet(label='MySpreadsheet')
	gendata(ss1)
	table2Nurbs(ss1,"simpe gen data")


	ss1=getSpreadsheet('MySpreadsheet')
	ss1.set("E15","-4000")
	App.activeDocument().recompute()
	table2Nurbs(ss1,"E15")


	#--------------------------------------------


	pps=table2array(ss1)
	pps.shape
	array2Nurbs(pps,1,9,1,11)

	array2Nurbs(pps,3,9,2,11)

	array2Nurbs(pps,1,11,3,11)

	pps[6,8,2]=2000
	array2Nurbs(pps,1,11,3,11)

	pps[4,6,2]=2000
	array2Nurbs(pps,1,11,3,11)

	pps[3,6,2]=-2000
	array2Nurbs(pps,0,11,3,11)




	xs=tabletop(ss1)
	xs

	ys=tableleft(ss1)
	ys




	# example from numpy 
	x = np.arange(-5.00, 5.00, 0.5)
	y = np.arange(-5.00, 5.00, 0.5)
	xx, yy = np.meshgrid(x, y)
	z = np.sin(xx**2+yy**2)

	setSpreadsheet(ss1,x,y,z)
	table2Nurbs(ss1,"initial")


	z[4:7,4:7]=5
	setSpreadsheet(ss1,x,y,z)
	table2Nurbs(ss1,"mountain 5")


	z[5:10,12:20]=3
	setSpreadsheet(ss1,x,y,z)

	table2Nurbs(ss1,"mountain 3")

	z = (xx-3)*(xx+4)*xx+yy**2
	z *= 0.1
	setSpreadsheet(ss1,x,y,z)
	table2Nurbs(ss1,"sum of cubic x and square y")

	z=np.sin(2*xx)+yy**2*0.1
	setSpreadsheet(ss1,x,y,z)
	table2Nurbs(ss1,"sum of sin and square")



