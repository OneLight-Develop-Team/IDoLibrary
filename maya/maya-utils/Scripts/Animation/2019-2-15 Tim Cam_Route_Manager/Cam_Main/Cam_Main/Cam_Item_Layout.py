# -*- coding:utf-8 -*-
# Require Header
import os
import json
from functools import partial

# Sys Header
import sys
import traceback
import subprocess

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
UI_PATH = os.path.join(DIR,"ui","Cam_Item_Layout.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

from maya import cmds

class Cam_Item_Layout(form_class,base_class):
    def __init__(self,MainWindow):
        super(Cam_Item_Layout,self).__init__()
        self.setupUi(self)
        self.MainWindow = MainWindow
        self.Item_Add_BTN.clicked.connect(self.Item_Add_Fn) 
        self.Item_Clear_BTN.clicked.connect(self.Item_Clear_Fn) 
        self.Cam_Item_Num = 0
        self.Cam_Item_Scroll.verticalScrollBar().valueChanged.connect(self.Scroll_Fn)
        self.Scroll_Offset = 0

        self.Attr = {}
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Add_CamGrp_LE"] = ""
        self.Attr["Add_Loc_LE"] = ""
        self.Attr["Name"] = ""

        # Note 功能按键
        self.Batch_Keyframe_BTN.clicked.connect(self.Batch_Keyframe_Fn)
        self.Select_Path_BTN.clicked.connect(self.Select_Path_Fn)
        self.Batch_Position_BTN.clicked.connect(self.Batch_Position_Fn)
        self.Batch_Constraint_BTN.clicked.connect(self.Batch_Constraint_Fn)

        # Note spliter
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)
        splitter.addWidget(self.Cam_Item_Scroll)
        splitter.addWidget(self.Button_Layout)
        num = len(self.VBox_Widget.children())
        self.VBox_Widget.layout().insertWidget(2,splitter)
        splitter.setSizes([1000,1])
    
    def Batch_Constraint_Fn(self):
        Cam_Grp = self.Attr["Add_CamGrp_LE"]
        Loc = self.Attr["Add_Loc_LE"]

        if not cmds.objExists(Cam_Grp): return
        if not cmds.objExists(Loc): return

        cmds.select(cl=1)
        cmds.select(Loc,add=1)

        ChildrenList = self.Item_Layout.children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                Cam_Loc = child.Attr["Add_Loc_LE"]
                if not cmds.objExists(Cam_Loc): continue
                cmds.select(Cam_Loc,add=1)
                child.Cam_Con_CB.setEnabled(True)

        cmds.select(Cam_Grp,add=1)
        orCns = cmds.orientConstraint(Loc,Cam_Grp,mo=0)[0]
        pnCns = cmds.pointConstraint(mo=0)[0]
        Attr_List = cmds.listAttr(pnCns,k=1,string="*W*")

        cmds.setAttr("%s.%s" % (pnCns,Attr_List[1]),1)
        for i,child in enumerate(ChildrenList):
            if i != 0:
                cmds.setAttr("%s.%s" % (pnCns,Attr_List[i+1]),0)
                try :
                    child.Cam_Con_CB.stateChanged.disconnect()
                except:
                    pass
                child.Cam_Con_CB.stateChanged.connect(partial(self.Cam_Con_CB_Fn,child,pnCns,Attr_List,i))

        self.Con_Keyframe_BTN.setEnabled(True)
        self.Con_Keyframe_BTN.clicked.connect(partial(self.Con_Keyframe_Fn,pnCns,Attr_List))
    
    def Cam_Con_CB_Fn(self,CB,pnCns,Attr_List,num,state):
        """
        Cam_Con_CB_Fn - CheckBox Signal
        
        # Note 复选框事件函数
        
        Arguments:
            CB {CheckBox} -- 复选框
            pnCns {ParenConstraint} -- 父子约束节点
            Attr_List {Attribute List} -- 父子约束节点下的属性列表
            num {number} -- 当前属性列表下的序号
            state {CheckBox state} -- 复选框的状态
        """ 
        
        ChildrenList = self.Item_Layout.children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                if child != CB:
                    child.Cam_Con_CB.blockSignals(True)
                    child.Cam_Con_CB.setChecked(False)
                    cmds.setAttr("%s.%s" % (pnCns,Attr_List[i+1]),0)

        if state == 2:
            CB.Cam_Con_CB.setChecked(True)
            cmds.setAttr("%s.%s" % (pnCns,Attr_List[num+1]),1)
            cmds.setAttr("%s.%s" % (pnCns,Attr_List[1]),0)
        else:
            CB.Cam_Con_CB.setChecked(False)
            cmds.setAttr("%s.%s" % (pnCns,Attr_List[num+1]),0)
            cmds.setAttr("%s.%s" % (pnCns,Attr_List[1]),1)

        for i,child in enumerate(ChildrenList):
            if i != 0:
                if child != CB:
                    child.Cam_Con_CB.blockSignals(False)

    def Con_Keyframe_Fn(self,pnCns,Attr_List):
        for i,Attr in enumerate(Attr_List):
            if i != 0:
                cmds.setKeyframe ("%s.%s" % (pnCns,Attr))

    def Batch_Position_Fn(self):

        ChildrenList = self.Item_Layout.children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                Base_Curve = self.Attr["Add_Crv_LE"]
                CamGrp = child.Attr["Add_CamGrp_LE"]
                if not cmds.objExists(Base_Curve): continue
                if not cmds.objExists(CamGrp): continue
                cmds.setAttr("%s.tx" % CamGrp,0)
                cmds.setAttr("%s.ty" % CamGrp,0)
                cmds.setAttr("%s.tz" % CamGrp,0)
                cmds.setAttr("%s.rx" % CamGrp,0)
                cmds.setAttr("%s.ry" % CamGrp,0)
                cmds.setAttr("%s.rz" % CamGrp,0)
                cmds.xform( CamGrp,cp=1 )
                cmds.delete(cmds.parentConstraint( Base_Curve,CamGrp ))
                Target_Curve = child.Attr["Add_Crv_LE"]
                if not cmds.objExists(Target_Curve): continue
                cmds.xform( Target_Curve,cp=1 )
                # Note 解除曲线的锁定
                cmds.setAttr("%s.tx" % Target_Curve,lock=False)
                cmds.setAttr("%s.ty" % Target_Curve,lock=False)
                cmds.setAttr("%s.tz" % Target_Curve,lock=False)
                cmds.setAttr("%s.rx" % Target_Curve,lock=False)
                cmds.setAttr("%s.ry" % Target_Curve,lock=False)
                cmds.setAttr("%s.rz" % Target_Curve,lock=False)
                cmds.delete(cmds.parentConstraint( Base_Curve,Target_Curve ))
                cmds.headsUpMessage(u"位置匹配完成")

    def Batch_Keyframe_Fn(self):
        ChildrenList = self.Item_Layout.children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                Path = child.Attr["Add_Motion_Path_LE"]
                if cmds.objExists(Path):
                    offset = cmds.keyframe(Path,q=1)[0] 
                    cmds.keyframe("%s.uValue"% Path,e=1,iub=1,r=1,o="over",tc=-offset)

    def Select_Path_Fn(self):
        cmds.select(cl=1)
        ChildrenList = self.Item_Layout.children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                if cmds.objExists(child.Attr["Add_Motion_Path_LE"]):
                    cmds.select(child.Attr["Add_Motion_Path_LE"],add=1)

        
    def Item_Add_Fn(self):
        self.Cam_Item_Num += 1
        return Cam_Item(self,self.MainWindow)
        
    def Item_Clear_Fn(self):
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Name"] = ""
        for i,child in enumerate(self.Item_Layout.children()):
            if i != 0:
                child.deleteLater()

    def Scroll_Fn(self):
        self.Scroll_Offset = self.Cam_Item_Scroll.verticalScrollBar().value()
        
