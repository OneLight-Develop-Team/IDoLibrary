# encoding=utf-8

u'''
########################################################################
#                                                                      #
#             VertexConstraint.py                                      #
#                                                                      #
#             Version 1.0.0     last modified 2019-1-9                 #
#                                                                      #
#             Copyright (C) 2018  FXTD-Odyssey                         #
#                                                                      #
#             Email: 820472580@qq.com                                  #
#                                                                      #
########################################################################

=============================    English   =============================

I N S T A L L:

Copy the "VertexConstraint.py" to your Maya plugins directory
and load the plugin via the plugin manager

Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\
Mac OS: Users/Shared/Autodesk/maya/XXXX/plug-ins


U S E:

First load the plugin via Window->Settings/Prefs->Plug-in Manager
Then select the ConstraintMesh followed by the mesh that should be Driven.
Finally execute following `Python` command:
    sys.FXTD_Odyssey_VertexConstraintDeformer()

=============================     中文     =============================

安 装：
复制 "VertexConstraint.py"  文件到Maya的插件加载目录
通过插件管理器加载插件

Windows 路径：Program Files\Autodesk\MayaXXXX\bin\plug-ins\
Mac OS  路径：Users/Shared/Autodesk/maya/XXXX/plug-ins

使 用 方 法：
首先去到  Window->Settings/Prefs->Plug-in Manager 加载插件
（强烈要求使用英文版避未知的BUG）
首先选择被约束物体，第二个物体是驱动物体。
最后执行 `Python` 命令：
    sys.FXTD_Odyssey_VertexConstraintDeformer()
'''

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
from maya import mel
import math

nodeName= "VertexConstraint"
nodeId = OpenMaya.MTypeId(0xAA2fff)

import maya.cmds as cmds
kApiVersion = cmds.about(apiVersion=True)
if kApiVersion < 201600:
    kInput = OpenMayaMPx.cvar.MPxDeformerNode_input
    kInputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
    kOutputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    kEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
    kGroupId = OpenMayaMPx.cvar.MPxDeformerNode_groupId
else:
    kInput = OpenMayaMPx.cvar.MPxGeometryFilter_input
    kInputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
    kOutputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom
    kEnvelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope
    kGroupId = OpenMayaMPx.cvar.MPxGeometryFilter_groupId
    
class VertexConstraint(OpenMayaMPx.MPxDeformerNode):
    
    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)
    
    def deform(self,dataBlock,geoIterator,matrix,geometryIndex):
        
        input = kInput
        dataHandleInputArray = dataBlock.outputArrayValue(input)
        dataHandleInputArray.jumpToElement(geometryIndex)
        dataHandleInputElement = dataHandleInputArray.outputValue()

        inputGeom = kInputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        inMesh = dataHandleInputGeom.asMesh()
        
        # Note 获取约束顶点
        inputVerticesHandle = dataBlock.inputValue( self.inputVertices )
        inputVerticesList = inputVerticesHandle.asString()
        
        # Note 空字符串跳出循环
        try:
            inputVerticesList = eval(inputVerticesList)
        except:
            return

        # Note 获取驱动物体
        inputMeshHandle = dataBlock.inputValue( self.inputMesh )
        inputMeshObject = inputMeshHandle.asMesh()
        inputMeshFn     = OpenMaya.MFnMesh(inputMeshObject)

        #Envelope
        envelope = kEnvelope
        dataHandleEnvelope = dataBlock.inputValue(envelope)
        envelopeValue = dataHandleEnvelope.asFloat()
        
        mPointArray_meshVert = OpenMaya.MPointArray()

        increment = 0
        while( not geoIterator.isDone()):
            pointPosition = geoIterator.position()

            TargetPoint = OpenMaya.MPoint()
            try :
                inputMeshFn.getPoint(int(inputVerticesList[increment]),TargetPoint)
            except:
                break
                
            weight = self.weightValue(dataBlock,geometryIndex,geoIterator.index())    
            pointPosition.x  = pointPosition.x + (TargetPoint.x - pointPosition.x) * weight * envelopeValue
            pointPosition.y  = pointPosition.y + (TargetPoint.y - pointPosition.y) * weight * envelopeValue
            pointPosition.z  = pointPosition.z + (TargetPoint.z - pointPosition.z) * weight * envelopeValue
            mPointArray_meshVert.append(pointPosition)
            #geoIterator.setPosition(pointPosition) 

            increment += 1
            geoIterator.next()

        geoIterator.setAllPositions(mPointArray_meshVert)
        
            
        
def deformerCreator():
    return OpenMayaMPx.asMPxPtr(VertexConstraint())


