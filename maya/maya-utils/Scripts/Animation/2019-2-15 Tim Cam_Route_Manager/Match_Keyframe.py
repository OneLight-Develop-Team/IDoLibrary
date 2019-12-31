import maya.cmds as cmds

# Note 这个插件用来获取运动路径关键帧并复制到相关MotionPath上

# # Note 获取 Keyframe_Value
# target = "Loc_uValue"
# Keyframe_Value = {}
# Keyframe_Value["key"] = []
# Keyframe_Value["Value"] = []
# Keyframe_Value["InTan_Type"] = []
# Keyframe_Value["InTan_Angle"] = []
# Keyframe_Value["InTan_Weight"] = []
# Keyframe_Value["OutTan_Type"] = []
# Keyframe_Value["OutTan_Angle"] = []
# Keyframe_Value["OutTan_Weight"] = []
# for key in cmds.keyframe(target,q=1):
#     cmds.currentTime(key,u=0)
#     Keyframe_Value["key"].append(key)
#     Keyframe_Value["Value"].append(cmds.keyframe(target,q=1,vc=1,time=(key,key))[0])
#     Keyframe_Value["InTan_Type"].append(cmds.keyTangent(target,q=1,itt=1,time=(key,key))[0])
#     Keyframe_Value["InTan_Angle"].append(cmds.keyTangent(target,q=1,ia=1,time=(key,key))[0])
#     Keyframe_Value["InTan_Weight"].append(cmds.keyTangent(target,q=1,iw=1,time=(key,key))[0])
#     Keyframe_Value["OutTan_Type"].append(cmds.keyTangent(target,q=1,ott=1,time=(key,key))[0])
#     Keyframe_Value["OutTan_Angle"].append(cmds.keyTangent(target,q=1,oa=1,time=(key,key))[0])
#     Keyframe_Value["OutTan_Weight"].append(cmds.keyTangent(target,q=1,ow=1,time=(key,key))[0])


def selectObj(text):
    sel = cmds.ls(sl=1)[0]
    cmds.textField(text,e=1,tx=sel)

def selectCrvObj(text):
    Selection = cmds.ls(sl=True,l=1)[0] 
    cmds.textField(text,e=1,tx=Selection)
    try:
        SelectionShape = cmds.listRelatives(Selection)[0]
        MotionPath = cmds.listConnections(SelectionShape,type="motionPath")[0]
        global MotionPath_Text
        cmds.textField(MotionPath_Text,e=1,tx=MotionPath)
    except:
        pass

def Keyframe_Match(MotionPathText,LocText):
    MotionPath = cmds.textField(MotionPathText,q=1,tx=1)
    Locator = cmds.textField(LocText,q=1,tx=1)
    Selection = cmds.ls(sl=1)[0]
    cmds.cutKey("%s.uValue"%MotionPath,clear=True)

    AnimCurve = cmds.listConnections( "%s.uValue"%Locator, d=False, s=True )[0]

    StartTime = cmds.findKeyframe(Locator,w="first")
    EndTime = cmds.findKeyframe(Locator,w="last")

    cmds.copyKey( "%s.uValue" % Locator, time=(StartTime,EndTime))
    cmds.pasteKey("%s.uValue" % MotionPath)

    cmds.headsUpMessage(u"关键帧匹配完成")


def init_UI():
    if cmds.window("Match_Toolkit",ex=1):
        cmds.deleteUI("Match_Toolkit")
    cmds.window("Match_Toolkit",t="对位工具")
    cmds.columnLayout(adj=1)
    cmds.button(l="引用动画",w=50,c="cmds.CreateReference()")
    cmds.separator(style="in")


    cmds.rowLayout( numberOfColumns=3,adjustableColumn=2)
    cmds.text(l=u"Locator",w=75)
    Loc_Text = cmds.textField()
    cmds.button(l="<<<",w=50,c="selectObj('%s')" % Loc_Text)
    cmds.setParent("..")

    cmds.separator(style="in")

    cmds.columnLayout(adj=1)
    cmds.rowLayout( numberOfColumns=3,adjustableColumn=2)
    cmds.text(l=u"路径曲线",w=75)
    objText = cmds.textField()
    cmds.button(l="<<<",w=50,c="selectCrvObj('%s')" % objText)
    cmds.setParent("..")
    cmds.rowLayout( numberOfColumns=3,adjustableColumn=2)
    cmds.text(l=u"MotionPath",w=75)
    global MotionPath_Text
    MotionPath_Text = cmds.textField()
    cmds.button(l="<<<",w=50,c="selectObj('%s')" % MotionPath_Text)
    cmds.setParent("..")
    cmds.button(l="关键帧匹配",c="Keyframe_Match('%s','%s')" %(MotionPath_Text,Loc_Text))
    cmds.showWindow()

init_UI()

