# -*- coding: utf-8 -*-
#-------------------------------------------------
#--
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


#\cond
import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


import Part,Points

import networkx as nx
import matplotlib.pyplot as plt

import networkx as nx

import random



def ptokey(v):
	return (round(v.x,2),round(v.y,2),round(v.z,2))



def rf(v):
	''' vector modification hook'''
	return v
	ff=0.001
	return v+ FreeCAD.Vector(ff*random.random(),ff*random.random(),ff*random.random())


def createFaceMidPointmodel(a):
	'''create an extented model with facepoints'''
	fs=a.Shape.Faces

	pts=[]
	col=[]

	for f in fs:
		c=f.CenterOfMass
		pts.append(c)
		for v in f.Vertexes: 
			p=v.Point
			pts.append(p)
			col.append(Part.makeLine(rf(c),rf(p)))

	import Points
	Points.show(Points.Points(pts))

	Part.show(Part.Compound(col))
	
	return App.ActiveDocument.ActiveObject



g=nx.Graph()
points={}



def loadModel(s):

	sp=s.Shape


	for i,v in enumerate(sp.Vertexes):
		pp=(round(v.Point.x,2),round(v.Point.y,2),round(v.Point.z,2))
		try: points[pp]
		except: 
			points[pp]=i
			g.add_node(i,pos=(v.Point.x,v.Point.y),keys=[],quality=0,vector=ptokey(v.Point))

	for e in sp.Edges:

		p1=e.Vertexes[0].Point
		i1=ptokey(p1)

		p2=e.Vertexes[1].Point
		i2=ptokey(p2)

		ge=g.add_edge(points[i1],points[i2],
			weight=round(e.Length,2),
			vector=p2-p1,
			fcedge=e
			)


	# calculate some topological/metrical information for the vertexes

	for n in g.nodes():
		es=g.edge[n]
		sl=0
		vs=FreeCAD.Vector()
		vds=0

		if len(es)>0:
			esl=[]
			for i,e in enumerate(es):
				esl.append(e)
				sl += g.edge[n][e]['vector'].Length
				vs += g.edge[n][e]['vector']

			vsn=FreeCAD.Vector(vs)

	#		print vsn,vsn.Lengt

			if 0:
				if vsn.Length < 1: 
					vsn= g.edge[n][esl[0]]['vector'].cross(g.edge[n][esl[2]]['vector'])

				if vsn.Length < 1: 
					vsn= g.edge[n][esl[0]]['vector'].cross(g.edge[n][esl[1]]['vector'])

	#		for  jj in range(len(esl)):
	#			print ("!---",jj,g.edge[n][esl[jj]]['vector'])
	#		print vsn
			if vsn.Length > 1: 
				vsn.normalize()
			else: vsn=0

			for e in es:
				v = FreeCAD.Vector(g.edge[n][e]['vector'])
				v.normalize()
				vd=v.dot(vs)
				vds +=vd

		g.node[n]['ec']=len(es)
		g.node[n]['vs']=vs
		g.node[n]['sl']=sl
		g.node[n]['vds']=vds
		g.node[n]['vs']=vs

def displayMatplot():
	# display in matplotlib
	pos=nx.get_node_attributes(g,'pos')
	nx.draw(g,pos)
	plt.show()
	# plt.savefig("/tmp/path.png")


def getkey(n):
	l=g.node[n]['vs'].Length
	if l == 0: l= 100000

	return (g.node[n]['ec'],round(g.node[n]['sl']/l,16),round(g.node[n]['vds']/l,14))


#---------------------------------------------------------------------------------

def createKeys():

	kp={}

	for n in g.nodes():
			key=getkey(n)
			g.node[n]['keys']= [key]
			try: kp[key] += 1
			except: kp[key] = 1

	anz=0
	print "Keys, count occur"
	for k in kp:
		print (k,kp[k])
		if kp[k]==1: anz += 1

	print ("top level marker points", len(g.nodes()),anz)
	return kp

def setQuality(nodes,kp):
	for n in nodes:
		key=getkey(n)
		if kp[key]==1:
			g.node[n]['quality']=1



def getNeighborEdges(n):
	''' freecad edges from a point n '''
	col=[]
	nbs=g.neighbors(n)
	#print nbs
	for nb in nbs:
	#	print g.edge[n][nb]
		col +=  [g.edge[n][nb]['fcedge']]
	return col

#----------------------------------------------------

def displayNB(nodes):
	''' diasplay neighbor edges as Part'''
	col=[]
	for n in nodes:
		col +=getNeighborEdges(n)
	Part.show(Part.Compound(col))



def berechneKeyLevel(i=1):
	'''key for level i is the i-th neighbor sum of the keys'''

	# berechen keys level i>0
	for n in g.nodes():
		nbs=g.neighbors(n)
		kka={}
		aas=0
		bbs=0
		ccs=0
		for nb in nbs:
			(a,b,c)=g.node[nb]['keys'][i-1]
			aas += a
			bbs += b
			ccs += c
		try: g.node[n]['keys'][i]=(aas,bbs,ccs)
		except: g.node[n]['keys'].append((aas,bbs,ccs))


