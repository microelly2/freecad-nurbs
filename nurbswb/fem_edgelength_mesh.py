import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import Part,Points

import networkx as nx
import matplotlib.pyplot as plt
import random
import os 
import nurbswb

import networkx as nx
import matplotlib.pyplot as plt
import random
import os 
import nurbswb


if 0:
	# load a testfile
	try:
		FreeCAD.open(u"/home/thomas/Schreibtisch/netz_test_data.fcstd")
		App.setActiveDocument("netz_test_data")
		App.ActiveDocument=App.getDocument("netz_test_data")
		Gui.ActiveDocument=Gui.getDocument("netz_test_data")
	except: pass


def copySketch(source,target):
	'''Sketch uebernehmen'''
	for g in source.Geometry:
		target.addGeometry(g)
	for eg in source.ExternalGeometry:
#		print (eg,	eg[0],eg[1])
		for g in eg[1]:
			target.addExternal(eg[0].Name,g)
	for i,c in enumerate(source.Constraints):
#		print i,c
		target.addConstraint(c)



def run(animate=True):

	def get_sval(s):
		'''parse the content substring of a geometry '''
		(a,b)=s.split("=")
		return int(eval(b))


	# open and reset the force visualisation sketch
	ska=App.ActiveDocument.getObject("Force")
	if ska==None:
		ska=App.ActiveDocument.addObject('Sketcher::SketchObject','Force')
		ska.ViewObject.LineColor=(1.0,.0,.0)
		ska.ViewObject.LineWidth=4

	gct=ska.GeometryCount
	for i in range(gct):
		ska.delGeometry(gct-i-1)

	ska.solve()


	if 1:

		# modul variables
		g=nx.Graph()
		points={}

		sks=Gui.Selection.getSelection()[0]
		
		sk=App.ActiveDocument.addObject('Sketcher::SketchObject',"CopySim_" + sks.Name)
		sk.Label='Copy of ' + sks.Label
		copySketch(sks,sk)

		for i,geo in enumerate(sk.Geometry):
	#		print geo.__class__.__name__
			if geo.__class__.__name__ <>  'LineSegment': continue
	#		print (i,geo.StartPoint,geo.EndPoint)
			g.add_node((i,1))
			g.add_node((i,2))




		for c in sk.Constraints:
		#	print c.Content
			tt=c.Content.split(' ')
			if  tt[2]<>'Type="1"': continue

			First=get_sval(tt[4])
			FirstPos=get_sval(tt[5])
			Second=get_sval(tt[6])
			SecondPos=get_sval(tt[7])

			if First=='-1' or Second=='-1': 
				continue

			g.add_edge(
					(int(First),int(FirstPos)),
					(int(Second),int(SecondPos))
				)

		# umwandeln in echten topologischen graphen
		conix={}
		g2=nx.Graph()

		for i,cons in enumerate(nx.connected_components(g)):
			conix[i]=cons
			g2.add_node(i)

		def findnode(n):
			for k in conix:
				if n in conix[k]:
					return k
			print "findnode fehler bei ",n
			return -1


		for i,geo in enumerate(sk.Geometry):

			# circle radius as 2D height
			if geo.__class__.__name__ ==  'Circle': 
				n1=findnode((i,3))
				g2.node[n1]['vector']= sk.getPoint(i,3)
				g2.node[n1]['radius']= 1.0*geo.Radius
				print ("circle found",geo.Radius,n1)
				continue

			# process only lines 
			if geo.__class__.__name__ <>  'LineSegment': continue

			n1=findnode((i,1))
			g2.node[n1]['vector']= sk.getPoint(i,1)
			n2=findnode((i,2))
			g2.node[n2]['vector']= sk.getPoint(i,2)
			g2.add_edge(n1,n2)

		rc=sk.solve()
		rc=App.activeDocument().recompute()

		for n2 in g2.nodes():
			try: z=g2.node[n2]['radius']
			except: 
				g2.node[n2]['radius']=0
				z=0

			if g2.node[n2]['radius']==0: 
				# gravitation
				z=-1

			g2.node[n2]['vector'].z=z
