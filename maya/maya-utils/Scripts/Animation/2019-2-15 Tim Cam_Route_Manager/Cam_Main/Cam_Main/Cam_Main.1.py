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

from Qt.QtCompat import wrapInstance

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","Cam_Main.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

import Cam_Item_Layout
import Cam_Attribute_Panel
reload(Cam_Item_Layout)
reload(Cam_Attribute_Panel)
from Cam_Item_Layout import Cam_Item_Layout
from Cam_Attribute_Panel import Cam_Attribute_Panel

class Cam_Main(form_class,base_class):
    def __init__(self):
        super(Cam_Main,self).__init__()
        self.setupUi(self)
        
        self.Cam_Item_Widget = Cam_Item_Layout(self)
        self.Cam_Attribute_Widget = Cam_Attribute_Panel(self)
        splitter = QSplitter()
        splitter.setHandleWidth(5)
        splitter.addWidget(self.Cam_Item_Widget)
        splitter.addWidget(self.Cam_Attribute_Widget)
        self.Main_Layout.layout().addWidget(splitter)

        self.Cam_Item_Widget.mousePressEvent = self.Cam_Item_Pressing_Event
        self.Default_Attr_Setting()
    

    def Default_Attr_Setting(self):
        self.Cam_Attribute_Widget.Cam_Name_Label.setText(u"<center> - 请选择镜头 - </center>")
        self.Cam_Attribute_Widget.Cam_Input_Toggle.setVisible(False)
        self.Cam_Attribute_Widget.Cam_Input_Layout.setVisible(False)
        self.Cam_Attribute_Widget.Cam_Output_Toggle.setVisible(False)
        self.Cam_Attribute_Widget.Cam_Output_Layout.setVisible(False)


    def Cam_Item_Pressing_Event(self,e):
        """
        mousePressEvent 
        # Note 点击事件触发
        """
        ##   Note 清空所有颜色轮廓
        for i,child in enumerate(self.Cam_Item_Widget.Item_Layout.children()):
            if i != 0:
                if child.Cam_Item.styleSheet() != "":
                    child.Cam_Item.setStyleSheet("")

        ##   Note 坐标偏移
        offset = 90-self.Cam_Item_Widget.Scroll_Offset
        for i,child in enumerate(self.Cam_Item_Widget.Item_Layout.children()):
            if i != 0:
                ##   Note 如果坐标匹配则载入相关数据
                if child.geometry().contains(e.pos().x(),e.pos().y()-offset):
                    child.Cam_Item.setStyleSheet("#Cam_Item{border:3px solid red}" )

                    CamName = child.Cam_LE.text()
                    self.Cam_Attribute_Widget.Cam_Name_Label.setText(u"<center> - %s - </center>" % CamName)
                    self.Cam_Attribute_Widget.Cam_Input_Toggle.setVisible(True)
                    self.Cam_Attribute_Widget.Cam_Input_Layout.setVisible(True)
                    self.Cam_Attribute_Widget.Cam_Output_Toggle.setVisible(True)
                    self.Cam_Attribute_Widget.Cam_Output_Layout.setVisible(True)
                    self.Cam_Attribute_Widget.Add_CamGrp_Layout.setVisible(True)
                    self.Cam_Attribute_Widget.Strat_Time_Layout.setVisible(True)
                    self.Cam_Attribute_Widget.End_Time_Layout.setVisible(True)
                    self.Cam_Attribute_Widget.Auto_Catch_Label.setVisible(True)
                    self.Cam_Attribute_Widget.Add_Loc_Layout.setVisible(True)

                    self.Cam_Attribute_Widget.Current_Item = child

                    if os.path.exists(GUI_STATE_PATH):
                        GUI_STATE = {}          
                        with open(GUI_STATE_PATH,'r') as f:
                            GUI_STATE = json.load(f)

                        Attr = GUI_STATE['Cam_Item'][CamName]["Attr"]
                        self.Cam_Attribute_Widget.Add_CamGrp_LE.setText(Attr["Add_CamGrp_LE"])
                        self.Cam_Attribute_Widget.Add_Loc_LE.setText(Attr["Add_Loc_LE"])
                        self.Cam_Attribute_Widget.Add_Crv_LE.setText(Attr["Add_Crv_LE"])
                        self.Cam_Attribute_Widget.Add_Motion_Path_LE.setText(Attr["Add_Motion_Path_LE"])
                        self.Cam_Attribute_Widget.Strat_Time_SB.setValue(int(Attr["Strat_Time_SB"]))
                        self.Cam_Attribute_Widget.End_Time_SB.setValue(int(Attr["End_Time_SB"]))
                        
                    else:
                       QMessageBox.warning(self, u"Warning", u"加载参数失败") 

                    break
        else:
            ##   Note 遍历全部对象说明没有匹配 使用默认情况
            if self.Cam_Item_Widget.Cam_Base_Label.geometry().contains(e.pos().x(),e.pos().y()-40):

                self.Cam_Attribute_Widget.Current_Item = self.Cam_Item_Widget

                self.Cam_Attribute_Widget.Cam_Input_Toggle.setVisible(True)
                self.Cam_Attribute_Widget.Cam_Input_Layout.setVisible(True)
                self.Cam_Attribute_Widget.Cam_Output_Toggle.setVisible(False)
                self.Cam_Attribute_Widget.Cam_Output_Layout.setVisible(False)
                self.Cam_Attribute_Widget.Add_CamGrp_Layout.setVisible(False)
                self.Cam_Attribute_Widget.Strat_Time_Layout.setVisible(False)
                self.Cam_Attribute_Widget.End_Time_Layout.setVisible(False)
                self.Cam_Attribute_Widget.Auto_Catch_Label.setVisible(False)
                self.Cam_Attribute_Widget.Add_Loc_Layout.setVisible(False)
                Cam_Base_Name = self.Cam_Item_Widget.Cam_Base_LE.text()
                self.Cam_Attribute_Widget.Cam_Name_Label.setText(u"<center> - %s - </center>" % Cam_Base_Name)

            else:
                self.Default_Attr_Setting()

    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['DOCK'] = self.DOCK
        GUI_STATE['Cam_Item'] = {}
        GUI_STATE['Cam_Base'] = {}
        
        for i,child in enumerate(self.Cam_Item_Widget.Item_Layout.children()):
            if i != 0:
                CamName = child.Cam_LE.text()
                GUI_STATE['Cam_Item'][CamName] = {}
                GUI_STATE['Cam_Item'][CamName]["Num"] = child.Num
                GUI_STATE['Cam_Item'][CamName]["Cam"] = child.Cam_LE.text()
                GUI_STATE['Cam_Item'][CamName]["Attr"] = {}
                GUI_STATE['Cam_Item'][CamName]["Attr"]["Add_Loc_LE"] = child.Attr["Add_Loc_LE"]
                GUI_STATE['Cam_Item'][CamName]["Attr"]["Add_Crv_LE"] = child.Attr["Add_Crv_LE"]
                GUI_STATE['Cam_Item'][CamName]["Attr"]["Add_Motion_Path_LE"] = child.Attr["Add_Motion_Path_LE"]
                GUI_STATE['Cam_Item'][CamName]["Attr"]["Add_CamGrp_LE"] = child.Attr["Add_CamGrp_LE"]
                GUI_STATE['Cam_Item'][CamName]["Attr"]["Strat_Time_SB"] = child.Attr["Strat_Time_SB"]
                GUI_STATE['Cam_Item'][CamName]["Attr"]["End_Time_SB"] = child.Attr["End_Time_SB"]

        GUI_STATE['Cam_Base']["Attr"] = {}
        GUI_STATE['Cam_Base']["Attr"]["Add_Crv_LE"] = self.Cam_Item_Widget.Attr["Add_Crv_LE"]
        GUI_STATE['Cam_Base']["Attr"]["Add_Motion_Path_LE"] = self.Cam_Item_Widget.Attr["Add_Motion_Path_LE"]
        GUI_STATE['Cam_Base']["Attr"]["Name"] = self.Cam_Item_Widget.Cam_Base_LE.text()

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

            for CamName in GUI_STATE['Cam_Item']:
                Cam     = self.Cam_Item_Widget.Item_Add_Fn()
                CamAttr = GUI_STATE['Cam_Item'][CamName]["Attr"]
                Cam.Num = GUI_STATE['Cam_Item'][CamName]["Num"]
                
                Cam.Attr["Add_Loc_LE"]         = CamAttr["Add_Loc_LE"]
                Cam.Attr["Add_Crv_LE"]         = CamAttr["Add_Crv_LE"]
                Cam.Attr["Add_Motion_Path_LE"] = CamAttr["Add_Motion_Path_LE"]
                Cam.Attr["Add_CamGrp_LE"]      = CamAttr["Add_CamGrp_LE"]
                Cam.Attr["Strat_Time_SB"]      = CamAttr["Strat_Time_SB"]
                Cam.Attr["End_Time_SB"]        = CamAttr["End_Time_SB"]

                Cam.Cam_LE.setText(GUI_STATE['Cam_Item'][CamName]["Cam"])

            self.Cam_Item_Widget.Attr["Add_Crv_LE"] = GUI_STATE['Cam_Base']["Attr"]["Add_Crv_LE"]
            self.Cam_Item_Widget.Attr["Add_Motion_Path_LE"] = GUI_STATE['Cam_Base']["Attr"]["Add_Motion_Path_LE"]
            self.Cam_Item_Widget.Cam_Base_LE.setText(GUI_STATE['Cam_Base']["Attr"]["Name"])


            return True
        else:
    
            if load==True:
                QMessageBox.warning(self, u"Warning", u"加载失败\n检查路径是否正确")
                return False
         

