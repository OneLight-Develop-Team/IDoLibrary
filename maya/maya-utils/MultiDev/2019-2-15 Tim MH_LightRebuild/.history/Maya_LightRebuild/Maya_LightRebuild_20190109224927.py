# -*- coding:utf-8 -*-

# Require Header
import os
import json
from functools import partial

# Sys Header
import sys
import traceback
import subprocess

from plugin.Qt.QtCore import *
from plugin.Qt.QtGui import *
from plugin.Qt.QtWidgets import *
from maya import cmds
import mtoa.utils

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

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","Maya_LightRebuild.ui") 
form_class , base_class = loadUiType(UI_PATH)

class Maya_LightRebuild(form_class,base_class):

    def __init__(self):
        super(Maya_LightRebuild,self).__init__()
        self.setupUi(self)
        self.Light_Import_BTN.clicked.connect(self.Light_Import_Fn)
        self.Light_Export_BTN.clicked.connect(self.Light_Export_Fn)
    
    def Light_Import_Fn(self):
        File_Path = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        # 空数组处理
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
            lightNameData = Light_Json['LightData'][lightName]

            if lightNameData['Type'] == "pointLight":
                light = cmds.pointLight(n=lightName)
            elif lightNameData['Type'] == "spotLight":
                light = cmds.spotLight(n=lightName)
                cmds.setAttr(light+".coneAngle",lightNameData['coneAngle'])
                cmds.setAttr(light+".penumbraAngle",lightNameData['penumbraAngle'])
                cmds.setAttr(light+".dropoff",lightNameData['dropoff'])
            elif lightNameData['Type'] == "areaLight":
                light = cmds.shadingNode('areaLight',asLight=1, n=lightNameData['Name'])
                # cmds.rename(light,lightNameData['Name'])
                # light = lightNameData['Name']
            elif lightNameData['Type'] == "directionalLight":
                light = cmds.directionalLight(n=lightName)
            elif lightNameData['Type'] == "aiSkyDomeLight":
                aiLight = mtoa.utils.createLocatorWithName("aiSkyDomeLight",lightName,asLight=True)
                rename(aiLight[1],lightNameData['Name'])
            elif lightNameData['Type'] == "aiAreaLight1":
                aiLight = mtoa.utils.createLocatorWithName("aiAreaLight",lightName,asLight=True)
                rename(aiLight[1],lightNameData['Name'])

            R = lightNameData['color']['R']
            G = lightNameData['color']['G']
            B = lightNameData['color']['B']
            try:
                cmds.setAttr(lightNameData['Name']+".color",R,G,B,type="double3")
            except:
                print light

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

            

    def Light_Export_Fn(self):
        File_Path = QFileDialog.getSaveFileName(self, caption=u"1", directory=".",filter="json (*.json)") 
        # 空数组处理
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
        Light_Json['Generate_Application'] = "Maya"
        Light_Json['LightData'] = {}

        lightList = cmds.ls(type='lightList')[0]
        lightList = cmds.listConnections( lightList + ".lights")
        for lightName in lightList:
            if cmds.getAttr(lightName+".visibility") == 0:
                continue
            light = cmds.listRelatives( lightName, c=1 )[0]
            Light_Json['LightData'][lightName]                    = {}
            Light_Json['LightData'][lightName]['Name']            = light
            Light_Json['LightData'][lightName]['Type']            = cmds.objectType(light)
            Light_Json['LightData'][lightName]['Intensity']       = cmds.getAttr(light+".intensity")
            Light_Json['LightData'][lightName]['Exposure']        = cmds.getAttr(light+".aiExposure")
            Light_Json['LightData'][lightName]['color']           = {}
            Light_Json['LightData'][lightName]['color']["R"]      = cmds.getAttr(light+".color")[0][0]
            Light_Json['LightData'][lightName]['color']["G"]      = cmds.getAttr(light+".color")[0][1]
            Light_Json['LightData'][lightName]['color']["B"]      = cmds.getAttr(light+".color")[0][2]
            Light_Json['LightData'][lightName]['Translate']       = {}
            Light_Json['LightData'][lightName]['Translate']['tx'] = cmds.getAttr(lightName+".tx")
            Light_Json['LightData'][lightName]['Translate']['ty'] = cmds.getAttr(lightName+".ty")
            Light_Json['LightData'][lightName]['Translate']['tz'] = cmds.getAttr(lightName+".tz")
            Light_Json['LightData'][lightName]['Rotate']          = {}
            Light_Json['LightData'][lightName]['Rotate']['rx']    = cmds.getAttr(lightName+".rx")
            Light_Json['LightData'][lightName]['Rotate']['ry']    = cmds.getAttr(lightName+".ry")
            Light_Json['LightData'][lightName]['Rotate']['rz']    = cmds.getAttr(lightName+".rz")
            Light_Json['LightData'][lightName]['Scale']           = {}
            Light_Json['LightData'][lightName]['Scale']['sx']     = cmds.getAttr(lightName+".sx")
            Light_Json['LightData'][lightName]['Scale']['sy']     = cmds.getAttr(lightName+".sy")
            Light_Json['LightData'][lightName]['Scale']['sz']     = cmds.getAttr(lightName+".sz")
            if cmds.objectType(light) == "spotLight" :
                Light_Json['LightData'][lightName]['coneAngle']     = cmds.getAttr(light+".coneAngle")
                Light_Json['LightData'][lightName]['penumbraAngle'] = cmds.getAttr(light+".penumbraAngle")
                Light_Json['LightData'][lightName]['dropoff']       = cmds.getAttr(light+".dropoff")


        try:
            with open(File_Path,'w') as f:
                json.dump(Light_Json,f,indent=4)
        except:
            if path != "": 
                QMessageBox.warning(self, u"Warning", u"空路径读取失败")
    
def main():
    ui = Maya_LightRebuild()
    ui.show()
    return ui