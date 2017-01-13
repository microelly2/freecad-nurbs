'''

import nurbswb.needle_models
reload(nurbswb.needle_models)

#App.activeDocument().MyNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelSpoon)
myNeedle=App.activeDocument().MyNeedle

#myNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelEd4)

myNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelSpoon)

'''

import numpy as np


class model():

	def __init__(self,bbl=5):
		self.curve=[
				[0,0,0], 
				[0,299,-30],[0,300,-30],
				[0,349,-300],[0,350,-300],
				[0,399,-500],[0,400,-500],
				[0,400,100],[0,400,101],
				[0,0,150],
				[0,-100,101],[0,-100,100],
				[0,-100,-100],[0,-99,-100],
			]

		self.sc=[[1,1]]*bbl
		self.twister=[[0,0,0]]*bbl
		self.bb=[[0,0,100*i] for i in range(bbl)]
		self.info='a generic model'



class modelA(model):
	''' halbscharfe kante '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,29,0],[0,30,0],[0,31,0],
				[100,30,25],
				[100,180,25],
				[-20,180,-5],
				[-20,-30,-5],
				[-100,-30,-25],[-99,-30,-25],
				[-100,-129,-25],[-100,-130,-25],[-99,-130,-25],
				[0,-40,-0]
			]

		self.bb= [[0,0,0],[0,0,50],[0,0,100],[0,0,200],[0,0,400],[0,0,499],[0,0,500],[0,0,600]]
		self.twister=[[0,0,0],[0,-25,0],[0,0,0],[00,0,0],[0,-25,0],[0,25,0],[0,25,0],[0,0,00]]
		self.sc=[[1,0],[1,0],[1,0],[1,0],[1,0],[1.3,0],[1.3,0],[1.,0]]


class modelB(model):
	''' schiefe abschlussebene '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,29,0],[0,30,0],[0,31,0],
				[100,30,25],
				[100,180,25],
				[-20,180,-5],
				[-20,-30,-5],
				[-100,-30,-25],[-99,-30,-25],
				[-100,-129,-25],[-100,-130,-25],[-99,-130,-25],
				[0,-40,-0]
			]

		self.bb= [[0,0,0],[0,0,50],[0,0,100],[0,0,200],[0,0,400],[0,0,499],[0,0,500],[0,0,501],[0,0,800]]
		self.twister=[[0,0,0],[0,-25,0],[0,0,0],[00,0,0],[0,-25,0],[0,25,0],[0,25,0],[0,25,0],[20,30,40]]
		self.sc=[[1,0],[1,0],[1,0],[1,0],[1,0],[1.3,0],[1.3,0],[1.3,0],[1.5,0]]


class modelC(model):
	''' rotate along z-axis '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,29,0],[0,30,0],[0,31,0],
				[100,30,25],
				[100,180,25],
				[-20,180,-5],
				[-20,-30,-5],
				[-100,-30,-25],[-99,-30,-25],
				[-100,-129,-25],[-100,-130,-25],[-99,-130,-25],
				[0,-40,-0]
			]

		self.bb= [[0,0,0],[0,0,50],[0,0,100],[0,0,200],[0,0,400],[0,0,499],[0,0,500],[0,0,501],[0,0,800]]
		self.twister=[[0,0,0],[0,0,40],[0,0,-20],[0,0,-20],[0,0,30],[0,0,0],[0,0,0],[0,0,0],[0,0,60]]
		self.sc=[[1,0],[1,0],[1,0],[1,0],[1,0],[1.3,0],[1.3,0],[1.3,0],[1.5,0]]


class modelD(model):
	''' rotate along y-axis '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,29,0],[0,30,0],[0,31,0],
				[100,30,25],
				[100,180,25],
				[-20,180,-5],
				[-20,-30,-5],
				[-100,-30,-25],[-99,-30,-25],
				[-100,-129,-25],[-100,-130,-25],[-99,-130,-25],
				[0,-40,-0]
			]

		self.bb= [[0,0,0],[0,0,50],[0,0,100],[0,0,200],[0,0,400],[0,0,499],[0,0,500],[0,0,501],[0,0,800]]
		self.twister=[[0,0,0],[0,45,0],[0,0,0],[00,0,0],[0,-45,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
		self.sc=[[1,0],[1,0],[1,0],[1,0],[1,0],[1.3,0],[1.3,0],[1.3,0],[1.5,0]]




class modelE(model):
	''' rotate along x-axis '''
	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,29,0],[0,30,0],[0,31,0],
				[100,30,25],
				[100,180,25],
				[-20,180,-5],
				[-20,-30,-5],
				[-100,-30,-25],[-99,-30,-25],
				[-100,-129,-25],[-100,-130,-25],[-99,-130,-25],
				[0,-40,-0]
			]

		self.bb= [[0,0,0],[0,0,50],[0,0,100],[0,0,200],[0,0,400],[0,0,499],[0,0,500],[0,0,501],[0,0,800]]
		self.twister=[[0,0,0],[35,0,0],[35,0,0],[00,0,0],[-45,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
		self.sc=[[1,0],[1,0],[1,0],[1,0],[1,0],[1.3,0],[1.3,0],[1.3,0],[1.5,0]]


class modelEd0(model):
	''' edge tests base '''
	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,40,0],[80,40,0],[80,80,0],
				[-80,80,0],
				[-80,-80,0],
				[80,-80,0],
				[80,-40,0],
				[0,-40,0]
			]

		self.bb=[[0,0,0],[0,0,100],[0,0,200],[0,0,300],[0,0,400]]
		self.twister=[[0,0,0]]*len(self.bb)
		self.sc=[[1,0]]*len(self.bb)



