import maya.cmds as cmds

# Note 这个插件用来获取摄像机相关的的动画 
# Note 通过新建一个locator约束烘焙解决世界坐标问题 
# Note 通过偏移关键帧将相关的信息合并到最后的位置

def selectObj(text):
    sel = cmds.ls(sl=1)[0]
    cmds.textField(text,e=1,tx=sel)

def Loc_Match(start,end):

    target = "target" 
    selList = cmds.ls(sl=1)
    for sel in selList:
        loc = cmds.spaceLocator(n="%s_Driven"%sel)[0]
        pnCns = cmds.pointConstraint(sel,loc,mo=0)[0]
        
        StartTime = cmds.intField(start,q=1,v=1)
        EndTime = cmds.intField(end,q=1,v=1)

        if StartTime == EndTime:
            StartTime = cmds.findKeyframe(sel,w="first")
            EndTime = cmds.findKeyframe(sel,w="last")

        cmds.bakeResults( loc,at="translate", t=(StartTime,EndTime), sb=1 )
        cmds.addAttr(loc,ln="start",at="long",k=1)
        cmds.addAttr(loc,ln="end",at="long",k=1)
        cmds.delete(pnCns)

    cmds.headsUpMessage(u"locator生成完毕")

def Keyframe_Match(text):
    target = cmds.textField(text,q=1,tx=1)
    selList = cmds.ls(sl=1)
    for sel in selList:
        StartTime = cmds.getAttr("%s.start"%sel)
        EndTime = cmds.getAttr("%s.end"%sel)

        if StartTime == EndTime:
            StartTime = cmds.findKeyframe(sel,w="first")
            EndTime = cmds.findKeyframe(sel,w="last")

        cmds.copyKey( sel, time=(StartTime,EndTime), option="curve" ,at="translate")
        targetEndTime = cmds.findKeyframe(target,w="last")
        cmds.pasteKey( target, time=(targetEndTime,targetEndTime) )

    cmds.headsUpMessage(u"关键帧匹配完成")


def init_UI():
    if cmds.window("Match_Toolkit",ex=1):
        cmds.deleteUI("Match_Toolkit")
    cmds.window("Match_Toolkit",t="对位工具")

    cmds.columnLayout(adj=1)

    cmds.rowLayout( numberOfColumns=2,  adjustableColumn=2)
    cmds.text(l=u"起始时间")
    start = cmds.intField(w=200)
    cmds.setParent("..")
    cmds.columnLayout(adj=1)
    cmds.rowLayout( numberOfColumns=2,  adjustableColumn=2 )
    cmds.text(l=u"结束时间")
    end = cmds.intField()
    cmds.setParent("..")

    cmds.columnLayout( adj=1,columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
    cmds.button(l="生成对位locator",c="Loc_Match('%s','%s')" % (start,end))

    cmds.separator(style="in")
    cmds.columnLayout(adj=1)
    cmds.rowLayout( numberOfColumns=3,adjustableColumn=2)
    cmds.text(l=u"目标物体")
    objText = cmds.textField()
    cmds.button(l="<<<",w=50,c="selectObj('%s')" % objText)
    cmds.setParent("..")
    cmds.button(l="关键帧匹配",c="Keyframe_Match('%s')" % objText)
    cmds.showWindow()

init_UI()
