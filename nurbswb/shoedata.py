
print "shoedata version 0.4"

# ebenes modell
bbps=[ 

		[260,0,15], #b
		[255,0,13], #b
		[250,0,11], #b

		[218,0,4], #st
		[168,0,0], # joint j
		[132,0,6], # girth
		[110,0,10], # waist
		[68,0,14], # instep ik
		[60,0,16], # heel pk
		[45,0,17], # heel2 ph
		[35,0,18], # wade aa
		[20,0,19], # wade aa
		[5,0,20], # wade aa
		[0,0,20], # wade aa

]

twister= [[0,0,0]]+[[0,0,0]]*3 + [[0,30,10]]+ [[0,30,0]]*3 +[[0,25,0]]+ [[0,20,0]]+ [[0,10,0]]*2 + [[0,10,0]]*2

sc= [[1,1]] + [[1,1]]*13 


labels=['B2','B1','B','ST','Joint','Girth','Waist','Instep',
	'Long Heel','oberHeel','Ankle 1','Ankle 2','Ankle 3','Ankle 4']
