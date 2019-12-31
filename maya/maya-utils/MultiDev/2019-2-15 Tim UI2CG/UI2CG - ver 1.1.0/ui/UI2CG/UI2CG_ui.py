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

class UI_Interface(base_class,form_class):
    def __init__(self,dock="dock"):
        self.DOCK = dock

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

        ptr = self.Dock_Win_Management(title="Default")

        super(UI_Interface,self).__init__(parent=ptr)
        self.parent().layout().addWidget(self)
        self.setupUi(self)
        
        self.Path_Toggle_Anim = QPropertyAnimation(self.Path_Layout, "maximumHeight")
        self.Path_Toggle_Anim.setDuration(300)
        self.Path_Toggle_Anim.setStartValue(0)
        self.Path_Toggle_Anim.setEndValue(self.Path_Layout.sizeHint().height())
        self.Path_Toggle.setCheckable(True)
        self.Path_Toggle.setChecked(True)
        self.Path_Toggle.toggled.connect(self.Path_Toggle_Fun)
        
        self.RequireHeader_Toggle_Anim = QPropertyAnimation(self.RequireHeader_Layout, "maximumHeight")
        self.RequireHeader_Toggle_Anim.setDuration(300)
        self.RequireHeader_Toggle_Anim.setStartValue(0)
        self.RequireHeader_Toggle_Anim.setEndValue(self.RequireHeader_Layout.sizeHint().height())
        self.RequireHeader_Toggle.setCheckable(True)
        self.RequireHeader_Toggle.setChecked(True)
        self.RequireHeader_Toggle.toggled.connect(self.RequireHeader_Toggle_Fun)
        
        self.CGHeader_Toggle_Anim = QPropertyAnimation(self.CGHeader_Layout, "maximumHeight")
        self.CGHeader_Toggle_Anim.setDuration(300)
        self.CGHeader_Toggle_Anim.setStartValue(0)
        self.CGHeader_Toggle_Anim.setEndValue(self.CGHeader_Layout.sizeHint().height())
        self.CGHeader_Toggle.setCheckable(True)
        self.CGHeader_Toggle.setChecked(True)
        self.CGHeader_Toggle.toggled.connect(self.CGHeader_Toggle_Fun)
        self.Load_Json_Fun()
    
    def Path_Toggle_Fun(self,Checked):
        if Checked:
            self.Path_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Path_Toggle_Anim.start()
            self.Path_Toggle.setText(u"▼设置文件路径")
            self.Path_Toggle.setStyleSheet('font:normal')
        else:
            self.Path_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Path_Toggle_Anim.start()
            self.Path_Toggle.setText(u"■设置文件路径")
            self.Path_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()
    
    def RequireHeader_Toggle_Fun(self,Checked):
        if Checked:
            self.RequireHeader_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.RequireHeader_Toggle_Anim.start()
            self.RequireHeader_Toggle.setText(u"▼通用头文件设置")
            self.RequireHeader_Toggle.setStyleSheet('font:normal')
        else:
            self.RequireHeader_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.RequireHeader_Toggle_Anim.start()
            self.RequireHeader_Toggle.setText(u"■通用头文件设置")
            self.RequireHeader_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()
    
    def CGHeader_Toggle_Fun(self,Checked):
        if Checked:
            self.CGHeader_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.CGHeader_Toggle_Anim.start()
            self.CGHeader_Toggle.setText(u"▼CG头文件设置")
            self.CGHeader_Toggle.setStyleSheet('font:normal')
        else:
            self.CGHeader_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.CGHeader_Toggle_Anim.start()
            self.CGHeader_Toggle.setText(u"■CG头文件设置")
            self.CGHeader_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()
    
    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['UI_Line_Text'] = self.UI_Line_Text.text() if len(self.UI_Line_Text.text())>0 else ""
        GUI_STATE['Py_Line_Text'] = self.Py_Line_Text.text() if len(self.Py_Line_Text.text())>0 else ""
        GUI_STATE['MayaWin_LE'] = self.MayaWin_LE.text() if len(self.MayaWin_LE.text())>0 else ""
        GUI_STATE['CGHeader_PTE'] = self.CGHeader_PTE.text() if len(self.CGHeader_PTE.text())>0 else ""
        GUI_STATE['OS_CB'] = self.OS_CB.isChecked()
        GUI_STATE['JSON_CB'] = self.JSON_CB.isChecked()
        GUI_STATE['Partial_CB'] = self.Partial_CB.isChecked()
        GUI_STATE['SYS_CB'] = self.SYS_CB.isChecked()
        GUI_STATE['Traceback_CB'] = self.Traceback_CB.isChecked()
        GUI_STATE['Copy_CB'] = self.Copy_CB.isChecked()
        GUI_STATE['Math_CB'] = self.Math_CB.isChecked()
        GUI_STATE['Array_CB'] = self.Array_CB.isChecked()
        GUI_STATE['Time_CB'] = self.Time_CB.isChecked()
        GUI_STATE['OpenMaya_CB'] = self.OpenMaya_CB.isChecked()
        GUI_STATE['OpenMayaUI_CB'] = self.OpenMayaUI_CB.isChecked()
        GUI_STATE['Mel_CB'] = self.Mel_CB.isChecked()
        GUI_STATE['Cmds_CB'] = self.Cmds_CB.isChecked()
        GUI_STATE['PyMel_CB'] = self.PyMel_CB.isChecked()
        GUI_STATE['OpenMayaMPx_CB'] = self.OpenMayaMPx_CB.isChecked()
        GUI_STATE['None_RB'] = self.None_RB.isChecked()
        GUI_STATE['Maya_RB'] = self.Maya_RB.isChecked()
        GUI_STATE['Houdini_RB'] = self.Houdini_RB.isChecked()
        GUI_STATE['NUKE_RB'] = self.NUKE_RB.isChecked()
        GUI_STATE['Path_Toggle_Check'] = self.Path_Toggle.isChecked()
        GUI_STATE['RequireHeader_Toggle_Check'] = self.RequireHeader_Toggle.isChecked()
        GUI_STATE['CGHeader_Toggle_Check'] = self.CGHeader_Toggle.isChecked()
        GUI_STATE['DOCK'] = self.DOCK
    
        try:
            with open(path,'w') as f:
                json.dump(GUI_STATE,f,indent=4)
        except:
            QMessageBox.warning(self, "Warning", "保存失败")
    
    def Load_Json_Fun(self,path=GUI_STATE_PATH,load=False):
        if os.path.exists(path):
            GUI_STATE = {}          
            with open(path,'r') as f:
                GUI_STATE = json.load(f)
            self.UI_Line_Text.setText(GUI_STATE['UI_Line_Text'])
            self.Py_Line_Text.setText(GUI_STATE['Py_Line_Text'])
            self.MayaWin_LE.setText(GUI_STATE['MayaWin_LE'])
            self.MayaWin_LE.setText(GUI_STATE['MayaWin_LE'])
            self.OS_CB.setChecked(GUI_STATE['OS_CB'])
            self.JSON_CB.setChecked(GUI_STATE['JSON_CB'])
            self.Partial_CB.setChecked(GUI_STATE['Partial_CB'])
            self.SYS_CB.setChecked(GUI_STATE['SYS_CB'])
            self.Traceback_CB.setChecked(GUI_STATE['Traceback_CB'])
            self.Copy_CB.setChecked(GUI_STATE['Copy_CB'])
            self.Math_CB.setChecked(GUI_STATE['Math_CB'])
            self.Array_CB.setChecked(GUI_STATE['Array_CB'])
            self.Time_CB.setChecked(GUI_STATE['Time_CB'])
            self.OpenMaya_CB.setChecked(GUI_STATE['OpenMaya_CB'])
            self.OpenMayaUI_CB.setChecked(GUI_STATE['OpenMayaUI_CB'])
            self.Mel_CB.setChecked(GUI_STATE['Mel_CB'])
            self.Cmds_CB.setChecked(GUI_STATE['Cmds_CB'])
            self.PyMel_CB.setChecked(GUI_STATE['PyMel_CB'])
            self.OpenMayaMPx_CB.setChecked(GUI_STATE['OpenMayaMPx_CB'])
            self.None_RB.setChecked(GUI_STATE['None_RB'])
            self.Maya_RB.setChecked(GUI_STATE['Maya_RB'])
            self.Houdini_RB.setChecked(GUI_STATE['Houdini_RB'])
            self.NUKE_RB.setChecked(GUI_STATE['NUKE_RB'])
            self.Path_Toggle.setChecked(GUI_STATE['Path_Toggle_Check'])
            self.RequireHeader_Toggle.setChecked(GUI_STATE['RequireHeader_Toggle_Check'])
            self.CGHeader_Toggle.setChecked(GUI_STATE['CGHeader_Toggle_Check'])
            self.Path_Toggle_Fun(GUI_STATE['Path_Toggle_Check'])
            self.Path_Toggle_Fun(GUI_STATE['Path_Toggle_Check'])
            self.RequireHeader_Toggle_Fun(GUI_STATE['RequireHeader_Toggle_Check'])
            self.RequireHeader_Toggle_Fun(GUI_STATE['RequireHeader_Toggle_Check'])
            self.CGHeader_Toggle_Fun(GUI_STATE['CGHeader_Toggle_Check'])
            self.CGHeader_Toggle_Fun(GUI_STATE['CGHeader_Toggle_Check'])
    
            return True
        else:
    
            if load==True:
                QMessageBox.warning(self, "Warning", "加载失败\n检查路径是否正确")
                return False

    # 关闭窗口时保存当前视窗选择
    def closeEvent(self, event,path=GUI_STATE_PATH):
        self.Save_Json_Fun(path=path)

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
                self.undockWindow = cmds.window( title=Title_Name,cc=partial(self.closeEvent,self.event))
            else:
                self.undockWindow = cmds.window( title=Title_Name,rc=partial(self.closeEvent,self.event))
            cmds.paneLayout()
            cmds.showWindow(self.undockWindow)
            ptr = mayaToQT(self.undockWindow)
            return ptr

        elif self.DOCK == "dock":
            window = cmds.window( title=Title_Name)
            cmds.paneLayout()
            self.dockControl = cmds.dockControl( area='right', content=window, label=Title_Name,floatChangeCommand=self.Win_Size_Adjustment,vcc=self.closeEvent)
            dock = mayaToQT(window)
            return dock

        elif self.DOCK == "workspace":
            name = title
            if cmds.workspaceControl(name,query=True,exists=True) :
                cmds.deleteUI(name)
            self.workspaceCtrl = cmds.workspaceControl(name,fl=True,label=Title_Name,vcc=self.closeEvent)
            cmds.paneLayout()
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace
