# -*- coding:utf-8 -*- 
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
import os
import sys

DIR_PATH = os.path.dirname(__file__)

PLUGIN_PATH = os.path.join(DIR_PATH,"plugin")
GUI_STATE_PATH = os.path.join(DIR_PATH,"json",'GUI_STATE.json')
UI_PATH = os.path.join(DIR_PATH,"ui",'UI2CG.ui')

sys.path.append(PLUGIN_PATH)

from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
from Qt import _uic as uic
import re
import traceback
import json
import shutil
import subprocess
from functools import partial

form_class , base_class = uic.loadUiType(UI_PATH)

class PreviewDialog(QDialog):
    def __init__(self, parent=None , text=""):
        super(PreviewDialog, self).__init__(parent)

        self.textBrowser = QPlainTextEdit(self)
        self.textBrowser.appendPlainText(text)

        def Copy():
            self.textBrowser.selectAll()
            self.textBrowser.copy()

        self.CopyBTN = QPushButton()
        self.CopyBTN.setStyleSheet("height:20px")
        self.CopyBTN.setText("复制全部")
        self.CopyBTN.clicked.connect(Copy)
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.addWidget(self.CopyBTN)
        self.setMinimumSize(800, 500)

class UI2CG(base_class,form_class):

    def __init__(self):
        super(UI2CG,self).__init__()
        self.setupUi(self)
        self.Pick_UI_BTN.clicked.connect(self.Browse_UI)
        self.Pick_Py_BTN.clicked.connect(self.Browse_PY)
        self.Execute_BTN.clicked.connect(self.Convert)
        self.PY_Path_BTN.clicked.connect(partial(self.Open_Directory,self.Py_Line_Text))
        self.UI_Path_BTN.clicked.connect(partial(self.Open_Directory,self.UI_Line_Text))

        self.Path_Toggle_Anim = QPropertyAnimation(self.Path_Layout, b"maximumHeight")
        self.Path_Toggle_Anim.setDuration(300)
        self.Path_Toggle_Anim.setStartValue(0)
        self.Path_Toggle_Anim.setEndValue(self.Path_Layout.sizeHint().height())
        self.Path_Toggle.setCheckable(True)
        self.Path_Toggle.setChecked(True)
        self.Path_Toggle.clicked.connect(self.Path_Toggle_Fun)

        self.RequireHeader_Toggle_Anim = QPropertyAnimation(self.RequireHeader_Layout, b"maximumHeight")
        self.RequireHeader_Toggle_Anim.setDuration(300)
        self.RequireHeader_Toggle_Anim.setStartValue(0)
        self.RequireHeader_Toggle_Anim.setEndValue(self.RequireHeader_Layout.sizeHint().height())
        self.RequireHeader_Toggle.setCheckable(True)
        self.RequireHeader_Toggle.setChecked(True)
        self.RequireHeader_Toggle.clicked.connect(self.RequireHeader_Toggle_Fun)
        
        self.CGHeader_Toggle_Anim = QPropertyAnimation(self.CGHeader_Layout, b"maximumHeight")
        self.CGHeader_Toggle_Anim.setDuration(300)
        self.CGHeader_Toggle_Anim.setStartValue(0)
        self.CGHeader_Toggle_Anim.setEndValue(self.CGHeader_Layout.sizeHint().height())
        self.CGHeader_Toggle.setCheckable(True)
        self.CGHeader_Toggle.setChecked(True)
        self.CGHeader_Toggle.clicked.connect(self.CGHeader_Toggle_Fun)

        self.Preview_BTN.clicked.connect(self.Preview_Fun)

        self.Load_Json_Fun()

    
    def Preview_Fun(self):
        Result = self.Process_UI_Data()
        self.dialogTextBrowser = PreviewDialog(self,text=Result)
        self.dialogTextBrowser.exec_()

    def Path_Toggle_Fun(self,Checked):
        if not Checked:
            self.Path_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Path_Toggle_Anim.start()
            self.Path_Toggle.setText(u"■设置文件路径")
            self.Path_Toggle.setStyleSheet('font:bold')
        else:
            self.Path_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Path_Toggle_Anim.start()
            self.Path_Toggle.setText(u"▼设置文件路径")
            self.Path_Toggle.setStyleSheet('font:normal')
        self.Save_Json_Fun()
    
    def RequireHeader_Toggle_Fun(self,Checked):
        if not Checked:
            self.RequireHeader_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.RequireHeader_Toggle_Anim.start()
            self.RequireHeader_Toggle.setText(u"■通用头文件设置")
            self.RequireHeader_Toggle.setStyleSheet('font:bold')
        else:
            self.RequireHeader_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.RequireHeader_Toggle_Anim.start()
            self.RequireHeader_Toggle.setText(u"▼通用头文件设置")
            self.RequireHeader_Toggle.setStyleSheet('font:normal')
        self.Save_Json_Fun()
    
    def CGHeader_Toggle_Fun(self,Checked):
        if not Checked:
            self.CGHeader_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.CGHeader_Toggle_Anim.start()
            self.CGHeader_Toggle.setText(u"■CG头文件设置")
            self.CGHeader_Toggle.setStyleSheet('font:bold')
        else:
            self.CGHeader_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.CGHeader_Toggle_Anim.start()
            self.CGHeader_Toggle.setText(u"▼CG头文件设置")
            self.CGHeader_Toggle.setStyleSheet('font:normal')
        self.Save_Json_Fun()
        
        
    def Browse_UI(self):
        ui_file = QFileDialog.getOpenFileNames(self, caption="获取ui文件", directory=".",filter="ui (*.ui)")
        # 空数组处理
        try:
            if type(ui_file) is tuple:
                ui_file = ui_file[0]
            if type(ui_file) is list:
                ui_file = ui_file[0]
        except:
            return
        
        self.UI_Line_Text.setText(QDir.toNativeSeparators(ui_file))
        self.Py_Line_Text.setText(QDir.toNativeSeparators("%s" % (ui_file.split('.')[0])))

    def Browse_PY(self):
        py_file = QFileDialog.getExistingDirectory(self, caption="保存文件到", directory=".")
        self.Py_Line_Text.setText(QDir.toNativeSeparators(py_file))

    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['UI_Line_Text'] = self.UI_Line_Text.text() if len(self.UI_Line_Text.text())>0 else ""
        GUI_STATE['Py_Line_Text'] = self.Py_Line_Text.text() if len(self.Py_Line_Text.text())>0 else ""
        GUI_STATE['OS_CB'] = self.OS_CB.isChecked()
        GUI_STATE['JSON_CB'] = self.JSON_CB.isChecked()
        GUI_STATE['Partial_CB'] = self.Partial_CB.isChecked()
        GUI_STATE['SYS_CB'] = self.SYS_CB.isChecked()
        GUI_STATE['Traceback_CB'] = self.Traceback_CB.isChecked()
        GUI_STATE['Subprocess_CB'] = self.Subprocess_CB.isChecked()
        GUI_STATE['Math_CB'] = self.Math_CB.isChecked()
        GUI_STATE['Array_CB'] = self.Array_CB.isChecked()
        GUI_STATE['Time_CB'] = self.Time_CB.isChecked()
        GUI_STATE['Mel_CB'] = self.Mel_CB.isChecked()
        GUI_STATE['OpenMayaUI_CB'] = self.OpenMayaUI_CB.isChecked()
        GUI_STATE['Cmds_CB'] = self.Cmds_CB.isChecked()
        GUI_STATE['OpenMayaMPx_CB'] = self.OpenMayaMPx_CB.isChecked()
        GUI_STATE['OpenMaya_CB'] = self.OpenMaya_CB.isChecked()
        GUI_STATE['PyMel_CB'] = self.PyMel_CB.isChecked()
        GUI_STATE['Maya_RB'] = self.Maya_RB.isChecked()
        GUI_STATE['Houdini_RB'] = self.Houdini_RB.isChecked()
        GUI_STATE['NUKE_RB'] = self.NUKE_RB.isChecked()
        GUI_STATE['Path_Toggle_Check'] = self.Path_Toggle.isChecked()
        GUI_STATE['RequireHeader_Toggle_Check'] = self.RequireHeader_Toggle.isChecked()
        GUI_STATE['CGHeader_Toggle_Check'] = self.CGHeader_Toggle.isChecked()
    
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
            self.OS_CB.setChecked(GUI_STATE['OS_CB'])
            self.JSON_CB.setChecked(GUI_STATE['JSON_CB'])
            self.Partial_CB.setChecked(GUI_STATE['Partial_CB'])
            self.SYS_CB.setChecked(GUI_STATE['SYS_CB'])
            self.Traceback_CB.setChecked(GUI_STATE['Traceback_CB'])
            self.Subprocess_CB.setChecked(GUI_STATE['Subprocess_CB'])
            self.Math_CB.setChecked(GUI_STATE['Math_CB'])
            self.Array_CB.setChecked(GUI_STATE['Array_CB'])
            self.Time_CB.setChecked(GUI_STATE['Time_CB'])
            self.Mel_CB.setChecked(GUI_STATE['Mel_CB'])
            self.OpenMayaUI_CB.setChecked(GUI_STATE['OpenMayaUI_CB'])
            self.Cmds_CB.setChecked(GUI_STATE['Cmds_CB'])
            self.OpenMayaMPx_CB.setChecked(GUI_STATE['OpenMayaMPx_CB'])
            self.OpenMaya_CB.setChecked(GUI_STATE['OpenMaya_CB'])
            self.PyMel_CB.setChecked(GUI_STATE['PyMel_CB'])
            self.Maya_RB.setChecked(GUI_STATE['Maya_RB'])
            self.Houdini_RB.setChecked(GUI_STATE['Houdini_RB'])
            self.NUKE_RB.setChecked(GUI_STATE['NUKE_RB'])
            
            self.CGHeader_Toggle.setChecked(GUI_STATE['CGHeader_Toggle_Check'])
            self.RequireHeader_Toggle.setChecked(GUI_STATE['RequireHeader_Toggle_Check'])
            self.Path_Toggle.setChecked(GUI_STATE['Path_Toggle_Check'])

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

    def closeEvent(self, event,path=GUI_STATE_PATH):
        self.Save_Json_Fun(path=path)
        
    def Open_Directory(self,text):
        Save_Location = text.text()
        if Save_Location == "":
            Save_Location = os.getcwd()
        else:
            Save_Location_temp = Save_Location.split('.')[0]
            if Save_Location_temp != Save_Location:
                Save_Location = os.path.split(Save_Location)[0]
        
        if os.path.exists(Save_Location):
            subprocess.call("explorer %s" % Save_Location, shell=True)
        else:
            QMessageBox.warning(self, "Warning", "路径不存在\n检查路径是否正确")

    
    def Process_Header_Data(self):
        UI_Location = self.UI_Line_Text.text()

        CodingHeader = "# -*- coding:utf-8 -*-" + "\n"

        # Maya Header
        MayaCmdsHeader = "import maya.cmds as cmds" + "\n"
        MayaMelHeader = "import maya.mel as mel" + "\n"
        PyMelHeader = "import pymel.core as pm" + "\n"
        OpenMayaHeader = "import maya.OpenMaya as OpenMaya" + "\n"
        OpenMayaUIHeader = "import maya.OpenMayaUI as omui" + "\n"
        OpenMayaMPxHeader = "import maya.OpenMayaMPx as OpenMayaMPx" + "\n"

        # Require Header
        OSHeader = "import os" + "\n"
        JsonHeader = "import json" + "\n"
        PartialHeader = "from functools import partial" + "\n"

        # Sys Header
        SysHeader = "import sys" + "\n"
        TracebackHeader = "import traceback" + "\n"
        SubprocessHeader = "import subprocess" + "\n"

        # Math Header
        MathHeader = "import math" + "\n"
        ArrayHeader = "import array" + "\n"
        TimeHeader = "import time" + "\n"

        # Qt Header
        QtHeader = """
import plugin.Qt as Qt
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
"""
        Result = ""
        Result += CodingHeader

        # 通用头文件
        Result += "\n" + "# Require Header" + "\n" if self.OS_CB.isChecked() or self.JsonHeader.isChecked() or self.PartialHeader.isChecked() else ""

        Result += OSHeader if self.OS_CB.isChecked() else ""
        Result += JsonHeader if self.JSON_CB.isChecked() else ""
        Result += PartialHeader if self.Partial_CB.isChecked() else ""

        Result += "\n" + "# Sys Header" + "\n" if self.SYS_CB.isChecked() or self.Traceback_CB.isChecked() or self.Subprocess_CB.isChecked() else ""

        Result += SysHeader if self.SYS_CB.isChecked() else ""
        Result += TracebackHeader if self.Traceback_CB.isChecked() else ""
        Result += SubprocessHeader if self.Subprocess_CB.isChecked() else ""

        Result += "\n" + "# Math Header" + "\n" if self.Math_CB.isChecked() or self.Array_CB.isChecked() or self.Time_CB.isChecked() else ""

        Result += MathHeader if self.Math_CB.isChecked() else ""
        Result += ArrayHeader if self.Array_CB.isChecked() else ""
        Result += TimeHeader if self.Time_CB.isChecked() else ""

        if self.RequireHeader_PTE.toPlainText() != "":
            Result += "\n" + "# Custom Header" + "\n"
            Result += self.RequireHeader_PTE.toPlainText() + "\n"

        # Maya 头文件
        Result += "\n" + "# Maya Header" + "\n" if self.Cmds_CB.isChecked() or self.Mel_CB.isChecked() or self.PyMel_CB.isChecked() or self.OpenMaya_CB.isChecked() or self.OpenMayaUI_CB.isChecked() or self.OpenMayaMPx_CB.isChecked() else ""

        Result += MayaCmdsHeader if self.Cmds_CB.isChecked() else ""
        Result += MayaMelHeader if self.Mel_CB.isChecked() else ""
        Result += PyMelHeader if self.PyMel_CB.isChecked() else ""
        Result += OpenMayaHeader if self.OpenMaya_CB.isChecked() else ""
        Result += OpenMayaUIHeader if self.OpenMayaUI_CB.isChecked() else ""
        Result += OpenMayaMPxHeader if self.OpenMayaMPx_CB.isChecked() else ""

        if self.CGHeader_PTE.toPlainText() != "":
            Result += "\n" + "# Custom CG Header" + "\n"
            Result += self.CGHeader_PTE.toPlainText() + "\n"

        Result += "\n" + QtHeader 

        return Result

    ##############################################
    #########      生成UI相关的代码      ##########
    ##############################################

    def Process_UI_Data(self):

        UI_Location = self.UI_Line_Text.text()
        try:
            
            with open(UI_Location, 'r' ) as f:
                uiFile = f.read()
        
        except Exception:
            traceback.print_exc()
            QMessageBox.warning(self, "Warning", "数据写入失败\n检查文件路径是否正确")
            return


        ##############################################
        ##########     Class 声明初始化     ###########
        ##############################################
        
        if self.Maya_RB.isChecked():

            winTitle = self.MayaWin_LE.text() if self.MayaWin_LE.text() != "" else "Default"

            Path_Init = """
from Qt.QtCompat import wrapInstance

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","{0}") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
""".format(os.path.split(UI_Location)[1])  

            Class_Init = """
from {0} import {0}

class {0}_UI_Interface({0}):
    def __init__(self,dock="undock"):
        self.DOCK = dock
        self.Prefix = ""
        self.undockWindow = ""
        self.dockControl = ""
        self.workspaceCtrl = ""

        # 读取当前DOCK属性
        if os.path.exists(GUI_STATE_PATH):
            GUI_STATE = {{}}
            with open(GUI_STATE_PATH,'r') as f:
                GUI_STATE = json.load(f)
            self.DOCK = GUI_STATE["DOCK"]

        # 如果是2017以前的版本 将workspace转换为dock
        if mel.eval("getApplicationVersionAsFloat;")<2017:
            if self.DOCK == "workspace":
                self.DOCK = "dock"

        self.ptr = self.Dock_Win_Management(title=u"{1}")

        super({0}_UI_Interface,self).__init__()
        
        if self.DOCK == "workspace":
            # QMainWindow 无法 addWidget
            self.ptr.layout().addWidget(self.Main_Menu_Bar)
            self.ptr.layout().addWidget(self.Main_Layout)
        else:
            self.ptr.layout().addWidget(self)

        self.Change_Win_Check = False
        self.Change_Win()

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
        self.More_Setting.triggered.connect(self.Change_Win)

""".format(os.path.split(UI_Location)[1].split(".")[0],winTitle)

