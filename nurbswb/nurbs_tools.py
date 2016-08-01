# nurbs tools


import Part

def showIsoparametricUCurve(bsplinesurface,u=0.5):
	''' create a curve in 3D space '''
	bc=bsplinesurface.uIso(u)
	Part.show(bc.toShape())

def showIsoparametricVCurve(bsplinesurface,v=0.5):
	''' create a curve in 3D space '''
	bc=bsplinesurface.vIso(v)
	Part.show(bc.toShape())



