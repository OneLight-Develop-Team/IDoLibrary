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

from Cap2Con_ui import UI_Interface
class Cap2Con(UI_Interface):
    def __init__(self,dock="dock"):
        super(Cap2Con,self).__init__(dock=dock)

        # 窗口设置按钮功能
        self.Maya_Dock.clicked.connect(partial(self.Dockable_Window_Fun,dock="dock"))
        self.Maya_Undock.clicked.connect(partial(self.Dockable_Window_Fun,dock="undock"))

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            self.Maya_Workspace.clicked.connect(partial(self.Dockable_Window_Fun,dock="workspace"))
        else:
            self.Maya_Workspace.setEnabled(False)

        self.Default_Setting.clicked.connect(partial(self.Dockable_Window_Fun,save=False))


        self.Capture_Auto_Pick_BTN.clicked.connect(self.Capture_Auto_Pick_BTN_Fun)

        self.Target_Auto_Pick_BTN.clicked.connect(self.Target_Auto_Pick_BTN_Fun)

        self.Constraint_BTN.clicked.connect(self.Constraint_BTN_Fun)

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
            
        global Cap2Con_UI 
        Cap2Con_UI = Cap2Con(dock=dock)
        Cap2Con_UI.show()

    def Capture_Auto_Pick_BTN_Fun(self):
        Ctrl = cmds.ls(sl=True)
        if len(Ctrl) == 0:
            cmds.warning(u"请选择一个用来约束的控制器再执行一键获取")
            cmds.headsUpMessage(u"请选择一个用来约束的控制器再执行一键获取")
            return

        ADV_NAME=[
            "FKHead_M",
            "FKWrist_L",
            "FKElbow_L",
            "FKShoulder_L",
            "FKScapula_L",
            "FKWrist_R",
            "FKElbow_R",
            "FKShoulder_R",
            "FKScapula_R",
            "FKChest_M",
            "FKSpine2_M",
            "FKRoot_M",
            "RootX_M",
            "FKHip_L",
            "FKKnee_L",
            "FKAnkle_L",
            "FKToes_L",
            "FKHip_R",
            "FKKnee_R",
            "FKAnkle_R",
            "FKToes_R",
            "PoleArm_R",
            "IKArm_R",
            "PoleArm_L",
            "IKArm_L",
            "PoleLeg_R",
            "IKLeg_R",
            "PoleLeg_L",
            "IKLeg_L",
        ]

        numCheck = 0
        for adv in ADV_NAME:
            if Ctrl[0].find(adv) != -1:
                prefix = Ctrl[0].split(adv)[0]
                break
            else:
                numCheck += 1

        if numCheck == len(ADV_NAME):
            cmds.warning(u"当前选择命名不匹配，请重新选择要约束的控制器")
            cmds.headsUpMessage(u"当前选择命名不匹配，请重新选择要约束的控制器")
            return

        cmds.select(prefix + "IKLeg_R")
        self.Capture_R_Foot_Pick_Fun()

        cmds.select(prefix + "PoleLeg_R")
        self.Capture_R_FootPV_Pick_Fun()

        cmds.select(prefix + "IKLeg_L")
        self.Capture_L_Foot_Pick_Fun()

        cmds.select(prefix + "PoleLeg_L")
        self.Capture_L_FootPV_Pick_Fun()

        cmds.select(prefix + "IKArm_R")
        self.Capture_R_Hand_Pick_Fun()

        cmds.select(prefix + "PoleArm_R")
        self.Capture_R_HandPV_Pick_Fun()

        cmds.select(prefix + "IKArm_L")
        self.Capture_L_Hand_Pick_Fun()

        cmds.select(prefix + "PoleArm_L")
        self.Capture_L_HandPV_Pick_Fun()

        cmds.select(prefix + "FKWrist_L")
        self.Capture_L_Wrist_Pick_Fun()

        cmds.select(prefix + "FKElbow_L")
        self.Capture_L_Elbow_Pick_Fun()

        cmds.select(prefix + "FKShoulder_L")
        self.Capture_L_Arm_Pick_Fun()

        cmds.select(prefix + "FKScapula_L")
        self.Capture_L_Shoulder_Pick_Fun()

        cmds.select(prefix + "FKWrist_R")
        self.Capture_R_Wrist_Pick_Fun()

        cmds.select(prefix + "FKElbow_R")
        self.Capture_R_Elbow_Pick_Fun()

        cmds.select(prefix + "FKShoulder_R")
        self.Capture_R_Arm_Pick_Fun()

        cmds.select(prefix + "FKScapula_R")
        self.Capture_R_Shoulder_Pick_Fun()

        cmds.select(prefix + "FKHead_M")
        self.Capture_Head_Pick_Fun()

        cmds.select(prefix + "FKChest_M")
        self.Capture_Upper_Spine_Pick_Fun()

        cmds.select(prefix + "FKSpine2_M")
        self.Capture_Mid_Spine_Pick_Fun()

        cmds.select(prefix + "FKRoot_M")
        self.Capture_Lower_Spine_Pick_Fun()

        cmds.select(prefix + "RootX_M")
        self.Capture_Body_Pick_Fun()

        cmds.select(prefix + "FKHip_L")
        self.Capture_L_Leg_Pick_Fun()

        cmds.select(prefix + "FKKnee_L")
        self.Capture_L_Knee_Pick_Fun()

        cmds.select(prefix + "FKAnkle_L")
        self.Capture_L_Ankle_Pick_Fun()

        cmds.select(prefix + "FKToes_L")
        self.Capture_L_Toe_Pick_Fun()

        cmds.select(prefix + "FKHip_R")
        self.Capture_R_Leg_Pick_Fun()

        cmds.select(prefix + "FKKnee_R")
        self.Capture_R_Knee_Pick_Fun()

        cmds.select(prefix + "FKAnkle_R")
        self.Capture_R_Ankle_Pick_Fun()

        cmds.select(prefix + "FKToes_R")
        self.Capture_R_Toe_Pick_Fun()

        self.Con_Check()
        self.Save_Json_Fun()        

    def Target_Auto_Pick_BTN_Fun(self):
        Ctrl = cmds.ls(sl=True)
        if len(Ctrl) == 0:
            cmds.warning(u"请选择一个用来约束的控制器再执行一键获取")
            cmds.headsUpMessage(u"请选择一个用来约束的控制器再执行一键获取")
            return

        TSM_NAME=[
            "Head_FK",
            "RightArm_Hand",
            "RightArm_Lower_Arm",
            "RightArm_Upper_Arm",
            "RightArm_Shoulder",
            "LeftArm_Hand",
            "LeftArm_Lower_Arm",
            "LeftArm_Upper_Arm",
            "LeftArm_Shoulder",
            "Spine_Torso_FK",
            "Spine_Middle_FK",
            "Spine_Pelvis_FK",
            "Upper_Body",
            "RightLeg_Upper_Leg",
            "RightLeg_Lower_Leg",
            "RightLeg_Foot",
            "RightLeg_Toe",
            "LeftLeg_Upper_Leg",
            "LeftLeg_Lower_Leg",
            "LeftLeg_Foot",
            "LeftLeg_Toe",
            "RightLeg_IK_Leg",
            "RightLeg_Leg_Pole_Vector",
            "LeftLeg_IK_Leg",
            "LeftLeg_Leg_Pole_Vector",
            "RightArm_Arm_IK",
            "RightArm_Arm_Pole_Vector",
            "LeftArm_Arm_IK",
            "LeftArm_Arm_Pole_Vector",
        ]

        numCheck = 0
        for tsm in TSM_NAME:
            if Ctrl[0].find(tsm) != -1:
                prefix = Ctrl[0].split(tsm)[0]
                break
            else:
                numCheck += 1

        if numCheck == len(TSM_NAME):
            cmds.warning(u"当前选择命名不匹配，请重新选择要约束的控制器")
            cmds.headsUpMessage(u"当前选择命名不匹配，请重新选择要约束的控制器")
            return

        cmds.select(prefix + "RightLeg_IK_Leg")
        self.Target_R_Foot_Pick_Fun()

        cmds.select(prefix + "RightLeg_Leg_Pole_Vector")
        self.Target_R_FootPV_Pick_Fun()

        cmds.select(prefix + "LeftLeg_IK_Leg")
        self.Target_L_Foot_Pick_Fun()

        cmds.select(prefix + "LeftLeg_Leg_Pole_Vector")
        self.Target_L_FootPV_Pick_Fun()

        cmds.select(prefix + "RightArm_Arm_IK")
        self.Target_R_Hand_Pick_Fun()

        cmds.select(prefix + "RightArm_Arm_Pole_Vector")
        self.Target_R_HandPV_Pick_Fun()

        cmds.select(prefix + "LeftArm_Arm_IK")
        self.Target_L_Hand_Pick_Fun()

        cmds.select(prefix + "LeftArm_Arm_Pole_Vector")
        self.Target_L_HandPV_Pick_Fun()

        cmds.select(prefix + "LeftArm_Hand")
        self.Target_L_Wrist_Pick_Fun()

        cmds.select(prefix + "LeftArm_Lower_Arm")
        self.Target_L_Elbow_Pick_Fun()

        cmds.select(prefix + "LeftArm_Upper_Arm")
        self.Target_L_Arm_Pick_Fun()

        cmds.select(prefix + "LeftArm_Shoulder")
        self.Target_L_Shoulder_Pick_Fun()

        cmds.select(prefix + "RightArm_Hand")
        self.Target_R_Wrist_Pick_Fun()

        cmds.select(prefix + "RightArm_Lower_Arm")
        self.Target_R_Elbow_Pick_Fun()

        cmds.select(prefix + "RightArm_Upper_Arm")
        self.Target_R_Arm_Pick_Fun()

        cmds.select(prefix + "RightArm_Shoulder")
        self.Target_R_Shoulder_Pick_Fun()

        cmds.select(prefix + "Head_FK")
        self.Target_Head_Pick_Fun()

        cmds.select(prefix + "Spine_Torso_FK")
        self.Target_Upper_Spine_Pick_Fun()

        cmds.select(prefix + "Spine_Middle_FK")
        self.Target_Mid_Spine_Pick_Fun()

        cmds.select(prefix + "Spine_Pelvis_FK")
        self.Target_Lower_Spine_Pick_Fun()

        cmds.select(prefix + "Upper_Body")
        self.Target_Body_Pick_Fun()

        cmds.select(prefix + "LeftLeg_Upper_Leg")
        self.Target_L_Leg_Pick_Fun()

        cmds.select(prefix + "LeftLeg_Lower_Leg")
        self.Target_L_Knee_Pick_Fun()

        cmds.select(prefix + "LeftLeg_Foot")
        self.Target_L_Ankle_Pick_Fun()

        cmds.select(prefix + "LeftLeg_Toe")
        self.Target_L_Toe_Pick_Fun()

        cmds.select(prefix + "RightLeg_Upper_Leg")
        self.Target_R_Leg_Pick_Fun()

        cmds.select(prefix + "RightLeg_Lower_Leg")
        self.Target_R_Knee_Pick_Fun()

        cmds.select(prefix + "RightLeg_Foot")
        self.Target_R_Ankle_Pick_Fun()

        cmds.select(prefix + "RightLeg_Toe")
        self.Target_R_Toe_Pick_Fun()

        self.Con_Check()
        self.Save_Json_Fun()        

    def Constraint_BTN_Fun(self):

        cmds.parentConstraint( self.Capture_L_Foot_LE.text(),self.Target_L_Foot_LE.text(), mo=True )
        cmds.parentConstraint( self.Capture_R_Foot_LE.text(),self.Target_R_Foot_LE.text(), mo=True )
        cmds.parentConstraint( self.Capture_L_FootPV_LE.text(),self.Target_L_FootPV_LE.text(), mo=True )
        cmds.parentConstraint( self.Capture_R_FootPV_LE.text(),self.Target_R_FootPV_LE.text(), mo=True )
        cmds.parentConstraint( self.Capture_L_Hand_LE.text(),self.Target_L_Hand_LE.text(), mo=True )
        cmds.parentConstraint( self.Capture_R_Hand_LE.text(),self.Target_R_Hand_LE.text(), mo=True )
        # cmds.aimConstraint( self.Capture_L_HandPV_LE.text(),self.Target_L_HandPV_LE.text(), mo=True )
        # cmds.aimConstraint( self.Capture_R_HandPV_LE.text(),self.Target_R_HandPV_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Wrist_LE.text(),self.Target_L_Wrist_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Elbow_LE.text(),self.Target_L_Elbow_LE.text(), mo=True,skip=("x","z") )

        cmds.orientConstraint( self.Capture_L_Arm_LE.text(),self.Target_L_Arm_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Shoulder_LE.text(),self.Target_L_Shoulder_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Wrist_LE.text(),self.Target_R_Wrist_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Elbow_LE.text(),self.Target_R_Elbow_LE.text(), mo=True,skip=("x","z") )

        cmds.orientConstraint( self.Capture_R_Arm_LE.text(),self.Target_R_Arm_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Shoulder_LE.text(),self.Target_R_Shoulder_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_Head_LE.text(),self.Target_Head_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_Upper_Spine_LE.text(),self.Target_Upper_Spine_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_Mid_Spine_LE.text(),self.Target_Mid_Spine_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_Lower_Spine_LE.text(),self.Target_Lower_Spine_LE.text(), mo=True )

        cmds.parentConstraint( self.Capture_Body_LE.text(),self.Target_Body_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Leg_LE.text(),self.Target_L_Leg_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Knee_LE.text(),self.Target_L_Knee_LE.text(), mo=True,skip=("x","y") )

        cmds.orientConstraint( self.Capture_L_Ankle_LE.text(),self.Target_L_Ankle_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_L_Toe_LE.text(),self.Target_L_Toe_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Leg_LE.text(),self.Target_R_Leg_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Knee_LE.text(),self.Target_R_Knee_LE.text(), mo=True,skip=("x","y") )

        cmds.orientConstraint( self.Capture_R_Ankle_LE.text(),self.Target_R_Ankle_LE.text(), mo=True )

        cmds.orientConstraint( self.Capture_R_Toe_LE.text(),self.Target_R_Toe_LE.text(), mo=True )

        cmds.headsUpMessage(u"约束完成")
        self.Save_Json_Fun()        

def main():
    # 检测不同的UI 全部删除
    global Cap2Con_UI 

    try:
        if cmds.window(Cap2Con_UI.undockWindow,query=True,exists=True) :
            cmds.deleteUI(Cap2Con_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(Cap2Con_UI.dockControl,query=True,exists=True) :
            cmds.deleteUI(Cap2Con_UI.dockControl)
    except:
        pass

    try:
        if cmds.workspaceControl(Cap2Con_UI.workspaceCtrl,query=True,exists=True) :
            cmds.deleteUI(Cap2Con_UI.workspaceCtrl)
    except:
        pass

    Cap2Con_UI = Cap2Con(dock="undock")
    Cap2Con_UI.show()
