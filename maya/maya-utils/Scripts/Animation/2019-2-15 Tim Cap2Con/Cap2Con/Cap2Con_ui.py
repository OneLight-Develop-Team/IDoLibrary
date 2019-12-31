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
UI_PATH = os.path.join(DIR,"ui","Cap2Con.ui") 
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

        ptr = self.Dock_Win_Management(title=u"ADV到TSM约束 动捕数据切换")

        super(UI_Interface,self).__init__(parent=ptr)
        self.parent().layout().addWidget(self)
        self.setupUi(self)

        self.Capture_Data_Toggle_Anim = QPropertyAnimation(self.Capture_Data_Layout, "maximumHeight")
        self.Capture_Data_Toggle_Anim.setDuration(300)
        self.Capture_Data_Toggle_Anim.setStartValue(0)
        self.Capture_Data_Toggle_Anim.setEndValue(self.Capture_Data_Layout.sizeHint().height())
        self.Capture_Data_Toggle_Check = False
        self.Capture_Data_Toggle.clicked.connect(self.Capture_Data_Toggle_Fun)

        self.Target_Data_Toggle_Anim = QPropertyAnimation(self.Target_Data_Layout, "maximumHeight")
        self.Target_Data_Toggle_Anim.setDuration(300)
        self.Target_Data_Toggle_Anim.setStartValue(0)
        self.Target_Data_Toggle_Anim.setEndValue(self.Target_Data_Layout.sizeHint().height())
        self.Target_Data_Toggle_Check = False
        self.Target_Data_Toggle.clicked.connect(self.Target_Data_Toggle_Fun)

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

        self.Capture_Mid_Spine_Get.setVisible(False)
        self.Capture_Mid_Spine_Pick.clicked.connect(self.Capture_Mid_Spine_Pick_Fun)

        self.Capture_Head_Get.setVisible(False)
        self.Capture_Head_Pick.clicked.connect(self.Capture_Head_Pick_Fun)

        self.Capture_L_Knee_Get.setVisible(False)
        self.Capture_L_Knee_Pick.clicked.connect(self.Capture_L_Knee_Pick_Fun)

        self.Capture_L_Ankle_Get.setVisible(False)
        self.Capture_L_Ankle_Pick.clicked.connect(self.Capture_L_Ankle_Pick_Fun)

        self.Capture_R_Shoulder_Get.setVisible(False)
        self.Capture_R_Shoulder_Pick.clicked.connect(self.Capture_R_Shoulder_Pick_Fun)

        self.Capture_R_Leg_Get.setVisible(False)
        self.Capture_R_Leg_Pick.clicked.connect(self.Capture_R_Leg_Pick_Fun)

        self.Capture_R_Knee_Get.setVisible(False)
        self.Capture_R_Knee_Pick.clicked.connect(self.Capture_R_Knee_Pick_Fun)

        self.Capture_R_Hand_Get.setVisible(False)
        self.Capture_R_Hand_Pick.clicked.connect(self.Capture_R_Hand_Pick_Fun)

        self.Capture_L_Hand_Get.setVisible(False)
        self.Capture_L_Hand_Pick.clicked.connect(self.Capture_L_Hand_Pick_Fun)

        self.Capture_L_HandPV_Get.setVisible(False)
        self.Capture_L_HandPV_Pick.clicked.connect(self.Capture_L_HandPV_Pick_Fun)

        self.Capture_Body_Get.setVisible(False)
        self.Capture_Body_Pick.clicked.connect(self.Capture_Body_Pick_Fun)

        self.Capture_R_HandPV_Get.setVisible(False)
        self.Capture_R_HandPV_Pick.clicked.connect(self.Capture_R_HandPV_Pick_Fun)

        self.Capture_L_Foot_Get.setVisible(False)
        self.Capture_L_Foot_Pick.clicked.connect(self.Capture_L_Foot_Pick_Fun)

        self.Capture_R_Foot_Get.setVisible(False)
        self.Capture_R_Foot_Pick.clicked.connect(self.Capture_R_Foot_Pick_Fun)

        self.Capture_L_FootPV_Get.setVisible(False)
        self.Capture_L_FootPV_Pick.clicked.connect(self.Capture_L_FootPV_Pick_Fun)

        self.Capture_R_FootPV_Get.setVisible(False)
        self.Capture_R_FootPV_Pick.clicked.connect(self.Capture_R_FootPV_Pick_Fun)

        self.Capture_L_Wrist_Get.setVisible(False)
        self.Capture_L_Wrist_Pick.clicked.connect(self.Capture_L_Wrist_Pick_Fun)

        self.Capture_Lower_Spine_Get.setVisible(False)
        self.Capture_Lower_Spine_Pick.clicked.connect(self.Capture_Lower_Spine_Pick_Fun)

        self.Capture_R_Ankle_Get.setVisible(False)
        self.Capture_R_Ankle_Pick.clicked.connect(self.Capture_R_Ankle_Pick_Fun)

        self.Capture_L_Leg_Get.setVisible(False)
        self.Capture_L_Leg_Pick.clicked.connect(self.Capture_L_Leg_Pick_Fun)

        self.Capture_R_Arm_Get.setVisible(False)
        self.Capture_R_Arm_Pick.clicked.connect(self.Capture_R_Arm_Pick_Fun)

        self.Capture_L_Arm_Get.setVisible(False)
        self.Capture_L_Arm_Pick.clicked.connect(self.Capture_L_Arm_Pick_Fun)

        self.Capture_L_Shoulder_Get.setVisible(False)
        self.Capture_L_Shoulder_Pick.clicked.connect(self.Capture_L_Shoulder_Pick_Fun)

        self.Capture_L_Toe_Get.setVisible(False)
        self.Capture_L_Toe_Pick.clicked.connect(self.Capture_L_Toe_Pick_Fun)

        self.Capture_R_Toe_Get.setVisible(False)
        self.Capture_R_Toe_Pick.clicked.connect(self.Capture_R_Toe_Pick_Fun)

        self.Capture_Upper_Spine_Get.setVisible(False)
        self.Capture_Upper_Spine_Pick.clicked.connect(self.Capture_Upper_Spine_Pick_Fun)

        self.Capture_R_Wrist_Get.setVisible(False)
        self.Capture_R_Wrist_Pick.clicked.connect(self.Capture_R_Wrist_Pick_Fun)

        self.Capture_L_Elbow_Get.setVisible(False)
        self.Capture_L_Elbow_Pick.clicked.connect(self.Capture_L_Elbow_Pick_Fun)

        self.Capture_R_Elbow_Get.setVisible(False)
        self.Capture_R_Elbow_Pick.clicked.connect(self.Capture_R_Elbow_Pick_Fun)

        self.Target_Lower_Spine_Get.setVisible(False)
        self.Target_Lower_Spine_Pick.clicked.connect(self.Target_Lower_Spine_Pick_Fun)

        self.Target_L_Wrist_Get.setVisible(False)
        self.Target_L_Wrist_Pick.clicked.connect(self.Target_L_Wrist_Pick_Fun)

        self.Target_R_Toe_Get.setVisible(False)
        self.Target_R_Toe_Pick.clicked.connect(self.Target_R_Toe_Pick_Fun)

        self.Target_L_Toe_Get.setVisible(False)
        self.Target_L_Toe_Pick.clicked.connect(self.Target_L_Toe_Pick_Fun)

        self.Target_L_Ankle_Get.setVisible(False)
        self.Target_L_Ankle_Pick.clicked.connect(self.Target_L_Ankle_Pick_Fun)

        self.Target_L_Knee_Get.setVisible(False)
        self.Target_L_Knee_Pick.clicked.connect(self.Target_L_Knee_Pick_Fun)

        self.Target_R_Ankle_Get.setVisible(False)
        self.Target_R_Ankle_Pick.clicked.connect(self.Target_R_Ankle_Pick_Fun)

        self.Target_R_Knee_Get.setVisible(False)
        self.Target_R_Knee_Pick.clicked.connect(self.Target_R_Knee_Pick_Fun)

        self.Target_L_Leg_Get.setVisible(False)
        self.Target_L_Leg_Pick.clicked.connect(self.Target_L_Leg_Pick_Fun)

        self.Target_Mid_Spine_Get.setVisible(False)
        self.Target_Mid_Spine_Pick.clicked.connect(self.Target_Mid_Spine_Pick_Fun)

        self.Target_Upper_Spine_Get.setVisible(False)
        self.Target_Upper_Spine_Pick.clicked.connect(self.Target_Upper_Spine_Pick_Fun)

        self.Target_R_Leg_Get.setVisible(False)
        self.Target_R_Leg_Pick.clicked.connect(self.Target_R_Leg_Pick_Fun)

        self.Target_R_Arm_Get.setVisible(False)
        self.Target_R_Arm_Pick.clicked.connect(self.Target_R_Arm_Pick_Fun)

        self.Target_L_Arm_Get.setVisible(False)
        self.Target_L_Arm_Pick.clicked.connect(self.Target_L_Arm_Pick_Fun)

        self.Target_R_Shoulder_Get.setVisible(False)
        self.Target_R_Shoulder_Pick.clicked.connect(self.Target_R_Shoulder_Pick_Fun)

        self.Target_L_Shoulder_Get.setVisible(False)
        self.Target_L_Shoulder_Pick.clicked.connect(self.Target_L_Shoulder_Pick_Fun)

        self.Target_Head_Get.setVisible(False)
        self.Target_Head_Pick.clicked.connect(self.Target_Head_Pick_Fun)

        self.Target_R_Hand_Get.setVisible(False)
        self.Target_R_Hand_Pick.clicked.connect(self.Target_R_Hand_Pick_Fun)

        self.Target_L_Hand_Get.setVisible(False)
        self.Target_L_Hand_Pick.clicked.connect(self.Target_L_Hand_Pick_Fun)

        self.Target_L_HandPV_Get.setVisible(False)
        self.Target_L_HandPV_Pick.clicked.connect(self.Target_L_HandPV_Pick_Fun)

        self.Target_Body_Get.setVisible(False)
        self.Target_Body_Pick.clicked.connect(self.Target_Body_Pick_Fun)

        self.Target_R_HandPV_Get.setVisible(False)
        self.Target_R_HandPV_Pick.clicked.connect(self.Target_R_HandPV_Pick_Fun)

        self.Target_L_Foot_Get.setVisible(False)
        self.Target_L_Foot_Pick.clicked.connect(self.Target_L_Foot_Pick_Fun)

        self.Target_R_Foot_Get.setVisible(False)
        self.Target_R_Foot_Pick.clicked.connect(self.Target_R_Foot_Pick_Fun)

        self.Target_L_FootPV_Get.setVisible(False)
        self.Target_L_FootPV_Pick.clicked.connect(self.Target_L_FootPV_Pick_Fun)

        self.Target_R_FootPV_Get.setVisible(False)
        self.Target_R_FootPV_Pick.clicked.connect(self.Target_R_FootPV_Pick_Fun)

        self.Target_L_Elbow_Get.setVisible(False)
        self.Target_L_Elbow_Pick.clicked.connect(self.Target_L_Elbow_Pick_Fun)

        self.Target_R_Wrist_Get.setVisible(False)
        self.Target_R_Wrist_Pick.clicked.connect(self.Target_R_Wrist_Pick_Fun)

        self.Target_R_Elbow_Get.setVisible(False)
        self.Target_R_Elbow_Pick.clicked.connect(self.Target_R_Elbow_Pick_Fun)
        self.Load_Json_Fun()

    def Capture_Mid_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_Mid_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_Mid_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Capture_Mid_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_Mid_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_Mid_Spine_LE.text() != "":
            self.Capture_Mid_Spine_Label.setVisible(False)
            self.Capture_Mid_Spine_Get.setVisible(True)
        else:
            self.Capture_Mid_Spine_Label.setVisible(True)
            self.Capture_Mid_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_Head_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_Head_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_Head_Get.clicked.disconnect()
            except:
                pass
            self.Capture_Head_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_Head_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_Head_LE.text() != "":
            self.Capture_Head_Label.setVisible(False)
            self.Capture_Head_Get.setVisible(True)
        else:
            self.Capture_Head_Label.setVisible(True)
            self.Capture_Head_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Knee_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Knee_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Knee_LE.text() != "":
            self.Capture_L_Knee_Label.setVisible(False)
            self.Capture_L_Knee_Get.setVisible(True)
        else:
            self.Capture_L_Knee_Label.setVisible(True)
            self.Capture_L_Knee_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Ankle_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Ankle_LE.text() != "":
            self.Capture_L_Ankle_Label.setVisible(False)
            self.Capture_L_Ankle_Get.setVisible(True)
        else:
            self.Capture_L_Ankle_Label.setVisible(True)
            self.Capture_L_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Shoulder_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Shoulder_LE.text() != "":
            self.Capture_R_Shoulder_Label.setVisible(False)
            self.Capture_R_Shoulder_Get.setVisible(True)
        else:
            self.Capture_R_Shoulder_Label.setVisible(True)
            self.Capture_R_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Leg_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Leg_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Leg_LE.text() != "":
            self.Capture_R_Leg_Label.setVisible(False)
            self.Capture_R_Leg_Get.setVisible(True)
        else:
            self.Capture_R_Leg_Label.setVisible(True)
            self.Capture_R_Leg_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Knee_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Knee_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Knee_LE.text() != "":
            self.Capture_R_Knee_Label.setVisible(False)
            self.Capture_R_Knee_Get.setVisible(True)
        else:
            self.Capture_R_Knee_Label.setVisible(True)
            self.Capture_R_Knee_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Hand_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Hand_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Hand_LE.text() != "":
            self.Capture_R_Hand_Label.setVisible(False)
            self.Capture_R_Hand_Get.setVisible(True)
        else:
            self.Capture_R_Hand_Label.setVisible(True)
            self.Capture_R_Hand_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Hand_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Hand_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Hand_LE.text() != "":
            self.Capture_L_Hand_Label.setVisible(False)
            self.Capture_L_Hand_Get.setVisible(True)
        else:
            self.Capture_L_Hand_Label.setVisible(True)
            self.Capture_L_Hand_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_HandPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_HandPV_LE.text() != "":
            self.Capture_L_HandPV_Label.setVisible(False)
            self.Capture_L_HandPV_Get.setVisible(True)
        else:
            self.Capture_L_HandPV_Label.setVisible(True)
            self.Capture_L_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_Body_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_Body_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_Body_Get.clicked.disconnect()
            except:
                pass
            self.Capture_Body_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_Body_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_Body_LE.text() != "":
            self.Capture_Body_Label.setVisible(False)
            self.Capture_Body_Get.setVisible(True)
        else:
            self.Capture_Body_Label.setVisible(True)
            self.Capture_Body_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_HandPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_HandPV_LE.text() != "":
            self.Capture_R_HandPV_Label.setVisible(False)
            self.Capture_R_HandPV_Get.setVisible(True)
        else:
            self.Capture_R_HandPV_Label.setVisible(True)
            self.Capture_R_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Foot_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Foot_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Foot_LE.text() != "":
            self.Capture_L_Foot_Label.setVisible(False)
            self.Capture_L_Foot_Get.setVisible(True)
        else:
            self.Capture_L_Foot_Label.setVisible(True)
            self.Capture_L_Foot_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Foot_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Foot_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Foot_LE.text() != "":
            self.Capture_R_Foot_Label.setVisible(False)
            self.Capture_R_Foot_Get.setVisible(True)
        else:
            self.Capture_R_Foot_Label.setVisible(True)
            self.Capture_R_Foot_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_FootPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_FootPV_LE.text() != "":
            self.Capture_L_FootPV_Label.setVisible(False)
            self.Capture_L_FootPV_Get.setVisible(True)
        else:
            self.Capture_L_FootPV_Label.setVisible(True)
            self.Capture_L_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_FootPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_FootPV_LE.text() != "":
            self.Capture_R_FootPV_Label.setVisible(False)
            self.Capture_R_FootPV_Get.setVisible(True)
        else:
            self.Capture_R_FootPV_Label.setVisible(True)
            self.Capture_R_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Wrist_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Wrist_LE.text() != "":
            self.Capture_L_Wrist_Label.setVisible(False)
            self.Capture_L_Wrist_Get.setVisible(True)
        else:
            self.Capture_L_Wrist_Label.setVisible(True)
            self.Capture_L_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_Lower_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_Lower_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_Lower_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Capture_Lower_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_Lower_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_Lower_Spine_LE.text() != "":
            self.Capture_Lower_Spine_Label.setVisible(False)
            self.Capture_Lower_Spine_Get.setVisible(True)
        else:
            self.Capture_Lower_Spine_Label.setVisible(True)
            self.Capture_Lower_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Ankle_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Ankle_LE.text() != "":
            self.Capture_R_Ankle_Label.setVisible(False)
            self.Capture_R_Ankle_Get.setVisible(True)
        else:
            self.Capture_R_Ankle_Label.setVisible(True)
            self.Capture_R_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Leg_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Leg_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Leg_LE.text() != "":
            self.Capture_L_Leg_Label.setVisible(False)
            self.Capture_L_Leg_Get.setVisible(True)
        else:
            self.Capture_L_Leg_Label.setVisible(True)
            self.Capture_L_Leg_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Arm_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Arm_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Arm_LE.text() != "":
            self.Capture_R_Arm_Label.setVisible(False)
            self.Capture_R_Arm_Get.setVisible(True)
        else:
            self.Capture_R_Arm_Label.setVisible(True)
            self.Capture_R_Arm_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Arm_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Arm_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Arm_LE.text() != "":
            self.Capture_L_Arm_Label.setVisible(False)
            self.Capture_L_Arm_Get.setVisible(True)
        else:
            self.Capture_L_Arm_Label.setVisible(True)
            self.Capture_L_Arm_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Shoulder_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Shoulder_LE.text() != "":
            self.Capture_L_Shoulder_Label.setVisible(False)
            self.Capture_L_Shoulder_Get.setVisible(True)
        else:
            self.Capture_L_Shoulder_Label.setVisible(True)
            self.Capture_L_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Toe_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Toe_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Toe_LE.text() != "":
            self.Capture_L_Toe_Label.setVisible(False)
            self.Capture_L_Toe_Get.setVisible(True)
        else:
            self.Capture_L_Toe_Label.setVisible(True)
            self.Capture_L_Toe_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Toe_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Toe_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Toe_LE.text() != "":
            self.Capture_R_Toe_Label.setVisible(False)
            self.Capture_R_Toe_Get.setVisible(True)
        else:
            self.Capture_R_Toe_Label.setVisible(True)
            self.Capture_R_Toe_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_Upper_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_Upper_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_Upper_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Capture_Upper_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_Upper_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_Upper_Spine_LE.text() != "":
            self.Capture_Upper_Spine_Label.setVisible(False)
            self.Capture_Upper_Spine_Get.setVisible(True)
        else:
            self.Capture_Upper_Spine_Label.setVisible(True)
            self.Capture_Upper_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Wrist_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Wrist_LE.text() != "":
            self.Capture_R_Wrist_Label.setVisible(False)
            self.Capture_R_Wrist_Get.setVisible(True)
        else:
            self.Capture_R_Wrist_Label.setVisible(True)
            self.Capture_R_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_L_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_L_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_L_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.Capture_L_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_L_Elbow_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_L_Elbow_LE.text() != "":
            self.Capture_L_Elbow_Label.setVisible(False)
            self.Capture_L_Elbow_Get.setVisible(True)
        else:
            self.Capture_L_Elbow_Label.setVisible(True)
            self.Capture_L_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()

    def Capture_R_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Capture_R_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Capture_R_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.Capture_R_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Capture_R_Elbow_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Capture_R_Elbow_LE.text() != "":
            self.Capture_R_Elbow_Label.setVisible(False)
            self.Capture_R_Elbow_Get.setVisible(True)
        else:
            self.Capture_R_Elbow_Label.setVisible(True)
            self.Capture_R_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_Lower_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_Lower_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_Lower_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Target_Lower_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_Lower_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_Lower_Spine_LE.text() != "":
            self.Target_Lower_Spine_Label.setVisible(False)
            self.Target_Lower_Spine_Get.setVisible(True)
        else:
            self.Target_Lower_Spine_Label.setVisible(True)
            self.Target_Lower_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Wrist_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Wrist_LE.text() != "":
            self.Target_L_Wrist_Label.setVisible(False)
            self.Target_L_Wrist_Get.setVisible(True)
        else:
            self.Target_L_Wrist_Label.setVisible(True)
            self.Target_L_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Toe_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Toe_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Toe_LE.text() != "":
            self.Target_R_Toe_Label.setVisible(False)
            self.Target_R_Toe_Get.setVisible(True)
        else:
            self.Target_R_Toe_Label.setVisible(True)
            self.Target_R_Toe_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Toe_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Toe_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Toe_LE.text() != "":
            self.Target_L_Toe_Label.setVisible(False)
            self.Target_L_Toe_Get.setVisible(True)
        else:
            self.Target_L_Toe_Label.setVisible(True)
            self.Target_L_Toe_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Ankle_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Ankle_LE.text() != "":
            self.Target_L_Ankle_Label.setVisible(False)
            self.Target_L_Ankle_Get.setVisible(True)
        else:
            self.Target_L_Ankle_Label.setVisible(True)
            self.Target_L_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Knee_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Knee_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Knee_LE.text() != "":
            self.Target_L_Knee_Label.setVisible(False)
            self.Target_L_Knee_Get.setVisible(True)
        else:
            self.Target_L_Knee_Label.setVisible(True)
            self.Target_L_Knee_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Ankle_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Ankle_LE.text() != "":
            self.Target_R_Ankle_Label.setVisible(False)
            self.Target_R_Ankle_Get.setVisible(True)
        else:
            self.Target_R_Ankle_Label.setVisible(True)
            self.Target_R_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Knee_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Knee_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Knee_LE.text() != "":
            self.Target_R_Knee_Label.setVisible(False)
            self.Target_R_Knee_Get.setVisible(True)
        else:
            self.Target_R_Knee_Label.setVisible(True)
            self.Target_R_Knee_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Leg_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Leg_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Leg_LE.text() != "":
            self.Target_L_Leg_Label.setVisible(False)
            self.Target_L_Leg_Get.setVisible(True)
        else:
            self.Target_L_Leg_Label.setVisible(True)
            self.Target_L_Leg_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_Mid_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_Mid_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_Mid_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Target_Mid_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_Mid_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_Mid_Spine_LE.text() != "":
            self.Target_Mid_Spine_Label.setVisible(False)
            self.Target_Mid_Spine_Get.setVisible(True)
        else:
            self.Target_Mid_Spine_Label.setVisible(True)
            self.Target_Mid_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_Upper_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_Upper_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_Upper_Spine_Get.clicked.disconnect()
            except:
                pass
            self.Target_Upper_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_Upper_Spine_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_Upper_Spine_LE.text() != "":
            self.Target_Upper_Spine_Label.setVisible(False)
            self.Target_Upper_Spine_Get.setVisible(True)
        else:
            self.Target_Upper_Spine_Label.setVisible(True)
            self.Target_Upper_Spine_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Leg_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Leg_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Leg_LE.text() != "":
            self.Target_R_Leg_Label.setVisible(False)
            self.Target_R_Leg_Get.setVisible(True)
        else:
            self.Target_R_Leg_Label.setVisible(True)
            self.Target_R_Leg_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Arm_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Arm_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Arm_LE.text() != "":
            self.Target_R_Arm_Label.setVisible(False)
            self.Target_R_Arm_Get.setVisible(True)
        else:
            self.Target_R_Arm_Label.setVisible(True)
            self.Target_R_Arm_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Arm_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Arm_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Arm_LE.text() != "":
            self.Target_L_Arm_Label.setVisible(False)
            self.Target_L_Arm_Get.setVisible(True)
        else:
            self.Target_L_Arm_Label.setVisible(True)
            self.Target_L_Arm_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Shoulder_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Shoulder_LE.text() != "":
            self.Target_R_Shoulder_Label.setVisible(False)
            self.Target_R_Shoulder_Get.setVisible(True)
        else:
            self.Target_R_Shoulder_Label.setVisible(True)
            self.Target_R_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Shoulder_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Shoulder_LE.text() != "":
            self.Target_L_Shoulder_Label.setVisible(False)
            self.Target_L_Shoulder_Get.setVisible(True)
        else:
            self.Target_L_Shoulder_Label.setVisible(True)
            self.Target_L_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_Head_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_Head_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_Head_Get.clicked.disconnect()
            except:
                pass
            self.Target_Head_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_Head_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_Head_LE.text() != "":
            self.Target_Head_Label.setVisible(False)
            self.Target_Head_Get.setVisible(True)
        else:
            self.Target_Head_Label.setVisible(True)
            self.Target_Head_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Hand_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Hand_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Hand_LE.text() != "":
            self.Target_R_Hand_Label.setVisible(False)
            self.Target_R_Hand_Get.setVisible(True)
        else:
            self.Target_R_Hand_Label.setVisible(True)
            self.Target_R_Hand_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Hand_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Hand_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Hand_LE.text() != "":
            self.Target_L_Hand_Label.setVisible(False)
            self.Target_L_Hand_Get.setVisible(True)
        else:
            self.Target_L_Hand_Label.setVisible(True)
            self.Target_L_Hand_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_HandPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_HandPV_LE.text() != "":
            self.Target_L_HandPV_Label.setVisible(False)
            self.Target_L_HandPV_Get.setVisible(True)
        else:
            self.Target_L_HandPV_Label.setVisible(True)
            self.Target_L_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_Body_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_Body_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_Body_Get.clicked.disconnect()
            except:
                pass
            self.Target_Body_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_Body_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_Body_LE.text() != "":
            self.Target_Body_Label.setVisible(False)
            self.Target_Body_Get.setVisible(True)
        else:
            self.Target_Body_Label.setVisible(True)
            self.Target_Body_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_HandPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_HandPV_LE.text() != "":
            self.Target_R_HandPV_Label.setVisible(False)
            self.Target_R_HandPV_Get.setVisible(True)
        else:
            self.Target_R_HandPV_Label.setVisible(True)
            self.Target_R_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Foot_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Foot_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Foot_LE.text() != "":
            self.Target_L_Foot_Label.setVisible(False)
            self.Target_L_Foot_Get.setVisible(True)
        else:
            self.Target_L_Foot_Label.setVisible(True)
            self.Target_L_Foot_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Foot_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Foot_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Foot_LE.text() != "":
            self.Target_R_Foot_Label.setVisible(False)
            self.Target_R_Foot_Get.setVisible(True)
        else:
            self.Target_R_Foot_Label.setVisible(True)
            self.Target_R_Foot_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_FootPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_FootPV_LE.text() != "":
            self.Target_L_FootPV_Label.setVisible(False)
            self.Target_L_FootPV_Get.setVisible(True)
        else:
            self.Target_L_FootPV_Label.setVisible(True)
            self.Target_L_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_FootPV_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_FootPV_LE.text() != "":
            self.Target_R_FootPV_Label.setVisible(False)
            self.Target_R_FootPV_Get.setVisible(True)
        else:
            self.Target_R_FootPV_Label.setVisible(True)
            self.Target_R_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_L_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_L_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_L_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.Target_L_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_L_Elbow_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_L_Elbow_LE.text() != "":
            self.Target_L_Elbow_Label.setVisible(False)
            self.Target_L_Elbow_Get.setVisible(True)
        else:
            self.Target_L_Elbow_Label.setVisible(True)
            self.Target_L_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Wrist_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Wrist_LE.text() != "":
            self.Target_R_Wrist_Label.setVisible(False)
            self.Target_R_Wrist_Get.setVisible(True)
        else:
            self.Target_R_Wrist_Label.setVisible(True)
            self.Target_R_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()

    def Target_R_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.Target_R_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.Target_R_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.Target_R_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.Target_R_Elbow_LE.setText("")
        self.Con_Check()
        self.Save_Json_Fun()
        
        if self.Target_R_Elbow_LE.text() != "":
            self.Target_R_Elbow_Label.setVisible(False)
            self.Target_R_Elbow_Get.setVisible(True)
        else:
            self.Target_R_Elbow_Label.setVisible(True)
            self.Target_R_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()

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

    def Capture_Data_Toggle_Fun(self):
        if self.Capture_Data_Toggle_Check:
            self.Capture_Data_Toggle_Check = False
            self.Capture_Data_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Capture_Data_Toggle_Anim.start()
            self.Capture_Data_Toggle.setText(u"▼ADV动捕数据 FK 控制器")
            self.Capture_Data_Toggle.setStyleSheet('font:normal')
        else:
            self.Capture_Data_Toggle_Check = True
            self.Capture_Data_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Capture_Data_Toggle_Anim.start()
            self.Capture_Data_Toggle.setText(u"■ADV动捕数据 FK 控制器")
            self.Capture_Data_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    def Target_Data_Toggle_Fun(self):
        if self.Target_Data_Toggle_Check:
            self.Target_Data_Toggle_Check = False
            self.Target_Data_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Target_Data_Toggle_Anim.start()
            self.Target_Data_Toggle.setText(u"▼TSM目标模型 FK 控制器")
            self.Target_Data_Toggle.setStyleSheet('font:normal')
        else:
            self.Target_Data_Toggle_Check = True
            self.Target_Data_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Target_Data_Toggle_Anim.start()
            self.Target_Data_Toggle.setText(u"■TSM目标模型 FK 控制器")
            self.Target_Data_Toggle.setStyleSheet('font:bold')
            
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
    
        try:
            GUI_STATE['Capture_Mid_Spine_LE'] = self.Capture_Mid_Spine_LE.text() if len(self.Capture_Mid_Spine_LE.text())>0 else ""
        except:
            return
        GUI_STATE['Capture_Head_LE'] = self.Capture_Head_LE.text() if len(self.Capture_Head_LE.text())>0 else ""
        GUI_STATE['Capture_L_Knee_LE'] = self.Capture_L_Knee_LE.text() if len(self.Capture_L_Knee_LE.text())>0 else ""
        GUI_STATE['Capture_L_Ankle_LE'] = self.Capture_L_Ankle_LE.text() if len(self.Capture_L_Ankle_LE.text())>0 else ""
        GUI_STATE['Capture_R_Shoulder_LE'] = self.Capture_R_Shoulder_LE.text() if len(self.Capture_R_Shoulder_LE.text())>0 else ""
        GUI_STATE['Capture_R_Leg_LE'] = self.Capture_R_Leg_LE.text() if len(self.Capture_R_Leg_LE.text())>0 else ""
        GUI_STATE['Capture_R_Knee_LE'] = self.Capture_R_Knee_LE.text() if len(self.Capture_R_Knee_LE.text())>0 else ""
        GUI_STATE['Capture_R_Hand_LE'] = self.Capture_R_Hand_LE.text() if len(self.Capture_R_Hand_LE.text())>0 else ""
        GUI_STATE['Capture_L_Hand_LE'] = self.Capture_L_Hand_LE.text() if len(self.Capture_L_Hand_LE.text())>0 else ""
        GUI_STATE['Capture_L_HandPV_LE'] = self.Capture_L_HandPV_LE.text() if len(self.Capture_L_HandPV_LE.text())>0 else ""
        GUI_STATE['Capture_Body_LE'] = self.Capture_Body_LE.text() if len(self.Capture_Body_LE.text())>0 else ""
        GUI_STATE['Capture_R_HandPV_LE'] = self.Capture_R_HandPV_LE.text() if len(self.Capture_R_HandPV_LE.text())>0 else ""
        GUI_STATE['Capture_L_Foot_LE'] = self.Capture_L_Foot_LE.text() if len(self.Capture_L_Foot_LE.text())>0 else ""
        GUI_STATE['Capture_R_Foot_LE'] = self.Capture_R_Foot_LE.text() if len(self.Capture_R_Foot_LE.text())>0 else ""
        GUI_STATE['Capture_L_FootPV_LE'] = self.Capture_L_FootPV_LE.text() if len(self.Capture_L_FootPV_LE.text())>0 else ""
        GUI_STATE['Capture_R_FootPV_LE'] = self.Capture_R_FootPV_LE.text() if len(self.Capture_R_FootPV_LE.text())>0 else ""
        GUI_STATE['Capture_L_Wrist_LE'] = self.Capture_L_Wrist_LE.text() if len(self.Capture_L_Wrist_LE.text())>0 else ""
        GUI_STATE['Capture_Lower_Spine_LE'] = self.Capture_Lower_Spine_LE.text() if len(self.Capture_Lower_Spine_LE.text())>0 else ""
        GUI_STATE['Capture_R_Ankle_LE'] = self.Capture_R_Ankle_LE.text() if len(self.Capture_R_Ankle_LE.text())>0 else ""
        GUI_STATE['Capture_L_Leg_LE'] = self.Capture_L_Leg_LE.text() if len(self.Capture_L_Leg_LE.text())>0 else ""
        GUI_STATE['Capture_R_Arm_LE'] = self.Capture_R_Arm_LE.text() if len(self.Capture_R_Arm_LE.text())>0 else ""
        GUI_STATE['Capture_L_Arm_LE'] = self.Capture_L_Arm_LE.text() if len(self.Capture_L_Arm_LE.text())>0 else ""
        GUI_STATE['Capture_L_Shoulder_LE'] = self.Capture_L_Shoulder_LE.text() if len(self.Capture_L_Shoulder_LE.text())>0 else ""
        GUI_STATE['Capture_L_Toe_LE'] = self.Capture_L_Toe_LE.text() if len(self.Capture_L_Toe_LE.text())>0 else ""
        GUI_STATE['Capture_R_Toe_LE'] = self.Capture_R_Toe_LE.text() if len(self.Capture_R_Toe_LE.text())>0 else ""
        GUI_STATE['Capture_Upper_Spine_LE'] = self.Capture_Upper_Spine_LE.text() if len(self.Capture_Upper_Spine_LE.text())>0 else ""
        GUI_STATE['Capture_R_Wrist_LE'] = self.Capture_R_Wrist_LE.text() if len(self.Capture_R_Wrist_LE.text())>0 else ""
        GUI_STATE['Capture_L_Elbow_LE'] = self.Capture_L_Elbow_LE.text() if len(self.Capture_L_Elbow_LE.text())>0 else ""
        GUI_STATE['Capture_R_Elbow_LE'] = self.Capture_R_Elbow_LE.text() if len(self.Capture_R_Elbow_LE.text())>0 else ""
        GUI_STATE['Target_Lower_Spine_LE'] = self.Target_Lower_Spine_LE.text() if len(self.Target_Lower_Spine_LE.text())>0 else ""
        GUI_STATE['Target_L_Wrist_LE'] = self.Target_L_Wrist_LE.text() if len(self.Target_L_Wrist_LE.text())>0 else ""
        GUI_STATE['Target_R_Toe_LE'] = self.Target_R_Toe_LE.text() if len(self.Target_R_Toe_LE.text())>0 else ""
        GUI_STATE['Target_L_Toe_LE'] = self.Target_L_Toe_LE.text() if len(self.Target_L_Toe_LE.text())>0 else ""
        GUI_STATE['Target_L_Ankle_LE'] = self.Target_L_Ankle_LE.text() if len(self.Target_L_Ankle_LE.text())>0 else ""
        GUI_STATE['Target_L_Knee_LE'] = self.Target_L_Knee_LE.text() if len(self.Target_L_Knee_LE.text())>0 else ""
        GUI_STATE['Target_R_Ankle_LE'] = self.Target_R_Ankle_LE.text() if len(self.Target_R_Ankle_LE.text())>0 else ""
        GUI_STATE['Target_R_Knee_LE'] = self.Target_R_Knee_LE.text() if len(self.Target_R_Knee_LE.text())>0 else ""
        GUI_STATE['Target_L_Leg_LE'] = self.Target_L_Leg_LE.text() if len(self.Target_L_Leg_LE.text())>0 else ""
        GUI_STATE['Target_Mid_Spine_LE'] = self.Target_Mid_Spine_LE.text() if len(self.Target_Mid_Spine_LE.text())>0 else ""
        GUI_STATE['Target_Upper_Spine_LE'] = self.Target_Upper_Spine_LE.text() if len(self.Target_Upper_Spine_LE.text())>0 else ""
        GUI_STATE['Target_R_Leg_LE'] = self.Target_R_Leg_LE.text() if len(self.Target_R_Leg_LE.text())>0 else ""
        GUI_STATE['Target_R_Arm_LE'] = self.Target_R_Arm_LE.text() if len(self.Target_R_Arm_LE.text())>0 else ""
        GUI_STATE['Target_L_Arm_LE'] = self.Target_L_Arm_LE.text() if len(self.Target_L_Arm_LE.text())>0 else ""
        GUI_STATE['Target_R_Shoulder_LE'] = self.Target_R_Shoulder_LE.text() if len(self.Target_R_Shoulder_LE.text())>0 else ""
        GUI_STATE['Target_L_Shoulder_LE'] = self.Target_L_Shoulder_LE.text() if len(self.Target_L_Shoulder_LE.text())>0 else ""
        GUI_STATE['Target_Head_LE'] = self.Target_Head_LE.text() if len(self.Target_Head_LE.text())>0 else ""
        GUI_STATE['Target_R_Hand_LE'] = self.Target_R_Hand_LE.text() if len(self.Target_R_Hand_LE.text())>0 else ""
        GUI_STATE['Target_L_Hand_LE'] = self.Target_L_Hand_LE.text() if len(self.Target_L_Hand_LE.text())>0 else ""
        GUI_STATE['Target_L_HandPV_LE'] = self.Target_L_HandPV_LE.text() if len(self.Target_L_HandPV_LE.text())>0 else ""
        GUI_STATE['Target_Body_LE'] = self.Target_Body_LE.text() if len(self.Target_Body_LE.text())>0 else ""
        GUI_STATE['Target_R_HandPV_LE'] = self.Target_R_HandPV_LE.text() if len(self.Target_R_HandPV_LE.text())>0 else ""
        GUI_STATE['Target_L_Foot_LE'] = self.Target_L_Foot_LE.text() if len(self.Target_L_Foot_LE.text())>0 else ""
        GUI_STATE['Target_R_Foot_LE'] = self.Target_R_Foot_LE.text() if len(self.Target_R_Foot_LE.text())>0 else ""
        GUI_STATE['Target_L_FootPV_LE'] = self.Target_L_FootPV_LE.text() if len(self.Target_L_FootPV_LE.text())>0 else ""
        GUI_STATE['Target_R_FootPV_LE'] = self.Target_R_FootPV_LE.text() if len(self.Target_R_FootPV_LE.text())>0 else ""
        GUI_STATE['Target_L_Elbow_LE'] = self.Target_L_Elbow_LE.text() if len(self.Target_L_Elbow_LE.text())>0 else ""
        GUI_STATE['Target_R_Wrist_LE'] = self.Target_R_Wrist_LE.text() if len(self.Target_R_Wrist_LE.text())>0 else ""
        GUI_STATE['Target_R_Elbow_LE'] = self.Target_R_Elbow_LE.text() if len(self.Target_R_Elbow_LE.text())>0 else ""
        GUI_STATE['Tab_Widget'] = self.Tab_Widget.currentIndex() 
        GUI_STATE['Capture_Data_Toggle_Check'] = self.Capture_Data_Toggle_Check
        GUI_STATE['Target_Data_Toggle_Check'] = self.Target_Data_Toggle_Check
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
            self.Capture_Mid_Spine_LE.setText(GUI_STATE['Capture_Mid_Spine_LE'])
            self.Capture_Head_LE.setText(GUI_STATE['Capture_Head_LE'])
            self.Capture_L_Knee_LE.setText(GUI_STATE['Capture_L_Knee_LE'])
            self.Capture_L_Ankle_LE.setText(GUI_STATE['Capture_L_Ankle_LE'])
            self.Capture_R_Shoulder_LE.setText(GUI_STATE['Capture_R_Shoulder_LE'])
            self.Capture_R_Leg_LE.setText(GUI_STATE['Capture_R_Leg_LE'])
            self.Capture_R_Knee_LE.setText(GUI_STATE['Capture_R_Knee_LE'])
            self.Capture_R_Hand_LE.setText(GUI_STATE['Capture_R_Hand_LE'])
            self.Capture_L_Hand_LE.setText(GUI_STATE['Capture_L_Hand_LE'])
            self.Capture_L_HandPV_LE.setText(GUI_STATE['Capture_L_HandPV_LE'])
            self.Capture_Body_LE.setText(GUI_STATE['Capture_Body_LE'])
            self.Capture_R_HandPV_LE.setText(GUI_STATE['Capture_R_HandPV_LE'])
            self.Capture_L_Foot_LE.setText(GUI_STATE['Capture_L_Foot_LE'])
            self.Capture_R_Foot_LE.setText(GUI_STATE['Capture_R_Foot_LE'])
            self.Capture_L_FootPV_LE.setText(GUI_STATE['Capture_L_FootPV_LE'])
            self.Capture_R_FootPV_LE.setText(GUI_STATE['Capture_R_FootPV_LE'])
            self.Capture_L_Wrist_LE.setText(GUI_STATE['Capture_L_Wrist_LE'])
            self.Capture_Lower_Spine_LE.setText(GUI_STATE['Capture_Lower_Spine_LE'])
            self.Capture_R_Ankle_LE.setText(GUI_STATE['Capture_R_Ankle_LE'])
            self.Capture_L_Leg_LE.setText(GUI_STATE['Capture_L_Leg_LE'])
            self.Capture_R_Arm_LE.setText(GUI_STATE['Capture_R_Arm_LE'])
            self.Capture_L_Arm_LE.setText(GUI_STATE['Capture_L_Arm_LE'])
            self.Capture_L_Shoulder_LE.setText(GUI_STATE['Capture_L_Shoulder_LE'])
            self.Capture_L_Toe_LE.setText(GUI_STATE['Capture_L_Toe_LE'])
            self.Capture_R_Toe_LE.setText(GUI_STATE['Capture_R_Toe_LE'])
            self.Capture_Upper_Spine_LE.setText(GUI_STATE['Capture_Upper_Spine_LE'])
            self.Capture_R_Wrist_LE.setText(GUI_STATE['Capture_R_Wrist_LE'])
            self.Capture_L_Elbow_LE.setText(GUI_STATE['Capture_L_Elbow_LE'])
            self.Capture_R_Elbow_LE.setText(GUI_STATE['Capture_R_Elbow_LE'])
            self.Target_Lower_Spine_LE.setText(GUI_STATE['Target_Lower_Spine_LE'])
            self.Target_L_Wrist_LE.setText(GUI_STATE['Target_L_Wrist_LE'])
            self.Target_R_Toe_LE.setText(GUI_STATE['Target_R_Toe_LE'])
            self.Target_L_Toe_LE.setText(GUI_STATE['Target_L_Toe_LE'])
            self.Target_L_Ankle_LE.setText(GUI_STATE['Target_L_Ankle_LE'])
            self.Target_L_Knee_LE.setText(GUI_STATE['Target_L_Knee_LE'])
            self.Target_R_Ankle_LE.setText(GUI_STATE['Target_R_Ankle_LE'])
            self.Target_R_Knee_LE.setText(GUI_STATE['Target_R_Knee_LE'])
            self.Target_L_Leg_LE.setText(GUI_STATE['Target_L_Leg_LE'])
            self.Target_Mid_Spine_LE.setText(GUI_STATE['Target_Mid_Spine_LE'])
            self.Target_Upper_Spine_LE.setText(GUI_STATE['Target_Upper_Spine_LE'])
            self.Target_R_Leg_LE.setText(GUI_STATE['Target_R_Leg_LE'])
            self.Target_R_Arm_LE.setText(GUI_STATE['Target_R_Arm_LE'])
            self.Target_L_Arm_LE.setText(GUI_STATE['Target_L_Arm_LE'])
            self.Target_R_Shoulder_LE.setText(GUI_STATE['Target_R_Shoulder_LE'])
            self.Target_L_Shoulder_LE.setText(GUI_STATE['Target_L_Shoulder_LE'])
            self.Target_Head_LE.setText(GUI_STATE['Target_Head_LE'])
            self.Target_R_Hand_LE.setText(GUI_STATE['Target_R_Hand_LE'])
            self.Target_L_Hand_LE.setText(GUI_STATE['Target_L_Hand_LE'])
            self.Target_L_HandPV_LE.setText(GUI_STATE['Target_L_HandPV_LE'])
            self.Target_Body_LE.setText(GUI_STATE['Target_Body_LE'])
            self.Target_R_HandPV_LE.setText(GUI_STATE['Target_R_HandPV_LE'])
            self.Target_L_Foot_LE.setText(GUI_STATE['Target_L_Foot_LE'])
            self.Target_R_Foot_LE.setText(GUI_STATE['Target_R_Foot_LE'])
            self.Target_L_FootPV_LE.setText(GUI_STATE['Target_L_FootPV_LE'])
            self.Target_R_FootPV_LE.setText(GUI_STATE['Target_R_FootPV_LE'])
            self.Target_L_Elbow_LE.setText(GUI_STATE['Target_L_Elbow_LE'])
            self.Target_R_Wrist_LE.setText(GUI_STATE['Target_R_Wrist_LE'])
            self.Target_R_Elbow_LE.setText(GUI_STATE['Target_R_Elbow_LE'])
            self.Tab_Widget.setCurrentIndex(int(GUI_STATE['Tab_Widget']))
            self.Capture_Data_Toggle_Check = GUI_STATE['Capture_Data_Toggle_Check']
            self.Target_Data_Toggle_Check = GUI_STATE['Target_Data_Toggle_Check']
            self.Window_Setting_Toggle_Check = GUI_STATE['Window_Setting_Toggle_Check']
            self.Attribute_Setting_Toggle_Check = GUI_STATE['Attribute_Setting_Toggle_Check']
            self.Capture_Data_Toggle_Fun()
            self.Capture_Data_Toggle_Fun()
            self.Target_Data_Toggle_Fun()
            self.Target_Data_Toggle_Fun()
            self.Window_Setting_Toggle_Fun()
            self.Window_Setting_Toggle_Fun()
            self.Attribute_Setting_Toggle_Fun()
            self.Attribute_Setting_Toggle_Fun()
            self.Con_Check()
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

    def Con_Check(self):
        
        num = 0

        if self.Capture_L_Wrist_LE.text() != "":
			num+=1

        if self.Capture_L_Elbow_LE.text() != "":
			num+=1

        if self.Capture_L_Arm_LE.text() != "":
			num+=1

        if self.Capture_L_Shoulder_LE.text() != "":
			num+=1

        if self.Capture_R_Wrist_LE.text() != "":
			num+=1

        if self.Capture_R_Elbow_LE.text() != "":
			num+=1

        if self.Capture_R_Arm_LE.text() != "":
			num+=1

        if self.Capture_R_Shoulder_LE.text() != "":
			num+=1

        if self.Capture_Head_LE.text() != "":
			num+=1

        if self.Capture_Upper_Spine_LE.text() != "":
			num+=1

        if self.Capture_Mid_Spine_LE.text() != "":
			num+=1

        if self.Capture_Lower_Spine_LE.text() != "":
			num+=1

        if self.Capture_Body_LE.text() != "":
			num+=1

        if self.Capture_L_Leg_LE.text() != "":
			num+=1

        if self.Capture_L_Knee_LE.text() != "":
			num+=1

        if self.Capture_L_Ankle_LE.text() != "":
			num+=1

        if self.Capture_L_Toe_LE.text() != "":
			num+=1

        if self.Capture_R_Leg_LE.text() != "":
			num+=1

        if self.Capture_R_Knee_LE.text() != "":
			num+=1

        if self.Capture_R_Ankle_LE.text() != "":
			num+=1

        if self.Capture_R_Toe_LE.text() != "":
			num+=1

        if self.Target_L_Wrist_LE.text() != "":
			num+=1

        if self.Target_L_Elbow_LE.text() != "":
			num+=1

        if self.Target_L_Arm_LE.text() != "":
			num+=1

        if self.Target_L_Shoulder_LE.text() != "":
			num+=1

        if self.Target_R_Wrist_LE.text() != "":
			num+=1

        if self.Target_R_Elbow_LE.text() != "":
			num+=1

        if self.Target_R_Arm_LE.text() != "":
			num+=1

        if self.Target_R_Shoulder_LE.text() != "":
			num+=1

        if self.Target_Head_LE.text() != "":
			num+=1

        if self.Target_Upper_Spine_LE.text() != "":
			num+=1

        if self.Target_Mid_Spine_LE.text() != "":
			num+=1

        if self.Target_Lower_Spine_LE.text() != "":
			num+=1

        if self.Target_Body_LE.text() != "":
			num+=1

        if self.Target_L_Leg_LE.text() != "":
			num+=1

        if self.Target_L_Knee_LE.text() != "":
			num+=1

        if self.Target_L_Ankle_LE.text() != "":
			num+=1

        if self.Target_L_Toe_LE.text() != "":
			num+=1

        if self.Target_R_Leg_LE.text() != "":
			num+=1

        if self.Target_R_Knee_LE.text() != "":
			num+=1

        if self.Target_R_Ankle_LE.text() != "":
			num+=1

        if self.Target_R_Toe_LE.text() != "":
			num+=1

        if num == 42:
            self.Constraint_BTN.setEnabled(True)
        else:
            self.Constraint_BTN.setEnabled(False)