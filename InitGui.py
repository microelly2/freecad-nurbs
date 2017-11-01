#***************************************************************************
#*																		*
#*   Copyright (c) 2016													* 
#*   <microelly2@freecadbuch.de>										* 
#*																		*
#*  This program is free software; you can redistribute it and/or modify*
#*  it under the terms of the GNU Lesser General Public License (LGPL)	*
#*  as published by the Free Software Foundation; either version 2 of	*
#*  the License, or (at your option) any later version.					*
#*  for detail see the LICENCE text file.								*
#*																		*
#*  This program is distributed in the hope that it will be useful,		*
#*  but WITHOUT ANY WARRANTY; without even the implied warranty of		*
#*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the		*
#*  GNU Library General Public License for more details.				*
#*																		*
#*  You should have received a copy of the GNU Library General Public	*
#*  License along with this program; if not, write to the Free Software	*
#*  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#*  USA																	*
#*																		*
#************************************************************************

__title__="FreeCAD Nurbs Library"


import FreeCAD, FreeCADGui
##-

# from workfeature macro
global get_SelectedObjects
def get_SelectedObjects(info=0, printError=True):
    """ Return selected objects as
        Selection = (Number_of_Points, Number_of_Edges, Number_of_Planes,
                    Selected_Points, Selected_Edges, Selected_Planes)
    """
    def storeShapeType(Object, Selected_Points, Selected_Edges, Selected_Planes):
        if Object.ShapeType == "Vertex":
            Selected_Points.append(Object)
            return True
        if Object.ShapeType == "Edge":
            Selected_Edges.append(Object)
            return True 
        if Object.ShapeType == "Face":
            Selected_Planes.append(Object)
            return True
        return False
            
    m_actDoc=FreeCAD.ActiveDocument
    
    if m_actDoc.Name:    
        # Return a list of SelectionObjects for a given document name.
        # "getSelectionEx" Used for selecting subobjects
        m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
 
        m_num = len(m_selEx)
        if info != 0:
            print_msg("m_selEx : " + str(m_selEx))
            print_msg("m_num   : " + str(m_num))
            
        if m_num >= 1: 
            Selected_Points = []
            Selected_Edges = []
            Selected_Planes = []
            Selected_Objects = []
            for Sel_i_Object in m_selEx:
                if info != 0:
                    print_msg("Processing : " + str(Sel_i_Object.ObjectName))
                                
                if Sel_i_Object.HasSubObjects:                
                    for Object in Sel_i_Object.SubObjects:
                        if info != 0:
                            print_msg("SubObject : " + str(Object)) 
                        if hasattr(Object, 'ShapeType'):
                            storeShapeType(Object, Selected_Points, Selected_Edges, Selected_Planes)
                        if hasattr(Object, 'Shape'):
                            Selected_Objects.append(Object)
                else:
                    if info != 0:
                        print_msg("Object : " + str(Sel_i_Object))
                    if hasattr(Sel_i_Object, 'Object'):
                        if hasattr(Sel_i_Object.Object, 'ShapeType'):
                            storeShapeType(Sel_i_Object.Object, Selected_Points, Selected_Edges, Selected_Planes)
                        if hasattr(Sel_i_Object.Object, 'Shape'):
                            if hasattr(Sel_i_Object.Object.Shape, 'ShapeType'):
                                if not storeShapeType(Sel_i_Object.Object.Shape, Selected_Points, Selected_Edges, Selected_Planes):
                                    Selected_Objects.append(Sel_i_Object.Object)
                    
                    
            Number_of_Points = len(Selected_Points)
            Number_of_Edges = len(Selected_Edges)
            Number_of_Planes = len(Selected_Planes)
            Selection = (Number_of_Points, Number_of_Edges, Number_of_Planes,
                    Selected_Points, Selected_Edges, Selected_Planes, Selected_Objects)
            if info != 0:
                print_msg("Number_of_Points, Number_of_Edges, Number_of_Planes," +
                           "Selected_Points, Selected_Edges, Selected_Planes , Selected_Objects = " + str(Selection))
            return Selection
        else:
            if info != 0:
                print_msg("No Object selected !")
            if printError:
                printError_msg("Select at least one object !")
            return None
    else:
        printError_msg("No active document !")
    return 