#         elif self.None_RB.isChecked():
#             Class_Init = """
# class UI_Interface(base_class,form_class):
#     def __init__(self):
#         super(UI_Interface,self).__init__()
#         self.setupUi(self)
# """
        ##############################################
        ##########     Toggle 控件的代码    ###########
        ##############################################

        reg = r'<widget class="QPushButton" name=".*?_Toggle".*?<string>▼(.*?)</string>'
        ToggleNameList = re.findall(re.compile(reg,re.DOTALL),uiFile)
        reg = r'<widget class="QPushButton" name="(.*?)_Toggle"'
        ToggleList = re.findall(re.compile(reg),uiFile)
        
        Toggle_Button_Click = ""
        Toggle_Button_Fun = ""
        num = 0

        for Toggle in ToggleList:
            
            Toggle_Button_Click +="""
        self.{0}_Toggle_Anim = QPropertyAnimation(self.{0}_Layout, b"maximumHeight")
        self.{0}_Toggle_Anim.setDuration(300)
        self.{0}_Toggle_Anim.setStartValue(0)
        self.{0}_Toggle_Anim.setEndValue(self.{0}_Layout.sizeHint().height())
        self.{0}_Toggle_Check = False
        self.{0}_Toggle.clicked.connect(self.{0}_Toggle_Fun)
""".format(Toggle)

            Toggle_Button_Fun +="""
    def {0}_Toggle_Fun(self):
        if self.{0}_Toggle_Check:
            self.{0}_Toggle_Check = False
            self.{0}_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.{0}_Toggle_Anim.start()
            self.{0}_Toggle.setText(u"▼{1}")
            self.{0}_Toggle.setStyleSheet('font:normal')
        else:
            self.{0}_Toggle_Check = True
            self.{0}_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.{0}_Toggle_Anim.start()
            self.{0}_Toggle.setText(u"■{1}")
            self.{0}_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()
""".format(Toggle,ToggleNameList[num])

            num += 1


        ##############################################
        ##########      Pick 控件的代码     ###########
        ##############################################
        if self.Maya_RB.isChecked():

            reg = r'<widget class="QPushButton" name="(.*?)_Pick"'
            PickList = re.findall(re.compile(reg),uiFile)

            Pick_Button_Click = ""
            Pick_Button_Fun = ""
            for Pick in PickList:
                
                Pick_Button_Click +="""
        self.{0}_Get.setVisible(False)
        self.{0}_Pick.clicked.connect(self.{0}_Pick_Fun)
""".format(Pick)

                Pick_Button_Fun +="""
    def {0}_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.{0}_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.{0}_Get.clicked.disconnect()
            except:
                pass
            self.{0}_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.{0}_LE.setText("")
        
        if self.{0}_LE.text() != "":
            self.{0}_Label.setVisible(False)
            self.{0}_Get.setVisible(True)
        else:
            self.{0}_Label.setVisible(True)
            self.{0}_Get.setVisible(False)

        self.Save_Json_Fun()
""".format(Pick)

        ##############################################
        ##########   导入导出JSON的UI实现   ###########
        ##############################################