def werteausLevel(i=1):
	''' whichpoint have uniqe keys at level i'''

	# count the key occurences
	kp={}
	for n in g.nodes():
		if g.node[n]['quality']==0:
			key=g.node[n]['keys'][i]
			try: kp[key] += 1
			except: kp[key] = 1

	# which points have unique keys
	anz=0
	anzg=0

	#count the unique points
	for k in kp:
		if kp[k]==1: anz += 1

	#set the quality of the unique points 
	for n in g.nodes():
		if g.node[n]['quality']==0:
			key=g.node[n]['keys'][i]
			if kp[key]==1:
				g.node[n]['quality']=i+1
				anzg += 1
		else:
			anzg +=1

	print ("level",i,"found",anz,"found overall",anzg, "not identified till now",len(g.nodes())-anzg)
	return anz


import random
def zeigeQ(i):
	''' display the indetification quality level as Sub Grid '''
	ns=[]
	for n in g.nodes():
		if g.node[n]['quality']==i:
			ns.append(n)
	# print ns
	displayNB(ns)
	App.ActiveDocument.ActiveObject.Label="Quality" +str(i)
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(
			random.random(),random.random(),random.random())




def run():
	s=Gui.Selection.getSelection()
	mp=createFaceMidPointmodel(s[0])
	loadModel(mp)
	kp=createKeys()
	setQuality(g.nodes(),kp)


	#calculate ans display top quality nodes
	if 1:
		ns=[]
		for n in g.nodes():
			if g.node[n]['quality']==1:
				ns.append(n)
		# print ns
		displayNB(ns)
		App.ActiveDocument.ActiveObject.Label="Top Quality"
		App.ActiveDocument.ActiveObject.ViewObject.LineColor=(
				random.random(),random.random(),random.random())




	# calculate all levels
	for i in range(1,10):
		berechneKeyLevel(i=i)
		rc=werteausLevel(i=i)
		if rc==0:break

	last=i
	# zeige alle indentifizierten Punkte im Verbund
	for i in range(1,last):
		zeigeQ(i)
	
	FreeCAD.g=g
	FreeCAD.a=s[0]

	bm=s[0]
	sp=bm.Shape
	
	for i,v in enumerate(sp.Vertexes):
		pp=(round(v.Point.x,2),round(v.Point.y,2),round(v.Point.z,2))
		try:
#			print (pp,i) 
#			print ("found ",points[pp])
			gi=points[pp]

			g.node[gi]["label"]=bm.Label+":Vertex"+str(i+1)
			print g.node[gi]
		except: 
			print "NOT FOUND"
			pass

	print len(sp.Vertexes)




def displayQualityPoints():
	'''display the quality points as point clouds'''
	g=FreeCAD.g
	for q in range(1,7):
		pts=[]
		for v in g.nodes():
			#print g.node[v]['quality']
			if  g.node[v]['quality']==q: pts.append(g.node[v]['vector'])

		print pts
		if pts<>[]:
			Points.show(Points.Points(pts))
			App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(
				random.random(),random.random(),random.random())
			App.ActiveDocument.ActiveObject.ViewObject.PointSize= 10

			App.ActiveDocument.ActiveObject.Label="Points Quality " +str(q)


def printData():
	'''print some diagnostic data'''
	g=FreeCAD.g
	for v in g.nodes():
		print v
		print g.node[v]['quality']
		print g.node[v]['keys']
		print g.node[v]['vector']
		print g.node[v]['keys'][g.node[v]['quality']-1]


def addToVertexStore():
	'''add the keys to the global vertex store'''

	try: FreeCAD.PT
	except: FreeCAD.PT={}

	print "addtoVertexStore"
	g=FreeCAD.g
	a=FreeCAD.a
	for v in g.nodes():
		
		try: g.node[v]['label']
		except: g.node[v]['label']='----'
		print g.node[v]['label']

		key=(a.Label,g.node[v]['label'],v,g.node[v]['keys'][g.node[v]['quality']-1],g.node[v]['quality'])
		try:
			if key not in FreeCAD.PT[g.node[v]['vector']]:
				FreeCAD.PT[g.node[v]['vector']] += [key]
				print "added"
		except:
			#FreeCAD.PT[g.node[v]['vector']] =[(a.Label,g.node[v]['label'],v,g.node[v]['keys'][g.node[v]['quality']-1],g.node[v]['quality'])]
			FreeCAD.PT[g.node[v]['vector']] = [key]


def resetVertexStore():
	FreeCAD.PT={}
	print FreeCAD.PT

#points=nurbswb.analyse_topology_v2.points
#print "count of points and helper points"
#len(points)

def printVertexStore(): 
	'''print the vertex store'''
	print "The vertex Store"
	for j in FreeCAD.PT:
		print
		print j
		vs=FreeCAD.PT[j]
		for v in vs:
			print v

def loadTest1():
	print __file__
	# hier relativen pfad reintun
	import FreeCAD
	FreeCAD.open(u"/home/thomas/Schreibtisch/zwei_gleiche_fenster.fcstd")
	App.setActiveDocument("zwei_gleiche_fenster")
	App.ActiveDocument=App.getDocument("zwei_gleiche_fenster")
	Gui.ActiveDocument=Gui.getDocument("zwei_gleiche_fenster")



import os, nurbswb

def loadTest2():
	__dir__ = os.path.dirname(nurbswb.__file__)

	FreeCAD.open(__dir__+"/../testdata/zwei_gleiche_fenster.fcstd")
	App.setActiveDocument("zwei_gleiche_fenster")
	App.ActiveDocument=App.getDocument("zwei_gleiche_fenster")
	Gui.ActiveDocument=Gui.getDocument("zwei_gleiche_fenster")
