# -*- coding:utf-8 -*-
# Require Header
import os
import json
from functools import partial

# Sys Header
import sys
import traceback
import subprocess

import plugin.Qt as Qt
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from maya import cmds

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
UI_PATH = os.path.join(DIR,"ui","Cam_Attrubte_Panel.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

class Cam_Attribute_Panel(form_class,base_class):
    def __init__(self,MainWindow):
        super(Cam_Attribute_Panel,self).__init__()
        self.setupUi(self)
        self.MainWindow = MainWindow

        self.Current_Item = None

        # Note - 功能函数
        self.Position_BTN.clicked.connect(self.Position_Fn)
        self.Keyframe_BTN.clicked.connect(self.Keyframe_Fn)

        # Note - 动画切换效果
        self.Cam_Input_Toggle_Anim = QPropertyAnimation(self.Cam_Input_Layout, b"maximumHeight")
        self.Cam_Input_Toggle_Anim.setDuration(300)
        self.Cam_Input_Toggle_Anim.setStartValue(0)
        self.Cam_Input_Toggle_Anim.setEndValue(self.Cam_Input_Layout.sizeHint().height())
        self.Cam_Input_Toggle_Check = False
        self.Cam_Input_Toggle.clicked.connect(self.Cam_Input_Toggle_Fn)

        self.Cam_Output_Toggle_Anim = QPropertyAnimation(self.Cam_Output_Layout, b"maximumHeight")
        self.Cam_Output_Toggle_Anim.setDuration(300)
        self.Cam_Output_Toggle_Anim.setStartValue(0)
        self.Cam_Output_Toggle_Anim.setEndValue(self.Cam_Output_Layout.sizeHint().height())
        self.Cam_Output_Toggle_Check = False
        self.Cam_Output_Toggle.clicked.connect(self.Cam_Output_Toggle_Fn)

        # Note - 选择功能函数
        self.Add_CamGrp_Get.setVisible(False)
        self.Add_CamGrp_Pick.clicked.connect(self.Add_CamGrp_Pick_Fun)

        self.Add_Crv_Get.setVisible(False)
        self.Add_Crv_Pick.clicked.connect(self.Add_Crv_Pick_Fun)

        self.Add_Loc_Get.setVisible(False)
        self.Add_Loc_Pick.clicked.connect(self.Add_Loc_Pick_Fun)
        
        self.Add_Motion_Path_Get.setVisible(False)
        self.Add_Motion_Path_Pick.clicked.connect(self.Add_Motion_Path_Pick_Fun)

        # Note - SpinBox
        self.Strat_Time_SB.valueChanged.connect(self.Strat_Time_SB_Fn)
        self.End_Time_SB.valueChanged.connect(self.End_Time_SB_Fn)

    def Strat_Time_SB_Fn(self):
        self.Current_Item.Attr["Strat_Time_SB"] = self.Strat_Time_SB.value()
        self.MainWindow.Save_Json_Fun()

    def End_Time_SB_Fn(self):
        self.Current_Item.Attr["End_Time_SB"] = self.End_Time_SB.value()
        self.MainWindow.Save_Json_Fun()

    def Check_Selection(self):
        """
        Check_Selection 
        # Note 检查是否选择好所有的东西
        """
        Check_List=[
            self.Add_Crv_LE.text()                              != "",
            self.Add_Loc_LE.text()                              != "",
            self.Add_Motion_Path_LE.text()                      != "",
            self.MainWindow.Cam_Item_Widget.Attr["Add_Crv_LE"]  != "",
            cmds.objExists(self.Add_Crv_LE.text()),
            cmds.objExists(self.Add_Loc_LE.text()),
            cmds.objExists(self.Add_Motion_Path_LE.text()),
            
            # End_Time_Cehck = self.End_Time_SB.value() != 0,
            # Start_Time_Cehck = self.Strat_Time_SB.value() != 0,
            cmds.objExists(self.MainWindow.Cam_Item_Widget.Attr["Add_Crv_LE"]),
        ]
        if not Check_List[-1]:
            self.MainWindow.Cam_Item_Widget.Cam_Base_Layout.setStyleSheet("background:red")
        else:
            self.MainWindow.Cam_Item_Widget.Cam_Base_Layout.setStyleSheet("")
            
        if not cmds.objExists(self.Add_Crv_LE.text()): self.Add_Crv_LE.setText("")
        if not cmds.objExists(self.Add_Loc_LE.text()): self.Add_Crv_LE.setText("")
        if not cmds.objExists(self.Add_Crv_LE.text()): self.Add_Crv_LE.setText("")
        if not cmds.objExists(self.MainWindow.Cam_Item_Widget.Attr["Add_Crv_LE"]): self.MainWindow.Cam_Item_Widget.Attr["Add_Crv_LE"] = ""

        if False in Check_List:
            return False 
        else:
            return True

    def Position_Fn(self):
        if self.Check_Selection():
            Base_Curve = self.MainWindow.Cam_Item_Widget.Attr["Add_Crv_LE"]
            CamGrp = self.Add_CamGrp_LE.text()
            cmds.xform( CamGrp,cp=1 )
            cmds.delete(cmds.parentConstraint( Base_Curve,CamGrp ))
            Target_Curve = self.Add_Crv_LE.text()
            # Note 解除曲线的锁定
            cmds.setAttr("%s.tx" % Target_Curve,lock=False)
            cmds.setAttr("%s.ty" % Target_Curve,lock=False)
            cmds.setAttr("%s.tz" % Target_Curve,lock=False)
            cmds.setAttr("%s.rx" % Target_Curve,lock=False)
            cmds.setAttr("%s.ry" % Target_Curve,lock=False)
            cmds.setAttr("%s.rz" % Target_Curve,lock=False)
            cmds.delete(cmds.parentConstraint( Base_Curve,Target_Curve ))
            cmds.headsUpMessage(u"位置匹配完成")
        else:
            cmds.warning(u"物体不存在或没有选择")
            cmds.headsUpMessage(u"物体不存在或没有选择")

    def Keyframe_Fn(self):
        if self.Check_Selection():
            Path = self.Add_Motion_Path_LE.text()
            offset = cmds.keyframe(Path,q=1)[0]
            cmds.keyframe("%s_uValue"% Path,e=1,iub=1,r=1,o="over",tc=-offset)
        else:
            cmds.warning(u"物体不存在或没有选择")
            cmds.headsUpMessage(u"物体不存在或没有选择")

    def Add_CamGrp_Pick_Fun(self):
        self.Check_Selection()
        if len(cmds.ls(sl=True)) > 0:
            Selection = cmds.ls(sl=True,l=1)[0] 
            # SelectionShape = cmds.listRelatives(Selection)[0]
            SelectionType = cmds.nodeType( Selection )
            if SelectionType == "transform":
                self.Add_CamGrp_LE.setText(Selection)
                self.Current_Item.Cam_LE.setText(Selection)
                self.Cam_Name_Label.setText(u"<center> - %s - </center>" % Selection)
                try :
                    self.Add_CamGrp_Get.clicked.disconnect()
                except:
                    pass
                self.Add_CamGrp_Get.clicked.connect(partial(self.Select_OBJ_Fun,Selection))

                # Note 自动获取相关的物体
                TypeList =[
                    "motionPath",
                    "nurbsCurve",
                    "locator",
                ]

                FnList = [
                    self.Add_Motion_Path_Pick_Fun,
                    self.Add_Crv_Pick_Fun,
                    self.Add_Loc_Pick_Fun,
                ]

                SelectionList = cmds.listRelatives(Selection,f=1)
                for sel in SelectionList:
                    try:
                        SelectionShape = cmds.listRelatives(sel,f=1)
                        SelectionType = cmds.nodeType( SelectionShape[0] )
                    except:
                        break
                    for i,Type in enumerate(TypeList):
                        if SelectionType == Type:
                            cmds.select(sel)
                            FnList[i]()
                            break

                self.Current_Item.Attr["Add_CamGrp_LE"] = self.Add_CamGrp_LE.text()
            else:
                cmds.warning(u"请选择组进行获取")
                cmds.headsUpMessage(u"请选择组进行获取")
        else :
            self.Add_CamGrp_LE.setText("")
        
        if self.Add_CamGrp_LE.text() != "":
            self.Current_Item.Attr["Add_CamGrp_LE"] = self.Add_CamGrp_LE.text()
            self.Add_CamGrp_Label.setVisible(False)
            self.Add_CamGrp_Get.setVisible(True)
        else:
            self.Add_CamGrp_Label.setVisible(True)
            self.Add_CamGrp_Get.setVisible(False)
        
        self.MainWindow.Save_Json_Fun()

    def Add_Motion_Path_Pick_Fun(self):
        self.Check_Selection()
        if len(cmds.ls(sl=True)) > 0:
            Selection = cmds.ls(sl=True,l=1)[0] 
            # SelectionShape = cmds.listRelatives(Selection)[0]
            SelectionType = cmds.nodeType( Selection )
            if SelectionType == "motionPath":
                self.Add_Motion_Path_LE.setText(Selection)
                try :
                    self.Add_Motion_Path_Get.clicked.disconnect()
                except:
                    pass
                self.Add_Motion_Path_Get.clicked.connect(partial(self.Select_OBJ_Fun,Selection))
            else:
                cmds.warning(u"请选择motionPath进行获取")
                cmds.headsUpMessage(u"请选择motionPath进行获取")
        else :
            self.Add_Motion_Path_LE.setText("")
        
        if self.Add_Motion_Path_LE.text() != "":
            self.Current_Item.Attr["Add_Motion_Path_LE"] = self.Add_Motion_Path_LE.text()
            self.Add_Motion_Path_Label.setVisible(False)
            self.Add_Motion_Path_Get.setVisible(True)
        else:
            self.Add_Motion_Path_Label.setVisible(True)
            self.Add_Motion_Path_Get.setVisible(False)

        self.MainWindow.Save_Json_Fun()
        

    def Add_Crv_Pick_Fun(self):
        self.Check_Selection()
        if len(cmds.ls(sl=True)) > 0:
            Selection = cmds.ls(sl=True,l=1)[0] 
            SelectionShape = cmds.listRelatives(Selection,pa=1)[0]
            SelectionType = cmds.nodeType( SelectionShape )
            if SelectionType == "nurbsCurve":
                self.Add_Crv_LE.setText(Selection)
                try :
                    self.Add_Crv_Get.clicked.disconnect()
                except:
                    pass
                self.Add_Crv_Get.clicked.connect(partial(self.Select_OBJ_Fun,Selection))

                # Note 自动识别MotionPath
                MotionPath = cmds.listConnections(SelectionShape,type="motionPath")[0]
                cmds.select(MotionPath)
                self.Add_Motion_Path_Pick_Fun()

            else:
                cmds.warning(u"请选择NurbsCurve进行获取")
                cmds.headsUpMessage(u"请选择NurbsCurve进行获取")
        else :
            self.Add_Crv_LE.setText("")
        
        if self.Add_Crv_LE.text() != "":
            self.Current_Item.Attr["Add_Crv_LE"] = self.Add_Crv_LE.text()
            self.Add_Crv_Label.setVisible(False)
            self.Add_Crv_Get.setVisible(True)
        else:
            self.Add_Crv_Label.setVisible(True)
            self.Add_Crv_Get.setVisible(False)

        self.MainWindow.Save_Json_Fun()
        

    def Add_Loc_Pick_Fun(self):
        self.Check_Selection()
        if len(cmds.ls(sl=True)) > 0 :
            Selection = cmds.ls(sl=True,l=1)[0] 
            SelectionShape = cmds.listRelatives(Selection,pa=1)[0]
            SelectionType = cmds.nodeType( SelectionShape )
            if SelectionType == "locator":
                self.Add_Loc_LE.setText(Selection)
                try :
                    self.Add_Loc_Get.clicked.disconnect()
                except:
                    pass
                self.Add_Loc_Get.clicked.connect(partial(self.Select_OBJ_Fun,Selection))
            else:
                cmds.warning(u"请选择Locator进行获取")
                cmds.headsUpMessage(u"请选择Locator进行获取")
        else :
            self.Add_Loc_LE.setText("")
        
        if self.Add_Loc_LE.text() != "":
            self.Current_Item.Attr["Add_Loc_LE"] = self.Add_Loc_LE.text()
            self.Add_Loc_Label.setVisible(False)
            self.Add_Loc_Get.setVisible(True)
        else:
            self.Add_Loc_Label.setVisible(True)
            self.Add_Loc_Get.setVisible(False)

        self.MainWindow.Save_Json_Fun()


    def Cam_Input_Toggle_Fn(self):
        if self.Cam_Input_Toggle_Check:
            self.Cam_Input_Toggle_Check = False
            self.Cam_Input_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Cam_Input_Toggle_Anim.start()
            self.Cam_Input_Toggle.setText(u"▼输入设置")
            self.Cam_Input_Toggle.setStyleSheet('font:normal')
        else:
            self.Cam_Input_Toggle_Check = True
            self.Cam_Input_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Cam_Input_Toggle_Anim.start()
            self.Cam_Input_Toggle.setText(u"■输入设置")
            self.Cam_Input_Toggle.setStyleSheet('font:bold')

        self.MainWindow.Save_Json_Fun()
        

    def Cam_Output_Toggle_Fn(self):
        if self.Cam_Output_Toggle_Check:
            self.Cam_Output_Toggle_Check = False
            self.Cam_Output_Toggle_Anim.setDirection(QAbstractAnimation.Forward)
            self.Cam_Output_Toggle_Anim.start()
            self.Cam_Output_Toggle.setText(u"▼输出设置")
            self.Cam_Output_Toggle.setStyleSheet('font:normal')
        else:
            self.Cam_Output_Toggle_Check = True
            self.Cam_Output_Toggle_Anim.setDirection(QAbstractAnimation.Backward)
            self.Cam_Output_Toggle_Anim.start()
            self.Cam_Output_Toggle.setText(u"■输出设置")
            self.Cam_Output_Toggle.setStyleSheet('font:bold')

        self.MainWindow.Save_Json_Fun()
        

    def Select_OBJ_Fun(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)