#------------------------------


import FreeCAD,FreeCADGui
import sys

#---------------------------------------------------------------------------
# define the Commands of the Test Application module
#---------------------------------------------------------------------------
class MyTestCmd2:
    """Opens a Qt dialog with all inserted unit tests"""
    def Activated(self):
        import QtUnitGui
        QtUnitGui.addTest("nurbswb.TestNurbsGui")
        QtUnitGui.addTest("nurbswb.TestNurbs")
        QtUnitGui.addTest("nurbswb.TestMeinAll.Col1")
        QtUnitGui.addTest("nurbswb.TestMeinAll.Col2")
        QtUnitGui.addTest("TestMeinAll.Col2")

    def GetResources(self):
        return {'MenuText': 'Test-test...', 'ToolTip': 'Runs the self-test for the workbench'}


FreeCADGui.addCommand('My_Test2'        ,MyTestCmd2())
# FreeCADGui.runCommand('My_Test2')





#------------------------------------------
# fast command adder template

import os, nurbswb
global __dir__
__dir__ = os.path.dirname(nurbswb.__file__)


global _Command
class _Command():

	def __init__(self,lib=None,name=None,icon='/../icons/nurbs.svg',command=None,modul='nurbswb'):

		if lib==None: lmod=modul
		else: lmod=modul+'.'+lib
		if command==None: command=lmod+".run()"
		else: command =lmod + "."+command

		self.lmod=lmod
		self.command=command
		self.modul=modul
		self.icon=  __dir__+ icon

		if name==None: name=command
		self.name=name


	def GetResources(self): 
		return {'Pixmap' : self.icon, 'MenuText': self.name, 'ToolTip': self.name } 

	def IsActive(self):
		if FreeCADGui.ActiveDocument: return True
		else: return False

	def Activated(self):
		#FreeCAD.ActiveDocument.openTransaction("create " + self.name)
		if self.command <> '':
			if self.modul <>'': modul=self.modul
			else: modul=self.name
			FreeCADGui.doCommand("import " + modul)
			FreeCADGui.doCommand("import "+self.lmod)
			FreeCADGui.doCommand("reload("+self.lmod+")")
			FreeCADGui.doCommand(self.command)
		#FreeCAD.ActiveDocument.commitTransaction()
		if FreeCAD.ActiveDocument <> None:
			FreeCAD.ActiveDocument.recompute()


class _alwaysActive(_Command):

	def IsActive(self):
			return True


#-----------------------------------------------
#
# condtions when a command should be active

def always():
	''' always'''
	return True

def ondocument():
	'''if a document is active'''
	return FreeCADGui.ActiveDocument <> None

def onselection():
	'''if at least one object is selected'''
	return len(FreeCADGui.Selection.getSelection())>0

def onselection1():
	'''if exactly one object is selected'''
	return len(FreeCADGui.Selection.getSelection())==1

def onselection2():
	'''if exactly two objects are selected'''
	return len(FreeCADGui.Selection.getSelection())==2

def onselection3():
	'''if exactly three objects are selected'''
	return len(FreeCADGui.Selection.getSelection())==3

def onselex():
	'''if at least one subobject is selected'''
	return len(FreeCADGui.Selection.getSelectionEx())<>0

def onselex1():
	'''if exactly one subobject is selected'''
	return len(FreeCADGui.Selection.getSelectionEx())==1


# the menu entry list
FreeCAD.tcmds5=[]

# create menu entries 
'''
def c1(menu,name,*info):
	global _Command
	name1="Nurbs_"+name
	t=_Command(name,*info)
	FreeCADGui.addCommand(name1,t)
	FreeCAD.tcmds5.append([menu,name1,name,'always',info])
'''

def c1a(menu,isactive,name,*info):
	global _Command
	name1="Nurbs_"+name
	t=_Command(name,*info)
	t.IsActive=isactive
	FreeCADGui.addCommand(name1,t)
	FreeCAD.tcmds5.append([menu,name1,name,isactive,info])

'''
def c2(menu,title,name,*info):
	#print info
	global _Command
	title1="Nurbs_"+title
	FreeCADGui.addCommand(title1,_Command(name,*info))
	FreeCAD.tcmds5.append([menu,title1,name,'always',info])
'''

