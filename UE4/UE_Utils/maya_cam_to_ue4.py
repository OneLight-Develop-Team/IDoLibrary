import maya.cmds as mc


windowID = "CameraWindowID"
if mc.window(windowID, q= True, exists = True):
    mc.deleteUI(windowID)
mc.window(windowID, rtf = True, wh = (10,35), title = "Unreal Camera Generator")
mc.showWindow(windowID)
PrimaryLayout = mc.columnLayout()
mc.rowColumnLayout(nc = 3)
CreateButton = mc.button(l = "Select All The Camera", w= 600, c = "createCameraBtnCmd()")


def getSelection():
    selection = mc.ls(sl = True)
    return selection


def createCameraBtnCmd():
    cam_list = getSelection()
    for index, cam in enumerate(cam_list):                
        # 建立相机
        cam_name = "UE4_" + str(cam).replace("cam", "Camera")
        Cam = mc.camera(n = cam_name)
        ExportCam = Cam[0]
        ExportCamShape = Cam[1]
        
        # 建立约束
        pointConst = mc.pointConstraint(cam, ExportCam, mo = False)[0]        
        # mc.setAttr(pointConst + ".offsetX", XOffsetValue)
        # mc.setAttr(pointConst + ".offsetZ", YOffsetValue)
        # mc.setAttr(pointConst + ".offsetY", ZOffsetValue)                        
        orientConst = mc.orientConstraint(cam, ExportCam, mo = False)[0]
        # mc.setAttr(orientConst + ".offsetY", 90)
        
        # 对新创建的相机做属性链接
        # 确保不管选择shape还是transform都没问题
        if mc.listRelatives(cam):
            ls = mc.listRelatives(cam)[0]
        else:
            ls = cam
        attrs = mc.listAttr(ls)
        for attr in attrs:
            try:
                con = mc.listConnections(str(ls) + "." + attr, plugs=True, connections=True)
            except ValueError:
                continue
            if con:
                source_node = con[1]
                to = str(ExportCamShape) + "." + str(con[0]).split(".")[1]
                mc.connectAttr(source_node, to)
        
        #bake偏移动画，偏移动画没办法使用默认的bake烘焙
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
        frames = end_frame - start_frame
        
        attrs = mc.listConnections(str(ExportCamShape) + ".horizontalFilmOffset", plugs=True, connections=True)
        mc.disconnectAttr(attrs[1], attrs[0])
        attrs = mc.listConnections(str(ExportCamShape) + ".verticalFilmOffset", plugs=True, connections=True)
        mc.disconnectAttr(attrs[1], attrs[0])        
        
        for frame in range(start_frame, end_frame):            
            offset_value = mc.getAttr(str(cam)+".filmOffset", time=frame)
            mc.setKeyframe(str(ExportCamShape), at='horizontalFilmOffset', v=offset_value[0][0], time=frame)
            mc.setKeyframe(str(ExportCamShape), at='verticalFilmOffset', v=offset_value[0][1], time=frame)
         
 