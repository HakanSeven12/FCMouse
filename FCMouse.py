from math import atan2, degrees
from PySide2 import QtCore, QtGui, QtWidgets
import time

force = 0
visible = 1
lastpos = FreeCAD.Vector(0, 0, 0)
view_time = time.time()
view_pos = [0, 0, 0]
autohide = 1
mv = FreeCADGui.getMainWindow()
dockSituations = {}

for dock in mv.findChildren(QtWidgets.QDockWidget):
    dockSituations[dock.objectName()] =  dock.isVisible()

try:
    view = FreeCADGui.ActiveDocument .ActiveView
except:
    FreeCAD.newDocument()
    view = FreeCADGui.ActiveDocument .ActiveView

def coordInput(point3d): 
    # point3d = Base.Vector(x, y, z)
    point2d = view.getPointOnScreen(point3d)
    size = view.getSize()
    coordX = point2d[0]
    coordY = size[1] - point2d[1]

    mw = FreeCADGui.getMainWindow()
    gl = mw.findChild(QtWidgets.QOpenGLWidget)
    me = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, QtCore.QPoint(coord[0],coord[1]),
        QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)

    app = QtWidgets.QApplication.instance()
    app.sendEvent(gl, me)

def angle2(VectorX1,VectorY1,VectorX2,VectorY2,mode):  # calculation of the inclination of a line from two Vectors
    deltaX = VectorX2 - VectorX1
    deltaY = VectorY2 - VectorY1
    angle = atan2(float(deltaY),float(deltaX)) #radian  (mode = 0)

    if mode ==1:               # if "mode" = 1 then display in degrees otherwise in radian
        angle = degrees(angle) # degres  (mode = 1)

    return round(angle,3)

def dist(vector1, vector2):
    #Distance between vectors
    if isinstance(vector1,FreeCAD.Vector) and isinstance(vector2,FreeCAD.Vector):
        return(vector1.sub(vector2)).Length