def c2a(menu,isactive,title,name,*info):
	global _Command
	t=_Command(name,*info)
	title1="Nurbs_"+title
	t.IsActive=isactive
	FreeCADGui.addCommand(title1,t)
	FreeCAD.tcmds5.append([menu,title1,name,isactive,info])


# special conditions fore actions
def onneedle():
	'''open the needle file'''
	dokname=FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetString("Document","Needle")
	try: App.getDocument(dokname); return True
	except: return False

def onspread():
	'''there should be a spreadsheet object'''
	try: App.ActiveDocument.Spreadsheet;return True
	except: return False


import nurbswb
import nurbswb.configuration


if FreeCAD.GuiUp:

	c1a(["Curves"],always,"scancut","cut Scanned Mesh ",'/../icons/mesh_cut.svg')
	c1a(["Curves"],ondocument,"weighteditor","Weight Editor")

	c1a(["Curves"],ondocument,"simplecurve","simplify curve")
	c1a(["Curves"],onselection1,"removeknot","remove a knot in a bspline")
	c1a(["Curves"],onselection2,"curvedistance","calculate the distance between two curves")
	c1a(["Curves"],always,"createsketchspline","create Sketcher BSpline from a curve",'/../icons/createsketchspline.svg')
	c1a(["Curves"],ondocument,"weighteditor","Weight Editor")
	#c2a(["Curves"],onselection1,'DraftBSpline Editor',"DraftBSplineEditor","Edit Draft Bspline",'/../icons/32px-draftbspline_edit.png',"run()")
	c2a(["Curves"],always,'DraftBSpline Editor',"DraftBSplineEditor","Edit Draft Bspline",'/../icons/32px-draftbspline_edit.png',"run()")

	c2a(["Curves"],always,'facedraw','facedraw','draw on a face','/../icons/draw.svg',"run()")
	c2a(["Curves"],always,'facedrawa','facedraw','create Map of a face','/../icons/draw.svg',"createMap()")
	c2a(["Curves"],always,'facedrawb','facedraw','create Grids for a face','/../icons/draw.svg',"createGrid()")
	
	c2a(["Curves"],always,'isodraw32','isodraw','3D to 2D','/../icons/draw.svg',"map3Dto2D()")
	c2a(["Curves"],always,'isodraw23','isodraw','2D to 3D','/../icons/draw.svg',"map2Dto3D()")
