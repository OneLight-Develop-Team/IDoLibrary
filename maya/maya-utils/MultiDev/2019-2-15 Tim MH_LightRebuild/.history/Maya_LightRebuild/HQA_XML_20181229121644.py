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
UI_PATH = os.path.join(DIR,"ui","HQA_XML.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

class HQA_XML(form_class,base_class):

    def __init__(self,dock="dock"):
        super(HQA_XML,self).__init__()
        self.setupUi(self)

        self.HQA_XML_BTN.clicked.connect(self.HQA_XML_BTN_Fun)

    def HQA_XML_BTN_Fun(self):
        # TODO test
        File_Path = QFileDialog.getSaveFileName(self, caption=u"1", directory=".",filter="hqa (*.hqa)") 
        # 空数组处理
        try:
            if type(File_Path) is tuple:
                File_Path = File_Path[0]
            if type(File_Path) is list:
                File_Path = File_Path[0]
        except:
            traceback.print_exc()
            return

        import xml.dom.minidom
        doc = xml.dom.minidom.Document() 
        HQA = doc.createElement('HQA')
        doc.appendChild(HQA)
        HQA.setAttribute('version', '1.0.0') 

        # 查询所有 Trasnform 节点
        TransformList = cmds.ls(type="transform",sl=1)

        # 如果没有选择则导出全部
        if len(TransformList) == 0:
            TransformList = cmds.ls(type="transform")


        cmds.progressWindow(	title=u'导出hqa',
					progress=0,
					status=u'导出hqa文件中...',
					isInterruptable=True )

        amount = 0.0

        try:
            for Transform in TransformList:
                # 查询关键信息
                KeyframeCheck = cmds.keyframe(Transform,q=1)

                # 进度条显示
                if cmds.progressWindow( query=True, isCancelled=True ) :
                    cmds.progressWindow(endProgress=1)
                    return
                
                amount += 1.0
                cmds.progressWindow( edit=True, progress=amount/len(TransformList)*100 )

                if KeyframeCheck:
                    # 获取关键帧属性
                    AnimCurveList = cmds.keyframe(Transform,q=1,n=1)
                    dagNode = doc.createElement('dagNode')
                    HQA.appendChild(dagNode)
                    dagNode.setAttribute('name',    Transform)
                    dagNode.setAttribute('uid',     cmds.ls(Transform,uid=1)[0])
                    # dagNode.setAttribute('parent',  cmds.listRelatives(Transform,p=1)[0])
                    dagNode.setAttribute('path',    cmds.ls(Transform,l=1 )[0])
                    animData = doc.createElement('animData')
                    dagNode.appendChild(animData)
                    for Curve in AnimCurveList:
                        animCurve = doc.createElement("animCruve")
                        animData.appendChild(animCurve)
                        animCurve.setAttribute('name',  Curve)
                        animCurve.setAttribute('uid',   cmds.ls(Curve,uid=1)[0])
                        FrameList = cmds.keyframe(Curve,q=1)
                        ValueList = cmds.keyframe(Curve,q=1,vc=1)
                        for i in range(len(FrameList)):
                            KeyframeTag = doc.createElement("keyframe")
                            animCurve.appendChild(KeyframeTag)
                            KeyframeTag.setAttribute('index', str(FrameList[i]))
                            KeyframeTag.setAttribute('value', str(ValueList[i]))
                            
        except:
            traceback.print_exc()
            cmds.progressWindow(endProgress=1)

        cmds.progressWindow(endProgress=1)

        with open(File_Path, 'w') as f:
            doc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")

        QMessageBox.warning(self, u"Warning", u"导出成功")
        self.Save_Json_Fun()        
    
    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['DOCK'] = self.DOCK
    
        try:
            with open(path,'w') as f:
                json.dump(GUI_STATE,f,indent=4)
        except:
            if path != "": 
                QMessageBox.warning(self, u"Warning", u"空路径读取失败")
    
    def Load_Json_Fun(self,path=GUI_STATE_PATH,load=False):
        if os.path.exists(path):
            GUI_STATE = {}          
            with open(path,'r') as f:
                GUI_STATE = json.load(f)
    
            return True
        else:
    
            if load==True:
                
                QMessageBox.warning(self, u"Warning", u"导入失败")
                return False
            