# create pattern for a sketch

import networkx as nx
import numpy as np
import random
from nurbswb.say import *

def vkey(vec):
	'''vector as key'''
	return tuple((round(vec[0],5),round(vec[1],5),round(vec[2],5)))




def splitEdges(obj=None):
	'''split edges on intersection points'''


	if obj==None:
		obj=Gui.Selection.getSelection()[0]

	es=obj.Shape.Edges

	g=nx.Graph()
	points={}
	vecs=[]


	# register all vertexes of the shape
	for vi,v in enumerate(obj.Shape.Vertexes):
		p=vkey(v.Point)
		points[tuple(p)]=vi
		vecs +=  [p]

	# register all edges of the shape
	for e in es:
		assert len(e.Vertexes)==2
		[p,q]=e.Vertexes
		kp=vkey(p.Point)
		kq=vkey(q.Point)
		g.add_edge(points[kp],points[kq],edge=e)

	# calculate the direction of the edges for each vertex
	for n in g.nodes():

		arcl={}
		for e in g.edges(n):
			fe=g.get_edge_data(*e)['edge']
			if (fe.valueAt(fe.FirstParameter)-FreeCAD.Vector(vecs[n])).Length<0.0001:
				arc=np.arctan2(*fe.tangentAt(fe.FirstParameter)[0:2])
			else:
				vv=fe.tangentAt(fe.LastParameter)*(-1)
				arc=np.arctan2(*vv[0:2])

			arcl[arc]=e
			sk=np.sort(arcl.keys())
			arcl2=[(arcl[k],k) for k in sk]
			g.node[n]['sortedEdges']=arcl2



	# Schnittpunkte

	pts=[]
	xyplane=Part.Plane()

	cuts=[]
	for c1i,c1 in enumerate(obj.Shape.Edges):
		(cmin,cmax)=c1.ParameterRange
		cuts += [[cmin,cmax]]

	cuts2=[]
	for c1i,c1 in enumerate(obj.Shape.Edges):
		(cmin,cmax)=c1.ParameterRange
		cuts2 += [[cmin,cmax]]

	for c1i,c1 in enumerate(obj.Shape.Edges):
		for c2i,c2 in enumerate(obj.Shape.Edges):
			c1=c1.toNurbs().Edge1
			c2=c2.toNurbs().Edge1
			if c1i<c2i:
				ips=c1.Curve.intersect2d(c2.Curve,xyplane)
				for p in ips:
					try:
						_ = points[vkey([p[0],p[1],0.0])]
					except:
						# liegt Punkt innen?
						pp=FreeCAD.Vector(p[0],p[1],0.0)
						(cmin,cmax)=c1.ParameterRange
						cp1=c1.Curve.parameter(pp)
						if cmin<cp1 and cp1<cmax:
							(cmin,cmax)=c2.ParameterRange
							cp=c2.Curve.parameter(pp)
							if (cmin<cp and cp<cmax):
								pts+=[FreeCAD.Vector(p[0],p[1])]	
								cuts[c1i] += [cp1]
								cuts2[c2i] += [cp]
								print ("schnitt",c1i,c2i,cp1,cp)

	# use the cutpoints to split all edges 
	newedges=[]
	oldedges=[]

	displayEdges=False
	for cus,cus2,e in zip(cuts,cuts2,obj.Shape.Edges):

		if len(cus)>2 and len(cus2)>2:
			cus=cus+cus2[2:]
		elif len(cus2)>2:
			cus=cus2

		if len(cus)>2:
			cus.sort()
			e=e.toNurbs().Edge1
			for i in range(len(cus)-1):
				c=e.Curve.copy()
				c.segment(cus[i],cus[i+1])
				#display the segement
				if displayEdges:
					Part.show(c.toShape())
					#App.ActiveDocument.ActiveObject.ViewObject.hide()
					App.ActiveDocument.ActiveObject.ViewObject.LineColor=(
							random.random(),random.random(),random.random())
				newedges+= [c.toShape()]
		else:
			oldedges += [e]

	if displayEdges:
		for e in oldedges:
				Part.show(e)
						#App.ActiveDocument.ActiveObject.ViewObject.hide()
				App.ActiveDocument.ActiveObject.ViewObject.LineColor=(
								random.random(),random.random(),random.random())


	# compound of all splitted esges
	Part.show(Part.Compound(newedges+oldedges))
	App.ActiveDocument.ActiveObject.ViewObject.PointColor=(1.,0.,0.)
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,1.,1.)
	App.ActiveDocument.ActiveObject.ViewObject.PointSize=6
	obj=App.ActiveDocument.ActiveObject
	obj.Label="split Edge" 

	return newedges+oldedges

