# -*- coding:utf-8 -*-

# Require Header
import os
import json
from functools import partial

# Sys Header
import sys
import traceback
import subprocess

# Maya Header
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


import plugin.Qt as Qt
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from Qt.QtCompat import wrapInstance

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","Cam_Main.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')

from Cam_Main import Cam_Main

class Cam_Main_UI_Interface(Cam_Main):
    def __init__(self,dock="undock"):
        self.DOCK = dock
        self.Prefix = ""
        self.undockWindow = ""
        self.dockControl = ""
        self.workspaceCtrl = ""

        # 读取当前DOCK属性
        if os.path.exists(GUI_STATE_PATH):
            GUI_STATE = {}
            with open(GUI_STATE_PATH,'r') as f:
                GUI_STATE = json.load(f)
            self.DOCK = GUI_STATE["DOCK"]

        # 如果是2017以前的版本 将workspace转换为dock
        if mel.eval("getApplicationVersionAsFloat;")<2017:
            if self.DOCK == "workspace":
                self.DOCK = "dock"

        self.ptr = self.Dock_Win_Management(title=u"镜头路线管理器 - Cam_Route_Manager")

        super(Cam_Main_UI_Interface,self).__init__()
        
        self.ptr.layout().addWidget(self)
        self.ptr.resize(700,500)
        self.Change_Win_Check = False

        # 窗口设置按钮功能
        self.Maya_Dock.triggered.connect(partial(self.Dockable_Window_Fun,dock="dock"))
        self.Maya_Undock.triggered.connect(partial(self.Dockable_Window_Fun,dock="undock"))

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            self.Maya_Workspace.triggered.connect(partial(self.Dockable_Window_Fun,dock="workspace"))
        else:
            self.Maya_Workspace.setEnabled(False)

        self.Default_Setting.triggered.connect(partial(self.Dockable_Window_Fun,save=False))
        self.Save_Setting.triggered.connect(self.Win_Save_JSON_Browse) 
        self.Load_Setting.triggered.connect(self.Win_Load_JSON_Browse)
        self.Help_Instruction.triggered.connect(self.Help_Instruction_Fun)

        self.Load_Json_Fun()

    def Win_Save_JSON_Browse(self):
        save_file = QFileDialog.getSaveFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(save_file) is tuple:
            save_file = save_file[0]
            if save_file == "":
                return 
        try:
            self.Save_Json_Fun(path=QDir.toNativeSeparators(save_file))
        except:
            QMessageBox.warning(self, u"Warning", u"保存失败")
            traceback.print_exc()
            return
        QMessageBox.information(self, u"保存成功", u"保存成功")

    def Win_Load_JSON_Browse(self):
        load_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(load_file) is tuple:
            load_file = load_file[0]
        check = self.Load_Json_Fun(path=QDir.toNativeSeparators(load_file),load=True)
        if check:
            QMessageBox.information(self, u"加载成功", u"加载成功")

    def Help_Instruction_Fun(self):
        try:
            if cmds.window(self.InstructionWin,query=True,exists=True) :
                cmds.deleteUI(self.InstructionWin)
        except:
            pass
        self.InstructionWin = cmds.window(t=u"使用说明",wh=(400,300),rtf=True,s=False)

        cmds.columnLayout(adj=True)
        cmds.text(l=u"————————————————主要用法————————————————",bgc=(1,.1,.1))
        cmds.textField(tx=u"1.点击添加镜头可以添加任意镜头",bgc=(.1,.1,.1),ed=0)
        cmds.textField(tx=u"2.选择添加的镜头（点击x按钮旁边即可选择）",bgc=(.1,.1,.1),ed=0)
        cmds.textField(tx=u"3.完善右侧面板上的信息（选中物体，然后点击右侧的按钮加选到面板上）",bgc=(.1,.1,.1),ed=0)
        cmds.textField(tx=u"4.完成所有镜头之后就可以点击左侧面板下方的按钮来完成操作",bgc=(.1,.1,.1),ed=0)
        cmds.text(l=u"制作者：梁伟添",bgc=(.1,.1,.1),al="right")
        cmds.text(l=u"2019年1月20日",bgc=(.1,.1,.1),al="right")
        

        cmds.showWindow(self.InstructionWin)

    def Dock_Win_Management(self,title="Defualt"):
        Title_Name = title
        def mayaToQT( name ):
            # Maya -> QWidget
            ptr = omui.MQtUtil.findControl( name )
            if ptr is None:         ptr = omui.MQtUtil.findLayout( name )
            if ptr is None:         ptr = omui.MQtUtil.findMenuItem( name )
            if ptr is not None:     return wrapInstance( long( ptr ), QWidget )

        if self.DOCK == "undock":
            # undock 窗口
            # win = omui.MQtUtil_mainWindow()
            if mel.eval("getApplicationVersionAsFloat;")>=2017:
                self.undockWindow = cmds.window(title=Title_Name,cc=self.Save_Json_Fun)
            else:
                self.undockWindow = cmds.window(title=Title_Name,rc=self.Save_Json_Fun)
            cmds.paneLayout()
            cmds.showWindow(self.undockWindow)
            ptr = mayaToQT(self.undockWindow)
            return ptr

        elif self.DOCK == "dock":
            window = cmds.window(title=Title_Name)
            cmds.paneLayout()
            self.dockControl = cmds.dockControl(area='right',fl=False,content=window, label=Title_Name,floatChangeCommand=self.Save_Json_Fun,vcc=self.Save_Json_Fun)

            # 显示当前面板
            cmds.evalDeferred("cmds.dockControl(\"" + self.dockControl  + "\",e=True,r=True)")
            
            dock = mayaToQT(window)
            return dock

        elif self.DOCK == "workspace":
            name = title
            self.workspaceCtrl = cmds.workspaceControl(name,tabToControl=["ChannelBoxLayerEditor",0],label=Title_Name,vcc=self.Save_Json_Fun)

            # 显示当前面板
            cmds.evalDeferred("cmds.workspaceControl(\"" + self.workspaceCtrl  + "\",e=True,r=True)")
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace

    def Dockable_Window_Fun(self,dock="undock",save=True):
        # 保存当前UI界面
        if save == True:
            self.DOCK = dock
            self.Save_Json_Fun()

        # 检测不同的UI 全部删除
        if cmds.window(self.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + self.undockWindow + "\")")

        if cmds.dockControl(self.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + self.dockControl + "\")")

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(self.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(self.workspaceCtrl)

        if save == False:
            os.remove(GUI_STATE_PATH)
            
        global Cam_Main_UI 
        Cam_Main_UI = Cam_Main_UI_Interface(dock=dock)

    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)

def main():
    # 检测不同的UI 全部删除
    global Cam_Main_UI 

    try:
        if cmds.window(Cam_Main_UI.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + Cam_Main_UI.undockWindow + "\")")
            # cmds.deleteUI(Cam_Main_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(Cam_Main_UI.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + Cam_Main_UI.dockControl + "\")")
            # cmds.deleteUI(Cam_Main_UI.dockControl)
    except:
        pass

    try:
        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(Cam_Main_UI.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(Cam_Main_UI.workspaceCtrl)
    except:
        pass

    Cam_Main_UI = Cam_Main_UI_Interface(dock="undock")
