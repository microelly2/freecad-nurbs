'''
create some helper parts like the facebinder
for nurbs surfaces
modes are ["poleGrid","isoGrid","Surface"]

'''


from say import *


class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.obj2=obj

# grundmethoden zum sichern

	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None


class Helper(PartFeature):
	def __init__(self, obj,uc=5,vc=5):
		PartFeature.__init__(self, obj)

		self.TypeId="NurbsHelper"
		obj.addProperty("App::PropertyLink","source","XYZ","Length of the Nurbs")
		obj.addProperty("App::PropertyEnumeration","mode","XYZ","").mode=["poleGrid","isoGrid","Surface"]


	def attach(self,vobj):
		print "attach -------------------------------------"
		self.Object = vobj.Object
#		self.obj2 = vobj.Object


	def execute(self, fp):
		#say("execute yy")
		fp.ViewObject.Proxy.updateData(fp,"Execute")
		pass


	def onChanged(self, fp, prop):
		pass
		# print "changed ",prop

	def onDocumentRestored(self, fp):
		say(["onDocumentRestored",str(fp.Label)+ ": "+str(fp.Proxy.__class__.__name__)])

	def create_knotes_shape2(self):
		bs=self.obj2.source.Proxy.getBS()
		#shape=nurbswb.helper.create_knotes_shape(None,bs)

		uk=bs.getUKnots()
		vk=bs.getVKnots()

		sss=[]

		for iu in uk:
			pps=[]
			for iv in vk:
				p=bs.value(iu,iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		for iv in vk:
			pps=[]
			for iu in uk:
				p=bs.value(iu,iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		comp=Part.Compound(sss)
		self.obj2.Shape=comp
		return comp






class ViewProviderHelper:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def attach(self, obj):
		''' Setup the scene sub-graph of the view provider, this method is mandatory '''
		obj.Proxy = self
		self.Object = obj
		return

	def updateData(self, fp, prop):
		if prop == "Shape": return
		if prop == "Placement": return
		pm=fp.Placement
		if fp.source<>None:
			#say("VO updateData " + prop)
			#say((fp,fp.source,fp.mode))
			try:
				mode=fp.mode
				if mode == "poleGrid":
					# fp.Shape=fp.source.Shape
					fp.Shape=fp.source.Proxy.create_uv_grid_shape()
				elif mode == "isoGrid":
					#fp.Shape=App.ActiveDocument.Torus.Shape
					#fp.Shape=fp.source.Proxy.create_grid_shape()
					fp.Proxy.create_knotes_shape2()
				else:
					# fp.Shape=App.ActiveDocument.Cylinder.Shape
					fp.Shape=fp.source.Shape
					pass
			except:
				sayexc("Shape from Source")
			fp.Placement=pm
		else:
			#sayW("no source Shape")
			pass
		return


	def onChanged(self, vp, prop):
		# print "VO changed ",prop
		pass

	def showVersion(self):
		cl=self.Object.Proxy.__class__.__name__
		PySide.QtGui.QMessageBox.information(None, "About ", "Nurbs"  +"\nVersion 0.0"  )


	def setupContextMenu(self, obj, menu):
		cl=self.Object.Proxy.__class__.__name__
		action = menu.addAction("About " + cl)
		action.triggered.connect(self.showVersion)

		action = menu.addAction("Edit ...")
		action.triggered.connect(self.edit)

#		for m in self.cmenu + self.anims():
#			action = menu.addAction(m[0])
#			action.triggered.connect(m[1])

	def getIcon(self):

		return """
			/* XPM */
			static const char * ViewProviderNurbs_xpm[] = {
			"16 16 6 1",
			" 	c None",
			".	c #141010",
			"+	c #615BD2",
			"@	c #C39D55",
			"#	c #000000",
			"$	c #57C355",
			"        ........",
			"   ......++..+..",
			"   .@@@@.++..++.",
			"   .@@@@.++..++.",
			"   .@@  .++++++.",
			"  ..@@  .++..++.",
			"###@@@@ .++..++.",
			"##$.@@$#.++++++.",
			"#$#$.$$$........",
			"#$$#######      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			" #$#$$$$$#      ",
			"  ##$$$$$#      ",
			"   #######      "};
			"""

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None



def makeHelper():

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Helper")
	a.Label="Nurbs Helper generated"
	Helper(a)
	ViewProviderHelper(a.ViewObject)
	a.ViewObject.ShapeColor=(0.00,1.00,1.00)
	a.ViewObject.Transparency = 70
	return a






def create_subface_shape(self,bs,umin,umax,vmin,vmax):

		uk=bs.getUKnots()
		vk=bs.getVKnots()

		sss=[]

		for iu in uk[umin:umax+1]:
			pps=[]
			for iv in vk[vmin:vmax+1]:
				p=bs.value(iu,iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		for iv in vk[vmin:vmax+1]:
			pps=[]
			for iu in uk[umin:umax+1]:
				p=bs.value(iu,iv)
				pps.append(p)
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)

		comp=Part.Compound(sss)
		return comp






def split_shape(self,bs,umin,umax,vmin,vmax):

	uk=bs.getUKnots()
	vk=bs.getVKnots()

	print (len(uk),len(vk))
	tt=bs.copy()
	tt.segment(uk[umin],uk[umax],vk[vmin],vk[vmax])

	sha=tt.toShape()
	return tt,sha


def makeHelperSel():
	for obj in Gui.Selection.getSelection():
		h=makeHelper()
		h.source=obj
		h.mode="isoGrid"
		h.Placement.Base.x=2400


if __name__ == '__main__':


	try:
		App.closeDocument("Unnamed")
		App.newDocument("Unnamed")
		App.setActiveDocument("Unnamed")
		App.ActiveDocument=App.getDocument("Unnamed")
		Gui.ActiveDocument=Gui.getDocument("Unnamed")
	except:
		pass

	import nurbswb.nurbs
	# nurbswb.nurbs.runtest()
	nurbswb.nurbs.testRandomB()
	

	hp=makeHelper()
	sayErr("created")
	# hp.source=App.ActiveDocument.Box
	hp.source=App.ActiveDocument.Nurbs
	
	sayErr("source changed")
	hp.mode="Surface"
	hp.Placement.Base.x=1200

	hp2=makeHelper()
	sayErr("created")
	# hp.source=App.ActiveDocument.Box
	hp2.source=App.ActiveDocument.Nurbs
	
	sayErr("source changed")
	hp2.mode="isoGrid"
	hp2.Placement.Base.x=2400


	hp3=makeHelper()
	sayErr("created")
	# hp.source=App.ActiveDocument.Box
	hp3.source=App.ActiveDocument.Nurbs
	
	sayErr("source changed")
	hp3.mode="poleGrid"
	hp3.Placement.Base.x=3600


	Gui.activeDocument().activeView().viewAxonometric()
	Gui.SendMsgToActiveView("ViewFit")



	bs=hp.source.Proxy.bs
	shape=create_knotes_shape(None,bs)

	hp.Shape=shape
	hp.Placement.Base.x=1200


	shape=create_subface_shape(None,bs,0,11,0,17)

	hp2.Shape=shape
	hp2.Placement.Base.x=2400




	tt1, shape1=split_shape(None,bs,0,7,0,8)
	tt2, shape2=split_shape(None,bs,0,-1,9,-1)


	hp3.Shape=comp=Part.Compound([shape1,shape2])
	hp3.Placement.Base.x=3600



	shape1=create_knotes_shape(None,tt1)
	shape2=create_knotes_shape(None,tt2)
	hp3.Shape=comp=Part.Compound([shape1,shape2])
	hp3.Placement.Base.x=3600



