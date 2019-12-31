
def Rotate_Value_Generate(AccuracyField):
    AccuracyField = cmds.floatField(AccuracyField,q=1,v=1)
    selList = cmds.ls(sl=1)
    for sel in selList:
        try:
            cmds.addAttr("%s.RotateSpeed"%sel,q=1,ex=1)
        except:
            cmds.addAttr(sel,ln="RotateSpeed",sn="rs",at="double",dv=0,k=1)
            
        Mel_Expression = """
            float $fps = `currentTimeUnitToFPS`;
            float $Offset = {1};
            float $CurrentFrame = `currentTime -query`;
            float $PrevFrame = $CurrentFrame - $Offset;
            float $RotateSpeed  = (`getAttr -time $CurrentFrame {0}.ry` - `getAttr -time $PrevFrame {0}.ry`)/(1*$Offset)*$fps;
            {0}.RotateSpeed = $RotateSpeed;
        """.format(sel,AccuracyField)
        cmds.expression(o=sel,s=Mel_Expression,ae=1,uc=all)

def Translate_Value_Generate(AccuracyField):
    AccuracyField = cmds.floatField(AccuracyField,q=1,v=1)
    selList = cmds.ls(sl=1)
    for sel in selList:
        try:
            cmds.addAttr("%s.TranslateSpeed"%sel,q=1,ex=1)
        except:
            cmds.addAttr(sel,ln="TranslateSpeed",sn="ts",at="double",dv=0,k=1)
            
        Mel_Expression = """
            float $fps = `currentTimeUnitToFPS`;
            float $Offset = {1};
            float $CurrentFrame = `currentTime -query`;
            float $PrevFrame = $CurrentFrame - $Offset;
            float $DistantTranslateX  = `getAttr -time $CurrentFrame {0}.tx` - `getAttr -time $PrevFrame {0}.tx`;
            float $DistantTranslateZ  = `getAttr -time $CurrentFrame {0}.tz` - `getAttr -time $PrevFrame {0}.tz`;
            float $TranslateSpeed = `sqrt ($DistantTranslateX * $DistantTranslateX + $DistantTranslateZ * $DistantTranslateZ)`/(1*$Offset)*$fps;
            {0}.TranslateSpeed = $TranslateSpeed;
        """.format(sel,AccuracyField)
        cmds.expression(o=sel,s=Mel_Expression,ae=1,uc=all)

def Rotate_Accel_Value_Generate(AccuracyField):
    AccuracyField = cmds.floatField(AccuracyField,q=1,v=1)
    selList = cmds.ls(sl=1)
    for sel in selList:
        try:
            cmds.addAttr("%s.RotateAccelSpeed"%sel,q=1,ex=1)
        except:
            cmds.addAttr(sel,ln="RotateAccelSpeed",sn="ras",at="double",dv=0,k=1)
            
        Mel_Expression = """
            float $fps = `currentTimeUnitToFPS`;
            float $Offset = {1};
            float $CurrentFrame = `currentTime -query`;

            float $PrevFrame = $CurrentFrame - $Offset;
            float $PrevSpeed  = (`getAttr -time $PrevFrame {0}.ry` - `getAttr -time ($PrevFrame-$Offset) {0}.ry`)/(1*$Offset)*$fps;

            float $NextFrame = $CurrentFrame + $Offset;
            float $NextSpeed  = (`getAttr -time $NextFrame {0}.ry` - `getAttr -time ($NextFrame-$Offset) {0}.ry`)/(1*$Offset)*$fps;

            float $RotateAccelSpeed;
            if($NextSpeed == 0 || $PrevSpeed == 0){{
                $RotateAccelSpeed = 0;
            }}else{{
                $RotateAccelSpeed = ($NextSpeed - $PrevSpeed)/(1*$Offset*2)*$fps;
            }}

            {0}.RotateAccelSpeed = $RotateAccelSpeed;
        """.format(sel,AccuracyField)

        cmds.expression(o=sel,s=Mel_Expression,ae=1,uc=all)

