#***************************************************************************
#*																		*
#*   Copyright (c) 2016													* 
#*   <edwardvmills@ ???													*
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

#------------------------------------------
# fast command adder template

import os, nurbswb
global __dir__
__dir__ = os.path.dirname(nurbswb.__file__)


global _Command
class _Command():

	def __init__(self,lib=None,name=None,icon='/../icons/eye.svg',command=None,modul='nurbswb'):

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
		FreeCAD.ActiveDocument.recompute()


class _alwaysActive(_Command):

	def IsActive(self):
			return True


#-----------------------------------------------
def always():
	return True

def ondocument():
	return FreeCADGui.ActiveDocument <> None

def onselection():
	return len(FreeCADGui.Selection.getSelection())>0

def onselection1():
	return len(FreeCADGui.Selection.getSelection())==1

def onselection2():
	return len(FreeCADGui.Selection.getSelection())==2

def onselection3():
	return len(FreeCADGui.Selection.getSelection())==3

def onselex():
	return len(FreeCADGui.Selection.getSelectionEx())<>0

def onselex1():
	return len(FreeCADGui.Selection.getSelectionEx())==1


FreeCAD.tcmds5=[]

def c1(menu,name,*info):
	global _Command
	name1="Nurbs_"+name
	t=_Command(name,*info)
	FreeCADGui.addCommand(name1,t)
	FreeCAD.tcmds5.append([menu,name1])

def c1a(menu,isactive,name,*info):
	global _Command
	name1="Nurbs_"+name
	t=_Command(name,*info)
	t.IsActive=isactive
	FreeCADGui.addCommand(name1,t)
	FreeCAD.tcmds5.append([menu,name1])

def c2(menu,title,name,*info):
	#print info
	global _Command
	title1="Nurbs_"+title
	FreeCADGui.addCommand(title1,_Command(name,*info))
	FreeCAD.tcmds5.append([menu,title1])

def c2a(menu,isactive,title,name,*info):
	#print info
	global _Command
	t=_Command(name,*info)
	title1="Nurbs_"+title
	t.IsActive=isactive
	FreeCADGui.addCommand(title1,t)
	FreeCAD.tcmds5.append([menu,title1])

#-------------------------------

# special conditions fore actions
def onneedle():
	dokname=FreeCAD.ParamGet('User parameter:Plugins/nurbs').GetString("Document","Needle")
	try: App.getDocument(dokname); return True
	except: return False

def onspread():
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

	#			'ToolTip': 'creates a new list of poles above the selected U line'
	c2a(["Needle"],ondocument,'Needle','needle','create a needle','/../icons/eye.svg',"run()")
	c2(["Needle"],'needle Change Model','needle_change_model','needle Change Model','/../icons/eye.svg',"run()")
	c2a(["Needle"],onselex1,'addULine','needle_cmds','add Meridian/Rib','/../icons/add_edge.svg',"cmdAdd()")
	c2a(["Needle"],onselex1,'deleteULine','needle_cmds','delete Meridian/Rib','/../icons/delete_edge.svg',"cmdDel()")
	c2a(["Needle"],onspread,'Open Spreadsheet','wheel_event','Open Spreadsheet','/../icons/eye.svg',"undock('Spreadsheet')")
	c2a(["Needle"],onneedle,'Edit Rib','wheel_event','Edit Rib','/../icons/eye.svg',"start('Rib_template')")
	c2a(["Needle"],onneedle,'Edit Backbone','wheel_event','Edit Backbone','/../icons/eye.svg',"start('Backbone')")


	c2a(["Faces","create"],always,'Random Plane',"nurbs","Create plane with randoms",'/../icons/plane.svg',"testRandomB()")
	c2a(["Faces","create"],always,'Random Torus',"nurbs","Create torus with randoms",'/../icons/torus.svg',"testRandomTorus()")
	c2a(["Faces","create"],always,'Random Cylinder',"nurbs","Create cylinder with randomness",'/../icons/cylinder.svg',"testRandomCylinder()")
	c2a(["Faces","create"],always,'Random Sphere',"nurbs","Create sphere with randomness",'/../icons/sphere.svg',"testRandomSphere()")
	c2a(["Faces","create"],ondocument,'simple Hood','simplehood','create a simple hood','/../icons/eye.svg',"run()")

	c2a(["Faces","create"],always,'Create Shoe','shoe','Create Shoe','/../icons/shoe.svg',"run()")
	c2a(["Faces","create"],always,'Create Sole','sole','Create Shoe Sole','/../icons/sole.svg',"run()")
	c2(["Faces"],'Sole Change Model','sole_change_model','Shoe Sole Change Model','/../icons/eye.svg',"run()")
	c2(["Faces"],'Iso Map','isomap','draw isomap of Face','/../icons/eye.svg',"run()")

	c2a(["Faces","create"],always,'Nurbs Editor','nurbs','creates a test nurbs','/../icons/zebra.svg',"runtest()")
	c2a(["Faces","create"],onselection,'UV Grid Generator','uvgrid_generator','create UV grid of the partr','/../icons/delete_edge.svg',"runSel()")
	c2a(["Faces","create"],onselection,'Nurbs Helper','helper','create helper objects of the part','/../icons/delete_edge.svg',"makeHelperSel()")

	c2a(["Faces"],always,'ZebraTool','zebratool','ZebraTool','/../icons/zebra.svg',"run()")
	c2a(["Curves"],always,'facedraw','facedraw','draw on a face','/../icons/draw.svg',"run()")

	c2a(["Faces"],always,'Curves to Face','curves2face','Curves to Face','/../icons/upgrade.svg',"run()")
	c2a(["Curves"],always,'scanbackbonecut','scanbackbonecut','Cut the Scan along backbone ','/../icons/backbonecut.svg',"run()")
	c2a(["Curves"],always,'transform_spline','transform_spline','perspective transformation of a Bbspline','',"run()")
	c2a(["Curves"],ondocument,'createcloverleaf','createcloverleaf','create a cloverleaf','/../icons/cloverleaf.svg',"run()")
	c2a(["Curves"],ondocument,'createshoerib','createshoerib','create a shoe last rib','/../icons/cloverleaf.svg',"run()")

	c2a(["Curves"],ondocument,'project_edge2face','project_edge2face','parallel projection of edge to face','/../icons/cloverleaf.svg',"run()")
	c2a(["Curves"],ondocument,'loft_selection','loft_selection','loft between two selections','/../icons/Loft.svg',"run()")

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
		
		cmds= ['Nurbs_ZebraTool','Nurbs_DraftBSpline Editor',
		'Nurbs_Create Shoe','Nurbs_Create Sole','Nurbs_Sole Change Model',
		'Nurbs_scanbackbonecut','Nurbs_createsketchspline','Nurbs_Curves to Face', 'Nurbs_facedraw',
		'Nurbs_createcloverleaf',
		'Part_Cone', 'Part_Cylinder','Draft_Move','Draft_Rotate','Draft_Point']

		if 1:
			self.appendToolbar("Nurbs", cmds )
			self.appendMenu("Nurbs", cmds)

		menues={}
		for (c,a) in FreeCAD.tcmds5:
			try:menues[tuple(c)].append(a)
			except: menues[tuple(c)]=[a]

		for m in menues:
			self.appendMenu(list(m),menues[m])

FreeCADGui.addWorkbench(NurbsWorkbench)

