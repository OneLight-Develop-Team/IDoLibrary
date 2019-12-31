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
UI_PATH = os.path.join(DIR,"ui","Maya_LightRebuild.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')

from Maya_LightRebuild import Maya_LightRebuild

class Maya_LightRebuild_UI_Interface(Maya_LightRebuild):
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

        self.ptr = self.Dock_Win_Management(title=u"Houdini&Maya灯光导入导出工具")

        super(Maya_LightRebuild_UI_Interface,self).__init__()
        
        if self.DOCK == "workspace":
            # QMainWindow 无法 addWidget
            self.ptr.layout().addWidget(self.Main_Menu_Bar)
            self.ptr.layout().addWidget(self.Main_Layout)
        else:
            self.ptr.layout().addWidget(self)

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
        print "save"
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
        cmds.textField(tx=u"————————————————主要用法————————————————",ed=False,bgc=(1,.1,.1))
        cmds.textField(tx=u"1.选择相关的灯光类型进行过滤",ed=False,bgc=(.1,.1,.1))
        cmds.textField(tx=u"2.选择相关的灯光导出，如果没有选择自动导出所有的灯光",ed=False,bgc=(.1,.1,.1))
        

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
            
        global Maya_LightRebuild_UI 
        Maya_LightRebuild_UI = Maya_LightRebuild_UI_Interface(dock=dock)

    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)

    

def main():
    # 检测不同的UI 全部删除
    global Maya_LightRebuild_UI 

    try:
        if cmds.window(Maya_LightRebuild_UI.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + Maya_LightRebuild_UI.undockWindow + "\")")
            # cmds.deleteUI(Maya_LightRebuild_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(Maya_LightRebuild_UI.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + Maya_LightRebuild_UI.dockControl + "\")")
            # cmds.deleteUI(Maya_LightRebuild_UI.dockControl)
    except:
        pass

    try:
        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(Maya_LightRebuild_UI.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(Maya_LightRebuild_UI.workspaceCtrl)
    except:
        pass

    Maya_LightRebuild_UI = Maya_LightRebuild_UI_Interface(dock="undock")
