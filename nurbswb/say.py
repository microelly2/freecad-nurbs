''' ausgabe von programmablaufinformationen, importieren der wichtigsten module'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- (c) microelly 2017 v 0.4
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------



##\cond
import FreeCAD
import FreeCADGui

App=FreeCAD
Gui=FreeCADGui

##\endcond

import PySide
from PySide import QtCore, QtGui

import FreeCAD
import Draft, Part

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm 

import os,random,time,sys,traceback

## 
#
## <A HREF="http://www.freecadbuch.de/doku.php?id=blog">FreeCAD Buch 2</A> 
#
# @author microelly
# @warning works only on linux, writes to /tmp/log.txt
#
# @param[in] s String to log
# @param[in] logon is logging on (False) 
#
#
# .



def log(s,logon=False):
	'''write to a logfile'''
	if logon:
		f = open('/tmp/log.txt', 'a')
		f.write(str(s) +'\n')
		f.close()

def sayd(s):
	'''print information if debug mode'''
	if hasattr(FreeCAD,'animation_debug'):
		log(str(s))
		FreeCAD.Console.PrintMessage(str(s)+"\n")

def say(s):
	'''print information to console''' 
	log(str(s))
	FreeCAD.Console.PrintMessage(str(s)+"\n")

def sayErr(s):
	'''print information as error'''
	log(str(s))
	FreeCAD.Console.PrintError(str(s)+"\n")


def sayW(s):
	'''print information as warning'''
	log(str(s))
	FreeCAD.Console.PrintWarning(str(s)+"\n")


def errorDialog(msg):
	''' pop up an error QMessageBox'''
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Critical,u"Error Message",msg )
    diag.setWindowFlags(PySide.QtCore.Qt.WindowStaysOnTopHint)
    diag.exec_()


def sayexc(mess=''):
	''' print message with traceback''' 
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=lls[(l-3):]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))