#			print "######              ",g2.node[n2]['vector'],g2.node[n2]['radius']


		loops=10
		for lp in range(10*loops+1):

			gct=ska.GeometryCount
			for i in range(gct):
				ska.delGeometry(gct-i-1)

			ska.solve()


			f=0.01
			col=[]
			sumforces=0

			for n in g2.nodes():

				#
				#
				# calculate the force in node n
				#
				#

				nbs=g2.neighbors(n)
				v0=g2.node[n]['vector']
				r=FreeCAD.Vector()

				for nb in nbs:

					#model A
					if 1:
						mk=2
						tf=g2.node[nb]['vector'] -v0 
						if tf.Length > mk:
							fac= 1.0*(tf.Length-mk)/mk
							tf=tf * fac
						else:
							tf= FreeCAD.Vector()

					#model B
					if 0:
						tf=g2.node[nb]['vector'] -v0 

					r += tf

				force=r*f

				#
				# apply the force
				#

				sumforces +=  force.Length
				vrc=v0+ force
				g2.node[n]['vector2']=vrc

				(a,b)=list(conix[n])[0]
				rc=sk.movePoint(a,b,vrc,0)

				rc=sk.solve()
				v1=sk.getPoint(a,b)

				g2.node[n]['vector2']=v1
				if vrc.z>0:
					g2.node[n]['vector2'].z=vrc.z

				# if a height is given by a circle preserve this value
				if g2.node[n]['radius']<>0:
					g2.node[n]['vector2'].z=g2.node[n]['radius']


				if force.Length> 0.1:
					ska.addGeometry(Part.Circle(v1,App.Vector(0,0,1),force.Length),False)
					ska.addGeometry(Part.LineSegment(v1,v1+force),False)

			#create the 3D model
			for e in g2.edges():
				(a,b)= e
				h=FreeCAD.Vector(0,0,random.random()*20)
				col += [Part.LineSegment(g2.node[a]['vector2'],g2.node[b]['vector2']).toShape()]

			color=(random.random(),random.random(),random.random())

			if animate: # update grid
				try:
					n3=FreeCAD.ActiveDocument.getObject("grid")
					if n3==None:
						n3=FreeCAD.ActiveDocument.addObject("Part::Feature","grid")
					n3.Shape=Part.Compound(col)
				except:
					Part.show(Part.Compound(col))
			else: # create new grif each time
				if lp % 2 == 0:
					#try:FreeCAD.ActiveDocument.ActiveObject.ViewObject.hide()
					#except: pass
					n3=FreeCAD.ActiveDocument.addObject("Part::Feature","grid")
					n3.Shape=Part.Compound(col)
					n3.ViewObject.Transparency=70
					n3.ViewObject.LineColor=color

			rc=App.activeDocument().recompute()
			print ("SUM FORCES",sumforces)
			Gui.updateGui()


			for n in g2.nodes():
				g2.node[n]['vector']=g2.node[n]['vector2']

			# erzuegen einer flaeche
		if 1:
			import numpy as np

			pts=[]

			for b in range(4):
				for a in range(5):
					n=findnode((a+b*5,1))
					pts.append(g2.node[n]['vector2'])
				n=findnode((a+b*5,2))
				pts.append(g2.node[n]['vector2'])


			pts=np.array(pts).reshape(4,6,3)
			bs=Part.BSplineSurface()
			bs.interpolate(pts)
			if 0:
				try:
					shape=App.ActiveDocument.Shape001
					shape.Shape=bs.toShape()
				except:
					Part.show(bs.toShape())
			else:
				n3=FreeCAD.ActiveDocument.addObject("Part::Spline","face")
				n3.Shape=bs.toShape()
				n3.ViewObject.Transparency=70
				n3.ViewObject.ShapeColor=color


		rc=App.activeDocument().recompute()

if __name__=='__manin__':
	run()