#	c2a(["Curves"],always,'importColorSVG','shoe_importSVG','import SVG for shoes','/../icons/draw.svg',"import_test()")
	c2a(["Curves"],always,'linkSVG','shoe_importSVG','create link to SVG file','/../icons/draw.svg',"create_svglink()")
	c2a(["Curves"],always,'beziera','bezier','selected face to sketch','/../icons/draw.svg',"faceToSketch()")
	c2a(["Curves"],always,'bezierb','bezier','selected edges to sketches','/../icons/draw.svg',"subsToSketch()")


	c2a(["Curves"],always,'transform_spline','transform_spline','perspective transformation of a Bbspline','/../icons/upgrade.svg',"run()")
	c2a(["Curves"],ondocument,'createcloverleaf','createcloverleaf','create a cloverleaf','/../icons/cloverleaf.svg',"run()")
	c2a(["Curves"],ondocument,'createshoerib','createshoerib','create a shoe last rib','/../icons/cloverleaf.svg',"run()")

	c2a(["Curves"],ondocument,'project_edge2face','project_edge2face','parallel projection of edge to face','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'loft_selection','loft_selection','loft between two selections','/../icons/Loft.svg',"run()")
	c2a(["Curves"],ondocument,'loft_selectionEdges','loft_selection','loft between two selected edges','/../icons/Loft.svg',"runOnEdges()")

	c2a(["Curves"],ondocument,'knotsandpoles','knotsandpoles','display knots and poles for selected curves','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'monitor','monitor','create a monitor for a curve length','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'param_bspline','param_bspline','create a parametric bspline with tangents','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'OffsetSpline','curves','create a Sketch for a OffsetSpline','/../icons/nurbs.svg',"runOffsetSpline()")
	c2a(["Curves"],ondocument,'Stare','curves','create a Sketch for a Star','/../icons/nurbs.svg',"runStar()")
	c2a(["Curves"],ondocument,'DynamicOffset','dynamicoffset','create a dynamic Offset','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'FloatList','datatools','create a floatlist','/../icons/nurbs.svg',"runFloatlist()")
	c2a(["Curves"],ondocument,'Sole','create_sole_sketch','create a sole as offsetspline','/../icons/nurbs.svg',"runSole()")
	c2a(["Curves"],onselection2,'MoveAlongCurve','move_along_curve','move an object #2 along a bspline curve #1','/../icons/nurbs.svg',"run()")
	c2a(["Curves"],ondocument,'SketchClone','sketchclone','create a semi clone of a sketch','/../icons/sketchdriver.svg',"runSketchClone()")


	c2a(["Faces","create"],always,'Random Plane',"nurbs","Create plane with randoms",'/../icons/plane.svg',"testRandomB()")
	c2a(["Faces","create"],always,'Random Torus',"nurbs","Create torus with randoms",'/../icons/torus.svg',"testRandomTorus()")
	c2a(["Faces","create"],always,'Random Cylinder',"nurbs","Create cylinder with randomness",'/../icons/cylinder.svg',"testRandomCylinder()")
	c2a(["Faces","create"],always,'Random Sphere',"nurbs","Create sphere with randomness",'/../icons/sphere.svg',"testRandomSphere()")
	c2a(["Faces","create"],ondocument,'simple Hood','simplehood','create a simple hood','/../icons/nurbs.svg',"run()")


	c2a(["Faces"],ondocument,'Sole Change Model','sole_change_model','Shoe Sole Change Model','/../icons/sole.svg',"run()")
	c2a(["Faces"],ondocument,'load Sole Height','load_sole_profile_height','Load Height Profile','/../icons/sole.svg',"run()")
	c2a(["Faces"],ondocument,'load Sole Widht','load_sole_profile_width','Load Width Profile','/../icons/sole.svg',"run()")

	c2a(["Faces"],ondocument,'Iso Map','isomap','draw isomap of Face','/../icons/nurbs.svg',"run()")

	c2a(["Faces","create"],always,'Nurbs Editor','nurbs','creates a test nurbs','/../icons/zebra.svg',"runtest()")
	c2a(["Faces","create"],onselection,'UV Grid Generator','uvgrid_generator','create UV grid of the partr','/../icons/nurbs.svg',"runSel()")
	c2a(["Faces","create"],onselection,'Nurbs Helper','helper','create helper objects of the part','/../icons/nurbs.svg',"makeHelperSel()")
	c2a(["Faces","create"],ondocument,'Create QR Code','createbitmap','create a qr code surface','/../icons/nurbs.svg',"run()")

	c2a(["Faces"],always,'filledface','filledface','createFilledFace','/../icons/nurbs.svg',"createFilledFace()")

	c2a(["Faces"],always,'ZebraTool','zebratool','ZebraTool','/../icons/zebra.svg',"run()")
	c2a(["Faces"],always,'Curves to Face','curves2face','Curves to Face','/../icons/upgrade.svg',"run()")
	c2a(["Faces"],always,'Segment','segment','Cut a segment of a Face','/../icons/nurbs.svg',"runsegment()")
	c2a(["Faces"],always,'FineSegment','segment','Cut a fine segment of a Face','/../icons/nurbs.svg',"runfinesegment()")
	c2a(["Faces"],always,'NurbsTrafo','segment','Transform a Face','/../icons/nurbs.svg',"runnurbstrafo()")
	c2a(["Faces"],always,'Tangent','tangentsurface','create a tangent Face','/../icons/nurbs.svg',"runtangentsurface()")
	c2a(["Faces"],always,'Seam','tangentsurface','create a Seam','/../icons/nurbs.svg',"runseam()")
	c2a(["Faces"],always,'Grid generator','uvgrid_generator','create a uv-grid for a Face','/../icons/nurbs.svg',"run()")


	c2a(["Topology"],always,'Topological Analyse','analyse_topology_v2','topological analyse','/../icons/nurbs.svg',"run()")
	c2a(["Topology"],always,'Topo8','analyse_topology_v2','display Quality Points','/../icons/nurbs.svg',"displayQualityPoints()")
	c2a(["Topology"],always,'Topo5','analyse_topology_v2','print Graph Data','/../icons/nurbs.svg',"printData()")

	c2a(["Topology"],always,'Topo4','analyse_topology_v2','add to Vertex Store','/../icons/nurbs.svg',"addToVertexStore()")
	c2a(["Topology"],always,'Topo2','analyse_topology_v2','print Vertex Store','/../icons/nurbs.svg',"printVertexStore()")
	c2a(["Topology"],always,'Topo3','analyse_topology_v2','reset Vertex Store','/../icons/nurbs.svg',"resetVertexStore()")
	
	c2a(["Topology"],always,'Topo6','analyse_topology_v2','load Test 1','/../icons/nurbs.svg',"loadTest1()")
	c2a(["Topology"],always,'Topo7','analyse_topology_v2','load Test 2','/../icons/nurbs.svg',"loadTest2()")




	c2a(["Workspace"],ondocument,'Create Workspace',None,"Create workspace",'/../icons/plane.svg',"createws()","workspace")
	c2a(["Workspace"],ondocument,'Create Link',None,"Create workspace link",'/../icons/plane.svg',"createlink()","workspace")

	c2a(["Needle"],ondocument,'Needle','needle','create a needle','/../icons/shoe.svg',"run()")
	c2a(["Needle"],onneedle,'needle Change Model','needle_change_model','needle Change Model','/../icons/shoe.svg',"run()")
	c2a(["Needle"],onselex1,'addULine','needle_cmds','add Meridian/Rib','/../icons/add_edge.svg',"cmdAdd()")
	c2a(["Needle"],onselex1,'deleteULine','needle_cmds','delete Meridian/Rib','/../icons/delete_edge.svg',"cmdDel()")
	c2a(["Needle"],onspread,'Open Spreadsheet','wheel_event','Open Spreadsheet','/../icons/nurbs.svg',"undock('Spreadsheet')")
	c2a(["Needle"],onneedle,'Edit Rib','wheel_event','Edit Rib','/../icons/nurbs.svg',"start('Rib_template')")
	c2a(["Needle"],onneedle,'Edit Backbone','wheel_event','Edit Backbone','/../icons/nurbs.svg',"start('Backbone')")

	c2a(["Shoe"],always,'Create Shoe','shoe','Create Shoe','/../icons/shoe.svg',"run()")
	c2a(["Shoe"],always,'scanbackbonecut','scanbackbonecut','Cut the Scan along backbone ','/../icons/backbonecut.svg',"run()")
	c2a(["Shoe"],always,'Create Sole','sole','Create Shoe Sole','/../icons/sole.svg',"run()")

	c2a(["Shoe"],ondocument,'toggleSketch','shoe_tools','toggle constraints of a rib','/../icons/toggleshoesketch.svg',"toggleShoeSketch()")
	c2a(["Shoe"],always,'Generate Docu',"gendok","generate menu structure docu for web",'/../icons/plane.svg',"run()")

	c2a(["Shoe"],always,'DriverSketch','skdriver','driver test for shoe rib','/../icons/toggleshoesketch.svg',"runribtest()")
	c2a(["Shoe"],always,'DriverSketchAll','skdriver','driver for all ribs','/../icons/toggleshoesketch.svg',"runribtest2()")

	c2a(["Shoe"],always,'RecomputeAll','skdriver','recompute shoe','/../icons/toggleshoesketch.svg',"recomputeAll()")

	c2a(["Shoe"],always,'LoadSketch','sketchmanager','load sketch from a sketchlib','/../icons/toggleshoesketch.svg',"runLoadSketch()")
	c2a(["Shoe"],always,'SaveSketch','sketchmanager','save sketch into the sketchlib','/../icons/toggleshoesketch.svg',"runSaveSketch()")
	c2a(["Shoe"],always,'DisplaySketchlib','sketchmanager','list all sketches of the sketchlib','/../icons/toggleshoesketch.svg',"runSketchLib()")



	c2a(["Nurbs"],always,'Grid','blender_grid','Create Grid',"/../icons/Draft_Grid.svg","run()")


	c2a(["Neo4j"],always,'Start','neodb','start db',"/../icons/neo4j.png","start()","graphdb")
	c2a(["Neo4j"],always,'Stop','neodb','stop db',"/../icons/neo4j_stop.png","stop()","graphdb")
	c2a(["Neo4j"],always,'Status','neodb','status db',"/../icons/neo4j_status.png","status()","graphdb")

	c2a(["Neo4j"],always,'Start_OF','openflights','import_Open Flights',"/../icons/openflights-import.png","load()","graphdb")
	c2a(["Neo4j"],always,'Reset_OG','openflights','reset_Open Flights',"/../icons/openflights.png","reset()","graphdb")

	c2a(["Sketchertools"],always,'Status1','feedbacksketch','fb sketch',"/../icons/neo4j_status.png","run()","sketcher")
	c2a(["Sketchertools"],always,'Status2','feedbacksketch','revers order of constraints A',"/../icons/neo4j_status.png","runA()","sketcher")
	c2a(["Sketchertools"],always,'Status3','feedbacksketch','create Example B',"/../icons/neo4j_status.png","runB()","sketcher")
	c2a(["Sketchertools"],always,'Status4','feedbacksketch','Copy 1.Sketch into 2nd Sketch',"/../icons/neo4j_status.png","runC()","sketcher")
	c2a(["Sketchertools"],always,'Status51','feedbacksketch','Create FeedBack with 1 client',"/../icons/neo4j_status.png","run1C()","sketcher")
	c2a(["Sketchertools"],always,'Status52','feedbacksketch','Create FeedBack with 2 clients',"/../icons/neo4j_status.png","run2C()","sketcher")
	c2a(["Sketchertools"],always,'Status53','feedbacksketch','Create FeedBack with 3 clients',"/../icons/neo4j_status.png","run3C()","sketcher")
#	for cmd in FreeCADGui.listCommands():
#		if cmd.startswith("Nurbs_"):
#			print cmd


'''

nd=App.newDocument("Unnamed")
App.setActiveDocument(nd.Name)
App.ActiveDocument=App.getDocument(nd.Name)
Gui.ActiveDocument=Gui.getDocument(nd.Name)
'''


class NurbsWorkbench(Workbench):
	'''Nurbs'''

	MenuText = "Nurbs"
	ToolTip = "Nurbs Editor"

	Icon= '''
/* XPM */
static char * nurbs_xpm[] = {
"16 16 2 1",
".	c #E12DEC",
"+	c #FFFFFF",
"................",
"................",
"................",
"................",
".........+++++..",
".........+++++..",
".........+++++..",
".........+++++..",
".........+++++..",
".........+++++..",
"................",
"................",
"................",
"................",
"................",
"................"};'''

	def GetClassName(self):
		return "Gui::PythonWorkbench"

	def Initialize(self):

		Gui.activateWorkbench("DraftWorkbench")
		Gui.activateWorkbench("SketcherWorkbench")

		cmds= ['Nurbs_ZebraTool','Nurbs_DraftBSpline Editor',
		'Nurbs_Create Shoe','Nurbs_Create Sole','Nurbs_Sole Change Model',
		'Nurbs_scanbackbonecut','Nurbs_createsketchspline','Nurbs_Curves to Face', 'Nurbs_facedraw',
		'Nurbs_createcloverleaf',
		'Part_Cone', 'Part_Cylinder','Draft_Move','Draft_Rotate','Draft_Point','Draft_ToggleGrid',
		'My_Test2','Nurbs_toggleSketch','Sketcher_NewSketch']

		if 1:
			self.appendToolbar("Nurbs", cmds )
			self.appendMenu("Nurbs", cmds)

		menues={}
		ml=[]
		for _t in FreeCAD.tcmds5:
			c=_t[0]
			a=_t[1]
			try:menues[tuple(c)].append(a)
			except: 
				menues[tuple(c)]=[a]
				ml.append(tuple(c))

		for m in ml:
			self.appendMenu(list(m),menues[m])

FreeCADGui.addWorkbench(NurbsWorkbench)