class modelEd1(model):
	''' edge tests base '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],[0,0,0],
				[0,40,0],[80,40,0],[80,80,0],
				[-80,80,0],
				[-80,-80,0],
				[80,-80,0],
				[80,-40,0],
				[0,-40,0]
			]

		self.bb=[[0,0,0],[0,0,100],[0,0,200],[0,0,300],[0,0,400]]
		self.twister=[[0,0,0]]*5
		self.sc=[[1,0]]*5




class modelEd2(model):
	''' edge tests roundings '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],[0,0,0],
				[0,39,0],[0,40,0],[0,40,1],
				[79,40,0],[80,40,0],[80,41,0],
				[80,60,0],[80,80,0],[60,80,0],
				[-60,80,0],[-80,80,0],[-80,60,0],
				[-80,-79,0],[-80,-80,0],[-79,-80,0],
				[79,-80,0],[80,-80,0],[80,-79,0],
				[80,-60,0],[80,-40,0],[60,-40,0],
				[20,-40,0],[0,-40,0],[0,-20,0],
			]

		self.bb=[[0,0,0],[0,0,100],[0,0,200],[0,0,300],[0,0,400]]
		self.twister=[[0,0,0]]*5
		self.sc=[[1,0],[1,0],[3,0],[0.3,0],[1,0]]



class modelEd3(model):
	''' edge tests backbone roundings base'''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],[0,0,0],
				[0,39,0],[0,40,0],[0,40,1],
				[79,40,0],[80,40,0],[80,41,0],
				[80,60,0],[80,80,0],[60,80,0],
				[-60,80,0],[-80,80,0],[-80,60,0],
				[-80,-79,0],[-80,-80,0],[-79,-80,0],
				[79,-80,0],[80,-80,0],[80,-79,0],
				[80,-60,0],[80,-40,0],[60,-40,0],
				[20,-40,0],[0,-40,0],[0,-20,0],
			]

		self.bb=[[0,0,0],[0,0,100],[100,0,100],[100,0,300],[0,0,300],[0,0,400],[-100,0,400],[-100,0,500],[0,0,500],[0,0,600]]
		self.twister=[[0,0,0]]*len(self.bb)
		self.sc=[[1,0]]*len(self.bb)


