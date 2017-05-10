'''

'''

import numpy as np


class model():

	def __init__(self):

		self.LL=244.0
#		self.LL=344.0
		self.LS=self.LL+70

		self.div12=[round(self.LL/11*i,1) for i in range(12)]

		#spitze
		h=18
		self.tt=[[[35,35,14],[40,28,h],[65,14,h],[70,0,h],[65,-15,h],[40,-15,h],[35,-20,14]]]

		#ferse
		h=30
		self.tf=[[[16,26,h],[8,18,h],[4,9,h],[0,0,h],[4,-7,h],[8,-14,h],[18,-22,h]]]

		self.weia=[-15,-22,	-28,-30,	-32,-33,	-34,-39,	-43,-42,	-37,-24,	-23]
		self.weib=[15,22,	26,25,		22,20,		22,23,		28,32,		43,45,	42]

		self.higha=[18,17,16,15,11,10,8,5, 0,2,5,9,14]
		self.highb=[17,17,16,15,11,10,8,4,1,2,5,9,14]
		self.highc=[17,17,16,15,25,35,35,15,5,1,2,5,9,14]
		self.highd=[0,0,10,10,10,20,20,10,10,10,10,0,0]
		self.highe=[0,1,2,3,2,1,0]

		self.info='a generic model'


class modelA(model):

	def __init__(self):
		model.__init__(self)
		#spitze
		h=18
		self.tt=[[[35,35,14],[40,28,h],[45,14,h],[50,0,h],[45,-15,h],[40,-15,h],[35,-20,14]]]
		self.tt=[[[5,35,14],[5,28,h],[10,14,h],[10,0,h],[10,-15,h],[5,-15,h],[5,-20,14]]]
		self.info='breit'


class modelB(model):

	def __init__(self):
		model.__init__(self)
		#spitze
		h=18
		self.tt=[[[35,35,14],[40,28,h],[145,14,h],[150,0,h],[45,-15,h],[40,-15,h],[35,-20,14]]]

		self.info='spitz'

class modelC(model):

	def __init__(self):
		model.__init__(self)
		#high heel
		self.higha=[130,130,130,110, 100,80,40,20, 0,2,5,9,14]
		#ferse
		h=130
		self.tf=[[[16,26,h],[8,18,h],[4,9,h],[0,0,h],[4,-7,h],[8,-14,h],[18,-22,h]]]
		#spitze
		h=18
		self.tt=[[[35,17,14],[40,15,h],[45,15,h],[55,0,h],[45,-10,h],[40,-15,h],[35,-17,14]]]

		self.info='high heel'



def listModels(silent=False):
	import nurbswb.sole_models
	reload(nurbswb.sole_models)
	l=[]
	for m in dir(nurbswb.sole_models):
		if m.startswith('model'):
			mm=eval("nurbswb.sole_models."+m+"()")
			if not silent:
				print (m,mm.info)
			l.append([m,mm.info])
	return l








if __name__=='__main__':


	listModels()

	# testcase

	class modelY(modelA):
		pass

	import nurbswb.sole
	reload(nurbswb.sole)
	nurbswb.sole.runA(model=modelY)



