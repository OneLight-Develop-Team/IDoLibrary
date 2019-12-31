# -*- coding:utf-8 -*-

# Require Header
import os
import json
from functools import partial

# Sys Header
import traceback
import subprocess

# Maya Header
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


import plugin.Qt as Qt
# 识别当前的使用的Qt库 从而导入正确的库
if Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
elif Qt.__binding__ == 'PySide':
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
    from PySide.QtCore import *
    from PySide.QtGui import *
    import pysideuic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    import pyside2uic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO


DIR = os.path.dirname(__file__)
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')

from abc_helper_ui import UI_Interface
class abc_helper(UI_Interface):
    def __init__(self,dock="dock"):
        super(abc_helper,self).__init__(dock=dock)

        # 窗口设置按钮功能
        self.Maya_Dock.clicked.connect(partial(self.Dockable_Window_Fun,dock="dock"))
        self.Maya_Undock.clicked.connect(partial(self.Dockable_Window_Fun,dock="undock"))

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            self.Maya_Workspace.clicked.connect(partial(self.Dockable_Window_Fun,dock="workspace"))
        else:
            self.Maya_Workspace.setEnabled(False)

        self.Default_Setting.clicked.connect(partial(self.Dockable_Window_Fun,save=False))


        self.NamespaceEditor_BTN.clicked.connect(self.NamespaceEditor_BTN_Fun)

        self.Hypershade_BTN.clicked.connect(self.Hypershade_BTN_Fun)

        self.Alembic_Import_BTN.clicked.connect(self.Alembic_Import_BTN_Fun)

        self.Cnvert_BTN.clicked.connect(self.Cnvert_BTN_Fun)

        self.Transfer_BTN.clicked.connect(self.Transfer_BTN_Fun)

        self.Alembic_Export_BTN.clicked.connect(self.Alembic_Export_BTN_Fun)

    def Dockable_Window_Fun(self,dock="undock",save=True):
        # 保存当前UI界面
        if save == True:
            self.DOCK = dock
            self.closeEvent(self.event)

        # 检测不同的UI 全部删除
        try:
            if cmds.window(self.undockWindow,query=True,exists=True) :
                cmds.deleteUI(self.undockWindow)
        except:
            pass

        try:
            if cmds.dockControl(self.dockControl,query=True,exists=True) :
                cmds.deleteUI(self.dockControl)
        except:
            pass

        try:
            if cmds.workspaceControl(self.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(self.workspaceCtrl)
        except:
            pass

        if save == False:
            os.remove(GUI_STATE_PATH)
            
        global abc_helper_UI 
        abc_helper_UI = abc_helper(dock=dock)
        abc_helper_UI.show()

    def NamespaceEditor_BTN_Fun(self):
        cmds.NamespaceEditor()
        self.Save_Json_Fun()        

    def Hypershade_BTN_Fun(self):
        cmds.HypershadeWindow()
        self.Save_Json_Fun()        

    def Alembic_Import_BTN_Fun(self):
        cmds.AlembicImport()
        self.Save_Json_Fun()        

    def Cnvert_BTN_Fun(self):
        sel = cmds.ls(sl=True,fl=True)

        for obj in sel:
                
            shapeNode = cmds.listRelatives(obj,children=True,shapes=True)

            SGNodeList = cmds.listConnections(shapeNode[0],type="shadingEngine")

            SGNodeList = list(set(SGNodeList))

            for SGNode in SGNodeList:

                shader = cmds.listConnections(SGNode + ".surfaceShader")

                cmds.select(cl=True)
                
                cmds.hyperShade( objects=shader[0] )

                cmds.ConvertSelectionToFaces()

                faceList = cmds.ls(sl=True,fl=True)

                cmds.sets(cl=(shader[0]+"SG"))

                for face in faceList :
                    if obj == face.split('.')[0]:
                        cmds.select(face)
                        cmds.sets(add=(shader[0]+"SG"))

        mel.eval("maintainActiveChangeSelectMode " + sel[-1] + ";")
        cmds.select(cl=True)
        cmds.headsUpMessage( u'转换成功' )
        self.Save_Json_Fun()        

    def Transfer_BTN_Fun(self):
        sel = cmds.ls(sl=True,fl=True)

        shapeNode = cmds.listRelatives(sel[0],children=True,shapes=True)

        SGNodeList = cmds.listConnections(shapeNode[0],type="shadingEngine")

        SGNodeList = list(set(SGNodeList))

        for each in SGNodeList:
            cmds.hyperShade(objects=each)
            sel_mat_face=cmds.ls(sl=True)
            
            ##剔除不是本物体的面 （按材质组选的面，有可能选择其他物体）
            mat_face_use=[]  
            for each_face in sel_mat_face:
                if each_face.find(sel[0])!=-1:  ##没有找到就返回-1
                    print each_face
                    mat_face_use.append(each_face)
            print mat_face_use       
            ##改为目标物体的面
            mat_face_obj=[]  
            for each_new in mat_face_use:
                mat_face_obj.append( each_new.replace(sel[0],sel[1]) )   

            cmds.select( mat_face_obj , r=True )
            cmds.hyperShade( assign = each )
            
        cmds.select(cl=True)
        cmds.headsUpMessage( u'传递成功' )
        self.Save_Json_Fun()        

    def Alembic_Export_BTN_Fun(self):
        check = self.Check_CheckBox(self.UV_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportUVWrite',check))

        check = self.Check_CheckBox(self.Face_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportWriteFaceSets',check))

        check = self.Check_CheckBox(self.Verbose_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportVerbose',check))

        check = self.Check_CheckBox(self.Color_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportWriteColorSets',check))

        check = self.Check_CheckBox(self.Render_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportRenderableOnly',check))

        check = self.Check_CheckBox(self.WS__CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportWorldSpace',check))

        check = self.Check_CheckBox(self.NM__CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportNoNormals',check))

        check = self.Check_CheckBox(self.Vis__CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportWriteVisibility',check))

        check = self.Check_CheckBox(self.Namespace_CB.isChecked())
        cmds.optionVar(iv=('Alembic_exportStripNamespaces',check))
        self.Save_Json_Fun()      

        cmds.AlembicExportSelection()

    def Check_CheckBox(self,CheckBox):
        if CheckBox:
            check = 1
        else:
            check = 0
        
        return check  

def main():
    # 检测不同的UI 全部删除
    global abc_helper_UI 

    try:
        if cmds.window(abc_helper_UI.undockWindow,query=True,exists=True) :
            cmds.deleteUI(abc_helper_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(abc_helper_UI.dockControl,query=True,exists=True) :
            cmds.deleteUI(abc_helper_UI.dockControl)
    except:
        pass

    try:
        if cmds.workspaceControl(abc_helper_UI.workspaceCtrl,query=True,exists=True) :
            cmds.deleteUI(abc_helper_UI.workspaceCtrl)
    except:
        pass

    abc_helper_UI = abc_helper(dock="undock")
    abc_helper_UI.show()