#         reg = r'<widget class="QPushButton" name="(.*?)_LoadJSON"'
#         LoadJSONList = re.findall(re.compile(reg),uiFile)

#         reg = r'<widget class="QPushButton" name="(.*?)_SaveJSON"'
#         SaveJSONList = re.findall(re.compile(reg),uiFile)

#         Load_JSON_BTN = ""
#         Load_JSON_Fun = ""
#         Save_JSON_BTN = ""
#         Save_JSON_Fun = ""
        
#         for LoadJSON in LoadJSONList:
            
#             Load_JSON_BTN +="""
#         self.{0}_LoadJSON_Label.setVisible(False)
#         self.{0}_LoadJSON_DIR.clicked.connect(partial(self.Open_Directory,self.{0}_LoadJSON_LE))
#         self.{0}_LoadJSON_Browse.clicked.connect(self.{0}_Load_JSON_Browse)
#         self.{0}_LoadJSON.clicked.connect(self.{0}_Load_JSON)
# """.format(LoadJSON)

#             Load_JSON_Fun += """
#     def {0}_Load_JSON_Browse(self):
#         load_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
#         if type(load_file) is tuple:
#             load_file = load_file[0]
#         self.{0}_LoadJSON_LE.setText(QDir.toNativeSeparators(load_file))
#         self.{0}_LoadJSON_Label.setVisible(False)
#         self.{0}_LoadJSON_DIR.setVisible(True)
# """.format(LoadJSON)