UI_PATH = os.path.join(DIR,"ui","Cam_Item.ui") 
form_class , base_class = loadUiType(UI_PATH)

class Cam_Item(form_class,base_class):

    def __init__(self,parent,MainWindow):
        super(Cam_Item,self).__init__()
        self.setupUi(self)
        self.MainWindow = MainWindow
        self.Cam_Del_BTN.clicked.connect(self.Cam_Del_BTN_Fn)
        # self.Cam_Con_CB.stateChanged.connect(self.Cam_Con_CB_Fn)

        # Note 初始化创建参数
        TotalCount = len(parent.Item_Layout.children())
        parent.Item_Layout.layout().insertWidget(TotalCount-1,self)
        self.Cam_LE.setText("Cam_Item_%s" % parent.Cam_Item_Num)
        self.Cam_Num_Label.setText(u"镜头%s" % TotalCount)
        self.setObjectName("Cam_Item_%s" % TotalCount)
        self.Num = TotalCount
        self.Attr = {}
        self.Attr["Add_CamGrp_LE"] = ""
        self.Attr["Add_Loc_LE"] = ""
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Strat_Time_SB"] = 0
        self.Attr["End_Time_SB"] = 0
        self.MainWindow.Save_Json_Fun()

    def Cam_Del_BTN_Fn(self):
        self.deleteLater()
        ChildrenList = self.parent().children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                if i > self.Num:
                    # Note 修正 child 的序号
                    child.Num -= 1
                    child.Cam_Num_Label.setText(u"镜头%s" % (i-1))
                    child.setObjectName("Cam_Item_%s" % (i-1))
                else:
                    child.Cam_Num_Label.setText(u"镜头%s" % i)
                    child.setObjectName("Cam_Item_%s" % i)
        
        self.Attr["Add_CamGrp_LE"] = ""
        self.Attr["Add_Loc_LE"] = ""
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Strat_Time_SB"] = ""
        self.Attr["End_Time_SB"] = ""
        self.MainWindow.Save_Json_Fun()

    


        