#points={}
#vecs=[]
#g=nx.Graph()





def createPattern(obj=None,rx=3,ry=2):
	'''create pattern subobjects'''

	if obj==None:
		obj=Gui.Selection.getSelection()[0]

	comp=obj.Shape

	# size of the pattern:
	sizex,sizey=3000,2000
	# repeats of the pattern rx,ry

	
	es=comp.Edges

#	global points,vecs,g
	points={}
	vecs=[]
	g=nx.Graph()

	for vi,v in enumerate(comp.Vertexes):
		p=vkey(v.Point)
		points[tuple(p)]=vi
		vecs +=  [p]

	for e in es:
		[p,q]=e.Vertexes
		kp=vkey(p.Point)
		kq=vkey(q.Point)
		g.add_edge(points[kp],points[kq],edge=e)


	for n in g.nodes():
		arcl={}
		for e in g.edges(n):
			fe=g.get_edge_data(*e)['edge']
			if (fe.valueAt(fe.FirstParameter)-FreeCAD.Vector(vecs[n])).Length<0.001:
				arc=np.arctan2(*fe.tangentAt(fe.FirstParameter)[0:2])
			else:
				vv=fe.tangentAt(fe.LastParameter)*(-1)
				arc=np.arctan2(*vv[0:2])

			arcl[arc]=e

		sk=np.sort(arcl.keys())
		arcl2=[(arcl[k],k) for k in sk]
		g.node[n]['sortedEdges']=arcl2



	def find_segment_step(n,alt,*a):
		'''find the next edge/vertex of a area segment'''
		se=g.node[n]['sortedEdges']
		pol=[n,alt]+ list(a)


		for i,(e,arc) in enumerate(se):
			(n1,n2)=e
			if n2==alt:
				(e,arc)=se[i-1]
				(n1,n2)=e
				pol =[n2] + pol
				if n1==n:
					return n2
#				else:
#					return (n2,n1)

		return None



	def show(pol):
		'''display the segment pattern'''

		print ("display border--------------------------------- ",pol)
		tz=App.ActiveDocument.addObject("Part::Feature","tracks")
		tz.ViewObject.LineColor=(random.random(),random.random(),random.random())
		tz.ViewObject.ShapeColor=tz.ViewObject.LineColor
		tz.ViewObject.LineWidth=3

		if 0: # display simplified polygon only
			pts=[FreeCAD.Vector(vecs[p]) for p in pol]
			tz.Shape=Part.makePolygon(pts)

		comps=[]
#		print "offssets----------------------------------------------------------"
#		print offsets
#		print 
		for j in range(len(pol)-1):
#			if g.get_edge_data(pol[j],pol[j+1])==None:
##				#continue
#	#			print "keine Kante robiere offset" 
#				print ("wolltebn",pol[j],pol[j+1])
#				print "------------------"
#				for (j2,off2) in  offsets[j]:
#				#	print ("off ",j2,off2)
#
#				#	print g.get_edge_data(pol[j+1],pol[j2])['edge']
#					#comps += [g.get_edge_data(pol[j+1],pol[j2])['edge']]
#					ess=g.get_edge_data(pol[j+1],pol[j2])['edge'].copy()
#				#	print "!!",FreeCAD.Vector(off2)
#					ess.Placement.Base = FreeCAD.Vector(off2)
#					print ("nehmen versetzt",pol[j+1],pol[j2])
#					ess.Placement.Base += FreeCAD.Vector(-00,00,0)
#					#print "POSS",ess.Placement.Base
#					comps += [ess]
#					print "--------XX-----"
#				#	print ("XX",j2,off2)
#			else:
#				print "normal weiter"
#				print ("nehmen direkt",pol[j],pol[j+1])
#				#print g.get_edge_data(pol[j],pol[j+1])['edge']

			comps += [ g.get_edge_data(pol[j],pol[j+1])['edge']]

#		print "comps ",comps