def Translate_Accel_Value_Generate(AccuracyField):
    AccuracyField = cmds.floatField(AccuracyField,q=1,v=1)
    selList = cmds.ls(sl=1)
    for sel in selList:
        try:
            cmds.addAttr("%s.TranslateAccelSpeed"%sel,q=1,ex=1)
        except:
            cmds.addAttr(sel,ln="TranslateAccelSpeed",sn="tas",at="double",dv=0,k=1)
            
        Mel_Expression = """
            float $fps = `currentTimeUnitToFPS`;
            float $Offset = {1};
            float $CurrentFrame = `currentTime -query`;
            float $PrevFrame = $CurrentFrame - $Offset;
            float $DistantTranslateX  = `getAttr -time $PrevFrame {0}.tx` - `getAttr -time ($PrevFrame-$Offset) {0}.tx`;
            float $DistantTranslateZ  = `getAttr -time $PrevFrame {0}.tz` - `getAttr -time ($PrevFrame-$Offset) {0}.tz`;
            float $PrevSpeed = `sqrt ($DistantTranslateX * $DistantTranslateX + $DistantTranslateZ * $DistantTranslateZ)`/(1*$Offset)*$fps;

            float $NextFrame = $CurrentFrame + $Offset;
            float $DistantTranslateX  = `getAttr -time $NextFrame {0}.tx` - `getAttr -time ($NextFrame-$Offset) {0}.tx`;
            float $DistantTranslateZ  = `getAttr -time $NextFrame {0}.tz` - `getAttr -time ($NextFrame-$Offset) {0}.tz`;
            float $NextSpeed = `sqrt ($DistantTranslateX * $DistantTranslateX + $DistantTranslateZ * $DistantTranslateZ)`/(1*$Offset)*$fps;

            float $TranslateAccelSpeed;
            if($NextSpeed == 0 || $PrevSpeed == 0){{
                $TranslateAccelSpeed = 0;
            }}else{{
                $TranslateAccelSpeed = ($NextSpeed - $PrevSpeed)/(1*$Offset*2)*$fps;
            }}

            {0}.TranslateAccelSpeed = $TranslateAccelSpeed;
        """.format(sel,AccuracyField)
        cmds.expression(o=sel,s=Mel_Expression,ae=1,uc=all)


def selectObj(text):
    if len(cmds.ls(sl=True)) > 0 :
        sel = cmds.ls(sl=1)[0]
        cmds.textField(text,e=1,tx=sel)
    else:
       cmds.textField(text,e=1,tx="") 

def Cam_Match(objText,Cam):
    Visualizer = cmds.textField(objText,q=1,tx=1)
    Camera = cmds.textField(Cam,q=1,tx=1)
    cmds.select(Visualizer)
    cmds.select(Camera,add=1)