class ViewObserver(QtWidgets.QLineEdit):
    def __init__(self, view):
        super(ViewObserver, self).__init__(Gui.getMainWindow())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.view = view
        self.show()

    
    def logPosition(self, info):
        global force
        global visible
        global lastpos
        global view_time
        global view_pos
        global autohide

        try:
            if (info["Key"] == "Q") and (info["State"] == "DOWN"):                        # SHIFT + Q for quit
                self.view.removeEventCallback("SoEvent",callback)                     # close event observationa
                autohide = (autohide + 1) % 2
                super().deleteLater()
                FreeCAD.Console.PrintMessage( "End Informations" + "\n")
        except:
            pass

        try:
            if (info["Key"] == "M") and (info["State"] == "DOWN"):                         # SHIFT + M for switch between modes
                force = (force + 1) % 3
        except:
            pass

        try:
            if (info["Key"] == "C") and (info["State"] == "DOWN"):                        # SHIFT + C for hidden / visible cursor info
                visible = (visible + 1) % 2
                self.setVisible(visible)
                FreeCAD.Console.PrintMessage( "visibility: "+ str(visible) + "\n")
        except:
            pass

        try:
            if (info["Key"] == "D") and (info["State"] == "DOWN"):                        # SHIFT + D for enable/disable autohide docks
                autohide = (autohide + 1) % 2
                FreeCAD.Console.PrintMessage( "autohide: "+ str(autohide) + "\n")
        except:
            pass

        dockAreas = {}
        pos = info["Position"]                                                                                        # if mouse in 3D view

        for dock in mv.findChildren(QtWidgets.QDockWidget):
            dockAreas[dock.objectName()] =  str(mv.dockWidgetArea(dock)).rpartition('.')[-1]

        for key, value in dockAreas.items():
            dock = mv.findChild(QtWidgets.QDockWidget, key)
            situation = dockSituations.get(key)

            if autohide:
                if ((pos[0] < 15) and (value == 'LeftDockWidgetArea')):
                    dock.show()

                elif ((pos[1] < 15) and (value == 'BottomDockWidgetArea')):
                    dock.show()

                elif ((pos[0] > view.getSize()[0] - 15) and (value == 'RightDockWidgetArea')):
                    dock.show()
                else:
                    dock.hide()
            elif situation:
                dock.show()
            else:
                dock.hide()

        """
        import time
        time = time.time()
        
        if (time - view_time < 1) or (view_pos != pos) or (visible != 1):
            InfoAnn.Visibility = 0
            view_time = time
            view_pos = pos
        else:
            InfoAnn.Visibility = 1
        """

        try:
            objectInfo = ""
            object = self.view.getObjectInfo(self.view.getCursorPos())                               # here for object preselected
            if object["Object"] != InfoAnn.ViewObject.Object.Name:
                objectInfo = object["Object"] + "." + object["Component"]                           # object + component
            curpos = FreeCAD.Vector(float(object["x"]),float(object["y"]),float(object["z"])) # vector on position mouse to object
        except:
            curpos = self.view.getPoint(pos)                                                                    # vector detect on mouse position 3D view

        try:
            if (info["Button"] == "BUTTON1") and (info["State"] == "DOWN"):                           # coordinates clic to mouse
                lastpos = curpos
        except:
            pass

        if force == 0:
            infoText = "X: " + str(round(curpos[0],3)) + "    Y: " + str(round(curpos[1],3)) + "    Z: " + str(round(curpos[2],3))

        elif (force == 1):
            coorBegin = "X1: " + str(round(lastpos[0],3)) + "    Y1: " + str(round(lastpos[1],3)) + "    Z1: " + str(round(lastpos[2],3))
            coorEnd = "X2: " + str(round(curpos[0],3)) + "    Y2: " + str(round(curpos[1],3)) + "    Z2: " + str(round(curpos[2],3))
            length = "L: " + str(round(dist(lastpos, curpos),3))
            alphaXY = str(round(angle2(lastpos[0],lastpos[1],curpos[0],curpos[1],1),3))
            alphaYZ = str(round(angle2(lastpos[1],lastpos[2],curpos[1],curpos[2],1),3))
            alphaXZ = str(round(angle2(lastpos[0],lastpos[2],curpos[0],curpos[2],1),3))

            angles = "XY: " + alphaXY + chr(176) + "    YZ: " + alphaYZ + chr(176) + "    XZ: " + alphaXZ + chr(176)    # unichr(176) = degrees character

            if objectInfo == "":
                infoText = coorBegin + "\n"  + coorEnd + "\n"  + length + "\n"  + angles
            else:
                infoText = objectInfo + "\n" + coorBegin + "\n"  + coorEnd + "\n"  + length + "\n"  + angles
        else:
            if objectInfo == "":
                infoText = "X: " + str(round(curpos[0],3)) + "    Y: " + str(round(curpos[1],3)) + "    Z: " + str(round(curpos[2],3))
            else:
                infoText = objectInfo + "\n"  + "X: " + str(round(curpos[0],3)) + "    Y: " + str(round(curpos[1],3)) + "    Z: " + str(round(curpos[2],3))

        position = QtGui.QCursor().pos()
        self.move(position.x() + 20, position.y() + 0)
        self.setText(infoText)
        fm = self.fontMetrics()
        self.setMinimumWidth(fm.width(infoText)+20)
        self.setMaximumWidth(fm.width(infoText)+21)
        
        if (pos[0] < 15) or (pos[1] < 50) or (pos[0] > view.getSize()[0] - 15) \
            or (pos[1] > view.getSize()[1] - 15): self.setVisible(0)
        else: self.setVisible(1)

FreeCAD.Console.PrintMessage("__________________Welcome to FCMouse__________________" + "\n")
FreeCAD.Console.PrintMessage("SHIFT + Q : quit" + "\n")
FreeCAD.Console.PrintMessage("SHIFT + M : switch between cursor info modes" + "\n")
FreeCAD.Console.PrintMessage("SHIFT + C : hidden / visible cursor info" + "\n")
FreeCAD.Console.PrintMessage("SHIFT + D : enable/disable autohide docks" + "\n")
FreeCAD.Console.PrintMessage("______________________________________________________" + "\n")

observer = ViewObserver(view)
callback = view.addEventCallback("SoEvent",observer.logPosition)
