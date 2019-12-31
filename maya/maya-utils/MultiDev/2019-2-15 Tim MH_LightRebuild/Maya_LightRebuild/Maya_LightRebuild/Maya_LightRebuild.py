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
UI_PATH = os.path.join(DIR,"ui","Maya_LightRebuild.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

class Maya_LightRebuild(form_class,base_class):
    def __init__(self,dock="dock"):
        super(Maya_LightRebuild,self).__init__()
        self.setupUi(self)


        self.Light_Import_BTN.clicked.connect(self.Light_Import_BTN_Fun)

        self.Light_Export_BTN.clicked.connect(self.Light_Export_BTN_Fun)

        self.CB_List = [
            self.AreaLight_CB,
            self.DirectionalLight_CB,
            self.PointLight_CB,
            self.SpotLight_CB,
            self.aiAreaLight_CB,
            self.aiSkyDomeLight_CB,
        ]
        self.Light_Type = [
            "areaLight",
            "directionalLight",
            "pointLight",
            "spotLight",
            "aiSkyDomeLight",
            "aiAreaLight",
        ]

    def Light_Import_BTN_Fun(self):
        File_Path = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        # Note 空数组处理
        try:
            if type(File_Path) is tuple:
                File_Path = File_Path[0]
            if type(File_Path) is list:
                File_Path = File_Path[0]
        except:
            traceback.print_exc()
            return
        
        if not os.path.exists(File_Path):
            return

        Light_Json = {}          
        with open(File_Path,'r') as f:
            Light_Json = json.load(f)

        for lightName in Light_Json['LightData']:
            
            if cmds.objExists(lightName):
                continue

            lightNameData = Light_Json['LightData'][lightName]

            # Note 检查灯光的类型
            if lightNameData['Type'] == "pointLight":
                light = cmds.pointLight(n=lightName)
            elif lightNameData['Type'] == "spotLight":
                light = cmds.spotLight(n=lightName)
                cmds.setAttr(light+".coneAngle",lightNameData['coneAngle'])
                cmds.setAttr(light+".penumbraAngle",lightNameData['penumbraAngle'])
                cmds.setAttr(light+".dropoff",lightNameData['dropoff'])
            elif lightNameData['Type'] == "areaLight":
                light = cmds.shadingNode('areaLight',asLight=1, n=lightNameData['Name'])
            elif lightNameData['Type'] == "directionalLight":
                light = cmds.directionalLight(n=lightName)
            elif lightNameData['Type'] == "aiSkyDomeLight":
                try:
                    aiLight = mtoa.utils.createLocatorWithName("aiSkyDomeLight",lightName,asLight=True)
                except:
                    print "fail to build the aiSkyDomeLight - skip this light"
                    continue
                cmds.rename(aiLight[0],lightNameData['Name'])
            elif lightNameData['Type'] == "aiAreaLight":
                try:
                    aiLight = mtoa.utils.createLocatorWithName("aiAreaLight",lightName,asLight=True)
                except:
                    print "fail to build the aiAreaLight - skip this light"
                    continue
                cmds.rename(aiLight[0],lightNameData['Name'])

            R = lightNameData['color']['R']
            G = lightNameData['color']['G']
            B = lightNameData['color']['B']
            cmds.setAttr(lightNameData['Name']+".color",R,G,B,type="double3")

            cmds.setAttr(lightNameData['Name']+".intensity",lightNameData['Intensity'])
            cmds.setAttr(lightNameData['Name']+".aiExposure",lightNameData['Exposure'])

            tx = lightNameData['Translate']['tx']
            ty = lightNameData['Translate']['ty']
            tz = lightNameData['Translate']['tz']
            cmds.setAttr(lightName+".tx",tx)
            cmds.setAttr(lightName+".ty",ty)
            cmds.setAttr(lightName+".tz",tz)

            rx = lightNameData['Rotate']['rx']
            ry = lightNameData['Rotate']['ry']
            rz = lightNameData['Rotate']['rz']
            cmds.setAttr(lightName+".rx",rx)
            cmds.setAttr(lightName+".ry",ry)
            cmds.setAttr(lightName+".rz",rz)

            sx = lightNameData['Scale']['sx']
            sy = lightNameData['Scale']['sy']
            sz = lightNameData['Scale']['sz']
            cmds.setAttr(lightName+".sx",sx)
            cmds.setAttr(lightName+".sy",sy)
            cmds.setAttr(lightName+".sz",sz)

        QMessageBox.warning(self, u"Success", u"Json Import Success!")
        self.Save_Json_Fun()        

    def Light_Export_BTN_Fun(self):
        File_Path = QFileDialog.getSaveFileName(self, caption=u"1", directory=".",filter="json (*.json)") 
        # Note 空数组处理
        try:
            if type(File_Path) is tuple:
                File_Path = File_Path[0]
            if type(File_Path) is list:
                File_Path = File_Path[0]
        except:
            traceback.print_exc()
            return

        Light_Json = {}
        Light_Json['Generate_Application'] = "Maya"
        Light_Json['LightData'] = {}
        
        lightList = cmds.ls(type='lightList')[0]
        lightList = cmds.listConnections( lightList + ".lights")

        selList = cmds.ls(sl=1)
        # Note 如果有选择的物体则将物体加入到数组当中
        if len(selList) > 0 :
            tempLightList = [sel for sel in selList if sel in lightList]
            lightList = tempLightList

        for lightName in lightList:
            # Note 如果灯光不可见则取消显示
            if cmds.getAttr(lightName+".visibility") == 0:
                continue
            
            light = cmds.listRelatives( lightName, c=1 )[0]
            if not self.CB_Check(cmds.objectType(light)):
                continue

            Light_Json['LightData'][lightName]                    = {}
            Light_Json['LightData'][lightName]['Name']            = light
            Light_Json['LightData'][lightName]['Type']            = cmds.objectType(light)
            Light_Json['LightData'][lightName]['Intensity']       = cmds.getAttr(light+".intensity")
            try:
                Light_Json['LightData'][lightName]['Exposure']    = cmds.getAttr(light+".aiExposure")
            except:
                print "fail to export the aiExposure attribute - skip this attribute"
            Light_Json['LightData'][lightName]['color']           = {}
            Light_Json['LightData'][lightName]['color']["R"]      = cmds.getAttr(light+".color")[0][0]
            Light_Json['LightData'][lightName]['color']["G"]      = cmds.getAttr(light+".color")[0][1]
            Light_Json['LightData'][lightName]['color']["B"]      = cmds.getAttr(light+".color")[0][2]
            # Note 获取世界坐标
            Translate = cmds.xform(q=1,ws=1,a=1,t=1)
            Light_Json['LightData'][lightName]['Translate']       = {}
            Light_Json['LightData'][lightName]['Translate']['tx'] = Translate[0]
            Light_Json['LightData'][lightName]['Translate']['ty'] = Translate[1]
            Light_Json['LightData'][lightName]['Translate']['tz'] = Translate[2]
            Rotate = cmds.xform(q=1,ws=1,a=1,ro=1)
            Light_Json['LightData'][lightName]['Rotate']          = {}
            Light_Json['LightData'][lightName]['Rotate']['rx']    = Rotate[0]
            Light_Json['LightData'][lightName]['Rotate']['ry']    = Rotate[1]
            Light_Json['LightData'][lightName]['Rotate']['rz']    = Rotate[2]
            Scale = cmds.xform(q=1,ws=1,a=1,s=1)
            Light_Json['LightData'][lightName]['Scale']           = {}
            Light_Json['LightData'][lightName]['Scale']['sx']     = Scale[0]
            Light_Json['LightData'][lightName]['Scale']['sy']     = Scale[1]
            Light_Json['LightData'][lightName]['Scale']['sz']     = Scale[2]
            if cmds.objectType(light) == "spotLight" :
                Light_Json['LightData'][lightName]['coneAngle']     = cmds.getAttr(light+".coneAngle")
                Light_Json['LightData'][lightName]['penumbraAngle'] = cmds.getAttr(light+".penumbraAngle")
                Light_Json['LightData'][lightName]['dropoff']       = cmds.getAttr(light+".dropoff")

        try:
            with open(File_Path,'w') as f:
                json.dump(Light_Json,f,indent=4)
            QMessageBox.warning(self, u"Success", u"Json Export Success!")
            
        except:
            QMessageBox.warning(self, u"Warning", u"Fail to export the Json file")
        self.Save_Json_Fun()        
    
    

    def CB_Check(self,objectType):
        for i,CB in enumerate(self.CB_List):
            if CB.isChecked() == True:
                continue
            else:
                if objectType == self.Light_Type[i]:
                    return False

        return True

    def Save_Json_Fun(self,path=GUI_STATE_PATH):
        GUI_STATE = {}
        GUI_STATE['aiSkyDomeLight_CB'] = self.aiSkyDomeLight_CB.isChecked()
        GUI_STATE['DirectionalLight_CB'] = self.DirectionalLight_CB.isChecked()
        GUI_STATE['AreaLight_CB'] = self.AreaLight_CB.isChecked()
        GUI_STATE['PointLight_CB'] = self.PointLight_CB.isChecked()
        GUI_STATE['SpotLight_CB'] = self.SpotLight_CB.isChecked()
        GUI_STATE['aiAreaLight_CB'] = self.aiAreaLight_CB.isChecked()
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
            self.aiSkyDomeLight_CB.setChecked(GUI_STATE['aiSkyDomeLight_CB'])
            self.DirectionalLight_CB.setChecked(GUI_STATE['DirectionalLight_CB'])
            self.AreaLight_CB.setChecked(GUI_STATE['AreaLight_CB'])
            self.PointLight_CB.setChecked(GUI_STATE['PointLight_CB'])
            self.SpotLight_CB.setChecked(GUI_STATE['SpotLight_CB'])
            self.aiAreaLight_CB.setChecked(GUI_STATE['aiAreaLight_CB'])
    
            return True
        else:
    
            if load==True:
                QMessageBox.warning(self, u"Warning", u"加载失败\n检查路径是否正确")
                return False