def Connect_Visualizer(Visualizer,Cam,Attr,SpeedAttr,MinVal,MaxVal):
    Cam = cmds.textField(Cam,q=1,tx=1)
    Visualizer = cmds.textField(Visualizer,q=1,tx=1)
    Attr = cmds.textField(Attr,q=1,tx=1)
    SpeedAttr = cmds.floatField(SpeedAttr,q=1,v=1)
    MinVal = cmds.floatField(MinVal,q=1,v=1)
    MaxVal = cmds.floatField(MaxVal,q=1,v=1)

    if MinVal >= MaxVal:
        cmds.headsUpMessage(u"最大值最小值输入不正确")
        cmds.warning(u"最大值最小值输入不正确")
        return

    try:
        print cmds.getAttr(Attr)
    except:
        cmds.headsUpMessage(u"没有找到相关的属性！！")
        cmds.warning(u"没有找到相关的属性！！")
        return

    if not cmds.objExists(Visualizer):
        cmds.headsUpMessage(u"没有找到 Visualizer !!")
        cmds.warning(u"没有找到 Visualizer !!")
        return

    if not cmds.objExists(Cam):
        cmds.headsUpMessage(u"没有找到 Camera !!")
        cmds.warning(u"没有找到 Camera !!")
        return

    Handle = cmds.listRelatives(Visualizer)[0]
    Digits = cmds.listRelatives(Visualizer)[1]
    HandleLocator = cmds.listRelatives(Handle)[0]
    if not cmds.objectType( HandleLocator ) == "locator":
        cmds.headsUpMessage(u"没有找到 Handle Locator , 请检查Visualizer是否选择正确或者层级是否有问题")
        cmds.warning(u"没有找到 Handle Locator , 请检查Visualizer是否选择正确或者层级是否有问题")
        return

    # Note UndoChunk Open
    cmds.undoInfo(ock=1)
    
    # Note 添加运动表达式
    ExpressionStr = """
        {0}.translateY = min(max({1},{3}),{4});
        {0}.translateX = (frame-1)/{2};
    """.format(Handle,Attr,SpeedAttr,MinVal,MaxVal)
    
    ExpressionNode = cmds.expression(s=ExpressionStr,o=Handle,ae=1,uc="all")

    # Note 生成运动曲线命令
    Start = cmds.playbackOptions(q=1,min=1)
    End = cmds.playbackOptions(q=1,max=1)
    TotalCount = abs(End - Start)
    Command = ""
    posStr = ""


    cmds.progressWindow(	title=u'生成曲线',
        progress=0,
        status=u'生成曲线中...',
        isInterruptable=True )

    amount = 0.0

    AnnotationGrp = []
    cmds.currentTime(Start)
    transform = cmds.xform(Handle,q=1,ws=1,t=1)
    tx = transform[0]
    ty = transform[1]
    tz = transform[2]
    StartAnnotation = cmds.annotate( Digits, tx='%s' % Start,p=(tx , ty, tz) )
    AnnotationGrp.append(StartAnnotation)
    while Start <= End:

        # 进度条显示
        if cmds.progressWindow( query=True, isCancelled=True ) :
            cmds.progressWindow(endProgress=1)
            cmds.undoInfo(cck=1)
            return

        cmds.progressWindow( edit=True, progress=amount/TotalCount*100 )
        amount += 1

        cmds.currentTime(Start)
        transform = cmds.xform(Handle,q=1,ws=1,t=1)
        tx = transform[0]
        ty = transform[1]
        tz = transform[2]

        if not Start == End:
            posStr += "(%s, %s, %s)," % (tx,ty,tz)
        else:
            posStr += "(%s, %s, %s)" % (tx,ty,tz)

        if ty == MinVal or ty == MaxVal:
            cmds.currentTime(Start+1)
            transform = cmds.xform(Handle,q=1,ws=1,t=1)
            if not ty == transform[1]:
                Annotation = cmds.annotate( Digits, tx='%s' % Start,p=(tx , ty, tz) )
                AnnotationGrp.append(Annotation)
            
            cmds.currentTime(Start-1)
            transform = cmds.xform(Handle,q=1,ws=1,t=1)
            if not ty == transform[1]:
                Annotation = cmds.annotate( Digits, tx='%s' % Start,p=(tx , ty, tz) )
                AnnotationGrp.append(Annotation)

        Start += 1

    cmds.progressWindow(endProgress=1)

    Command = "cmds.curve(d=1,p=[%s])" % posStr
    # Note 生成运动曲线
    CrvNode = eval(Command) 

    # Note 生成文字提示
    EndAnnotation = cmds.annotate( Digits, tx='%s' % End,p=(tx , ty, tz) )
    AnnotationGrp.append(EndAnnotation)
    
    tx = cmds.polyEvaluate( Digits,b=True )[0][0]
    ty = cmds.polyEvaluate( Digits,b=True )[1][0]
    tz = 0
    AttrAnnotation = cmds.annotate( Digits, tx='%s' % Attr,p=(tx , ty-2, tz) )
    
    # Note 添加曲线运动 Expression
    ExpressionStr = "%s.translateX = -(frame-1)/%s;" % (CrvNode,SpeedAttr)
    cmds.expression(ExpressionNode,e=1,s=ExpressionStr)

    # Note 整理
    cmds.currentTime(cmds.playbackOptions(q=1,min=1))
    cmds.setAttr("%s.tx"%Handle,0)
    cmds.setAttr("%s.ty"%Handle,0)
    cmds.setAttr("%s.tz"%Handle,0)

    cmds.parent( CrvNode, Visualizer, relative=True )

    cmds.parent( AttrAnnotation, Digits, relative=True )
    cmds.setAttr("%s.displayArrow"%AttrAnnotation,0)
    for Annotation in AnnotationGrp:
        cmds.parent( Annotation, CrvNode, relative=True )
        cmds.setAttr("%s.displayArrow"%Annotation,0)
        
    cmds.setAttr("%s.overrideEnabled"%CrvNode,1)
    cmds.setAttr("%s.overrideColor"%CrvNode,17)

    # Note 拼接到摄像机上
    pnCns = cmds.parentConstraint(Cam,Visualizer,mo=0)[0]
    cmds.move( 0, -2, -10, Visualizer, r=1 , os=1 , wd=1 )
    cmds.scale( 0.15, 0.15, 0.15, Visualizer, r=1  )
    # Note 保持当前偏移
    cmds.parentConstraint(Cam,pnCns,e=1,mo=1)

    # Note UndoChunk Close
    cmds.undoInfo(cck=1)


