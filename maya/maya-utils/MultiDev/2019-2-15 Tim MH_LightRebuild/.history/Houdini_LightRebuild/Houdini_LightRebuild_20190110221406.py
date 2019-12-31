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
import hou

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
UI_PATH = os.path.join(DIR,"ui","Houdini_LightRebuild.ui") 
form_class , base_class = loadUiType(UI_PATH)

class Houdini_LightRebuild(form_class,base_class):

    def __init__(self):
        super(Houdini_LightRebuild,self).__init__()
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

        ExistLightList = []
        Nodes = hou.node('/obj').glob('*')
        for node in Nodes:
            if node.type().name() == 'hlight::2.0':
                ExistLightList.append(node)
        
        for lightName in Light_Json['LightData']:
            lightNameData = Light_Json['LightData'][lightName]
            
            for ExistLight in ExistLightList:
                if ExistLight.name() == lightName:
                    print "skip - " + ExistLight.name()
                    continue

            Obj = hou.node("/obj")

            if lightNameData['Type'] == "aiAreaLight":
                Light = Obj.createNode("envlight", node_name=lightName)
            else:
                Light = Obj.createNode("hlight::2.0", node_name=lightName)

            if lightNameData['Type'] == "pointLight":
                Light.parm("light_type").set("point")
            elif lightNameData['Type'] == "spotLight":
                Light.parm("coneenable").set(True)
                Light.parm("coneangle").set(lightNameData['coneAngle'])
                Light.parm("conedelta").set(lightNameData['penumbraAngle'])
                Light.parm("coneroll").set(lightNameData['dropoff'])
            elif lightNameData['Type'] == "areaLight":
                Light.parm("light_type").set("grid")
            elif lightNameData['Type'] == "directionalLight":
                Light.parm("light_type").set("distant")
            elif lightNameData['Type'] == "aiAreaLight":
                Light.parm("light_type").set("grid")

            Light.parm("light_colorr").set(lightNameData['color']['R'])
            Light.parm("light_colorg").set(lightNameData['color']['G'])
            Light.parm("light_colorb").set(lightNameData['color']['B'])
            Light.parm("light_intensity").set(lightNameData['Intensity'])
            Light.parm("light_exposure").set(lightNameData['Exposure'])
            Light.parm("tx").set(lightNameData['Translate']['tx'])
            Light.parm("ty").set(lightNameData['Translate']['ty'])
            Light.parm("tz").set(lightNameData['Translate']['tz'])
            Light.parm("rx").set(lightNameData['Translate']['rx'])
            Light.parm("ry").set(lightNameData['Translate']['ry'])
            Light.parm("rz").set(lightNameData['Translate']['rz'])
            Light.parm("sx").set(lightNameData['Translate']['sx'])
            Light.parm("sy").set(lightNameData['Translate']['sy'])
            Light.parm("sz").set(lightNameData['Translate']['sz'])
            

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
    ui = Houdini_LightRebuild()
    ui.show()
    return ui