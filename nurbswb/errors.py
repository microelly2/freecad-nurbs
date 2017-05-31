'''methods to display runtime errors'''

import FreeCAD
from PySide import QtGui
import sys
import traceback


def showdialog(title="Fehler",
               text="Schau in den ReportView fuer mehr Details", detail=None):
    '''display a window with: title,text and detail'''

    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Warning)
    msg.setText(text)
    msg.setWindowTitle(title)
    if detail != None:
        msg.setDetailedText(detail)
    msg.exec_()


def sayexc(title='Fehler', mess=''):
    '''display exception trace in Console
    and pop up a window with title, message'''

    exc_type, exc_value, exc_traceback = sys.exc_info()
    ttt = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    lls = eval(ttt)
    laa = len(lls)
    la2 = lls[(laa - 3):]
    FreeCAD.Console.PrintError(mess + "\n" + "-->  ".join(la2))
    showdialog(title, text=mess, detail="--> ".join(la2))

#  geometry check
#  App.ActiveDocument.Cone.Shape.check()
