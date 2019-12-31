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

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","abc_helper.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
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

        ptr = self.Dock_Win_Management(title=u"Alembic 导入导出助手")

        super(UI_Interface,self).__init__(parent=ptr)
        self.parent().layout().addWidget(self)
        self.setupUi(self)

        self.Export_Toggle_Anim = QPropertyAnimation(self.Export_Layout, "maximumHeight")
        self.Export_Toggle_Anim.setDuration(300)
        self.Export_Toggle_Anim.setStartValue(0)
        self.Export_Toggle_Anim.setEndValue(self.Export_Layout.sizeHint().height())
        self.Export_Toggle_Check = False
        self.Export_Toggle.clicked.connect(self.Export_Toggle_Fun)

        self.Convert_Toggle_Anim = QPropertyAnimation(self.Convert_Layout, "maximumHeight")
        self.Convert_Toggle_Anim.setDuration(300)
        self.Convert_Toggle_Anim.setStartValue(0)
        self.Convert_Toggle_Anim.setEndValue(self.Convert_Layout.sizeHint().height())
        self.Convert_Toggle_Check = False
        self.Convert_Toggle.clicked.connect(self.Convert_Toggle_Fun)

        self.Window_Setting_Toggle_Anim = QPropertyAnimation(self.Window_Setting_Layout, "maximumHeight")
        self.Window_Setting_Toggle_Anim.setDuration(300)
        self.Window_Setting_Toggle_Anim.setStartValue(0)
        self.Window_Setting_Toggle_Anim.setEndValue(self.Window_Setting_Layout.sizeHint().height())
        self.Window_Setting_Toggle_Check = False
        self.Window_Setting_Toggle.clicked.connect(self.Window_Setting_Toggle_Fun)

        self.Attribute_Setting_Toggle_Anim = QPropertyAnimation(self.Attribute_Setting_Layout, "maximumHeight")
        self.Attribute_Setting_Toggle_Anim.setDuration(300)
        self.Attribute_Setting_Toggle_Anim.setStartValue(0)
        self.Attribute_Setting_Toggle_Anim.setEndValue(self.Attribute_Setting_Layout.sizeHint().height())
        self.Attribute_Setting_Toggle_Check = False
        self.Attribute_Setting_Toggle.clicked.connect(self.Attribute_Setting_Toggle_Fun)

        self.Win_LoadJSON_Label.setVisible(False)
        self.Win_LoadJSON_DIR.clicked.connect(partial(self.Open_Directory,self.Win_LoadJSON_LE))
        self.Win_LoadJSON_Browse.clicked.connect(self.Win_Load_JSON_Browse)
        self.Win_LoadJSON.clicked.connect(self.Win_Load_JSON)

        self.Win_SaveJSON_Label.setVisible(False)
        self.Win_SaveJSON_DIR.clicked.connect(partial(self.Open_Directory,self.Win_SaveJSON_LE))
        self.Win_SaveJSON_Browse.clicked.connect(self.Win_Save_JSON_Browse)
        self.Win_SaveJSON.clicked.connect(self.Win_Save_JSON)
        self.Load_Json_Fun()

    def Win_Load_JSON_Browse(self):
        load_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(load_file) is tuple:
            load_file = load_file[0]
        self.Win_LoadJSON_LE.setText(QDir.toNativeSeparators(load_file))
        self.Win_LoadJSON_Label.setVisible(False)
        self.Win_LoadJSON_DIR.setVisible(True)

    def Win_Load_JSON(self):
        Load_Path = self.Win_LoadJSON_LE.text()
        check = self.Load_Json_Fun(path=Load_Path,load=True)
        if check:
            QMessageBox.information(self, u"加载成功", u"加载成功")

    def Win_Save_JSON_Browse(self):
        save_file = QFileDialog.getSaveFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(save_file) is tuple:
            save_file = save_file[0]
        self.Win_SaveJSON_LE.setText(QDir.toNativeSeparators(save_file))
        self.Win_SaveJSON_Label.setVisible(False)
        self.Win_SaveJSON_DIR.setVisible(True)

    def Win_Save_JSON(self):
        Save_Path = self.Win_SaveJSON_LE.text()
        try:
            self.Save_Json_Fun(path=Save_Path)
        except:
            QMessageBox.warning(self, u"Warning", u"保存失败")
            traceback.print_exc()
            return
        QMessageBox.information(self, u"保存成功", u"保存成功")

    def Export_Toggle_Fun(self):
        if self.Export_Toggle_Check:
            self.Export_Toggle_Check = False
            self.Export_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Export_Toggle_Anim.start()
            self.Export_Toggle.setText(u"▼alembic导出")
            self.Export_Toggle.setStyleSheet('font:normal')
        else:
            self.Export_Toggle_Check = True
            self.Export_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Export_Toggle_Anim.start()
            self.Export_Toggle.setText(u"■alembic导出")
            self.Export_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    def Convert_Toggle_Fun(self):
        if self.Convert_Toggle_Check:
            self.Convert_Toggle_Check = False
            self.Convert_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Convert_Toggle_Anim.start()
            self.Convert_Toggle.setText(u"▼材质转换")
            self.Convert_Toggle.setStyleSheet('font:normal')
        else:
            self.Convert_Toggle_Check = True
            self.Convert_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Convert_Toggle_Anim.start()
            self.Convert_Toggle.setText(u"■材质转换")
            self.Convert_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    def Window_Setting_Toggle_Fun(self):
        if self.Window_Setting_Toggle_Check:
            self.Window_Setting_Toggle_Check = False
            self.Window_Setting_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Window_Setting_Toggle_Anim.start()
            self.Window_Setting_Toggle.setText(u"▼窗口设置")
            self.Window_Setting_Toggle.setStyleSheet('font:normal')
        else:
            self.Window_Setting_Toggle_Check = True
            self.Window_Setting_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Window_Setting_Toggle_Anim.start()
            self.Window_Setting_Toggle.setText(u"■窗口设置")
            self.Window_Setting_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    def Attribute_Setting_Toggle_Fun(self):
        if self.Attribute_Setting_Toggle_Check:
            self.Attribute_Setting_Toggle_Check = False
            self.Attribute_Setting_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Attribute_Setting_Toggle_Anim.start()
            self.Attribute_Setting_Toggle.setText(u"▼设置记录")
            self.Attribute_Setting_Toggle.setStyleSheet('font:normal')
        else:
            self.Attribute_Setting_Toggle_Check = True
            self.Attribute_Setting_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Attribute_Setting_Toggle_Anim.start()
            self.Attribute_Setting_Toggle.setText(u"■设置记录")
            self.Attribute_Setting_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()
    
    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['Verbose_CB'] = self.Verbose_CB.isChecked()
        GUI_STATE['NM__CB'] = self.NM__CB.isChecked()
        GUI_STATE['Render_CB'] = self.Render_CB.isChecked()
        GUI_STATE['Namespace_CB'] = self.Namespace_CB.isChecked()
        GUI_STATE['UV_CB'] = self.UV_CB.isChecked()
        GUI_STATE['Color_CB'] = self.Color_CB.isChecked()
        GUI_STATE['Face_CB'] = self.Face_CB.isChecked()
        GUI_STATE['WS__CB'] = self.WS__CB.isChecked()
        GUI_STATE['Vis__CB'] = self.Vis__CB.isChecked()
        GUI_STATE['Tab_Widget'] = self.Tab_Widget.currentIndex() 
        GUI_STATE['Export_Toggle_Check'] = self.Export_Toggle_Check
        GUI_STATE['Convert_Toggle_Check'] = self.Convert_Toggle_Check
        GUI_STATE['Window_Setting_Toggle_Check'] = self.Window_Setting_Toggle_Check
        GUI_STATE['Attribute_Setting_Toggle_Check'] = self.Attribute_Setting_Toggle_Check
        GUI_STATE['DOCK'] = self.DOCK
    
        try:
            with open(path,'w') as f:
                json.dump(GUI_STATE,f,indent=4)
        except:
            if path != "": 
                QMessageBox.warning(self, u"Warning", u"保存失败")
    
    def Load_Json_Fun(self,path=GUI_STATE_PATH,load=False):
        if os.path.exists(path):
            GUI_STATE = {}          
            with open(path,'r') as f:
                GUI_STATE = json.load(f)
            self.Verbose_CB.setChecked(GUI_STATE['Verbose_CB'])
            self.NM__CB.setChecked(GUI_STATE['NM__CB'])
            self.Render_CB.setChecked(GUI_STATE['Render_CB'])
            self.Namespace_CB.setChecked(GUI_STATE['Namespace_CB'])
            self.UV_CB.setChecked(GUI_STATE['UV_CB'])
            self.Color_CB.setChecked(GUI_STATE['Color_CB'])
            self.Face_CB.setChecked(GUI_STATE['Face_CB'])
            self.WS__CB.setChecked(GUI_STATE['WS__CB'])
            self.Vis__CB.setChecked(GUI_STATE['Vis__CB'])
            self.Tab_Widget.setCurrentIndex(int(GUI_STATE['Tab_Widget']))
            self.Export_Toggle_Check = GUI_STATE['Export_Toggle_Check']
            self.Convert_Toggle_Check = GUI_STATE['Convert_Toggle_Check']
            self.Window_Setting_Toggle_Check = GUI_STATE['Window_Setting_Toggle_Check']
            self.Attribute_Setting_Toggle_Check = GUI_STATE['Attribute_Setting_Toggle_Check']
            self.Export_Toggle_Fun()
            self.Export_Toggle_Fun()
            self.Convert_Toggle_Fun()
            self.Convert_Toggle_Fun()
            self.Window_Setting_Toggle_Fun()
            self.Window_Setting_Toggle_Fun()
            self.Attribute_Setting_Toggle_Fun()
            self.Attribute_Setting_Toggle_Fun()
    
            return True
        else:
    
            if load==True:
                QMessageBox.warning(self, u"Warning", u"加载失败\n检查路径是否正确")
                return False

    def Open_Directory(self,LineEdit):
        Save_Location = LineEdit.text()
        if Save_Location == "":
            Save_Location = os.getcwd()
        else:
            Save_Location_temp = Save_Location.split('.')[0]
            if Save_Location_temp != Save_Location:
                Save_Location = os.path.split(Save_Location)[0]
        
        if os.path.exists(Save_Location):
            subprocess.call("explorer %s" % Save_Location, shell=True)
        else:
            QMessageBox.warning(self, u"警告", u"路径不存在\n检查路径是否正确")

    # 关闭窗口时保存当前视窗选择
    def closeEvent(self, event):
        self.Save_Json_Fun()

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
                self.undockWindow = cmds.window( title=Title_Name,cc=self.Save_Json_Fun)
            else:
                self.undockWindow = cmds.window( title=Title_Name,rc=self.Save_Json_Fun)
            cmds.paneLayout()
            cmds.showWindow(self.undockWindow)
            ptr = mayaToQT(self.undockWindow)
            return ptr

        elif self.DOCK == "dock":
            window = cmds.window( title=Title_Name)
            cmds.paneLayout()
            self.dockControl = cmds.dockControl( area='right', content=window, label=Title_Name,floatChangeCommand=self.Save_Json_Fun,vcc=self.Save_Json_Fun)
            dock = mayaToQT(window)
            return dock

        elif self.DOCK == "workspace":
            name = title
            if cmds.workspaceControl(name,query=True,exists=True) :
                cmds.deleteUI(name)
            self.workspaceCtrl = cmds.workspaceControl(name,fl=True,label=Title_Name,vcc=self.Save_Json_Fun)
            cmds.paneLayout()
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace

    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)