class modelEd4(model):
	''' edge tests backbone roundings '''

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0],[0,0,0],
				[0,39,0],[0,40,0],[0,40,1],
				[79,40,0],[80,40,0],[80,41,0],
				[80,60,0],[80,80,0],[60,80,0],
				[-60,80,0],[-80,80,0],[-80,60,0],
				[-80,-79,0],[-80,-80,0],[-79,-80,0],
				[79,-80,0],[80,-80,0],[80,-79,0],
				[80,-60,0],[80,-40,0],[60,-40,0],
				[20,-40,0],[0,-40,0],[0,-20,0],
			]

		self.bb=[[0,0,0],
			[0,0,80],[0,0,100],[20,0,100],
			[80,0,100],[100,0,100],[100,0,120],
			
			[100,0,299],[100,0,300],[99,0,300],
			[1,0,300],[0,0,300],[0,0,301],
			
			[0,0,399],[0,0,400],[-1,0,400],
			[-70,0,400],[-100,0,400],[-100,0,430],
			
			[-100,0,499],[-100,0,500],[-99,0,500],
			[-40,0,500],[0,0,500],[0,0,540],
			
			[0,0,600]]
		self.twister=[[0,0,0]]*len(self.bb)
		self.sc=[[1,0]]*len(self.bb)



class modelSpoon(model):

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0], 
				[0,50,10],
				[0,99,40],[0,100,40],[0,100,35],
				[0,50,10],
				[0,0,-10],
				[0,-50,10],
				[0,-100,35],[0,-100,40],[0,-99,40],
				[0,-50,10],
			]

		self.bb=[[0,0,0],[150,0,-20],[250,0,-10],[297,0,20],[300,0,20]]
		self.twister=[[0,0,0],[0,45,0],[0,70,0],[0,90,0],[0,90,0]]
		self.sc=[[1,1],[2.0,1.7],[1.3,1.],[0.8,0.02],[0.01,0.001]]



if 0:

	App.activeDocument().MyNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelSpoon)
	App.activeDocument().MyNeedle.Proxy.getExampleModel(nurbswb.needle_models.modelEd4)

'''
	modelA(ss)
	modelB(ss)
	modelC(ss)
	modelD(ss)

	modelE(ss)


	modelEd0(ss)
	modelEd1(ss)
	modelEd2(ss)
	modelEd3(ss)
	modelEd4(ss)


	modelSpoon(ss)
'''




class modelXY(model):

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0], 
				[0,399,0],[0,400,0],
				[0,400,100],[0,400,101],
				[0,0,400],
				[0,-100,101],[0,-100,100],
				[0,-100,0],[0,-99,0],
			]

		self.bb=[[0,0,0],[200,0,0],[400,0,0],[600,0,0],[1000,0,00],[2001,0,00]]
		self.twister=[[0,-90,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,90,0]]
		self.sc=[[2,1],[3,5],[4,5],[4,5],[3,5],[2,1]]


class modelX(model):

	def __init__(self):
		model.__init__(self)
		self.curve=[
				[0,0,0], 
				[0,299,-30],[0,300,-30],
				[0,349,-300],[0,350,-300],
				[0,399,-500],[0,400,-500],
				[0,400,100],[0,400,101],
				[0,0,150],
				[0,-100,101],[0,-100,100],
				[0,-100,-100],[0,-99,-100],
			]

		self.bb=[[0,0,0],[200,0,0],[300,0,0],[410,0,0],[1000,0,00],[2001,0,00]]
		self.twister=[[0,-90,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,90,0]]
		self.sc=[[0.2,0.1],[3,1],[2.1,0.1],[.1,0.1],[.1,0.4],[.2,.4]]




class modelS1(model):

	def __init__(self,bbl=12):
		model.__init__(self)
		self.curve=[
				[200,0,0],
				[200,600,0],
				[-200,400,0],
				[-200,0,0],
			]

		self.sc=[[1,1]]*bbl

		self.twister=[[0,0,0]]*bbl

		self.twister[3]=[0,0,50] # rotate on x-axis
		self.twister[4]=[0,60,0] # rotate on y-axis
		self.twister[5]=[70,0,0] # rotate on z-axis

		self.bb=[[0,0,300*i] for i in range(bbl)]
		self.bb[10][1]=300 # move in y-direction
		self.bb[8][0]=300 # move in x-direction
		self.info="Testmodel"


class modelSimple(model):

	def __init__(self,bbl=4):
		model.__init__(self)
		self.curve=[
				[200,0,0],
				[200,600,0],
				[-200,400,0],
				[-200,0,0],
			]

		self.sc=[[1,1]]*bbl

		self.twister=[[0,0,0]]*bbl


		self.bb=[[0,0,200*i] for i in range(bbl)]
		self.info="Testmodel simple 4 x 12"





class modelFillet(model):

	def __init__(self,bbl=4):
		model.__init__(self)
		self.curve=[
				[180,5,0],[210,0,0],[220,0,0],[230,0,0], [250,0,0],[260,0,0], # Tangentialuebergang  1
				[50,50,0], # innere Form des Profiles
				[0,150,0],[0,130,0],[0,120,0],[0,110,0],[0,105,0],[0,100,0], # Tangentialuebergang 2
				[50,50,0],[-50,-50,0],	[100,50,0] # Form des Profils aussen
			]

		self.sc=[[1,1]]*bbl

		self.twister=[[0,0,0]]*bbl


		self.bb=[[0,0,300*i] for i in range(bbl)]
		self.info="Testmodel Fillet"






class modelCarRoof(model):

	def __init__(self,bbl=10):
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,-99,0],[0,-100,0],[0,-100,1],[0,-100,40],
				#breite kante
				[0,-70,40],	[0,-70,35],
				
				# mittelsteg
				[0,-10,35],
				[0,-10,40],
				[0,-9,40],
				[0,9,40],
				[0,10,40],
				[0,10,35],
				
				# schmale kante
				[0,90,35],[0,90,40],
				[0,100,40],[0,100,1],[0,100,0],[0,91,0]
			]

		self.sc=[[1,2]]*bbl

		self.twister=[[0,90,0]]*bbl
		self.twister[0]=[0,180,0]
		self.twister[1]=[0,135,0]


		self.bb=[[0,0,40*i] for i in range(bbl)]
		self.bb[1]=[0,0,10]
		self.bb[2]=[0,0,20]
		self.bb[3]=[0,0,21]
		self.sc[1]=[1,3]
		
		self.sc[5]=[1,1.8]
		self.sc[6]=[1,1.8]
		self.bb[5]=[0,0,160]
		self.bb[6]=[0,0,280]
		
		self.info="Testmodel Autodach"



class modelS(model): # car 

	def __init__(self):
		bbl=15
		model.__init__(self)
		self.curve=[
				[0,0,0],
				[0,-199,0],[0,-200,0],[0,-200,1],[0,-200,40],
				#breite kante
#				[0,-70,40],	[0,-70,35],
				
				# mittelsteg
#				[0,-10,35],
#				[0,-10,40],
				[0,-150,180],
				[0,-140,180],
				[0,0,180],
				[0,140,180],
				[0,150,180],
#				[0,10,40],
#				[0,10,35],
				
				# schmale kante
#				[0,90,35],[0,90,40],
				[0,200,40],[0,200,1],[0,200,0],[0,199,0]
			]

		self.sc=[[3,2]]*bbl

		self.twister=[[0,90,0]]*bbl
		self.twister[0]=[0,180,0]
		self.twister[1]=[0,135,0]

		self.twister[-1]=[0,0,0]
		self.twister[-2]=[0,45,0]

		self.bb=[[0,0,40*i] for i in range(bbl)]
		self.bb[1]=[0,0,20]
		self.bb[2]=[0,0,40]
		self.bb[3]=[0,0,60]
		self.bb[4]=[0,0,160]
		self.bb[5]=[0,0,1200]
		self.bb[6]=[0,0,2000]
		self.bb[7]=[0,0,2200]
		self.bb[8]=[0,0,3000]
		
		self.bb[14]=[0,0,4500]
		self.bb[13]=[0,0,4480]
		self.bb[12]=[0,0,4460]
		self.bb[11]=[0,0,4300]
		self.bb[10]=[0,0,4000]
		self.bb[9]=[0,0,3200]

		self.sc[0]=[3,3]
		self.sc[1]=[3,3]
		self.sc[5]=[3.2,2]
		self.sc[6]=[4,2]
		self.sc[7]=[4,4.8]
		self.sc[14]=[3,3]
		self.sc[13]=[3,3]
		self.sc[10]=[4,2]
		self.sc[9]=[4,4.8]
		self.sc[8]=[4,4.8]

		self.info="Testmodel Autodach"




