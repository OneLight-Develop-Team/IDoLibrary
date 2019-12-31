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

import sys
import plugin.Qt as Qt

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","TSM_Mirror.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')

from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
from Qt.QtCompat import wrapInstance

def loadUiType(uiFile):
    """
    Pyside "loadUiType" command like PyQt4 has one, so we have to convert the 
    ui file to py code in-memory first and then execute it in a special frame
    to retrieve the form_class.
    """
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

form_class , base_class = loadUiType(UI_PATH)

class UI_Interface(base_class,form_class):
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

        self.ptr = self.Dock_Win_Management(title=u"TSM 镜像工具")

        super(UI_Interface,self).__init__(parent=self.ptr)
        
        self.setupUi(self)
        
        if self.DOCK == "workspace":
            # QMainWindow 无法 addWidget
            self.parent().layout().addWidget(self.Main_Menu_Bar)
            self.parent().layout().addWidget(self.Main_Layout)
        else:
            self.parent().layout().addWidget(self)

        self.TSM_Data_Toggle_Anim = QPropertyAnimation(self.TSM_Data_Layout, "maximumHeight")
        self.TSM_Data_Toggle_Anim.setDuration(300)
        self.TSM_Data_Toggle_Anim.setStartValue(0)
        self.TSM_Data_Toggle_Anim.setEndValue(self.TSM_Data_Layout.sizeHint().height())
        self.TSM_Data_Toggle_Check = False
        self.TSM_Data_Toggle.clicked.connect(self.TSM_Data_Toggle_Fun)

        self.TSM_Mirror_Toggle_Anim = QPropertyAnimation(self.TSM_Mirror_Layout, "maximumHeight")
        self.TSM_Mirror_Toggle_Anim.setDuration(300)
        self.TSM_Mirror_Toggle_Anim.setStartValue(0)
        self.TSM_Mirror_Toggle_Anim.setEndValue(self.TSM_Mirror_Layout.sizeHint().height())
        self.TSM_Mirror_Toggle_Check = False
        self.TSM_Mirror_Toggle.clicked.connect(self.TSM_Mirror_Toggle_Fun)

        self.TSM_R_Wrist_Get.setVisible(False)
        self.TSM_R_Wrist_Pick.clicked.connect(self.TSM_R_Wrist_Pick_Fun)

        self.TSM_L_Knee_Get.setVisible(False)
        self.TSM_L_Knee_Pick.clicked.connect(self.TSM_L_Knee_Pick_Fun)

        self.TSM_Lower_Spine_Get.setVisible(False)
        self.TSM_Lower_Spine_Pick.clicked.connect(self.TSM_Lower_Spine_Pick_Fun)

        self.TSM_L_Leg_Get.setVisible(False)
        self.TSM_L_Leg_Pick.clicked.connect(self.TSM_L_Leg_Pick_Fun)

        self.TSM_R_Toe_Get.setVisible(False)
        self.TSM_R_Toe_Pick.clicked.connect(self.TSM_R_Toe_Pick_Fun)

        self.TSM_L_Ankle_Get.setVisible(False)
        self.TSM_L_Ankle_Pick.clicked.connect(self.TSM_L_Ankle_Pick_Fun)

        self.TSM_R_Knee_Get.setVisible(False)
        self.TSM_R_Knee_Pick.clicked.connect(self.TSM_R_Knee_Pick_Fun)

        self.TSM_Mid_Spine_Get.setVisible(False)
        self.TSM_Mid_Spine_Pick.clicked.connect(self.TSM_Mid_Spine_Pick_Fun)

        self.TSM_R_Ankle_Get.setVisible(False)
        self.TSM_R_Ankle_Pick.clicked.connect(self.TSM_R_Ankle_Pick_Fun)

        self.TSM_Upper_Spine_Get.setVisible(False)
        self.TSM_Upper_Spine_Pick.clicked.connect(self.TSM_Upper_Spine_Pick_Fun)

        self.TSM_L_Arm_Get.setVisible(False)
        self.TSM_L_Arm_Pick.clicked.connect(self.TSM_L_Arm_Pick_Fun)

        self.TSM_R_Leg_Get.setVisible(False)
        self.TSM_R_Leg_Pick.clicked.connect(self.TSM_R_Leg_Pick_Fun)

        self.TSM_R_Arm_Get.setVisible(False)
        self.TSM_R_Arm_Pick.clicked.connect(self.TSM_R_Arm_Pick_Fun)

        self.TSM_L_Toe_Get.setVisible(False)
        self.TSM_L_Toe_Pick.clicked.connect(self.TSM_L_Toe_Pick_Fun)

        self.TSM_L_Wrist_Get.setVisible(False)
        self.TSM_L_Wrist_Pick.clicked.connect(self.TSM_L_Wrist_Pick_Fun)

        self.TSM_R_Shoulder_Get.setVisible(False)
        self.TSM_R_Shoulder_Pick.clicked.connect(self.TSM_R_Shoulder_Pick_Fun)

        self.TSM_L_Elbow_Get.setVisible(False)
        self.TSM_L_Elbow_Pick.clicked.connect(self.TSM_L_Elbow_Pick_Fun)

        self.TSM_R_Elbow_Get.setVisible(False)
        self.TSM_R_Elbow_Pick.clicked.connect(self.TSM_R_Elbow_Pick_Fun)

        self.TSM_L_FootPV_Get.setVisible(False)
        self.TSM_L_FootPV_Pick.clicked.connect(self.TSM_L_FootPV_Pick_Fun)

        self.TSM_L_Foot_Get.setVisible(False)
        self.TSM_L_Foot_Pick.clicked.connect(self.TSM_L_Foot_Pick_Fun)

        self.TSM_L_Hand_Get.setVisible(False)
        self.TSM_L_Hand_Pick.clicked.connect(self.TSM_L_Hand_Pick_Fun)

        self.TSM_L_HandPV_Get.setVisible(False)
        self.TSM_L_HandPV_Pick.clicked.connect(self.TSM_L_HandPV_Pick_Fun)

        self.TSM_R_Hand_Get.setVisible(False)
        self.TSM_R_Hand_Pick.clicked.connect(self.TSM_R_Hand_Pick_Fun)

        self.TSM_Body_Get.setVisible(False)
        self.TSM_Body_Pick.clicked.connect(self.TSM_Body_Pick_Fun)

        self.TSM_R_Foot_Get.setVisible(False)
        self.TSM_R_Foot_Pick.clicked.connect(self.TSM_R_Foot_Pick_Fun)

        self.TSM_L_Shoulder_Get.setVisible(False)
        self.TSM_L_Shoulder_Pick.clicked.connect(self.TSM_L_Shoulder_Pick_Fun)

        self.TSM_Head_Get.setVisible(False)
        self.TSM_Head_Pick.clicked.connect(self.TSM_Head_Pick_Fun)

        self.TSM_R_FootPV_Get.setVisible(False)
        self.TSM_R_FootPV_Pick.clicked.connect(self.TSM_R_FootPV_Pick_Fun)

        self.TSM_Neck_Get.setVisible(False)
        self.TSM_Neck_Pick.clicked.connect(self.TSM_Neck_Pick_Fun)

        self.TSM_R_HandPV_Get.setVisible(False)
        self.TSM_R_HandPV_Pick.clicked.connect(self.TSM_R_HandPV_Pick_Fun)

        self.TSM_Main_Get.setVisible(False)
        self.TSM_Main_Pick.clicked.connect(self.TSM_Main_Pick_Fun)

        self.TSM_Character_Get.setVisible(False)
        self.TSM_Character_Pick.clicked.connect(self.TSM_Character_Pick_Fun)
        self.Load_Json_Fun()

    def TSM_R_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Wrist_LE.setText("")
        
        if self.TSM_R_Wrist_LE.text() != "":
            self.TSM_R_Wrist_Label.setVisible(False)
            self.TSM_R_Wrist_Get.setVisible(True)
        else:
            self.TSM_R_Wrist_Label.setVisible(True)
            self.TSM_R_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Knee_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Knee_LE.setText("")
        
        if self.TSM_L_Knee_LE.text() != "":
            self.TSM_L_Knee_Label.setVisible(False)
            self.TSM_L_Knee_Get.setVisible(True)
        else:
            self.TSM_L_Knee_Label.setVisible(True)
            self.TSM_L_Knee_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Lower_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Lower_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Lower_Spine_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Lower_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Lower_Spine_LE.setText("")
        
        if self.TSM_Lower_Spine_LE.text() != "":
            self.TSM_Lower_Spine_Label.setVisible(False)
            self.TSM_Lower_Spine_Get.setVisible(True)
        else:
            self.TSM_Lower_Spine_Label.setVisible(True)
            self.TSM_Lower_Spine_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Leg_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Leg_LE.setText("")
        
        if self.TSM_L_Leg_LE.text() != "":
            self.TSM_L_Leg_Label.setVisible(False)
            self.TSM_L_Leg_Get.setVisible(True)
        else:
            self.TSM_L_Leg_Label.setVisible(True)
            self.TSM_L_Leg_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Toe_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Toe_LE.setText("")
        
        if self.TSM_R_Toe_LE.text() != "":
            self.TSM_R_Toe_Label.setVisible(False)
            self.TSM_R_Toe_Get.setVisible(True)
        else:
            self.TSM_R_Toe_Label.setVisible(True)
            self.TSM_R_Toe_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Ankle_LE.setText("")
        
        if self.TSM_L_Ankle_LE.text() != "":
            self.TSM_L_Ankle_Label.setVisible(False)
            self.TSM_L_Ankle_Get.setVisible(True)
        else:
            self.TSM_L_Ankle_Label.setVisible(True)
            self.TSM_L_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Knee_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Knee_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Knee_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Knee_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Knee_LE.setText("")
        
        if self.TSM_R_Knee_LE.text() != "":
            self.TSM_R_Knee_Label.setVisible(False)
            self.TSM_R_Knee_Get.setVisible(True)
        else:
            self.TSM_R_Knee_Label.setVisible(True)
            self.TSM_R_Knee_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Mid_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Mid_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Mid_Spine_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Mid_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Mid_Spine_LE.setText("")
        
        if self.TSM_Mid_Spine_LE.text() != "":
            self.TSM_Mid_Spine_Label.setVisible(False)
            self.TSM_Mid_Spine_Get.setVisible(True)
        else:
            self.TSM_Mid_Spine_Label.setVisible(True)
            self.TSM_Mid_Spine_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Ankle_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Ankle_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Ankle_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Ankle_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Ankle_LE.setText("")
        
        if self.TSM_R_Ankle_LE.text() != "":
            self.TSM_R_Ankle_Label.setVisible(False)
            self.TSM_R_Ankle_Get.setVisible(True)
        else:
            self.TSM_R_Ankle_Label.setVisible(True)
            self.TSM_R_Ankle_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Upper_Spine_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Upper_Spine_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Upper_Spine_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Upper_Spine_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Upper_Spine_LE.setText("")
        
        if self.TSM_Upper_Spine_LE.text() != "":
            self.TSM_Upper_Spine_Label.setVisible(False)
            self.TSM_Upper_Spine_Get.setVisible(True)
        else:
            self.TSM_Upper_Spine_Label.setVisible(True)
            self.TSM_Upper_Spine_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Arm_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Arm_LE.setText("")
        
        if self.TSM_L_Arm_LE.text() != "":
            self.TSM_L_Arm_Label.setVisible(False)
            self.TSM_L_Arm_Get.setVisible(True)
        else:
            self.TSM_L_Arm_Label.setVisible(True)
            self.TSM_L_Arm_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Leg_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Leg_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Leg_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Leg_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Leg_LE.setText("")
        
        if self.TSM_R_Leg_LE.text() != "":
            self.TSM_R_Leg_Label.setVisible(False)
            self.TSM_R_Leg_Get.setVisible(True)
        else:
            self.TSM_R_Leg_Label.setVisible(True)
            self.TSM_R_Leg_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Arm_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Arm_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Arm_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Arm_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Arm_LE.setText("")
        
        if self.TSM_R_Arm_LE.text() != "":
            self.TSM_R_Arm_Label.setVisible(False)
            self.TSM_R_Arm_Get.setVisible(True)
        else:
            self.TSM_R_Arm_Label.setVisible(True)
            self.TSM_R_Arm_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Toe_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Toe_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Toe_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Toe_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Toe_LE.setText("")
        
        if self.TSM_L_Toe_LE.text() != "":
            self.TSM_L_Toe_Label.setVisible(False)
            self.TSM_L_Toe_Get.setVisible(True)
        else:
            self.TSM_L_Toe_Label.setVisible(True)
            self.TSM_L_Toe_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Wrist_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Wrist_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Wrist_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Wrist_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Wrist_LE.setText("")
        
        if self.TSM_L_Wrist_LE.text() != "":
            self.TSM_L_Wrist_Label.setVisible(False)
            self.TSM_L_Wrist_Get.setVisible(True)
        else:
            self.TSM_L_Wrist_Label.setVisible(True)
            self.TSM_L_Wrist_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Shoulder_LE.setText("")
        
        if self.TSM_R_Shoulder_LE.text() != "":
            self.TSM_R_Shoulder_Label.setVisible(False)
            self.TSM_R_Shoulder_Get.setVisible(True)
        else:
            self.TSM_R_Shoulder_Label.setVisible(True)
            self.TSM_R_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Elbow_LE.setText("")
        
        if self.TSM_L_Elbow_LE.text() != "":
            self.TSM_L_Elbow_Label.setVisible(False)
            self.TSM_L_Elbow_Get.setVisible(True)
        else:
            self.TSM_L_Elbow_Label.setVisible(True)
            self.TSM_L_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Elbow_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Elbow_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Elbow_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Elbow_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Elbow_LE.setText("")
        
        if self.TSM_R_Elbow_LE.text() != "":
            self.TSM_R_Elbow_Label.setVisible(False)
            self.TSM_R_Elbow_Get.setVisible(True)
        else:
            self.TSM_R_Elbow_Label.setVisible(True)
            self.TSM_R_Elbow_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_FootPV_LE.setText("")
        
        if self.TSM_L_FootPV_LE.text() != "":
            self.TSM_L_FootPV_Label.setVisible(False)
            self.TSM_L_FootPV_Get.setVisible(True)
        else:
            self.TSM_L_FootPV_Label.setVisible(True)
            self.TSM_L_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Foot_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Foot_LE.setText("")
        
        if self.TSM_L_Foot_LE.text() != "":
            self.TSM_L_Foot_Label.setVisible(False)
            self.TSM_L_Foot_Get.setVisible(True)
        else:
            self.TSM_L_Foot_Label.setVisible(True)
            self.TSM_L_Foot_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Hand_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Hand_LE.setText("")
        
        if self.TSM_L_Hand_LE.text() != "":
            self.TSM_L_Hand_Label.setVisible(False)
            self.TSM_L_Hand_Get.setVisible(True)
        else:
            self.TSM_L_Hand_Label.setVisible(True)
            self.TSM_L_Hand_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_HandPV_LE.setText("")
        
        if self.TSM_L_HandPV_LE.text() != "":
            self.TSM_L_HandPV_Label.setVisible(False)
            self.TSM_L_HandPV_Get.setVisible(True)
        else:
            self.TSM_L_HandPV_Label.setVisible(True)
            self.TSM_L_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Hand_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Hand_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Hand_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Hand_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Hand_LE.setText("")
        
        if self.TSM_R_Hand_LE.text() != "":
            self.TSM_R_Hand_Label.setVisible(False)
            self.TSM_R_Hand_Get.setVisible(True)
        else:
            self.TSM_R_Hand_Label.setVisible(True)
            self.TSM_R_Hand_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Body_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Body_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Body_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Body_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Body_LE.setText("")
        
        if self.TSM_Body_LE.text() != "":
            self.TSM_Body_Label.setVisible(False)
            self.TSM_Body_Get.setVisible(True)
        else:
            self.TSM_Body_Label.setVisible(True)
            self.TSM_Body_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_Foot_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_Foot_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_Foot_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_Foot_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_Foot_LE.setText("")
        
        if self.TSM_R_Foot_LE.text() != "":
            self.TSM_R_Foot_Label.setVisible(False)
            self.TSM_R_Foot_Get.setVisible(True)
        else:
            self.TSM_R_Foot_Label.setVisible(True)
            self.TSM_R_Foot_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_L_Shoulder_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_L_Shoulder_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_L_Shoulder_Get.clicked.disconnect()
            except:
                pass
            self.TSM_L_Shoulder_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_L_Shoulder_LE.setText("")
        
        if self.TSM_L_Shoulder_LE.text() != "":
            self.TSM_L_Shoulder_Label.setVisible(False)
            self.TSM_L_Shoulder_Get.setVisible(True)
        else:
            self.TSM_L_Shoulder_Label.setVisible(True)
            self.TSM_L_Shoulder_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Head_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Head_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Head_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Head_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Head_LE.setText("")
        
        if self.TSM_Head_LE.text() != "":
            self.TSM_Head_Label.setVisible(False)
            self.TSM_Head_Get.setVisible(True)
        else:
            self.TSM_Head_Label.setVisible(True)
            self.TSM_Head_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_FootPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_FootPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_FootPV_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_FootPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_FootPV_LE.setText("")
        
        if self.TSM_R_FootPV_LE.text() != "":
            self.TSM_R_FootPV_Label.setVisible(False)
            self.TSM_R_FootPV_Get.setVisible(True)
        else:
            self.TSM_R_FootPV_Label.setVisible(True)
            self.TSM_R_FootPV_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Neck_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Neck_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Neck_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Neck_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Neck_LE.setText("")
        
        if self.TSM_Neck_LE.text() != "":
            self.TSM_Neck_Label.setVisible(False)
            self.TSM_Neck_Get.setVisible(True)
        else:
            self.TSM_Neck_Label.setVisible(True)
            self.TSM_Neck_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_R_HandPV_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_R_HandPV_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_R_HandPV_Get.clicked.disconnect()
            except:
                pass
            self.TSM_R_HandPV_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_R_HandPV_LE.setText("")
        
        if self.TSM_R_HandPV_LE.text() != "":
            self.TSM_R_HandPV_Label.setVisible(False)
            self.TSM_R_HandPV_Get.setVisible(True)
        else:
            self.TSM_R_HandPV_Label.setVisible(True)
            self.TSM_R_HandPV_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Main_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Main_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Main_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Main_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Main_LE.setText("")
        
        if self.TSM_Main_LE.text() != "":
            self.TSM_Main_Label.setVisible(False)
            self.TSM_Main_Get.setVisible(True)
        else:
            self.TSM_Main_Label.setVisible(True)
            self.TSM_Main_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def TSM_Character_Pick_Fun(self):
        if len(cmds.ls(sl=True)) > 0:
            self.TSM_Character_LE.setText(cmds.ls(sl=True)[0])
            try :
                self.TSM_Character_Get.clicked.disconnect()
            except:
                pass
            self.TSM_Character_Get.clicked.connect(partial(self.Select_OBJ_Fun,cmds.ls(sl=True)[0]))
        else :
            self.TSM_Character_LE.setText("")
        
        if self.TSM_Character_LE.text() != "":
            self.TSM_Character_Label.setVisible(False)
            self.TSM_Character_Get.setVisible(True)
        else:
            self.TSM_Character_Label.setVisible(True)
            self.TSM_Character_Get.setVisible(False)

        self.Save_Json_Fun()
        self.TSM_Check()

    def Win_Load_JSON_Browse(self):
        load_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(load_file) is tuple:
            load_file = load_file[0]
        self.Win_LoadJSON_LE.setText(QDir.toNativeSeparators(load_file))
        self.Win_LoadJSON_Label.setVisible(False)
        self.Win_LoadJSON_DIR.setVisible(True)

        Load_Path = self.Win_LoadJSON_LE.text()
        check = self.Load_Json_Fun(path=Load_Path,load=True)
        if check:
            QMessageBox.information(self, u"加载成功", u"加载成功")

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


    def TSM_Data_Toggle_Fun(self):
        if self.TSM_Data_Toggle_Check:
            self.TSM_Data_Toggle_Check = False
            self.TSM_Data_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.TSM_Data_Toggle_Anim.start()
            self.TSM_Data_Toggle.setText(u"▼获取TSM目标模型 控制器")
            self.TSM_Data_Toggle.setStyleSheet('font:normal')
        else:
            self.TSM_Data_Toggle_Check = True
            self.TSM_Data_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.TSM_Data_Toggle_Anim.start()
            self.TSM_Data_Toggle.setText(u"■获取TSM目标模型 控制器")
            self.TSM_Data_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    def TSM_Mirror_Toggle_Fun(self):
        if self.TSM_Mirror_Toggle_Check:
            self.TSM_Mirror_Toggle_Check = False
            self.TSM_Mirror_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.TSM_Mirror_Toggle_Anim.start()
            self.TSM_Mirror_Toggle.setText(u"▼镜像设置")
            self.TSM_Mirror_Toggle.setStyleSheet('font:normal')
        else:
            self.TSM_Mirror_Toggle_Check = True
            self.TSM_Mirror_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.TSM_Mirror_Toggle_Anim.start()
            self.TSM_Mirror_Toggle.setText(u"■镜像设置")
            self.TSM_Mirror_Toggle.setStyleSheet('font:bold')
            
        self.Save_Json_Fun()

    
    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
    
        try:
            GUI_STATE['TSM_R_Wrist_LE'] = self.TSM_R_Wrist_LE.text() if len(self.TSM_R_Wrist_LE.text())>0 else ""
        except:
            return
        GUI_STATE['TSM_L_Knee_LE'] = self.TSM_L_Knee_LE.text() if len(self.TSM_L_Knee_LE.text())>0 else ""
        GUI_STATE['TSM_Lower_Spine_LE'] = self.TSM_Lower_Spine_LE.text() if len(self.TSM_Lower_Spine_LE.text())>0 else ""
        GUI_STATE['TSM_L_Leg_LE'] = self.TSM_L_Leg_LE.text() if len(self.TSM_L_Leg_LE.text())>0 else ""
        GUI_STATE['TSM_R_Toe_LE'] = self.TSM_R_Toe_LE.text() if len(self.TSM_R_Toe_LE.text())>0 else ""
        GUI_STATE['TSM_L_Ankle_LE'] = self.TSM_L_Ankle_LE.text() if len(self.TSM_L_Ankle_LE.text())>0 else ""
        GUI_STATE['TSM_R_Knee_LE'] = self.TSM_R_Knee_LE.text() if len(self.TSM_R_Knee_LE.text())>0 else ""
        GUI_STATE['TSM_Mid_Spine_LE'] = self.TSM_Mid_Spine_LE.text() if len(self.TSM_Mid_Spine_LE.text())>0 else ""
        GUI_STATE['TSM_R_Ankle_LE'] = self.TSM_R_Ankle_LE.text() if len(self.TSM_R_Ankle_LE.text())>0 else ""
        GUI_STATE['TSM_Upper_Spine_LE'] = self.TSM_Upper_Spine_LE.text() if len(self.TSM_Upper_Spine_LE.text())>0 else ""
        GUI_STATE['TSM_L_Arm_LE'] = self.TSM_L_Arm_LE.text() if len(self.TSM_L_Arm_LE.text())>0 else ""
        GUI_STATE['TSM_R_Leg_LE'] = self.TSM_R_Leg_LE.text() if len(self.TSM_R_Leg_LE.text())>0 else ""
        GUI_STATE['TSM_R_Arm_LE'] = self.TSM_R_Arm_LE.text() if len(self.TSM_R_Arm_LE.text())>0 else ""
        GUI_STATE['TSM_L_Toe_LE'] = self.TSM_L_Toe_LE.text() if len(self.TSM_L_Toe_LE.text())>0 else ""
        GUI_STATE['TSM_L_Wrist_LE'] = self.TSM_L_Wrist_LE.text() if len(self.TSM_L_Wrist_LE.text())>0 else ""
        GUI_STATE['TSM_R_Shoulder_LE'] = self.TSM_R_Shoulder_LE.text() if len(self.TSM_R_Shoulder_LE.text())>0 else ""
        GUI_STATE['TSM_L_Elbow_LE'] = self.TSM_L_Elbow_LE.text() if len(self.TSM_L_Elbow_LE.text())>0 else ""
        GUI_STATE['TSM_R_Elbow_LE'] = self.TSM_R_Elbow_LE.text() if len(self.TSM_R_Elbow_LE.text())>0 else ""
        GUI_STATE['TSM_L_FootPV_LE'] = self.TSM_L_FootPV_LE.text() if len(self.TSM_L_FootPV_LE.text())>0 else ""
        GUI_STATE['TSM_L_Foot_LE'] = self.TSM_L_Foot_LE.text() if len(self.TSM_L_Foot_LE.text())>0 else ""
        GUI_STATE['TSM_L_Hand_LE'] = self.TSM_L_Hand_LE.text() if len(self.TSM_L_Hand_LE.text())>0 else ""
        GUI_STATE['TSM_L_HandPV_LE'] = self.TSM_L_HandPV_LE.text() if len(self.TSM_L_HandPV_LE.text())>0 else ""
        GUI_STATE['TSM_R_Hand_LE'] = self.TSM_R_Hand_LE.text() if len(self.TSM_R_Hand_LE.text())>0 else ""
        GUI_STATE['TSM_Body_LE'] = self.TSM_Body_LE.text() if len(self.TSM_Body_LE.text())>0 else ""
        GUI_STATE['TSM_R_Foot_LE'] = self.TSM_R_Foot_LE.text() if len(self.TSM_R_Foot_LE.text())>0 else ""
        GUI_STATE['TSM_L_Shoulder_LE'] = self.TSM_L_Shoulder_LE.text() if len(self.TSM_L_Shoulder_LE.text())>0 else ""
        GUI_STATE['TSM_Head_LE'] = self.TSM_Head_LE.text() if len(self.TSM_Head_LE.text())>0 else ""
        GUI_STATE['TSM_R_FootPV_LE'] = self.TSM_R_FootPV_LE.text() if len(self.TSM_R_FootPV_LE.text())>0 else ""
        GUI_STATE['TSM_Neck_LE'] = self.TSM_Neck_LE.text() if len(self.TSM_Neck_LE.text())>0 else ""
        GUI_STATE['TSM_R_HandPV_LE'] = self.TSM_R_HandPV_LE.text() if len(self.TSM_R_HandPV_LE.text())>0 else ""
        GUI_STATE['TSM_Main_LE'] = self.TSM_Main_LE.text() if len(self.TSM_Main_LE.text())>0 else ""
        GUI_STATE['TSM_Character_LE'] = self.TSM_Character_LE.text() if len(self.TSM_Character_LE.text())>0 else ""
        GUI_STATE['Tab_Widget'] = self.Tab_Widget.currentIndex() 
        GUI_STATE['TSM_Data_Toggle_Check'] = self.TSM_Data_Toggle_Check
        GUI_STATE['TSM_Mirror_Toggle_Check'] = self.TSM_Mirror_Toggle_Check
        GUI_STATE['TSM_Mirror_CB'] = self.TSM_Mirror_CB.isChecked()
        GUI_STATE['XY_Plane_CB'] = self.XY_Plane_CB.isChecked()
        GUI_STATE['XZ_Plane_CB'] = self.XZ_Plane_CB.isChecked()
        GUI_STATE['YZ_Plane_CB'] = self.YZ_Plane_CB.isChecked()
        GUI_STATE['DOCK'] = self.DOCK
        GUI_STATE['Prefix'] = self.Prefix
        GUI_STATE['Start_Time_SB'] = self.Start_Time_SB.value()
        GUI_STATE['End_Time_SB'] = self.End_Time_SB.value()
    
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
            self.TSM_R_Wrist_LE.setText(GUI_STATE['TSM_R_Wrist_LE'])
            self.TSM_L_Knee_LE.setText(GUI_STATE['TSM_L_Knee_LE'])
            self.TSM_Lower_Spine_LE.setText(GUI_STATE['TSM_Lower_Spine_LE'])
            self.TSM_L_Leg_LE.setText(GUI_STATE['TSM_L_Leg_LE'])
            self.TSM_R_Toe_LE.setText(GUI_STATE['TSM_R_Toe_LE'])
            self.TSM_L_Ankle_LE.setText(GUI_STATE['TSM_L_Ankle_LE'])
            self.TSM_R_Knee_LE.setText(GUI_STATE['TSM_R_Knee_LE'])
            self.TSM_Mid_Spine_LE.setText(GUI_STATE['TSM_Mid_Spine_LE'])
            self.TSM_R_Ankle_LE.setText(GUI_STATE['TSM_R_Ankle_LE'])
            self.TSM_Upper_Spine_LE.setText(GUI_STATE['TSM_Upper_Spine_LE'])
            self.TSM_L_Arm_LE.setText(GUI_STATE['TSM_L_Arm_LE'])
            self.TSM_R_Leg_LE.setText(GUI_STATE['TSM_R_Leg_LE'])
            self.TSM_R_Arm_LE.setText(GUI_STATE['TSM_R_Arm_LE'])
            self.TSM_L_Toe_LE.setText(GUI_STATE['TSM_L_Toe_LE'])
            self.TSM_L_Wrist_LE.setText(GUI_STATE['TSM_L_Wrist_LE'])
            self.TSM_R_Shoulder_LE.setText(GUI_STATE['TSM_R_Shoulder_LE'])
            self.TSM_L_Elbow_LE.setText(GUI_STATE['TSM_L_Elbow_LE'])
            self.TSM_R_Elbow_LE.setText(GUI_STATE['TSM_R_Elbow_LE'])
            self.TSM_L_FootPV_LE.setText(GUI_STATE['TSM_L_FootPV_LE'])
            self.TSM_L_Foot_LE.setText(GUI_STATE['TSM_L_Foot_LE'])
            self.TSM_L_Hand_LE.setText(GUI_STATE['TSM_L_Hand_LE'])
            self.TSM_L_HandPV_LE.setText(GUI_STATE['TSM_L_HandPV_LE'])
            self.TSM_R_Hand_LE.setText(GUI_STATE['TSM_R_Hand_LE'])
            self.TSM_Body_LE.setText(GUI_STATE['TSM_Body_LE'])
            self.TSM_R_Foot_LE.setText(GUI_STATE['TSM_R_Foot_LE'])
            self.TSM_L_Shoulder_LE.setText(GUI_STATE['TSM_L_Shoulder_LE'])
            self.TSM_Head_LE.setText(GUI_STATE['TSM_Head_LE'])
            self.TSM_R_FootPV_LE.setText(GUI_STATE['TSM_R_FootPV_LE'])
            self.TSM_Neck_LE.setText(GUI_STATE['TSM_Neck_LE'])
            self.TSM_R_HandPV_LE.setText(GUI_STATE['TSM_R_HandPV_LE'])
            self.TSM_Main_LE.setText(GUI_STATE['TSM_Main_LE'])
            self.TSM_Character_LE.setText(GUI_STATE['TSM_Character_LE'])
            self.Tab_Widget.setCurrentIndex(int(GUI_STATE['Tab_Widget']))
            self.TSM_Data_Toggle_Check = GUI_STATE['TSM_Data_Toggle_Check']
            self.TSM_Mirror_Toggle_Check = GUI_STATE['TSM_Mirror_Toggle_Check']
            self.TSM_Mirror_CB.setChecked(GUI_STATE['TSM_Mirror_CB'])
            self.XY_Plane_CB.setChecked(GUI_STATE['XY_Plane_CB'])
            self.XZ_Plane_CB.setChecked(GUI_STATE['XZ_Plane_CB'])
            self.YZ_Plane_CB.setChecked(GUI_STATE['YZ_Plane_CB'])
            self.Prefix = GUI_STATE['Prefix']
            self.Start_Time_SB.setValue(int(GUI_STATE['Start_Time_SB']))
            self.End_Time_SB.setValue(int(GUI_STATE['End_Time_SB']))

            self.TSM_Data_Toggle_Fun()
            self.TSM_Data_Toggle_Fun()
            self.TSM_Mirror_Toggle_Fun()
            self.TSM_Mirror_Toggle_Fun()
            self.TSM_Check()
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
            
            # string $channelsLayersDockControl = getUIComponentDockControl(“Channel Box / Layer Editor”, false);
            # workspaceControl –e –tabToControl $channelsLayersDockControl -1 yourWorkspaceControl;
            self.workspaceCtrl = cmds.workspaceControl(name,tabToControl=["ChannelBoxLayerEditor",0],label=Title_Name,vcc=self.Save_Json_Fun)

            # 显示当前面板
            cmds.evalDeferred("cmds.workspaceControl(\"" + self.workspaceCtrl  + "\",e=True,r=True)")
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace
    
    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)

    def TSM_Check(self):
        
        num = 0

        if self.TSM_L_Wrist_LE.text() != "":
			num+=1

        if self.TSM_L_Elbow_LE.text() != "":
			num+=1

        if self.TSM_L_Arm_LE.text() != "":
			num+=1

        if self.TSM_L_Shoulder_LE.text() != "":
			num+=1

        if self.TSM_R_Wrist_LE.text() != "":
			num+=1

        if self.TSM_R_Elbow_LE.text() != "":
			num+=1

        if self.TSM_R_Arm_LE.text() != "":
			num+=1

        if self.TSM_R_Shoulder_LE.text() != "":
			num+=1

        if self.TSM_Head_LE.text() != "":
			num+=1

        if self.TSM_Upper_Spine_LE.text() != "":
			num+=1

        if self.TSM_Mid_Spine_LE.text() != "":
			num+=1

        if self.TSM_Lower_Spine_LE.text() != "":
			num+=1

        if self.TSM_Body_LE.text() != "":
			num+=1

        if self.TSM_L_Leg_LE.text() != "":
			num+=1

        if self.TSM_L_Knee_LE.text() != "":
			num+=1

        if self.TSM_L_Ankle_LE.text() != "":
			num+=1

        if self.TSM_L_Toe_LE.text() != "":
			num+=1

        if self.TSM_R_Leg_LE.text() != "":
			num+=1

        if self.TSM_R_Knee_LE.text() != "":
			num+=1

        if self.TSM_R_Ankle_LE.text() != "":
			num+=1

        if self.TSM_R_Toe_LE.text() != "":
			num+=1
            

        if self.TSM_R_Hand_LE.text() != "":
			num+=1
        if self.TSM_R_HandPV_LE.text() != "":
			num+=1
        if self.TSM_L_Hand_LE.text() != "":
			num+=1
        if self.TSM_L_HandPV_LE.text() != "":
			num+=1

        if self.TSM_R_Foot_LE.text() != "":
			num+=1
        if self.TSM_R_FootPV_LE.text() != "":
			num+=1
        if self.TSM_L_Foot_LE.text() != "":
			num+=1
        if self.TSM_L_FootPV_LE.text() != "":
			num+=1

        if self.TSM_Neck_LE.text() != "":
			num+=1
        if self.TSM_Main_LE.text() != "":
			num+=1
        if self.TSM_Character_LE.text() != "":
			num+=1

        if num == 32:
            self.TSM_Mirror_BTN.setEnabled(True)
            self.TSM_Mirror_Anim_BTN.setEnabled(True)
        else:
            self.TSM_Mirror_BTN.setEnabled(False)
            self.TSM_Mirror_Anim_BTN.setEnabled(False)