#             Load_JSON_Fun += """
#     def {0}_Load_JSON(self):
#         Load_Path = self.{0}_LoadJSON_LE.text()
#         check = self.Load_Json_Fun(path=Load_Path,load=True)
#         if check:
#             QMessageBox.information(self, u"加载成功", u"加载成功")
# """.format(LoadJSON)

        
#         for SaveJSON in SaveJSONList:

#             Save_JSON_BTN +="""
#         self.{0}_SaveJSON_Label.setVisible(False)
#         self.{0}_SaveJSON_DIR.clicked.connect(partial(self.Open_Directory,self.{0}_SaveJSON_LE))
#         self.{0}_SaveJSON_Browse.clicked.connect(self.{0}_Save_JSON_Browse)
#         self.{0}_SaveJSON.clicked.connect(self.{0}_Save_JSON)
# """.format(SaveJSON)

#             Save_JSON_Fun += """
#     def {0}_Save_JSON_Browse(self):
#         save_file = QFileDialog.getSaveFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
#         if type(save_file) is tuple:
#             save_file = save_file[0]
#         self.{0}_SaveJSON_LE.setText(QDir.toNativeSeparators(save_file))
#         self.{0}_SaveJSON_Label.setVisible(False)
#         self.{0}_SaveJSON_DIR.setVisible(True)
# """.format(SaveJSON)