class modelS(model): # cyclic demo

	def __init__(self,bbl=4):
		model.__init__(self)
		self.curve=[
				[0,-300,0],
				[150,-150,0],[200,100,0],
				[10,0,0],[100,-100,0],
				[0,-200,0],
				[-100,-100,0],[-10,0,0],
				[-200,100,0],[-150,-150,0],
			]

		self.bb=[[0,0,5*i] for i in range(bbl)]
		self.sc=[[1,1]]*bbl
		self.twister=[[0,0,0]]*bbl



class modelK(model): # coladose geknickt

	def __init__(self):
		bbl=15
		model.__init__(self)
		self.curve=[
				[100,0,0],[70,00,70],[0,0,100],[-70,0,70],
				[-100,0,0],[-70,0,-70],[0,0,-100],[70,0,-70],
			]

		self.bb=[[0,0,30*i] for i in range(bbl)]
		self.sc=[[1,1]]*bbl
		for i in range(4,7): 
			self.sc[i]=[1,0.1]

		self.twister=[[90,0,0]]*bbl
		for i in range(4,7): 
			self.sc[i]=[1,0.3]
			self.twister[i]=[90,0,20*i]
		for i in range(7,bbl): 
			self.sc[i]=[0.7+1.0*i/bbl,0.3+1.9*(1.0*(bbl-i)/bbl)**1.2]
			self.twister[i]=[90,5,20*8]




class modelCarWindow(model):

	def __init__(self,bbl=4):
		model.__init__(self)
		self.curve=[
				[0,0,20],[0,-20,0],
				[0,-100,0],[1,-100,0],[50,-100,0],
				[40,-30,0],[40,0,20],
			]

		self.sc=[[1,1]]*bbl
		self.twister=[[0,0,0]]*bbl

		self.bb=[[0,0,1*i] for i in range(bbl)]
		self.info="Testmodel Fenster"








class modelBanana(model):

	def __init__(self):
		model.__init__(self)

		# 3 edges model
		# self.curve=[[0,0,0], [100,100,0],[-100,100,0],[-30,0,0]]

		# 4 edges model
		self.curve=np.array([
					[0,0,0], 
					[60,0,0],[65,0,0],
					[80,120,0],[77,125,0],
					[-70,150,0],[-80,150,0],[-80,140,0], # very strong edge
					[-100,0,0], # very soft edge
					[-30,0,0]
				])

		self.sc=np.array([
					[0.8,0.8],[1,1],[1,1], # blossom
					[4,4],[5,5],[4,3], # belly
					[1,1],[1,1.4],[1.3,1.3] # stalk
			])

		self.bb=np.array([
					[0,-40,100],[0,-30,110],[0,0,120], # blossom
					[0,0,140],[0,100,600],[0,0,1200], # belly
					[0,0,1250],[0,0,1290],[0,-200,1450]  # stalk
			])

		self.twister=np.array([
				[-30,-15,-10,-10,15,30,40,50,80], # Crooked banana y
				[0,0,0,0,-30,0,0,20,20], # some torsion of blossom and stalk: y,z
				[15,10,0,0,0,10,0,0,30]
			]).swapaxes(0,1)


class modelMiniBanana(modelBanana):
	def __init__(self):
		modelBanana.__init__(self)
		self.info='downscaled banana with factor 1/10'
		self.curve *= 0.1
		self.bb *= 0.1

#App.activeDocument().MyNeedle.Proxy.getExampleModel(modelMiniBanana)
#App.activeDocument().MyNeedle.Shape.BoundBox.DiagonalLength

class modelPicoBanana(modelBanana):
	def __init__(self):
		modelBanana.__init__(self)
		self.info='downscaled banana with factor 1/50'
		self.curve *= 0.02
		self.bb *= 0.02

#App.activeDocument().MyNeedle.Proxy.getExampleModel(modelMiniBanana)
#App.activeDocument().MyNeedle.Shape.BoundBox.DiagonalLength


'''
def listModels():
	import nurbswb.needle_models
	reload(nurbswb.needle_models)
	for m in dir(nurbswb.needle_models):
		if m.startswith('model'):
			mm=eval("nurbswb.needle_models."+m+"()")
			print (m,mm)
			print (mm.info)

listModels()
'''

if __name__=='__main__':
	# testcase

	class modelY(modelBanana):
		pass

	App.activeDocument().MyNeedle.Proxy.lock=False
	App.activeDocument().MyNeedle.Proxy.getExampleModel(modelY)
