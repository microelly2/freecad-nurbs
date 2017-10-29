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


import Part

import networkx as nx
import matplotlib.pyplot as plt

import networkx as nx


s=Gui.Selection.getSelection()
s0=s[0]
sp=s0.Shape


g=nx.Graph()


def ptokey(v):
	return (round(v.x,2),round(v.y,2),round(v.z,2))




points={}

for i,v in enumerate(sp.Vertexes):
	pp=(round(v.Point.x,2),round(v.Point.y,2),round(v.Point.z,2))
	try: points[pp]
	except: 
		points[pp]=i
		g.add_node(i,pos=(v.Point.x,v.Point.y),keys=[],quality=0)

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
		for e in es:
			sl += g.edge[n][e]['vector'].Length
			vs += g.edge[n][e]['vector']

		vsn=FreeCAD.Vector(vs)
		vsn.normalize()

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


if 0: # display in matplotlib
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
	''' diasplay neigbor edges as Part'''
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
				g.node[n]['quality']=i
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




kp=createKeys()
setQuality(g.nodes(),kp)

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




def run():
	print "run huhu"