#             Save_JSON_Fun += """
#     def {0}_Save_JSON(self):
#         Save_Path = self.{0}_SaveJSON_LE.text()
#         try:
#             self.Save_Json_Fun(path=Save_Path)
#         except:
#             QMessageBox.warning(self, u"Warning", u"保存失败")
#             traceback.print_exc()
#             return
#         QMessageBox.information(self, u"保存成功", u"保存成功")
# """.format(SaveJSON)

        
        ##############################################
        ###########       其他相关的函数      #########
        ##############################################

#         CloseFun = """
#     # 关闭窗口时保存当前视窗选择
#     def closeEvent(self, event):
#         self.Save_Json_Fun()
# """
        MayaDockFun = """
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
            cmds.evalDeferred("cmds.dockControl(\\"" + self.dockControl  + "\\",e=True,r=True)")
            
            dock = mayaToQT(window)
            return dock

        elif self.DOCK == "workspace":
            name = title
            self.workspaceCtrl = cmds.workspaceControl(name,tabToControl=["ChannelBoxLayerEditor",0],label=Title_Name,vcc=self.Save_Json_Fun)

            # 显示当前面板
            cmds.evalDeferred("cmds.workspaceControl(\\"" + self.workspaceCtrl  + "\\",e=True,r=True)")
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace
"""

        Select_OBJ_Fun = """
    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)
"""
        Change_Win_Fun = """
    def Change_Win(self):
        if self.Change_Win_Check:
            self.setMinimumSize(518,500)
            self.Change_Win_Check = False
            self.More_Setting.setText(u"关闭更多设置")
            self.Tab_Widget.setVisible(True)
            self.Tab_1.layout().addWidget(self.Main_Scroll)
        else:
            self.setMinimumSize(300,280)
            self.Change_Win_Check = True
            self.More_Setting.setText(u"开启更多设置")
            self.Tab_Widget.setVisible(False)
            self.Main_Layout.layout().addWidget(self.Main_Scroll)
"""
        Win_Save_JSON_Browse = """
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
"""
        Win_Load_JSON_Browse = """
    def Win_Load_JSON_Browse(self):
        load_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(load_file) is tuple:
            load_file = load_file[0]
        check = self.Load_Json_Fun(path=QDir.toNativeSeparators(load_file),load=True)
        if check:
            QMessageBox.information(self, u"加载成功", u"加载成功")
"""
        Help_Instruction_Fun = """
    def Help_Instruction_Fun(self):
        try:
            if cmds.window(self.InstructionWin,query=True,exists=True) :
                cmds.deleteUI(self.InstructionWin)
        except:
            pass
        self.InstructionWin = cmds.window(t=u"使用说明",wh=(400,300),rtf=True,s=False)

        cmds.columnLayout(adj=True)
        cmds.textField(tx=u"————————————————主要用法————————————————",ed=False,bgc=(1,.1,.1))
        

        cmds.showWindow(self.InstructionWin)
"""

#         Open_DIR = """
#     def Open_Directory(self,LineEdit):
#         Save_Location = LineEdit.text()
#         if Save_Location == "":
#             Save_Location = os.getcwd()
#         else:
#             Save_Location_temp = Save_Location.split('.')[0]
#             if Save_Location_temp != Save_Location:
#                 Save_Location = os.path.split(Save_Location)[0]
        