def nodeInitializer():    

    tAttr = OpenMaya.MFnTypedAttribute()
    VertexConstraint.inputVertices = tAttr.create( "inputVertices", "inVert",OpenMaya.MFnData.kString)
    
    gAttr = OpenMaya.MFnGenericAttribute()
    VertexConstraint.inputMesh = gAttr.create( "inputMesh", "inMesh")
    gAttr.addDataAccept( OpenMaya.MFnData.kMesh )
    gAttr.setHidden(True)

    VertexConstraint.addAttribute(VertexConstraint.inputVertices)
    VertexConstraint.addAttribute(VertexConstraint.inputMesh)
    
    outputGeom = kOutputGeom
    VertexConstraint.attributeAffects(VertexConstraint.inputVertices,outputGeom )
    VertexConstraint.attributeAffects(VertexConstraint.inputMesh,outputGeom )

    
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject,"FXTD-odyssey","1.0.0")
    try:
        mplugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer,OpenMayaMPx.MPxNode.kDeformerNode)
        ''' This is to explicitly define that weights attribute of the deformer is paintable'''
        OpenMaya.MGlobal.executeCommand("makePaintable -attrType \"multiFloat\" -sm deformer \""+nodeName+"\" \"weights\";")
    except:
        sys.stderr.write("Failed to register node: %s" % nodeName)
        raise

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % nodeName)
        raise


# initializeMel = '''
# global proc VertexConstraintDeformer()
# {
#     string $sel[] = `ls -sl -tr`;
#     if (size($sel)==2)
#     {
#         string $shape[] = `listRelatives -s $sel[1]`;
#         string $Deformer[] = `deformer -typ "VertexConstraint" -n "VertexConstraintDeformer" $sel[0]`;
#         connectAttr -f ($shape[0]+".worldMesh[0]") ($Deformer[0]+".inputMesh");
#     }
#     else
#     {
#         error "%s";
#     }
# }

# ''' % u"请选择两个物体进行约束：第一个物体是被约束物体，第二个物体是驱动物体。"
# mel.eval( initializeMel )

def VertexConstraintDeformer():

    u'''
    VertexConstraint [English :Vertex Constraint to the closet Vertex instead using vertexID like Blendshape]
    VertexConstraint [中文：寻找模型最近的顶点进行顶点约束实现Blendshape的效果，但是不受模型的VertexID影响]

    U S E:
        Select the ConstraintMesh followed by the mesh that should be Driven.
        Execute function.

    使 用 方 法：
        首先选择被约束物体，第二个物体则是驱动物体。
        执行本函数。

    '''

    sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(sel)
        
    selList = cmds.ls(sl=1,tr=1)
    if len(selList) == 2:
        # Note 冻结变换
        cmds.makeIdentity( selList[0],apply=True, t=1, r=1, s=1, n=0,pn=1)
        cmds.makeIdentity( selList[1],apply=True, t=1, r=1, s=1, n=0,pn=1)

        # Note 选择对应的顶点
        nodeDagPath = OpenMaya.MDagPath()
        comp        = OpenMaya.MObject()
        sel.getDagPath(0, nodeDagPath,comp)

        # Note 初始化变量
        space = OpenMaya.MSpace.kWorld

        TargetNodeDagPath = OpenMaya.MDagPath()
        sel.getDagPath(1, TargetNodeDagPath)
        TargetMfnMesh     = OpenMaya.MFnMesh(TargetNodeDagPath)

        # Note 获取 iterator
        itr = OpenMaya.MItMeshVertex(nodeDagPath, comp)

        vertexList = []
        
        while not itr.isDone():
            
            # Note 获取最近的poly面序号
            TargetPoint = OpenMaya.MPoint()
            util = OpenMaya.MScriptUtil()
            util.createFromInt(0)
            idPointer = util.asIntPtr()
            TargetMfnMesh.getClosestPoint(itr.position(), TargetPoint, space, idPointer)  
            idx = OpenMaya.MScriptUtil(idPointer).asInt()

            # Note 通过序号获取面
            faceList = OpenMaya.MSelectionList()
            faceName = "%s.f[%s]" % (TargetNodeDagPath.fullPathName(),idx)
            faceList.add(faceName)

            # Note 将获取的面转为顶点
            verticesList = OpenMaya.MIntArray()
            TargetMfnMesh.getPolygonVertices(idx,verticesList)

            closestVert = None
            minLength = None
            # Note 遍历顶点找出最靠近的顶点
            for i in range(verticesList.length()):
                vertexPoint = OpenMaya.MPoint()
                TargetMfnMesh.getPoint(verticesList[i],vertexPoint)
                thisLength = vertexPoint.distanceTo(itr.position())
                if minLength is None or thisLength < minLength:
                    minLength = thisLength
                    closestVert = verticesList[i]
            vertexList.append(closestVert)
            itr.next()

        # Note 制作变形器
        Deformer = cmds.deformer(selList[0],typ="VertexConstraint",n="VertexConstraintDeformer")[0]
        
        # Note 连接属性
        shape = cmds.listRelatives(selList[1],s=1)[0]
        cmds.connectAttr( "%s.worldMesh[0]" % shape ,'%s.inputMesh'% Deformer ,f=1)
        cmds.parentConstraint(selList[1],selList[0],mo=1)
        
        # AttrString = "cmds.setAttr('%s.inputVertices'," % Deformer
        # AttrString += "%s," % len(vertexList)
        # for num in vertexList:
        #     AttrString += "'%s'," % num
        # AttrString += "type='stringArray')"

        AttrString = "cmds.setAttr('%s.inputVertices'," % Deformer
        AttrString += "'%s'," % vertexList
        AttrString += "type='string')"

        eval(AttrString)
        
    else:
        cmds.warning(u"请选择两个物体进行约束：第一个物体是被约束物体，第二个物体是驱动物体。")

# make the function globally
sys.FXTD_Odyssey_VertexConstraintDeformer = VertexConstraintDeformer