# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- zebra stripes macro 
#--
#-- (c) chris_g 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

# http://forum.freecadweb.org/viewtopic.php?f=22&t=15343&start=10


import FreeCAD
import FreeCADGui
import Part
from PySide import QtGui, QtCore
from pivy import coin

Gui=FreeCADGui



from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Zebra(object):
    def setupUi(self, Zebra):
        Zebra.setObjectName(_fromUtf8("Zebra"))
        Zebra.resize(241, 302)
        self.verticalLayoutWidget = QtGui.QWidget(Zebra)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 221, 251))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label, QtCore.Qt.AlignHCenter)
        self.horizontalSlider = QtGui.QSlider(self.verticalLayoutWidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.verticalLayout.addWidget(self.horizontalSlider)
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2, QtCore.Qt.AlignHCenter)
        self.horizontalSlider_2 = QtGui.QSlider(self.verticalLayoutWidget)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName(_fromUtf8("horizontalSlider_2"))
        self.verticalLayout.addWidget(self.horizontalSlider_2)
        self.label_3 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3, QtCore.Qt.AlignHCenter)
        self.horizontalSlider_3 = QtGui.QSlider(self.verticalLayoutWidget)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName(_fromUtf8("horizontalSlider_3"))
        self.verticalLayout.addWidget(self.horizontalSlider_3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton, QtCore.Qt.AlignHCenter)

        self.retranslateUi(Zebra)
#        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("released()")), Zebra.close)
#        QtCore.QMetaObject.connectSlotsByName(Zebra)

    def retranslateUi(self, Zebra):
        Zebra.setWindowTitle(_translate("Zebra", "Zebra Stripes Tool", None))
        self.label.setText(_translate("Zebra", "Black Stripes Width", None))
        self.label_2.setText(_translate("Zebra", "Scale", None))
        self.label_3.setText(_translate("Zebra", "Rotation", None))
        self.pushButton.setText(_translate("Zebra", "Quit", None))





class zebra():
    def __init__(self):

        self.zebraWidget = QtGui.QWidget()
        self.ui = Ui_Zebra()
        self.ui.setupUi(self.zebraWidget)

        self.StripeWidth = 25
        self.Scale = 20
        self.Rotation = 157

        self.coinSetUp()

        self.ui.horizontalSlider.setMaximum(50)
        self.ui.horizontalSlider.valueChanged[int].connect(self.changeSlide_1)
        self.ui.horizontalSlider.setValue(self.StripeWidth)

        self.ui.horizontalSlider_2.setMaximum(40)
        self.ui.horizontalSlider_2.valueChanged[int].connect(self.changeSlide_2)
        self.ui.horizontalSlider_2.setValue(self.Scale)

        self.ui.horizontalSlider_3.setMaximum(314)
        self.ui.horizontalSlider_3.valueChanged[int].connect(self.changeSlide_3)
        self.ui.horizontalSlider_3.setValue(self.Rotation)

        self.ui.pushButton.clicked.connect(self.quit)

        # self.zebraWidget.show()

    def coinSetUp(self):
        print "coinSetUp"
        self.TexW = 10
        self.TexH = 100

        self.sg = Gui.ActiveDocument.ActiveView.getSceneGraph()
        print str( Gui.ActiveDocument.Document.Label )
        print str( self.sg )
        

        self.stripes = coin.SoTexture2()
        self.sg.insertChild(self.stripes,0)
        self.stripes.filename = ""

        self.string = '\xff' * 50 + '\x00' * self.StripeWidth
        self.chars = self.string * self.TexW * self.TexH

        self.img = coin.SoSFImage()
        self.img.setValue(coin.SbVec2s(len(self.string) * self.TexW ,self.TexH), 1, self.chars);

        self.stripes.image = self.img

        # **** here we can transform the texture
        self.transTexture = coin.SoTexture2Transform()
        self.sg.insertChild(self.transTexture,1)
        #transTexture.translation.setValue(1, 1)
        self.transTexture.scaleFactor.setValue(self.Scale, self.Scale)
        self.transTexture.rotation.setValue(1. * self.Rotation / 100)
        #transTexture.center.setValue(0, .5)

        self.tc = coin.SoTextureCoordinateEnvironment()
        self.sg.insertChild(self.tc,2)

    def coinQuit(self):
        print "coinQuit"
        self.sg.removeChild(self.tc)
        self.sg.removeChild(self.transTexture)
        self.sg.removeChild(self.stripes)

    def changeSlide_1(self, value):
        print "Stripes width : "+str(value)
        self.StripeWidth = value
        self.string = '\xff' * 50 + '\x00' * self.StripeWidth
        self.chars = self.string * self.TexW * self.TexH
        self.img.setValue(coin.SbVec2s(0 ,0), 1, '');
        self.img.setValue(coin.SbVec2s(len(self.string) * self.TexW ,self.TexH), 1, self.chars);
        self.stripes.image = self.img

    def changeSlide_2(self, value):
        print "scale : "+str(value)
        self.Scale = value
        if self.Scale < 20 :
            scale = 1. * self.Scale / 20
        else:
            scale = self.Scale -19
        self.transTexture.scaleFactor.setValue(scale, scale)

    def changeSlide_3(self, value):
        print "Rotation : "+str(value)
        self.Rotation = value
        self.transTexture.rotation.setValue(1. * self.Rotation / 100)

    def quit(self):
        print "Quit ..."
        self.coinQuit()
        print "huu"
        print self.zebraWidget.parent()
        print self.zebraWidget.parent().parent()
        self.zebraWidget.parent().parent().close()
        




def run():
	dw=QtGui.QDockWidget()
	dw.setWindowTitle("Zebra Tool")
	centralWidget = QtGui.QWidget()
	dw.setWidget(centralWidget)        
	layout = QtGui.QVBoxLayout()
	centralWidget.setLayout(layout)
	dw.setMinimumSize(250, 305)
	z=zebra()
	layout.addWidget(z.zebraWidget)

	FreeCADWindow = FreeCADGui.getMainWindow() 
	FreeCADWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea,dw) 




