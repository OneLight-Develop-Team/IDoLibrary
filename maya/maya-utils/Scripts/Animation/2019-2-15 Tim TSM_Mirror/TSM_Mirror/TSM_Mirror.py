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
DIR = os.path.dirname(__file__)
PLUGIN_PATH = os.path.join(DIR,"plugin") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
UI_PATH = os.path.join(DIR,"ui","TSM_Mirror.ui") 
sys.path.append(PLUGIN_PATH)

from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
from Qt.QtCompat import *

from TSM_Mirror_ui import UI_Interface
# from TSM_Mirror_ui import setup_ui


class TSM_Mirror(UI_Interface):

    def __init__(self,dock="dock"):
        super(TSM_Mirror,self).__init__(dock=dock)
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

        self.TSM_Auto_Pick_BTN.clicked.connect(self.TSM_Auto_Pick_BTN_Fun)

        self.TSM_Mirror_Anim_BTN.clicked.connect(self.TSM_Mirror_Anim_BTN_Fun)
        
        self.TSM_Mirror_BTN.clicked.connect(self.TSM_Mirror_BTN_Fun)

        # 初始化 数组

        self.Pick_FN_List = [
            self.TSM_Head_Pick_Fun,
            self.TSM_R_Wrist_Pick_Fun,
            self.TSM_R_Elbow_Pick_Fun,
            self.TSM_R_Arm_Pick_Fun,
            self.TSM_R_Shoulder_Pick_Fun,
            self.TSM_L_Wrist_Pick_Fun,
            self.TSM_L_Elbow_Pick_Fun,
            self.TSM_L_Arm_Pick_Fun,
            self.TSM_L_Shoulder_Pick_Fun,
            self.TSM_Upper_Spine_Pick_Fun,
            self.TSM_Mid_Spine_Pick_Fun,
            self.TSM_Lower_Spine_Pick_Fun,
            self.TSM_Body_Pick_Fun,
            self.TSM_R_Leg_Pick_Fun,
            self.TSM_R_Knee_Pick_Fun,
            self.TSM_R_Ankle_Pick_Fun,
            self.TSM_R_Toe_Pick_Fun,
            self.TSM_L_Leg_Pick_Fun,
            self.TSM_L_Knee_Pick_Fun,
            self.TSM_L_Ankle_Pick_Fun,
            self.TSM_L_Toe_Pick_Fun,

            self.TSM_R_Foot_Pick_Fun,
            self.TSM_R_FootPV_Pick_Fun,
            self.TSM_L_Foot_Pick_Fun,
            self.TSM_L_FootPV_Pick_Fun,

            self.TSM_R_Hand_Pick_Fun,
            self.TSM_R_HandPV_Pick_Fun,
            self.TSM_L_Hand_Pick_Fun,
            self.TSM_L_HandPV_Pick_Fun,

            self.TSM_Main_Pick_Fun,
            self.TSM_Character_Pick_Fun,
            self.TSM_Neck_Pick_Fun,
        ]

        self.TSM_Controller=[
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
            "Main",
            "Character",
            "Head_Neck",
            "Head_FK",

            "LeftFinger4_finger_control",
            "LeftFinger3_finger_control",
            "LeftFinger2_finger_control",
            "LeftFinger1_finger_control",
            "LeftThumb_finger_control",

            "RightFinger4_finger_control",
            "RightFinger3_finger_control",
            "RightFinger2_finger_control",
            "RightFinger1_finger_control",
            "RightThumb_finger_control",

            "LeftFinger1_finger_IK",
            "LeftFinger2_finger_IK",
            "LeftFinger3_finger_IK",
            "LeftFinger4_finger_IK",

            "RightFinger1_finger_IK",
            "RightFinger2_finger_IK",
            "RightFinger3_finger_IK",
            "RightFinger4_finger_IK",
            
            "LeftArm_Standard_Pole_Vector",
            "RightArm_Standard_Pole_Vector",
            "LeftLeg_Standard_Pole_Vector",
            "RightLeg_Standard_Pole_Vector",

            # "LeftLeg_FootMover",
            # "RightLeg_FootTranslate",
            # "LeftArm_HandTranslate",
            # "RightArm_HandTranslate",
        ]

        self.FKLegList=[
            "RightLeg_Upper_Leg",
            "RightLeg_Lower_Leg",
            "RightLeg_Foot",
            "RightLeg_Toe",
            "LeftLeg_Upper_Leg",
            "LeftLeg_Lower_Leg",
            "LeftLeg_Foot",
            "LeftLeg_Toe",
        ]

        self.IKArmList=[
            "RightArm_Arm_IK",
            "RightArm_Arm_Pole_Vector",
            "LeftArm_Arm_IK",
            "LeftArm_Arm_Pole_Vector",
        ]

        self.IKLegList=[
            "RightLeg_IK_Leg",
            "RightLeg_Leg_Pole_Vector",
            "LeftLeg_IK_Leg",
            "LeftLeg_Leg_Pole_Vector",
        ]

        self.FingerList=[
            "LeftFinger1_finger_control",
            "LeftFinger2_finger_control",
            "LeftFinger3_finger_control",
            "LeftFinger4_finger_control",
            "LeftThumb_finger_control",
        ]

        self.AttrList=[
            "tx",
            "ty",
            "tz",
            "rx",
            "ry",
            "rz",
            "sx",
            "sy",
            "sz",
            "rotateAxisX",
            "rotateAxisY",
            "rotateAxisZ",
        ]

        self.BodyAttrList=[
            "LeftArm_FKIK",
            "LeftArm_Isolation",
            "LeftLeg_FKIK",
            "LeftLeg_Isolation",
        ]
        self.FingerAttrList=[
            "FingerStretch",
            "SideToSide",
            "Side_to_side",
            "FingerIK",
            "LastJoint",
            "MiddleJoint",
        ]
        self.HandAttrList=[
            "shut",
            "finger4",
            "finger3",
            "finger2",
            "finger1",
            "thumb",
        ]
        self.FK_Arm_HandAttrList=[
            "ArmStretch",
            "ElbowSlide",
            "TwistPlacement",
            "IKasFK",
            "NullifyTwist",
            "AddToTwist",
        ]
        self.FK_Upper_ArmAttrList=[
            # "TwistPlacement",
            "NullifyTwist",
            "AddToTwist",
        ]
        self.IK_ArmAttrList=[
            "ArmStretch",
            "ElbowSlide",
            "AutoStretch",
            "ForearmBendX",
            "ForearmBendY",
            "TwistPlacement",
            "ArmThicknessX",
            "ArmThicknessY",
            "NullifyTwist",
            "AddToTwist",
            "StandardPoleVector",
            # "standardpoleisolation",
        ]
        self.IK_LegAttrList=[
            "RaiseHeel",
            "RaiseToe",
            "SwivelFoot",
            "LegStretch",
            "AutoStretch",
            "KneeSlide",
            "StandardPoleVector",
            "toetip",
            "ankleX",
            "ankleY",
            "ankleZ",
            "knee_follow",
        ]
        self.FK_Leg_FootAttrList=[
            "LegStretch",
            "KneeSlide",
            "CalfBendX",
            "CalfBendY",
            "LegThicknessX",
            "LegThicknessY",
            "IKasFK",
        ]
        self.FK_Leg_Upper_LegAttrList=[
            "ThighBendX",
            "ThighBendY",
            "TwistPlacement",
            "RemoveTwist",
            "AddToTwist",
        ]

    def Help_Instruction_Fun(self):
        try:
            if cmds.window(self.InstructionWin,query=True,exists=True) :
                cmds.deleteUI(self.InstructionWin)
        except:
            pass
        self.InstructionWin = cmds.window(t=u"使用说明",wh=(400,300),rtf=True,s=False)

        cmds.columnLayout(adj=True)
        cmds.textField(tx=u"————————————————主要用法————————————————",ed=False,bgc=(1,.1,.1))
        cmds.textField(tx=u"step0：对TSM的控制器烘焙关键帧",ed=False,bgc=(.3,1,.3))
        cmds.textField(tx=u"step1：选择一个TSM主要的控制器",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"step2：设置镜像的时间范围",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"step3：选择镜像平面",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"step4：点击镜像当前帧测试镜像效果",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"step5：点击镜像时间范围关键帧即可镜像",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"————————————————辅助说明————————————————",ed=False,bgc=(1,.1,.1))

        cmds.textField(tx=u"1.在插件设置的下拉菜单可以开启更为详细的设置选项",ed=False,bgc=(.3,1,.3))
        cmds.textField(tx=u"2.镜像设置可以设置镜像当前帧是否要设置关键帧",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"3.一键获取中获取到的所有控制器全部在 `获取TSM目标模型 控制器中`",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"4.可以手动修改自动获取到的控制器",ed=False,bgc=(.3,.3,.3))
        cmds.textField(tx=u"5.当时间范围的起始时间和结束时间相等，就会获取所有关键帧",ed=False,bgc=(.3,1,.3))
        cmds.textField(tx=u"6.镜像平面会镜像最外层的世界坐标位置，如果角色不在原点，请考虑使用",ed=False,bgc=(.3,1,.3))

        cmds.showWindow(self.InstructionWin)

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

    def Dockable_Window_Fun(self,dock="undock",save=True):
        
        # 保存当前UI界面
        if save == True:
            self.DOCK = dock
            self.Save_Json_Fun()
        
        # 检测不同的UI 全部删除
        # evalDeferred 防止Maya删除UI的时候崩溃
        if cmds.window(self.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + self.undockWindow + "\")")

        if cmds.dockControl(self.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + self.dockControl + "\")")

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(self.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(self.workspaceCtrl)

        if save == False:
            if os.path.exists(GUI_STATE_PATH):
                os.remove(GUI_STATE_PATH)
            
        global TSM_Mirror_UI 
        TSM_Mirror_UI = TSM_Mirror(dock=dock)

    def TSM_Auto_Pick_BTN_Fun(self):
        Ctrl = cmds.ls(sl=True)
        if len(Ctrl) == 0:
            cmds.warning(u"请选择一个用来约束的控制器再执行一键获取")
            cmds.headsUpMessage(u"请选择一个用来约束的控制器再执行一键获取")
            return

        numCheck = 0
        for tsm in self.TSM_Controller:
            if Ctrl[0].find(tsm) != -1:
                self.Prefix = Ctrl[0].split(tsm)[0]
                break
            else:
                numCheck += 1

        if numCheck == len(self.TSM_Controller):
            cmds.warning(u"当前选择命名不匹配，请重新选择控制器")
            cmds.headsUpMessage(u"当前选择命名不匹配，请重新选择控制器")
            return

        count = 0
        for TSM in self.TSM_Controller:
            cmds.select(self.Prefix + TSM)
            try:
                self.Pick_FN_List[count]()
            except:
                break
            count += 1

        self.TSM_Check()
        self.Save_Json_Fun()

    def TSM_Controller_Check(self):
        
        # 清空当前选择
        cmds.select(cl=True)
        count = 0
        check = True
        for controller in self.TSM_Controller:
            if not cmds.objExists(self.Prefix + controller):
                # 清空不存在的控制器
                try:
                    self.Pick_FN_List[count]()
                except:
                    break
                check = False
            count += 1

        if check:
            return True
        else:
            cmds.warning(u"当前选择不存在，请重新获取控制器")
            cmds.headsUpMessage(u"当前选择不存在，请重新获取控制器")
            return False

    def TSM_Mirror_BTN_Fun(self):
        
        # 检查是否有控制器不存在
        if not self.TSM_Controller_Check():
            return

        L_CtrlList = {}
        L_Count = 0
        R_CtrlList = {}
        R_Count = 0
        
        for controller in self.TSM_Controller:

            if controller.find("Left") != -1:
                L_CtrlList[controller] = {}
            elif controller.find("Right") != -1:
                R_CtrlList[controller] = {}

            for Attr in self.AttrList:
                # 跳过冻结的属性
                if not cmds.getAttr(self.Prefix + controller + "." + Attr,l=True):
                    Val = cmds.getAttr(self.Prefix + controller + "." + Attr)
                    # 记录数据
                    if controller.find("Left") != -1:
                        L_CtrlList[controller][Attr] = Val
                        if controller.find("Thumb") != -1:
                            if Attr == "rx" or Attr == "ry":
                                L_CtrlList[controller][Attr] = -Val
                    elif controller.find("Right") != -1:
                        R_CtrlList[controller][Attr] = Val
                        if controller.find("Thumb") != -1:
                            if Attr == "rx" or Attr == "ry":
                                R_CtrlList[controller][Attr] = -Val
                    # 翻转主骨骼
                    elif controller.find("Head") != -1:
                        if Attr == "rx" or Attr == "ry":
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                    elif controller.find("Spine") != -1:
                        if Attr == "rz" or Attr == "ry":
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                    elif controller.find("Body") != -1:
                        if Attr == "tx" or Attr == "rz" or Attr == "ry":
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                    elif controller.find("Character") != -1:
                        if Attr == "tx" and self.YZ_Plane_CB.isChecked():
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                        elif Attr == "ty" and self.XY_Plane_CB.isChecked():
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                        elif Attr == "tz" and self.YZ_Plane_CB.isChecked():
                            cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                            if self.TSM_Mirror_CB.isChecked():
                                cmds.setKeyframe(self.Prefix + controller + "." + Attr)
                
                            
        for L_Ctrl in L_CtrlList:
            R_Ctrl = L_Ctrl.replace("Left","Right")
    
            for Attr in L_CtrlList[L_Ctrl]:
                if not cmds.getAttr(self.Prefix + L_Ctrl + "." + Attr,l=True):
                    # 全部镜像
                    cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,L_CtrlList[L_Ctrl][Attr])
                    # FK 负值处理
                    for Leg in self.FKLegList:
                        if R_Ctrl.find(Leg) != -1:
                            if Attr == "rx" or Attr == "ry":
                                cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr])
                                if self.TSM_Mirror_CB.isChecked():
                                    cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)
                                    
                    # IK 手臂 负值处理
                    for Arm in self.IKArmList:
                        if R_Ctrl.find(Arm) != -1:
                            if Attr == "tx" or Attr == "ty" or Attr == "tz":
                                cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr])
                                if self.TSM_Mirror_CB.isChecked():
                                    cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

                    for Leg in self.IKLegList:
                        if R_Ctrl.find(Leg) != -1:
                            if R_Ctrl.find("IK") != -1: # 脚的处理
                                if Attr == "tx" or  Attr == "ry" or Attr == "rz":
                                    cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr])
                                    if self.TSM_Mirror_CB.isChecked():
                                        cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)
                            else: # PV的处理
                                if Attr == "rx" or Attr == "rz" or Attr == "ty":
                                    cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr])
                                    if self.TSM_Mirror_CB.isChecked():
                                        cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

            for Attr in R_CtrlList[R_Ctrl]:
                if not cmds.getAttr(self.Prefix + R_Ctrl + "." + Attr,l=True):
                    # 全部镜像
                    cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,R_CtrlList[R_Ctrl][Attr])
                    # FK 负值处理
                    for Leg in self.FKLegList:
                        if L_Ctrl.find(Leg) != -1:
                            if Attr == "rx" or Attr == "ry":
                                cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr])
                                if self.TSM_Mirror_CB.isChecked():
                                    cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)
                    # IK 负值处理
                    for Arm in self.IKArmList:
                        if L_Ctrl.find(Arm) != -1:
                            if Attr == "tx" or Attr == "ty" or Attr == "tz":
                                cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr])
                                if self.TSM_Mirror_CB.isChecked():
                                    cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)

                    for Leg in self.IKLegList:
                        if L_Ctrl.find(Leg) != -1:
                            if L_Ctrl.find("IK") != -1: # 脚的处理
                                if Attr == "tx" or  Attr == "ry" or Attr == "rz":
                                    cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr])
                                    if self.TSM_Mirror_CB.isChecked():
                                        cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)
                            else: # PV的处理
                                if Attr == "rx" or Attr == "rz" or Attr == "ty":
                                    cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr])
                                    if self.TSM_Mirror_CB.isChecked():
                                        cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)

        ########################################
        ########    其余的属性 镜像    ##########
        ########################################
        # 身体
        for Attr in self.BodyAttrList:
            Handler = self.Prefix + "Upper_Body"
            if not cmds.getAttr(Handler + "." + Attr,l=True):
                L_Attr = Attr
                R_Attr = Attr.replace("Left","Right")
                L_Val = cmds.getAttr(Handler + "." + L_Attr)
                R_Val = cmds.getAttr(Handler + "." + R_Attr)
                cmds.setAttr(Handler + "." + L_Attr,R_Val)
                cmds.setAttr(Handler + "." + R_Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(Handler + "." + L_Attr)
                    cmds.setKeyframe(Handler + "." + R_Attr)

        # 手指
        for Finger in self.FingerList:
            L_Handler = self.Prefix + Finger
            R_Handler = self.Prefix + Finger.replace("Left","Right")
            for Attr in self.FingerAttrList:
                try:
                    if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                        R_Val = cmds.getAttr(R_Handler + "." + Attr)
                        L_Val = cmds.getAttr(L_Handler + "." + Attr)
                        cmds.setAttr(L_Handler + "." + Attr,R_Val)
                        cmds.setAttr(R_Handler + "." + Attr,L_Val)
                        if self.TSM_Mirror_CB.isChecked():
                            cmds.setKeyframe(L_Handler + "." + Attr)
                            cmds.setKeyframe(R_Handler + "." + Attr)
                except:
                    pass
                
        # 手
        for Attr in self.HandAttrList:
            L_Handler = self.Prefix + "LeftHand_CC"
            R_Handler = self.Prefix + "RightHand_CC"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # FK手臂
        for Attr in self.FK_Arm_HandAttrList:
            L_Handler = self.Prefix + "LeftArm_Hand"
            R_Handler = self.Prefix + "RightArm_Hand"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # FK肩膀
        for Attr in self.FK_Upper_ArmAttrList:
            L_Handler = self.Prefix + "LeftArm_Upper_Arm"
            R_Handler = self.Prefix + "RightArm_Upper_Arm"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # IK手臂
        for Attr in self.IK_ArmAttrList:
            L_Handler = self.Prefix + "LeftArm_Arm_IK"
            R_Handler = self.Prefix + "RightArm_Arm_IK"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # IK腿部
        for Attr in self.IK_LegAttrList:
            L_Handler = self.Prefix + "LeftLeg_IK_Leg"
            R_Handler = self.Prefix + "RightLeg_IK_Leg"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # FK脚
        for Attr in self.FK_Leg_FootAttrList:
            L_Handler = self.Prefix + "LeftLeg_Foot"
            R_Handler = self.Prefix + "RightLeg_Foot"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # FK腿部
        for Attr in self.FK_Leg_Upper_LegAttrList:
            L_Handler = self.Prefix + "LeftLeg_Upper_Leg"
            R_Handler = self.Prefix + "RightLeg_Upper_Leg"
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                R_Val = cmds.getAttr(R_Handler + "." + Attr)
                L_Val = cmds.getAttr(L_Handler + "." + Attr)
                cmds.setAttr(L_Handler + "." + Attr,R_Val)
                cmds.setAttr(R_Handler + "." + Attr,L_Val)
                if self.TSM_Mirror_CB.isChecked():
                    cmds.setKeyframe(L_Handler + "." + Attr)
                    cmds.setKeyframe(R_Handler + "." + Attr)

        # print L_CtrlList
        # print R_CtrlList
                

    def TSM_Mirror_Anim_BTN_Fun(self):
        
        StartTime = self.Start_Time_SB.value()
        EndTime = self.End_Time_SB.value()
        timeCheck = True
        if StartTime > EndTime:
            cmds.warning(u"起始时间大于结束时间，自动将时间对调")
            StartTime = self.End_Time_SB.value()
            EndTime = self.Start_Time_SB.value()
            
        elif StartTime == EndTime:
            cmds.warning(u"起始时间等于结束时间，自动获取所有的关键帧")
            timeCheck = False

        
        # 检查是否有控制器不存在
        if not self.TSM_Controller_Check():
            return

        ####################################### 
        #######      获取左右数据       ######## 
        #######################################

        cmds.progressWindow(	title=u'TSM镜像',
					progress=0,
					status=u'获取左右镜像数据...',
					isInterruptable=True )

        amount = 0.0

        L_CtrlList = {}
        L_Count = 0
        R_CtrlList = {}
        R_Count = 0

        try:
            for controller in self.TSM_Controller:

                if controller.find("Left") != -1:
                    L_CtrlList[controller] = {}
                elif controller.find("Right") != -1:
                    R_CtrlList[controller] = {}

                # 进度条显示
                if cmds.progressWindow( query=True, isCancelled=True ) :
                    cmds.progressWindow(endProgress=1)
                    return
                
                amount += 1.0
                cmds.progressWindow( edit=True, progress=amount/len(self.TSM_Controller)*100 )
                
                for Attr in self.AttrList:

                    # 查询控制器上的关键帧数据
                    if timeCheck:
                        Keyframe = cmds.keyframe(self.Prefix + controller + "." + Attr,time=(StartTime,EndTime),q=True)
                    else:
                        Keyframe = cmds.keyframe(self.Prefix + controller + "." + Attr,q=True)
                        
                    
                    if Keyframe != None:
                        
                        if controller.find("Left") != -1:
                            L_CtrlList[controller][Attr] = {}
                        elif controller.find("Right") != -1:
                            R_CtrlList[controller][Attr] = {}

                        # 遍历相关的关键帧
                        for Frame in Keyframe:
                            Val = cmds.getAttr(self.Prefix + controller + "." + Attr,time=Frame)
                            # 左边的数据
                            if controller.find("Left") != -1:
                                L_CtrlList[controller][Attr][Frame] = Val
                                if controller.find("Thumb") != -1:
                                    if Attr == "rx" or Attr == "ry":
                                        L_CtrlList[controller][Attr][Frame] = -Val
                            # 右边的数据
                            elif controller.find("Right") != -1:
                                R_CtrlList[controller][Attr][Frame] = Val
                                if controller.find("Thumb") != -1:
                                    if Attr == "rx" or Attr == "ry":
                                        R_CtrlList[controller][Attr][Frame] = -Val
                            # 翻转主骨骼
                            elif controller.find("Head") != -1:
                                cmds.progressWindow( edit=True, status=u'镜像根部控制器...' )
                                if Attr == "rx" or Attr == "ry":
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                            elif controller.find("Spine") != -1:
                                if Attr == "rz" or Attr == "ry":
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                            elif controller.find("Body") != -1:
                                if Attr == "rz" or Attr == "ry" or Attr == "tx":
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                            elif controller.find("Character") != -1:
                                if Attr == "tx" and self.YZ_Plane_CB.isChecked():
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                                elif Attr == "ty" and self.XY_Plane_CB.isChecked():
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                                elif Attr == "tz" and self.YZ_Plane_CB.isChecked():
                                    cmds.setAttr(self.Prefix + controller + "." + Attr,-Val)
                                    cmds.setKeyframe(self.Prefix + controller + "." + Attr,time=Frame)
                
        except:
            traceback.print_exc()
            cmds.progressWindow(endProgress=1)

        cmds.progressWindow(endProgress=1)
        
        # print L_CtrlList
        # print R_CtrlList

        ####################################### 
        #######        镜像数据         ######## 
        #######################################

        cmds.progressWindow(	title=u'TSM镜像',
					progress=0,
					status=u'镜像左右控制器...',
					isInterruptable=True )
        amount = 0.0

        try:

            for L_Ctrl in L_CtrlList:

                R_Ctrl = L_Ctrl.replace("Left","Right")

                # 进度条显示
                if cmds.progressWindow( query=True, isCancelled=True ) :
                    return
                
                amount += 1.0
                cmds.progressWindow( edit=True, progress=amount/len(L_CtrlList)*100 )

                ####################################### 
                #######        处理右边         ######## 
                #######################################
                # 删除关键帧
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='tx')
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='ty')
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='tz')
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='rx')
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='ry')
                cmds.cutKey(self.Prefix + R_Ctrl,clear=True,time=(StartTime,EndTime),attribute='rz')

                for Attr in L_CtrlList[L_Ctrl]:
                    if not cmds.getAttr(self.Prefix + L_Ctrl + "." + Attr,l=True):
                        for Frame in L_CtrlList[L_Ctrl][Attr]:
                            # 去到记录的关键帧
                            cmds.currentTime(Frame,u=False)

                            # 先镜像数值
                            cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,L_CtrlList[L_Ctrl][Attr][Frame])
                            cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

                            # FK 负值处理
                            for Leg in self.FKLegList:
                                if R_Ctrl.find(Leg) != -1:
                                    if Attr == "rx" or Attr == "ry":
                                        cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr][Frame])
                                        cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

                            # IK 手臂 负值处理
                            for Arm in self.IKArmList:
                                if R_Ctrl.find(Arm) != -1:
                                    if Attr == "tx" or Attr == "ty" or Attr == "tz":
                                        cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr][Frame])
                                        cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

                            # IK 脚 负值处理
                            for Leg in self.IKLegList:
                                if R_Ctrl.find(Leg) != -1:
                                    if R_Ctrl.find("IK") != -1: # 脚的处理
                                        if Attr == "tx" or  Attr == "ry" or Attr == "rz":
                                            cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr][Frame])
                                            cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)
                                    else: # PV的处理
                                        if Attr == "rx" or Attr == "rz" or Attr == "ty":
                                            cmds.setAttr(self.Prefix + R_Ctrl + "." + Attr,-L_CtrlList[L_Ctrl][Attr][Frame])
                                            cmds.setKeyframe(self.Prefix + R_Ctrl + "." + Attr)

                ####################################### 
                #######        处理左边         ######## 
                #######################################
                # 删除所有关键帧
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='tx')
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='ty')
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='tz')
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='rx')
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='ry')
                cmds.cutKey(self.Prefix + L_Ctrl,clear=True,time=(StartTime,EndTime),attribute='rz')
                
                for Attr in R_CtrlList[R_Ctrl]:
                    if not cmds.getAttr(self.Prefix + R_Ctrl + "." + Attr,l=True):
                        for Frame in R_CtrlList[R_Ctrl][Attr]:
                            # 去到记录的关键帧
                            cmds.currentTime(Frame,u=False)

                            # 先镜像数值
                            cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,R_CtrlList[R_Ctrl][Attr][Frame])
                            cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)
                            # FK 负值处理
                            for Leg in self.FKLegList:
                                if L_Ctrl.find(Leg) != -1:
                                    if Attr == "rx" or Attr == "ry":
                                        cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr][Frame])
                                        cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)
                            # IK 负值处理
                            for Arm in self.IKArmList:
                                if L_Ctrl.find(Arm) != -1:
                                    if Attr == "tx" or Attr == "ty" or Attr == "tz":
                                        cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr][Frame])
                                        cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)

                            for Leg in self.IKLegList:
                                if L_Ctrl.find(Leg) != -1:
                                    if L_Ctrl.find("IK") != -1: # 脚的处理
                                        if Attr == "tx" or  Attr == "ry" or Attr == "rz":
                                            cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr][Frame])
                                            cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)
                                    else: # PV的处理
                                        if Attr == "rx" or Attr == "rz" or Attr == "ty":
                                            cmds.setAttr(self.Prefix + L_Ctrl + "." + Attr,-R_CtrlList[R_Ctrl][Attr][Frame])
                                            cmds.setKeyframe(self.Prefix + L_Ctrl + "." + Attr)

        except:
            traceback.print_exc()
            cmds.progressWindow(endProgress=1)
            
        cmds.progressWindow(endProgress=1)

        ########################################
        ########    其余的属性 镜像    ##########
        ########################################

        cmds.progressWindow(	title=u'TSM镜像',
					progress=0,
					status=u'镜像自定义属性...',
					isInterruptable=True )
        amount = 0.0

        # 进度条显示
        if cmds.progressWindow( query=True, isCancelled=True ) :
            cmds.progressWindow(endProgress=1)
            return
            
        # 身体
        for Attr in self.BodyAttrList:
            Handler = self.Prefix + "Upper_Body"
            L_Attr = Attr
            R_Attr = Attr.replace("Left","Right")
            if not cmds.getAttr(Handler + "." + Attr,l=True):
                # 查询控制器上的关键帧数据
                try:
                    if timeCheck:
                        Keyframe = cmds.keyframe(Handler + "." + L_Attr,time=(StartTime,EndTime),q=True)
                        Keyframe += cmds.keyframe(Handler + "." + R_Attr,time=(StartTime,EndTime),q=True)
                        Keyframe = list(set(Keyframe))
                    else:
                        Keyframe = cmds.keyframe(Handler + "." + L_Attr,q=True)
                        Keyframe += cmds.keyframe(Handler + "." + R_Attr,q=True)
                        Keyframe = list(set(Keyframe))
                except:
                    cmds.warning(Handler + "." + L_Attr + u" 没有关键帧可以匹配 " + Handler + "." + R_Attr + u" - 跳过当前属性")
                    cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                    break

                for Frame in Keyframe:
                    L_Val = cmds.getAttr(Handler + "." + L_Attr,time=Frame)
                    R_Val = cmds.getAttr(Handler + "." + R_Attr,time=Frame)
                    
                    cmds.setAttr(Handler + "." + L_Attr,R_Val)
                    cmds.setAttr(Handler + "." + R_Attr,L_Val)
                    cmds.setKeyframe(Handler + "." + L_Attr,time=Frame)
                    cmds.setKeyframe(Handler + "." + R_Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )

        # 手指
        for Finger in self.FingerList:
            L_Handler = self.Prefix + Finger
            R_Handler = self.Prefix + Finger.replace("Left","Right")
            for Attr in self.FingerAttrList:
                # 查询控制器上的关键帧数据
                try:
                    if timeCheck:
                        Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                        Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                        Keyframe = list(set(Keyframe))
                    else:
                        Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                        Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                        Keyframe = list(set(Keyframe))
                except ValueError:
                    break
                except:
                    cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                    cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                    break

                if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                    for Frame in Keyframe:
                        R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                        L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                        cmds.setAttr(L_Handler + "." + Attr,R_Val)
                        cmds.setAttr(R_Handler + "." + Attr,L_Val)
                        cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                        cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )

        # 手
        for Attr in self.HandAttrList:
            L_Handler = self.Prefix + "LeftHand_CC"
            R_Handler = self.Prefix + "RightHand_CC"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)
                    
        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        
        # FK手臂
        for Attr in self.FK_Arm_HandAttrList:
            L_Handler = self.Prefix + "LeftArm_Hand"
            R_Handler = self.Prefix + "RightArm_Hand"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        
        # FK肩膀
        for Attr in self.FK_Upper_ArmAttrList:
            L_Handler = self.Prefix + "LeftArm_Upper_Arm"
            R_Handler = self.Prefix + "RightArm_Upper_Arm"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        
        # IK手臂
        for Attr in self.IK_ArmAttrList:
            L_Handler = self.Prefix + "LeftArm_Arm_IK"
            R_Handler = self.Prefix + "RightArm_Arm_IK"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )

        # IK腿部
        for Attr in self.IK_LegAttrList:
            L_Handler = self.Prefix + "LeftLeg_IK_Leg"
            R_Handler = self.Prefix + "RightLeg_IK_Leg"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        
        # FK脚
        for Attr in self.FK_Leg_FootAttrList:
            L_Handler = self.Prefix + "LeftLeg_Foot"
            R_Handler = self.Prefix + "RightLeg_Foot"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)

        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        
        # FK腿部
        for Attr in self.FK_Leg_Upper_LegAttrList:
            L_Handler = self.Prefix + "LeftLeg_Upper_Leg"
            R_Handler = self.Prefix + "RightLeg_Upper_Leg"
            # 查询控制器上的关键帧数据
            try:
                if timeCheck:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,time=(StartTime,EndTime),q=True)
                    Keyframe = list(set(Keyframe))
                else:
                    Keyframe = cmds.keyframe(L_Handler + "." + Attr,q=True)
                    Keyframe += cmds.keyframe(R_Handler + "." + Attr,q=True)
                    Keyframe = list(set(Keyframe))
            except:
                cmds.warning(L_Handler + "." + Attr + u" 没有关键帧可以匹配 " + R_Handler + "." + Attr + u" - 跳过当前属性")
                cmds.headsUpMessage(u"部分属性已跳过，请打开脚本编辑器查看")
                break
            
            if not cmds.getAttr(L_Handler + "." + Attr,l=True) and not cmds.getAttr(R_Handler + "." + Attr,l=True):
                for Frame in Keyframe:
                    R_Val = cmds.getAttr(R_Handler + "." + Attr,time=Frame)
                    L_Val = cmds.getAttr(L_Handler + "." + Attr,time=Frame)
                    cmds.setAttr(L_Handler + "." + Attr,R_Val)
                    cmds.setAttr(R_Handler + "." + Attr,L_Val)
                    cmds.setKeyframe(L_Handler + "." + Attr,time=Frame)
                    cmds.setKeyframe(R_Handler + "." + Attr,time=Frame)
                    
        amount += 1.0
        cmds.progressWindow( edit=True, progress=amount/9*100 )
        cmds.progressWindow(endProgress=1)

        cmds.currentTime(cmds.currentTime(q=True),u=True)

        # cmds.keyframe(q=True)

        self.Save_Json_Fun()        

def main():
    # 检测不同的UI 全部删除
    global TSM_Mirror_UI 

    try:
        if cmds.window(TSM_Mirror_UI.undockWindow,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + TSM_Mirror_UI.undockWindow + "\")")
            print "undockWindow"
    except:
        pass

    try:
        if cmds.dockControl(TSM_Mirror_UI.dockControl,query=True,exists=True) :
            cmds.evalDeferred("cmds.deleteUI(\"" + TSM_Mirror_UI.dockControl + "\")")
            print TSM_Mirror_UI.base_instance
    except:
        pass

    try:
        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            if cmds.workspaceControl(TSM_Mirror_UI.workspaceCtrl,query=True,exists=True) :
                cmds.deleteUI(TSM_Mirror_UI.workspaceCtrl)
                print "workspaceCtrl"
    except:
        pass

    TSM_Mirror_UI = TSM_Mirror(dock="undock")
