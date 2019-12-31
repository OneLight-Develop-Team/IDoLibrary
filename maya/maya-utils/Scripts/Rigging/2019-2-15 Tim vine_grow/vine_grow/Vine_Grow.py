# -*- coding:utf-8 -*-
import os
import json
import traceback
from functools import partial
from maya import OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
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
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from UI_Interface import Interface

DIR_PATH = os.path.dirname(__file__)
GUI_STATE_PATH = os.path.join(DIR_PATH,"json",'GUI_STATE.json')

# 主功能
class Vine_Grow(Interface):
    def __init__(self,dock="dock"):
        super(Vine_Grow,self).__init__(dock=dock)

        self.Loc_Generate_Btn.clicked.connect(self.Loc_Generate)
        self.Switch_Btn.clicked.connect(self.Jnt_Switch)
        self.Rig_Generate_Btn.clicked.connect(self.Rig_Generate)
        self.Rig_Back_Btn.clicked.connect(self.Rig_Back)

        # 窗口设置按钮功能
        self.Dock_Btn.clicked.connect(partial(self.Dockable_Window_Fun,dock="dock"))
        self.Undock_Btn.clicked.connect(partial(self.Dockable_Window_Fun,dock="undock"))

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            self.Workspace_Btn.clicked.connect(partial(self.Dockable_Window_Fun,dock="workspace"))
        else:
            self.Workspace_Btn.setEnabled(False)

        self.Default_Setting_Btn.clicked.connect(partial(self.Dockable_Window_Fun,save=False))

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
            
        global Vine_Grow_UI 
        Vine_Grow_UI = Vine_Grow(dock=dock)
        Vine_Grow_UI.show()
        
    def Loc_Generate(self):
        cmds.select(self.Rig_Obj_Text.text())
        boundingBox = cmds.polyEvaluate( boundingBox=True )

        x = (boundingBox[0][0] + boundingBox[0][1])/2
        y = (boundingBox[1][0] + boundingBox[1][1])/2
        z = (boundingBox[2][0] + boundingBox[2][1])/2

        if self.X_RadioButton.isChecked():
            cmds.spaceLocator( p=(boundingBox[0][0], y, z) )
            cmds.CenterPivot()
            self.Get_Start_JNT()
            cmds.spaceLocator( p=(boundingBox[0][1], y, z) )
            cmds.CenterPivot()
            self.Get_End_JNT()
        if self.Y_RadioButton.isChecked():
            cmds.spaceLocator( p=(x, boundingBox[1][0], z) )
            cmds.CenterPivot()
            self.Get_Start_JNT()
            cmds.spaceLocator( p=(x, boundingBox[1][1], z) )
            cmds.CenterPivot()
            self.Get_End_JNT()
        if self.Z_RadioButton.isChecked():
            cmds.spaceLocator( p=(x, y , boundingBox[2][0]) )
            cmds.CenterPivot()
            self.Get_Start_JNT()
            cmds.spaceLocator( p=(x, y , boundingBox[2][1]) )
            cmds.CenterPivot()
            self.Get_End_JNT()
        
    def Rig_Obj_Check(self):
        Rig_Check = False
        try:
            cmds.select(self.End_JNT)
        except Exception:
            self.End_JNT_Text.setText("")
            self.End_JNT_GetBtn.setVisible(False)
            self.End_JNT_Label.setVisible(True)
            cmds.headsUpMessage( u'结束参考节点不存在！！！' )
            cmds.warning( u'结束参考节点不存在！！！' )
            Rig_Check = True
        try:
            cmds.select(self.Start_JNT)
        except Exception:
            self.Start_JNT_Text.setText("")
            self.Start_JNT_GetBtn.setVisible(False)
            self.Start_JNT_Label.setVisible(True)
            cmds.headsUpMessage( u'起始参考节点不存在！！！' )
            cmds.warning( u'起始参考节点不存在！！！' )
            Rig_Check = True

        try:
            cmds.select(self.Rig_Obj)
        except Exception:
            self.Rig_Obj_Text.setText("")
            self.Rig_Obj_GetBtn.setVisible(False)
            self.Rig_Obj_Label.setVisible(True)
            cmds.headsUpMessage( u'绑定的模型不存在！！！' )
            cmds.warning( u'绑定的模型不存在！！！' )
            Rig_Check = True

        return Rig_Check

    def Jnt_Switch(self):

        if self.Rig_Obj_Check():
            return
            
        temp_JNT = self.Start_JNT
        cmds.select(self.End_JNT)
        self.Get_Start_JNT()
        cmds.select(temp_JNT)
        self.Get_End_JNT()
        cmds.select(cl=True)

    # 一键生成按钮
    def Rig_Generate(self):
        
        ############################################## 
        ##########     检查物体是否存在    ############ 
        ############################################## 

        if self.Rig_Obj_Check():
            return

        # 开启还原按钮
        self.Rig_Back_Btn.setEnabled(True)

        ############################################## 
        #############      获取变量     ############### 
        ############################################## 

        # 获取数值
        Main_JNT_Num = int(self.Main_JNT_Num.text()) if self.Main_JNT_Num.text() != "" else 20
        IK_JNT_Num = int(self.IK_JNT_Num.text()) if self.IK_JNT_Num.text() != "" else 20
        Curve_Span_Num = int(self.Curve_Span_Num.text()) if self.Curve_Span_Num.text() != "" else 20

        # 获取命名
        Geo_Name_Text = self.Geo_Name_Text.text() if self.Geo_Name_Text.text() != "" else "TengMan"
        Main_JNT_Name_Text = self.Main_JNT_Name_Text.text() if self.Main_JNT_Name_Text.text() != "" else "gan_joint"
        IK_JNT_Name_Text = self.IK_JNT_Name_Text.text() if self.IK_JNT_Name_Text.text() != "" else "ganJoint"
        Curve_Name_Text = self.Curve_Name_Text.text() if self.Curve_Name_Text.text() != "" else "gan"
        IK_CTRL_Name_Text = self.IK_CTRL_Name_Text.text() if self.IK_CTRL_Name_Text.text() != "" else "gan_ctrl"
        Start_Ctrl_Text = self.Start_Ctrl_Text.text() if self.Start_Ctrl_Text.text() != "" else "main2"
        End_IK_Text = self.End_IK_Text.text() if self.End_IK_Text.text() != "" else "main"
        Character_Ctrl_Text = self.Character_Ctrl_Text.text() if self.Character_Ctrl_Text.text() != "" else "Character"

        # 获取按钮颜色
        styleSheet = self.IK_CTRL_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])/255
        g = float(styleSheet[1])/255
        b = float(styleSheet[2].split(")")[0])/255
        IK_CTRL_ColorBtn = (r,g,b)

        styleSheet = self.Start_Ctrl_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])/255
        g = float(styleSheet[1])/255
        b = float(styleSheet[2].split(")")[0])/255
        Start_Ctrl_ColorBtn = (r,g,b)

        styleSheet = self.End_IK_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])/255
        g = float(styleSheet[1])/255
        b = float(styleSheet[2].split(")")[0])/255
        End_IK_ColorBtn = (r,g,b)

        styleSheet = self.Character_Ctrl_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])/255
        g = float(styleSheet[1])/255
        b = float(styleSheet[2].split(")")[0])/255
        Character_Ctrl_ColorBtn = (r,g,b)

        ############################################## 
        ###############      绑定      ############### 
        ############################################## 

        # 获取起始节点和结束节点坐标
        

        cmds.select(self.Start_JNT)
        Start_JNT_Coordinate = cmds.xform(q=True,a=True,ws=True,piv=True)

        cmds.select(self.End_JNT)
        
        End_JNT_Coordinate = cmds.xform(q=True,a=True,ws=True,piv=True)
        cmds.select(cl=True)

        

        # 批量生成主关节
        Xdistance = End_JNT_Coordinate[0] - Start_JNT_Coordinate[0]
        Ydistance = End_JNT_Coordinate[1] - Start_JNT_Coordinate[1]
        Zdistance = End_JNT_Coordinate[2] - Start_JNT_Coordinate[2]

        # 主控制器
        cmds.circle( nr=(Xdistance, Ydistance, Zdistance), c=(End_JNT_Coordinate[0], End_JNT_Coordinate[1], End_JNT_Coordinate[2]),n=End_IK_Text,r=1)
        Main_Ctrl = cmds.ls(sl=True)[0]
        cmds.setAttr(Main_Ctrl + ".overrideEnabled",1)

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            cmds.setAttr(Main_Ctrl + ".overrideRGBColors",1)
            cmds.setAttr(Main_Ctrl + ".overrideColorRGB",End_IK_ColorBtn[0],End_IK_ColorBtn[1],End_IK_ColorBtn[2])
        else:
            cmds.setAttr( Main_Ctrl +".overrideRGBColors",0)
            cmds.setAttr( Main_Ctrl +".overrideColor",self.End_IK_ColorSlider.value())
            
        
        cmds.setAttr(Main_Ctrl+".visibility",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main_Ctrl+".sx",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main_Ctrl+".sy",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main_Ctrl+".sz",lock=True,keyable=False,channelBox=False)
        cmds.addAttr(ln="show_mod",at="double",min=0,max=1,dv=1)
        cmds.setAttr(Main_Ctrl+".show_mod",edit=True,keyable=True)
        cmds.addAttr(ln="grow",at="double",min=0,max=10,dv=10)

        for Main_JNT in range(Main_JNT_Num):
            x = Xdistance * Main_JNT / (Main_JNT_Num-1) + Start_JNT_Coordinate[0]
            y = Ydistance * Main_JNT / (Main_JNT_Num-1) + Start_JNT_Coordinate[1]
            z = Zdistance * Main_JNT / (Main_JNT_Num-1) + Start_JNT_Coordinate[2]
            JNT = cmds.joint( p=(x, y, z), n = Main_JNT_Name_Text + str(Main_JNT+1))
            cmds.setAttr( JNT + ".tx", k=False,cb=True )
            cmds.setAttr( JNT + ".ty", k=False,cb=True )
            cmds.setAttr( JNT + ".tz", k=False,cb=True )
            cmds.setAttr( JNT + ".rx", k=False,cb=True )
            cmds.setAttr( JNT + ".ry", k=False,cb=True )
            cmds.setAttr( JNT + ".rz", k=False,cb=True )
            cmds.setAttr( JNT + ".sx", k=False,cb=True )
            cmds.setAttr( JNT + ".sy", k=False,cb=True )
            cmds.setAttr( JNT + ".sz", k=False,cb=True )
            cmds.setAttr( JNT + ".visibility", k=False,cb=True  )
            cmds.expression( s=JNT + ".sx = "+ Main_Ctrl +".grow/10/"+str(Main_JNT+1) )
            cmds.expression( s=JNT + ".sy = "+ Main_Ctrl +".grow/10/"+str(Main_JNT+1) )
            cmds.expression( s=JNT + ".sz = "+ Main_Ctrl +".grow/10/"+str(Main_JNT+1) )
            if Main_JNT == 0:
                Start_Main_JNT = cmds.ls(sl=True)[0]

        # 生成IK控制器
        End_Main_JNT = cmds.ls(sl=True)
        cmds.select(Start_Main_JNT)
        cmds.select(End_Main_JNT,tgl=True)
        ikList = cmds.ikHandle(sol="ikSplineSolver" )
        
        # 生成控制器
        cmds.select(cl=True)
        CtrlList = []
        for IK_JNT in range(IK_JNT_Num):
            x = Xdistance * IK_JNT / (IK_JNT_Num-1) + Start_JNT_Coordinate[0]
            y = Ydistance * IK_JNT / (IK_JNT_Num-1) + Start_JNT_Coordinate[1]
            z = Zdistance * IK_JNT / (IK_JNT_Num-1) + Start_JNT_Coordinate[2]
            cmds.joint( p=(x, y, z), n = IK_JNT_Name_Text + str(IK_JNT+1))

            Curent_JNT = cmds.ls(sl=True)[0]

            IK_JNT_Coordinate = cmds.xform(q=True,ws=True,t=True)

            cmds.circle( nr=(Xdistance, Ydistance, Zdistance), c=(IK_JNT_Coordinate[0], IK_JNT_Coordinate[1], IK_JNT_Coordinate[2]),n=IK_CTRL_Name_Text+str(IK_JNT+1),r=0.4)

            IK_Ctrl = cmds.ls(sl=True)[0]

            cmds.setAttr( IK_Ctrl +".overrideEnabled",1)

            if mel.eval("getApplicationVersionAsFloat;")>=2017:
                cmds.setAttr( IK_Ctrl +".overrideRGBColors",1)
                cmds.setAttr( IK_Ctrl +".overrideColorRGB",IK_CTRL_ColorBtn[0],IK_CTRL_ColorBtn[1],IK_CTRL_ColorBtn[2])
            else:
                cmds.setAttr( IK_Ctrl +".overrideRGBColors",0)
                cmds.setAttr( IK_Ctrl +".overrideColor",self.IK_CTRL_ColorSlider.value())

            cmds.CenterPivot()
            # 冻结变换
            cmds.makeIdentity( apply=True, t=1, r=1, s=1, n=2 )

            CtrlList.append(cmds.ls(sl=True)[0])

            cmds.parentConstraint( CtrlList[IK_JNT] , Curent_JNT )

            cmds.select(Curent_JNT)
            cmds.setAttr( Curent_JNT + ".tx", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".ty", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".tz", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".rx", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".ry", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".rz", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".sx", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".sy", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".sz", k=False,cb=True )
            cmds.setAttr( Curent_JNT + ".visibility", k=False,cb=True )

            if IK_JNT == 0:
                Start_IK_JNT = cmds.ls(sl=True)[0]

        
        # 将IK关节蒙皮到曲线上
        cmds.select(ikList[2])
        cmds.rebuildCurve( rt=0, s=Curve_Span_Num )
        cmds.select(Start_IK_JNT,hi=True)
        cmds.select(ikList[2],tgl=True)
        # 绑定设置
        cmds.optionVar(iv=('bindTo',2))
        cmds.optionVar(iv=('skinMethod',1))
        cmds.optionVar(iv=('multipleBindPosesOpt',1))
        cmds.optionVar(iv=('bindMethod',1))
        cmds.optionVar(iv=('removeUnusedInfluences',0))
        cmds.optionVar(iv=('colorizeSkeleton',0))
        cmds.optionVar(iv=('maxInfl',3))
        cmds.optionVar(iv=('normalizeWeights',2))
        cmds.optionVar(iv=('obeyMaxInfl',2))

        cmds.SmoothBindSkin()

        # 绑定主物体
        cmds.select(Start_Main_JNT,hi=True)
        cmds.select(self.Rig_Obj,tgl=True)
        cmds.SmoothBindSkin()

        ############################################## 
        #############      管理层级     ############### 
        ##############################################
        # 删除参考
        if self.Delete_CheckBox.isChecked():
            cmds.delete(self.Start_JNT)
            cmds.delete(self.End_JNT)
        
        # 模型打组
        cmds.select(self.Rig_Obj)
        Geo_Grp = cmds.group(n=Geo_Name_Text+"_geo")
        
        # 控制器打组
        CtrlList = list(reversed(CtrlList))
        Grp = ""
        for Ctrl in CtrlList:
            cmds.select(Ctrl)
            cmds.group(n=Ctrl+"_C")
            IKFKC_Grp = cmds.group(n=Ctrl+"_IKFKC")
            if Grp != "":
                cmds.parent( Grp, IKFKC_Grp )
            cmds.select(IKFKC_Grp)
            Grp = cmds.group(n=Ctrl+"_G")

        # MotionSystem 打组
        cmds.select(Start_IK_JNT)
        temp = cmds.group(n=Start_IK_JNT+"_G")
        cmds.setAttr(temp+".visibility",0)
        cmds.setAttr(temp+".visibility",lock=True)
        cmds.setAttr( temp + ".tx", lock=True )
        cmds.setAttr( temp + ".ty", lock=True )
        cmds.setAttr( temp + ".tz", lock=True )
        cmds.setAttr( temp + ".rx", lock=True )
        cmds.setAttr( temp + ".ry", lock=True )
        cmds.setAttr( temp + ".rz", lock=True )
        cmds.setAttr( temp + ".sx", lock=True )
        cmds.setAttr( temp + ".sy", lock=True )
        cmds.setAttr( temp + ".sz", lock=True )
        cmds.select(Grp,tgl=True)
        MotionSystem_Grp = cmds.group(n="MotionSystem")

        
        # DeformationSystem 打组
        cmds.select(Start_Main_JNT)
        Start_Main_JNT_Grp = cmds.group(n=Start_Main_JNT+"_G")
        cmds.setAttr( Start_Main_JNT_Grp+".visibility",0)
        cmds.setAttr( Start_Main_JNT_Grp+".visibility",lock=True)
        cmds.setAttr( Start_Main_JNT_Grp + ".tx", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".ty", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".tz", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".rx", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".ry", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".rz", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".sx", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".sy", lock=True )
        cmds.setAttr( Start_Main_JNT_Grp + ".sz", lock=True )
        DeformationSystem_Grp = cmds.group(n="DeformationSystem")

        # 主控制器打组
        cmds.circle( nr=(Xdistance, Ydistance, Zdistance), c=(Start_JNT_Coordinate[0], Start_JNT_Coordinate[1], Start_JNT_Coordinate[2]),n=Start_Ctrl_Text,r=1)

        Main2_Ctrl = cmds.ls(sl=True)[0]

        cmds.setAttr(Main2_Ctrl + ".overrideEnabled",1)
        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            cmds.setAttr(Main2_Ctrl + ".overrideRGBColors",1)
            cmds.setAttr(Main2_Ctrl + ".overrideColorRGB",Start_Ctrl_ColorBtn[0],Start_Ctrl_ColorBtn[1],Start_Ctrl_ColorBtn[2])
        else:
            cmds.setAttr( Main2_Ctrl +".overrideRGBColors",0)
            cmds.setAttr( Main2_Ctrl +".overrideColor",self.Start_Ctrl_ColorSlider.value())

        

        cmds.setAttr(Main2_Ctrl+".visibility",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main2_Ctrl+".sx",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main2_Ctrl+".sy",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(Main2_Ctrl+".sz",lock=True,keyable=False,channelBox=False)

        cmds.select(DeformationSystem_Grp)
        cmds.select(MotionSystem_Grp,tgl=True)
        cmds.select(Main2_Ctrl,tgl=True)
        cmds.parent()

        cmds.pickWalk( direction='up' )
        Main2_Ctrl = cmds.ls(sl=True)[0]
        Main2_Ctrl_C = cmds.group(n=Main2_Ctrl+"_C")
        Main2_Ctrl_G = cmds.group(n=Main2_Ctrl+"_G")
        Main2_Ctrl = cmds.ls(sl=True)[0]

        cmds.setAttr(Main_Ctrl+".grow",edit=True,keyable=True)
        cmds.connectAttr(Main_Ctrl+".show_mod",Geo_Grp+".visibility")
        cmds.parent(Main2_Ctrl,Main_Ctrl)
        cmds.pickWalk( direction='up' )
        cmds.group(n=Main_Ctrl+"_C")
        cmds.group(n=Main_Ctrl+"_G")

        Main_Ctrl_G = cmds.ls(sl=True)[0]

        cmds.curve(d=1, p=[(-1, 0,-1), (-1, 0,1), (1, 0, 1), (1,0, -1), (-1, 0,-1)], k=[0,1,2,3,4] ,n=Character_Ctrl_Text)

        Character = cmds.ls(sl=True)[0]
        cmds.setAttr(Character + ".overrideEnabled",1)

        if mel.eval("getApplicationVersionAsFloat;")>=2017:
            cmds.setAttr(Character + ".overrideRGBColors",1)
            cmds.setAttr(Character + ".overrideColorRGB",Character_Ctrl_ColorBtn[0],Character_Ctrl_ColorBtn[1],Character_Ctrl_ColorBtn[2])
        else:
            cmds.setAttr( Character +".overrideRGBColors",0)
            cmds.setAttr( Character +".overrideColor",self.Character_Ctrl_ColorSlider.value())

        
        cmds.setAttr(Character+".visibility",lock=True,keyable=False,channelBox=False)
        cmds.xform(a=True,ws=True,t=(End_JNT_Coordinate[0], End_JNT_Coordinate[1], End_JNT_Coordinate[2]))
        cmds.parent(Main_Ctrl_G,Character)
        cmds.pickWalk( direction='up' )
        cmds.group(n=Character+"_C")
        cmds.group(n=Character+"_G")
        Grp = cmds.group(n=Geo_Name_Text+"_rig")

        # 设置 other_G 中的属性
        cmds.setAttr(ikList[2]+".visibility",0)
        cmds.setAttr(ikList[2]+".visibility",lock=True,keyable=False,channelBox=False)
        cmds.setAttr(ikList[0]+".visibility",0)
        cmds.setAttr(ikList[0]+".visibility",lock=True)
        cmds.setAttr( ikList[0] + ".tx", lock=True )
        cmds.setAttr( ikList[0] + ".ty", lock=True )
        cmds.setAttr( ikList[0] + ".tz", lock=True )
        cmds.setAttr( ikList[0] + ".rx", lock=True )
        cmds.setAttr( ikList[0] + ".ry", lock=True )
        cmds.setAttr( ikList[0] + ".rz", lock=True )
        cmds.setAttr( ikList[0] + ".sx", lock=True )
        cmds.setAttr( ikList[0] + ".sy", lock=True )
        cmds.setAttr( ikList[0] + ".sz", lock=True )
        cmds.setAttr( ikList[0] + ".poleVectorX", lock=True )
        cmds.setAttr( ikList[0] + ".poleVectorY", lock=True )
        cmds.setAttr( ikList[0] + ".poleVectorZ", lock=True )
        cmds.setAttr( ikList[0] + ".offset", lock=True )
        cmds.setAttr( ikList[0] + ".roll", lock=True )
        cmds.setAttr( ikList[0] + ".twist", lock=True )
        cmds.setAttr( ikList[0] + ".ikBlend", lock=True )
        
        # 重命名曲线
        cmds.rename(ikList[2],Curve_Name_Text)
        # other_G 打组
        cmds.select(ikList[0])
        cmds.select(Curve_Name_Text,tgl=True)
        cmds.group(n="IK_G")
        cmds.group(n="other_G")
        cmds.pickWalk( direction='up' )
        cmds.select(Grp,tgl=True)
        cmds.parent()
        Other_Grp = cmds.pickWalk( direction='up' )

        cmds.select(Geo_Grp)
        self.Main_Grp = cmds.group(n=Geo_Name_Text+"_all")
        cmds.select(Other_Grp)
        cmds.select(self.Main_Grp,tgl=True)
        cmds.parent()

    def Rig_Back(self):
        self.Rig_Back_Btn.setEnabled(False)
        cmds.select(self.Rig_Obj)
        cmds.parent(w=True)
        cmds.delete(self.Main_Grp)
    
def main():
    # 检测不同的UI 全部删除
    global Vine_Grow_UI 

    try:
        if cmds.window(Vine_Grow_UI.undockWindow,query=True,exists=True) :
            cmds.deleteUI(Vine_Grow_UI.undockWindow)
    except:
        pass

    try:
        if cmds.dockControl(Vine_Grow_UI.dockControl,query=True,exists=True) :
            cmds.deleteUI(Vine_Grow_UI.dockControl)
    except:
        pass

    try:
        if cmds.workspaceControl(Vine_Grow_UI.workspaceCtrl,query=True,exists=True) :
            cmds.deleteUI(Vine_Grow_UI.workspaceCtrl)
    except:
        pass

    Vine_Grow_UI = Vine_Grow(dock="undock")
    Vine_Grow_UI.show()