#         if os.path.exists(Save_Location):
#             subprocess.call("explorer %s" % Save_Location, shell=True)
#         else:
#             QMessageBox.warning(self, u"警告", u"路径不存在\\n检查路径是否正确")
# """
        Dock_Win_Fun = """
    def Dockable_Window_Fun(self,dock="undock",save=True):
        # 保存当前UI界面
        if save == True:
            self.DOCK = dock
            self.Save_Json_Fun()

        # 检测不同的UI 全部删除
        if cmds.window(self.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\\"" + self.undockWindow + "\\")")

        if cmds.dockControl(self.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\\"" + self.dockControl + "\\")")

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(self.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(self.workspaceCtrl)

        if save == False:
            os.remove(GUI_STATE_PATH)
            
        global {0}_UI 
        {0}_UI = {0}_UI_Interface(dock=dock)
""".format(os.path.split(UI_Location)[1].split(".")[0])
        
        Main_Fun = """
def main():
    # 检测不同的UI 全部删除
    global {0}_UI 

    try:
        if cmds.window({0}_UI.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\\"" + {0}_UI.undockWindow + "\\")")
            # cmds.deleteUI({0}_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl({0}_UI.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\\"" + {0}_UI.dockControl + "\\")")
            # cmds.deleteUI({0}_UI.dockControl)
    except:
        pass

    try:
        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl({0}_UI.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI({0}_UI.workspaceCtrl)
    except:
        pass

    {0}_UI = {0}_UI_Interface(dock="undock")
""".format(os.path.split(UI_Location)[1].split(".")[0])

        ##############################################
        ################    合并代码     ##############
        ##############################################
        Result = ""
        
        Result += self.Process_Header_Data()

        Result += Path_Init 
        Result += Class_Init 

        Result += Toggle_Button_Click
        if self.Maya_RB.isChecked():
            Result += Pick_Button_Click
        # 读取Json数据
        Result += "    " + "    " + "self.Load_Json_Fun()" + "\n"

        Result += Toggle_Button_Fun
        Result += Change_Win_Fun
        Result += Win_Save_JSON_Browse
        Result += Win_Load_JSON_Browse
        Result += Help_Instruction_Fun

        if self.Maya_RB.isChecked():
            Result += Pick_Button_Fun
            Result += MayaDockFun
            Result += Dock_Win_Fun
            Result += Select_OBJ_Fun

        Result += Main_Fun

        return Result

    ##############################################
    #######     *生成Maya逻辑代码Py文件*   #########
    ##############################################
    def Maya_Data(self):
        UI_Location = self.UI_Line_Text.text()
        try:
            
            with open(UI_Location, 'r' ) as f:
                uiFile = f.read()
        
        except Exception:
            traceback.print_exc()
            QMessageBox.warning(self, "Warning", "数据写入失败\n检查文件路径是否正确")
            return

        Path_Init = """
from Qt.QtCompat import wrapInstance

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","{0}") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
""".format(os.path.split(UI_Location)[1])  

        # UI Header
        UIHeader = """
def loadUiType(uiFile):
    import plugin.Qt as Qt
    if Qt.__binding__.startswith('PyQt'):
        from Qt import _uic as uic
        return uic.loadUiType(uiFile)
    elif Qt.__binding__ == 'PySide':
        import pysideuic as uic
    else:
        import pyside2uic as uic
        
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO

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
"""

        Load_UI = "form_class , base_class = loadUiType(UI_PATH)"

        Init_Class = """

class {0}(form_class,base_class):
    def __init__(self,dock="dock"):
        super({0},self).__init__()
        self.setupUi(self)

""".format(os.path.split(UI_Location)[1].split(".")[0])

        reg = r'<widget class="QPushButton" name="(.*?)_BTN"'
        BTNList = re.findall(re.compile(reg),uiFile)

        BTN_Click = ""
        BTN_Fun = ""

        for BTN in BTNList:
            BTN_Click +="""
        self.{0}_BTN.clicked.connect(self.{0}_BTN_Fun)
""".format(BTN)

            BTN_Fun += """
    def {0}_BTN_Fun(self):
        pass
        self.Save_Json_Fun()        
""".format(BTN)

        

        ##############################################
        ###########     Json 存储可变控件     #########
        ##############################################
        
        reg = r'<widget class="QPlainTextEdit" name="(.*?)">'
        QPlainTextEditList = re.findall(re.compile(reg),uiFile)

        reg = r'<widget class="QLineEdit" name="(.*?)">'
        QLineEditList = re.findall(re.compile(reg),uiFile)

        reg = r'<widget class="QCheckBox" name="(.*?)">'
        QCheckBoxList = re.findall(re.compile(reg),uiFile)

        reg = r'<widget class="QRadioButton" name="(.*?)">'
        QRadioButtonList = re.findall(re.compile(reg),uiFile)
        
        reg = r'<widget class="QSlider" name="(.*?)">'
        QSliderList = re.findall(re.compile(reg),uiFile)
        
        reg = r'<widget class="QTabWidget" name="(.*?)">'
        QTabWidgetList = re.findall(re.compile(reg),uiFile)

        reg = r'<widget class="QPushButton" name="(.*?)_ColorBTN"'
        ColorBTNList = re.findall(re.compile(reg),uiFile)

        LoadJsonFun = """
def Load_Json_Fun(self,path=GUI_STATE_PATH,load=False):
    if os.path.exists(path):
        GUI_STATE = {}          
        with open(path,'r') as f:
            GUI_STATE = json.load(f)
""" 

        SaveJsonFun = "\n" + "def Save_Json_Fun(self,path=GUI_STATE_PATH):"  + "\n"
        SaveJsonFun += "    " + "GUI_STATE = {}"  + "\n"

        num = 0 
        for QLineEdit in QLineEditList:
            # 如果是第一个 给个异常防止报错
            if num == 0:
                SaveJsonFun +="""
    try:
        GUI_STATE['{0}'] = self.{0}.text() if len(self.{0}.text())>0 else ""
    except:
        return
""".format(QLineEdit)
                
            else :
                SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.text() if len(self.{0}.text())>0 else \"\"".format(QLineEdit) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setText(GUI_STATE['{0}'])".format(QLineEdit) + "\n"

            num += 1

        for QPlainText in QPlainTextEditList:
            SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.toPlainText() if len(self.{0}.toPlainText())>0 else \"\"".format(QPlainText) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setText(GUI_STATE['{0}'])".format(QLineEdit) + "\n"


        for QCheckBox in QCheckBoxList:
            SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.isChecked()".format(QCheckBox) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setChecked(GUI_STATE['{0}'])".format(QCheckBox) + "\n"

        
        for QRadioButton in QRadioButtonList:
            SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.isChecked()".format(QRadioButton) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setChecked(GUI_STATE['{0}'])".format(QRadioButton) + "\n"
        
        for QSlider in QSliderList:
            SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.value()".format(QSlider) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setValue(GUI_STATE['{0}'])".format(QSlider) + "\n"
        
        for QTabWidget in QTabWidgetList:
            SaveJsonFun += "    " + "GUI_STATE['{0}'] = self.{0}.currentIndex() ".format(QTabWidget) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}.setCurrentIndex(int(GUI_STATE['{0}']))".format(QTabWidget) + "\n"
        
        reg = r'<widget class="QPushButton" name="(.*?)_Toggle"'
        ToggleList = re.findall(re.compile(reg),uiFile)

        for Toggle in ToggleList:
            SaveJsonFun += "    " + "GUI_STATE['{0}_Toggle_Check'] = self.{0}_Toggle_Check".format(Toggle) + "\n"

            LoadJsonFun += "    " + "    " + "self.{0}_Toggle_Check = GUI_STATE['{0}_Toggle_Check']".format(Toggle) + "\n"
                    
        ColorNum = 0
        for ColorBTN in ColorBTNList:
            SaveJsonFun +="""
    styleSheet = self.{0}.styleSheet().split("(")[1].split(",")
    r = float(styleSheet[0])
    g = float(styleSheet[1])
    b = float(styleSheet[2].split(")")[0])
    color = (r,g,b)
    GUI_STATE['{0}'] = (color[0],color[1],color[2])
""".format(ColorBTN)
            
            if ColorNum == 0:
                LoadJsonFun += "\n" + "    " + "    " + "if mel.eval(\"getApplicationVersionAsFloat;\")>=2017:" + "\n"

            LoadJsonFun +="""
            r = GUI_STATE['{0}'][0]
            g = GUI_STATE['{0}'][1]
            b = GUI_STATE['{0}'][2]
            self.{0}.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))
""".format(ColorBTN)

            ColorNum += 1

        # 如果是Maya的代码 记录当前窗口状态
        if self.Maya_RB.isChecked():
            SaveJsonFun +=  "    " + "GUI_STATE['DOCK'] = self.DOCK" + "\n"

            # for Pick in PickList:
            #     SaveJsonFun += "    " + "GUI_STATE['{0}_Pick_Check'] = self.{0}_Get.isVisible()".format(Pick) + "\n"

            #     LoadJsonFun += "    " + "    " + "self.{0}_Get.setVisible(GUI_STATE['{0}_Pick_Check'])".format(Pick) + "\n"
            #     LoadJsonFun += "    " + "    " + "self.{0}_Label.setVisible(not GUI_STATE['{0}_Pick_Check'])".format(Pick) + "\n"
            #     LoadJsonFun += "    " + "    " + "if self.{0}_LE.text() != \"\"".format(Pick) + "\n"
            #     LoadJsonFun += "    " + "    " + "    " + "self.{0}_Get.clicked.connect(partial(self.Select_OBJ_Fun,self.{0}_LE.text()))".format(Pick) + "\n"
            
        # 完成 Json 存储函数
        SaveJsonFun +="""
    try:
        with open(path,'w') as f:
            json.dump(GUI_STATE,f,indent=4)
    except:
        if path != "": 
            QMessageBox.warning(self, u"Warning", u"保存失败")
"""

        
        # 完成 Json 读取函数
        for Toggle in ToggleList:
            LoadJsonFun += "    " + "    " + "self.{0}_Toggle_Fun()".format(Toggle) + "\n"
            LoadJsonFun += "    " + "    " + "self.{0}_Toggle_Fun()".format(Toggle) + "\n"

        LoadJsonFun += """
        return True
    else:

        if load==True:
            QMessageBox.warning(self, u"Warning", u"加载失败\\n检查路径是否正确")
            return False
"""


        # 处理 Json 函数的缩进
        reg = r'.*\n'
        SaveJsonList = re.findall(re.compile(reg),SaveJsonFun)
        NewSaveJsonList = ""
        for SaveJson in SaveJsonList:
            NewSaveJsonList += "    " + SaveJson

        SaveJsonFun = NewSaveJsonList

        # 处理 读取Json 按钮缩进
        reg = r'.*\n'
        LoadJsonList = re.findall(re.compile(reg),LoadJsonFun)
        NewLoadJsonList = ""
        for LoadJson in LoadJsonList:
            NewLoadJsonList += "    " + LoadJson
        LoadJsonFun = NewLoadJsonList


        Result = ""
        Result += self.Process_Header_Data()
        Result += UIHeader
        Result += Path_Init
        Result += Load_UI
        Result += Init_Class
        Result += BTN_Click
        Result += BTN_Fun
        Result += SaveJsonFun
        Result += LoadJsonFun
        return Result
    
    ##############################################
    #######     *生成install.mel文件*     #########
    ##############################################
    def Install_Mel(self):
        UI_Location = self.UI_Line_Text.text()

        Mel = ""

        Mel += """
string $subDir = "{0}/";
string $scriptName="{0}";
string $scirptExt = "py";

string $ImagePath = "/icon/{0}" ;
string $iconExt="png";

global string $gShelfTopLevel;
string $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;
setParent $currentShelf;
string $asInstallScriptLocation=`asInstallScriptLocation`;

string $command="import sys\\nsys.path.append(\\"" + $asInstallScriptLocation + $subDir + "\\")\\nimport " + $scriptName +"\\nimport " + $scriptName + "_ui\\nreload(" + $scriptName + ")\\nreload(" + $scriptName + "_ui)\\n\\n" + $scriptName + "_ui.main()";
string $sourceFile=$asInstallScriptLocation+ $subDir + $scriptName+"."+$scirptExt;

if (`asMayaVersionAsFloat`<2012)
	$iconExt="xpm";
string $icon=$asInstallScriptLocation + $subDir + $ImagePath + "." +$iconExt;
if (!`file -q -ex $sourceFile`)
	error ("Something went wrong, can not find: \\""+$sourceFile+"\\"");
shelfButton
	-command $command
	-annotation $scriptName
	-label $scriptName
	-image $icon
	-image1 $icon
	-sourceType "python"
;

global proc asInstallScriptLocator (){{}}

global proc string asInstallScriptLocation ()
{{
string $whatIs=`whatIs asInstallScriptLocator`;
string $fullPath=`substring $whatIs 25 999`;
string $buffer[];
string $slash="/";
if (`gmatch $whatIs "*\\\\\\*"`)//sourced from ScriptEditor
	$slash="\\\\";
int $numTok=`tokenize $fullPath $slash $buffer`;
int $numLetters=size($fullPath);
int $numLettersLastFolder=size($buffer[$numTok-1]);
string $scriptLocation=`substring $fullPath 1 ($numLetters-$numLettersLastFolder)`;
return $scriptLocation;
}}

global proc float asMayaVersionAsFloat ()
{{
float $version=2012;
if (`exists getApplicationVersionAsFloat`)
	return `getApplicationVersionAsFloat`;
string $versionString=`about -v`;
string $tempString[];
string $char;
tokenize $versionString $tempString;
//default to 2012, if versionString is not all numbers
for ($i=0;$i<size($tempString[0]);$i++)
	{{
	$char=`substring $tempString[0] ($i+1) ($i+1)`;
	if (!`gmatch $char "[0-9]"`)
		return 2012;
	}}
$version=$tempString[0];
return $version;
}}
""".format(os.path.split(UI_Location)[1].split(".")[0])

        return Mel

    def Convert(self):
        directory = self.Py_Line_Text.text()
        UI_Location = self.UI_Line_Text.text()
        
        Module = ""
        HeaderCheck = False

        if not self.Subprocess_CB.isChecked():
            HeaderCheck = True
            Module += "> subprocess" + "\n"

        if not self.Traceback_CB.isChecked():
            HeaderCheck = True
            Module += "> traceback" + "\n"
            
        if not self.OS_CB.isChecked():
            HeaderCheck = True
            Module += "> os" + "\n"

        if not self.JSON_CB.isChecked():
            HeaderCheck = True
            Module += "> json" + "\n"

        if not self.Partial_CB.isChecked():
            HeaderCheck = True
            Module += "> partial" + "\n"

        if self.Maya_RB.isChecked():
            if not self.OpenMayaUI_CB.isChecked():
                HeaderCheck = True
                Module += "> maya.OpenMayaUI" + "\n"

            if not self.Mel_CB.isChecked():
                HeaderCheck = True
                Module += "> maya.mel" + "\n"

            if not self.Cmds_CB.isChecked():
                HeaderCheck = True
                Module += "> maya.cmds" + "\n"

        if HeaderCheck:
            reply = QMessageBox.question(self, u'模块文件缺失',
            u"当前操作缺失模块\n%s运行代码会导致错误\n你确定要继续执行生成吗？" % Module, QMessageBox.Yes, QMessageBox.No)
 
            if reply == QMessageBox.No:
                return
        
        CodeDir = os.path.join(directory,os.path.split(UI_Location)[1].split(".")[0])
        pluginDir = os.path.join(CodeDir,"plugin")
        jsonDir = os.path.join(CodeDir,"json")
        iconDir = os.path.join(CodeDir,"icon")
        uiDir = os.path.join(CodeDir,"ui")
        if not os.path.exists(directory):
            os.mkdir(directory)
            if not os.path.exists(CodeDir):
                os.mkdir(CodeDir)

            if not os.path.exists(pluginDir):
                os.mkdir(pluginDir)
            if not os.path.exists(jsonDir):
                os.mkdir(jsonDir)
            if not os.path.exists(iconDir):
                os.mkdir(iconDir)
            if not os.path.exists(uiDir):
                os.mkdir(uiDir)
        
        # 复制UI文件
        UI_Target = os.path.join(uiDir,os.path.split(UI_Location)[1])
        shutil.copyfile(UI_Location,UI_Target)
            
        # 复制Qt文件
        Qt_Location = os.path.join(DIR_PATH,"plugin",'Qt.py')
        Qt_Target = os.path.join(pluginDir,'Qt.py')
        shutil.copyfile(Qt_Location,Qt_Target)

        # 生成 __init__ Python文件
        Init_Location = os.path.join(pluginDir,'__init__.py')
        with open(Init_Location, 'w' ):
            pass

        # 设置Py文件路径
        UI_Compile_Location = os.path.join(CodeDir,os.path.split(UI_Location)[1].split(".")[0]+"_ui.py")

        UI_Result = self.Process_UI_Data()
        
        
        with open(UI_Compile_Location, 'w'  ) as f:
            f.write(UI_Result)

        if self.Maya_RB.isChecked():
            Maya_Result = self.Maya_Data()
            Maya_PY_Location = os.path.join(CodeDir,os.path.split(UI_Location)[1].split(".")[0]+".py")
            with open(Maya_PY_Location, 'w'  ) as f:
                f.write(Maya_Result)

            Mel_Result = self.Install_Mel()
            Maya_Mel_Location = os.path.join(directory,"install.mel")
            with open(Maya_Mel_Location, 'w'  ) as f:
                f.write(Mel_Result)


        QMessageBox.information(self, u"提示", u"数据写入完成")

app = QApplication(sys.argv)
dl = UI2CG()
dl.show()
app.exec_()
