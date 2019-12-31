# -*- coding:utf-8 -*-

# Require Header
import os
import json
from functools import partial

# Sys Header
import traceback

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
    import pysideuic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO
else:
    import pyside2uic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO

from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
from Qt.QtCompat import *


def loadUiType(uiFile):
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type
        # in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('%s'%widget_class)

    return form_class, base_class

dirname = os.path.dirname(__file__)
UI_PATH = os.path.join(dirname,"ui","UI2CG.ui") 
GUI_STATE_PATH = os.path.join(dirname, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

from UI2CG_ui import UI_Interface
class UI2CG(UI_Interface):
    def __init__(self,dock="dock"):
        super(UI2CG,self).__init__(dock=dock)

        # 窗口设置按钮功能
        self.Maya_Dock_BTN.clicked.connect(partial(self.Dockable_Window_Fun,dock="dock"))
        self.Maya_Undock_BTN.clicked.connect(partial(self.Dockable_Window_Fun,dock="undock"))

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            self.Maya_Workspace_BTN.clicked.connect(partial(self.Dockable_Window_Fun,dock="workspace"))
        else:
            self.Maya_Workspace_BTN.setEnabled(False)

        self.Default_Setting_BTN.clicked.connect(partial(self.Dockable_Window_Fun,save=False))

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
            
        global UI2CG_UI 
        UI2CG_UI = UI2CG(dock=dock)
        UI2CG_UI.show()

def main():
    # 检测不同的UI 全部删除
    global UI2CG_UI 

    try:
        if cmds.window(UI2CG_UI.undockWindow,query=True,exists=True) :
            cmds.deleteUI(UI2CG_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(UI2CG_UI.dockControl,query=True,exists=True) :
            cmds.deleteUI(UI2CG_UI.dockControl)
    except:
        pass

    try:
        if cmds.workspaceControl(UI2CG_UI.workspaceCtrl,query=True,exists=True) :
            cmds.deleteUI(UI2CG_UI.workspaceCtrl)
    except:
        pass

    UI2CG_UI = UI2CG(dock="undock")
    UI2CG_UI.show()