def init_UI():
    if cmds.window("Cam_Visualizer_Toolkit",ex=1):
        cmds.deleteUI("Cam_Visualizer_Toolkit")
    cmds.window("Cam_Visualizer_Toolkit",t=u"速度属性生成显示工具")

    cmds.columnLayout( adj=1,columnAttach=('both', 15), rowSpacing=15, columnWidth=50 )

    cmds.separator()

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=2)
    cmds.text(l=u"计算精度",w=100)
    AccuracyField = cmds.floatField(v=0.0001,minValue=0.0001,maxValue=1)
    cmds.setParent("..")

    cmds.button(l=u"位移速度属性",c="Translate_Value_Generate('%s')" % AccuracyField)
    cmds.button(l=u"位移加速度属性",c="Translate_Accel_Value_Generate('%s')" % AccuracyField)
    cmds.button(l=u"旋转速度属性",c="Rotate_Value_Generate('%s')" % AccuracyField)
    cmds.button(l=u"旋转加速度属性",c="Rotate_Accel_Value_Generate('%s')" % AccuracyField)

    cmds.separator()

    cmds.columnLayout( adj=1, rowSpacing=5, columnWidth=50 )
    cmds.button(l="导入物体",c="cmds.Import()")
    cmds.rowLayout( numberOfColumns=2,adjustableColumn=1)
    Visualizer = cmds.textField(pht=u"选择导入的 Visualizer 物体 点击右侧按钮选择")
    cmds.button(l="<<<",w=50,c="selectObj('%s')" % Visualizer)
    cmds.setParent("..")

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=1)
    Cam = cmds.textField(pht=u"选择导入的 摄像机 物体 点击右侧按钮选择")
    cmds.button(l="<<<",w=50,c="selectObj('%s')" % Cam)
    cmds.setParent("..")

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=2)
    cmds.text(l=u"输入要显示的属性",w=100)
    Attr = cmds.textField(pht=u"例；pCube1.tx")
    cmds.setParent("..")

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=2)
    cmds.text(l=u"输入曲线刷新速度",w=100)
    SpeedAttr = cmds.floatField(v=10)
    cmds.setParent("..")

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=2)
    cmds.text(l=u"最大值",w=100)
    MaxVal = cmds.floatField(v=5)
    cmds.setParent("..")

    cmds.rowLayout( numberOfColumns=2,adjustableColumn=2)
    cmds.text(l=u"最小值",w=100)
    MinVal = cmds.floatField(v=-5)
    cmds.setParent("..")

    cmds.button(l="一键生成",c="Connect_Visualizer('%s','%s','%s','%s','%s','%s')" % (Visualizer,Cam,Attr,SpeedAttr,MinVal,MaxVal))

    cmds.setParent("..")
    cmds.separator()

    cmds.showWindow()

init_UI()
