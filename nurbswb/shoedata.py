print "shoedata version 0.91"

# rotations and scaling
twister= [[0,0,0]]*4 + [[0,30,0]]*4 + [[0,25,0]] + [[0,20,0]]+ [[0,10,0]]*4
twister= [[0,0,0]]*4 + [[0,30,-10]]+[[0,30,0]]*3 + [[0,25,0]] + [[0,20,0]]+ [[0,10,0]]*4
sc= [[1,1]]*14 

# backbone (red line)
bbps=[ 
		[280,0,11+9], #  not used
		[260,0,11+3], #  outside

		[250,0,11], # top
		[218,0,4], # st 

		[168,0,0], # joint j
		[132,0,6], # girth
		[110,0,10], # waist
		[68,0,14], # instep ik

		[60,0,16], #  leg
		[45,0,17], #  leg
		[35,0,18], #  leg
		[20,0,19], #  leg

		[5,0,20], #  inner back end 
		[0,0,20], #  back end heel
	]

# 3D Boxes for the ribs
boxes=[

		[8,0,-24,8+2], # not used
#		[12,0,-20,8+4], # vorspitze
#		[12,0,-25,14],# spizte fuss

		[10,0,-16,8+4], # vorspitze
		[12,0,-25,14],# spizte fuss

		[21-2,0,-30,20-4-2],
		
		[40,0,-40,20+2], # sp == einschnitt, zehengelenk? 

		[50-3,0,-40-2,38+2], # joint J3
		[45,0,-40+8,56], # waist
		[40,0,-40+8,65+1], # girth
		[40-5,0,-40+8+4,100-3], # instep I

		[40-5,0,-30+2,100+3],# oeffnung short heel
		[35-2,0,-30+2,100+0],# knoechel 1
		[33-2,0,-30+2,100-6],# knoechel 2
		[30-3,0,-30+5,100-6],# knoechel 3

		[20-3,0,-20+3,100-6],# vorbereitung abschluss hinten
		[1,0,-1,100-6], # abschluss hinten

		]



# 3D Boxes for the ribs  - feinarbeit
boxes=[

		[8,0,-24,8+2], # not used
#		[12,0,-20,8+4], # vorspitze
#		[12,0,-25,14],# spizte fuss

		[10,0,-16,8+4], # vorspitze
		[12+10,0,-25+10,14],# spizte fuss

		[21-2+5+5,0,-30+5+5,20-4],
		
		[40,0,-40,20+2], # sp == einschnitt, zehengelenk? 

		[50-8,0,-40-8,38+4], # joint J3
		[45-10,0,-40-3,56+2], # waist
		[40-10+2,0,-40+2,65+2], # girth
		[40-8,0,-40+5,100-3], # instep I

		[40-10+3,0,-30-4+3,100+3],# oeffnung short heel
		[35-5,0,-30+2,100+0],# knoechel 1
		[33-2,0,-30+2,100-6],# knoechel 2
		[30-3,0,-30+5,100-6],# knoechel 3

		[20-3,0,-20+3,100-6],# vorbereitung abschluss hinten
		[1,0,-1,100-6], # abschluss hinten

		]



boxes_ex1=[

		[7,0,-25,8], # not used
		[7,0,-25,8], # vorspitze

		[7,0,-25,20-4-4-4],# spizte fuss
		[21-2,0,-30,20-4-2],
		
		[40,0,-40,20+2], # sp == einschnitt, zehengelenk? 

		[50-3,0,-40-2,38+2], # joint J3
		[45,0,-40+8,56], # waist
		[40-30,0,-40+8,65+1], # girth
		[40-20,0,-40,100-3], # instep I

		[40-5,0,-30+2,100+3],# oeffnung short heel
		[35-2,0,-30+2,100+0],# knoechel 1
		[33-2,0,-30+2,100-6],# knoechel 2
		[30-3,0,-30+5,100-6],# knoechel 3

		[20-3,0,-20+3,100-6],# vorbereitung abschluss hinten
		[1,0,-1,100-6], # abschluss hinten

		]



# control of output

# show loft of the profiles
showlofts=False

# show scaled models 
showscales=False
scaleIn=0.98
scaleOut=1.02