#		comps=[ g.get_edge_data(pol[j],pol[j+1])['edge'] for j in range(len(pol)-1)]

		if 10: # display curves compound
			tz.Shape=Part.Compound(comps)



		# display faces
		s1=Part.makeFilledFace(Part.__sortEdges__(comps))
		if s1.isNull(): raise RuntimeError('Failed to create face')
		col=[]
		
		for xc in range(rx):
			for yc in range(ry):
				sn=s1.copy()
				sn.Placement.Base.x=sizex*xc
				sn.Placement.Base.y=sizey*yc
				col +=[sn]

		tz.Shape=Part.Compound(col+comps)
		tz.Placement.Base.z=random.random()-tz.Shape.Area*0.00001



	def find_all_segments():
		'''find all closed areas'''

		lg=max(g.nodes())+1
		used=np.zeros(lg*lg).reshape(lg,lg)

		for n in g.nodes():
			for n2 in g.nodes():
				liste=[n,n2]
				start=liste[0]
				liste2=liste
				rc=-1

				while rc!=None and rc not in liste:

					liste=liste2
					rc=find_segment_step(*liste)
					try:
						[rc1,rc2]=rc
						liste2 = [rc1,rc2]+liste
						rc=rc1
					except:
						liste2 = [rc]+liste
#				print "fertig while ",liste2

				if (liste2[0]==liste2[-1] or liste2[1]==liste2[-1]) and len(liste2)>3 :
#					print "auswertugn"
					if liste2[1]==liste2[-1]:
						liste2=liste2[1:]
					if not used[liste2[0],liste2[1]] and not used[liste2[1],liste2[2]] :
						show(liste2)
					for i in range(len(liste2)):
						used[liste2[i-1],liste2[i]]=1
				Gui.updateGui()


	find_all_segments()


def createSinglePattern():
	createPattern(obj=None,rx=1,ry=1)


def createArray():
	''' array aus edges machen'''
	#obj=FreeCAD.ActiveDocument.Sketch
	edges=[]

	for obj in Gui.Selection.getSelection():
		edges += obj.Shape.Edges

	es2=[]
	xc=3
	yc=2
	for xi in range(xc):
		for yi in range(yc):
			for e in edges:
				e2=e.copy()
				e2.Placement.Base.x += 1000*xi
				e2.Placement.Base.y += 1000*yi
				es2 += [e2]


	a=FreeCAD.Vector(0,0)
	b=FreeCAD.Vector(xc*1000,0)
	d=FreeCAD.Vector(0,yc*1000)
	c=FreeCAD.Vector(xc*1000,yc*1000)

	es2 += [Part.makePolygon([a,b,c,d,a])]

	Part.show(Part.Compound(es2))
	App.ActiveDocument.ActiveObject.Label="Array from generic pattern"
	return App.ActiveDocument.ActiveObject



def removeEdges():
	'''remove selected edges from collection'''

	sel=Gui.Selection.getSelectionEx()[0]


	todelete=[]
	for sun in sel.SubElementNames:
		en=int(sun[4:])-1
		print en
		todelete += [en]

	print todelete
	eds=sel.Object.Shape.Edges
	eds2=[]
	for i,e in enumerate(eds):
		if i not in todelete:
			eds2+= [e]
		else:
			print "skip",i

	Part.show(Part.Compound(eds2))
	if 0:
		sel.Object.ViewObject.hide()
	else:
		sel.Object.ViewObject.LineWidth=1
		sel.Object.ViewObject.LineColor=(1.,1.,1.)
		App.ActiveDocument.ActiveObject.ViewObject.LineColor=(0.,0.,1.)
		App.ActiveDocument.ActiveObject.ViewObject.LineWidth=10



if 0:


	obj=createArray()


	# testdaten default Sketch
	#obj=App.ActiveDocument.Sketch#001
	#obj=App.ActiveDocument.Shape#001

	newedges=splitEdges(obj)

	# compound of all splitted esges
	Part.show(Part.Compound(newedges))
	App.ActiveDocument.ActiveObject.ViewObject.PointColor=(1.,0.,0.)
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=(1.,1.,1.)
	App.ActiveDocument.ActiveObject.ViewObject.PointSize=6
	obj=App.ActiveDocument.ActiveObject
	obj.Label="split Edge" 

	#App.ActiveDocument.ActiveObject.ViewObject.hide()

	# new we start again to find the area segments
	comp=Part.Compound(newedges)
	createPattern(comp)

#
