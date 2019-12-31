# coding:utf-8
import os,re,sys,shutil
import hou
import _alembic_hom_extensions as abc
import toolutils



def loopThroughDir(dir):
    sub_dirs = os.listdir(dir)
    for sub_dir in sub_dirs:
        path = dir + "/" + sub_dir
        if os.path.isdir(path) and not re.findall(".*?(?:back|bak|temp).*?", sub_dir):
            loopThroughDir(path)
        elif os.path.splitext(sub_dir)[1] == ".hip" :
            file_list.append(path)




def listHipFile():
    '''
    对选择的文件夹下包括所有子路径下的hip文件进行输出，不包括自动备份的文件
    文件管理器版本
    ''' 
    global file_list
    file_list = []
    dir = hou.expandString(hou.ui.selectFile())
    loopThroughDir(dir)
    for file in file_list:
        print file
    print "this dir and its sub_dirs contains %d hip files" % len(file_list) 




########################################
#下面这一段针对批量重命名之后，帧范围没有加_导致时间不对的问题做解决
#import os
#files = os.listdir(r"E:\DGSC\sim\asd")
#for file in files:
#    pre = file[:-12]
#    ext = file.split(file[:-12])[1]
#    os.rename("E:/DGSC/sim/asd/"+file,"E:/DGSC/sim/asd/"+pre+"_"+ext)
########################################




def renameSequence(n=4, new_name="", time_offset=0, find="", replace=""):
    '''
    只针对命名规范的文件序列使用, 如：xxxxx.0007.ext
    调用后时间序号前不管是下划线还是句号都会被统一成句号
    可以偏移正负帧，但是帧号不可能为负
    可以查找替换
    名字****2015.0001.ext这样的是不能正确重命名的
    offset太小的可能不成功，重名了
    可以作用于任意帧位数的序列，即作用于$F，输入-1即可
    '''
    path = hou.ui.selectFile(title="choose sequence")
    # 如果是压缩路径，$F不能expand, 缓存序列可能不包含当前帧,
    # 但是$HIP是需要被expand的
    if "$HIP" in path:
        hip_path = hou.expandString("$HIP")
        path = path.replace("$HIP",hip_path)
    if os.path.isdir(path):
        hou.ui.displayMessage("please select file not directory")
        return
    if not path:
        return
    dir = os.path.split(path)[0] + "/"  # 获得所选取的文件的路径
    basename = os.path.basename(path)   # 获取文件名和扩展
    ext = os.path.splitext(path)[1]     # 获取扩展名

    # 输入序列帧位数和新名称，并根据名称使用正则表达式来单独获取没有位数的名称和位数
    input = hou.ui.readMultiInput("please input", ["frame scale number", "new name","time offset", "find", "replace"])
    if input[1][0]:
        n = int(input[1][0])
    
    if input[1][1]:
        new_name = input[1][1]
        if new_name[-1] != "." and new_name[-1] != "_":
            new_name = new_name + "."

    if input[1][2]:
        time_offset = int(input[1][2])
    
    if input[1][3]:
        find = input[1][3]
    
    if input[1][4]:
        replace = input[1][4]    

    # 设置正则表达式规则    
    if n != -1:
        pattern = "(?:.*?)(\d{%d}).*?" % n                  # 用来捕捉数字
        temp_pattern = "(.*?)(?:\d{%d}|[$F]).*?" % n        # 用来判断除了数字的部分是不是一致
    else:
        pattern = "(?:.*?)(\d{1,}).*?"                   # 用来捕捉数字
        temp_pattern = "(.*?)(?:\d{1,}|[$F]).*?"         # 用来判断除了数字的部分是不是一致
    
    files = os.listdir(dir)     
    modify_count = 0

    for file in files:
        if find and replace:    #查找替换, 执行了查找替换就不会执行重命名了
            replace_name = file.replace(find,replace)
            os.rename(dir + file, dir + replace_name)
            modify_count += 1
        
        if not find and not replace:
            # files就是basename
            # 使用正则分组匹配获取没有序列数字的名称, 对比看看是不是想要修改的序列文件，缩小修改范围
            # 最后比较扩展名，进一步缩小范围
            a = re.findall(temp_pattern, file)
            b = re.findall(temp_pattern, basename)
            if a:
                a = a[0]
            if b:
                b = b[0]
            file_ext  = os.path.splitext(file)[1]
            file_name = a
            if not new_name:
                new_name = file_name[:-1] + "."                
            if a == b and file_ext == ext:
                # 捕获数字
                match_obj = re.match(pattern, file, re.DOTALL)            
                if match_obj:    
                    print match_obj.groups()
                    frame_number = int(match_obj.groups()[0])

                    # 如果要偏移时间帧，则执行该语句
                    if time_offset != 0:
                        frame_number += time_offset
                        if frame_number < 0:    #当帧小于0的时候中断执行，因为有覆盖报错机制，所以不用额外去设计算法
                            print "less than frame 0"
                            break

                    # python处理0001是按照1来对待，需要在前面补足0
                    frame_number = str(frame_number)
                    frame_digits = len(frame_number)
                    add_digits = 4 - frame_digits
                    for i in range(add_digits):
                        frame_number = "0" + frame_number

                    # 针对houdini的双后缀压缩格式
                    if ext == ".sc":
                        os.rename(dir + match_obj.string, dir + new_name + frame_number + ".bgeo" + ext)
                    else:
                        os.rename(dir + match_obj.string, dir + new_name + frame_number + ext)
                    
                    modify_count += 1
    print "%d files have been renamed" % modify_count




def removeSequence(f_num=4):
    '''
    选择一个序列帧，会自动删除这一帧所在的序列到temp_dir, 可以多项删除
    '''
    # 弹出选择对话框
    paths = hou.ui.selectFile(multiple_select=1)
    if not paths:
        return
    input = hou.ui.readMultiInput("please input", ["frame scale number", "new folder name"])
    
    if input[1][0]:
        f_num = int(input[1][0])
    folder_name = input[1][1]    

    file_count = 0          
    
    # houdini多选返回是个字符串，以;作为分隔
    sel_paths = paths.split()

    for path in sel_paths:
        if path==";":
            continue
        
        # 如果是压缩路径，$F不能expand, 缓存序列可能不包含当前帧,
        # 但是$HIP是需要被expand的
        if "$HIP" in path:
            hip_path = hou.expandString("$HIP")
            path = path.replace("$HIP",hip_path)
        if os.path.isdir(path):
            hou.ui.displayMessage("please select file not directory")
            return
        if not path:
            return
            
        # 默认删除四位数的
        if f_num==-1:
            pattern = "(.*?)(?:\d{1,}|\$F).*?"     
        else:
            pattern = "(.*?)(?:\d{%d}|\$F).*?" % f_num
        
        dir = os.path.split(path)[0] + "/"  # 获得所选取的文件的路径
        basename = os.path.basename(path)   # 获取文件名和扩展
        ext = os.path.splitext(path)[1]     # 获取扩展名

        # 在当前路径中添加一个temp文件夹 
        # 1的时候使用序列名作为文件夹名
        # 可以自己输入文件夹名, 或者路径
        if not folder_name:
            new_dir = dir+"temp_dir" 
        elif ":" in folder_name:
            new_dir = folder_name
        elif folder_name == "1":
            private_name = re.findall(pattern, basename)
            new_dir = dir + private_name[0]
            if new_dir[-1] == "_":
                new_dir = new_dir[:-1]
        else:
            new_dir = dir + folder_name           

        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
               
        files = os.listdir(dir)
        for file in files:
            a = re.findall(pattern, file) 
            b = re.findall(pattern, basename)
            if a == b and os.path.splitext(file)[1] == ext:
                match_obj = re.match(pattern, file, re.DOTALL)
                if match_obj:
                    shutil.move(dir+file, new_dir)
                    file_count+=1
        
    print "%d files have been moved" % file_count




def removeFile():
    '''
    在当前目录下创建一个temp目录，用来存放符合条件的文件, 使用re来删除, 待改进，$F被expand的时候需要慎重考虑
    '''
    # 弹出选择对话框
    sel_file = hou.expandString(hou.ui.selectFile(file_type = hou.fileType.Directory),title="choose directory")
    if os.path.isdir(sel_file):
        dir = sel_file
    else:
        hou.ui.displayMessage("no directory selected")
        sys.exit(1)
        
    # 在当前路径中添加一个temp文件夹
    new_dir = dir+"temp_dir" 
    files = os.listdir(dir)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        
    # 输入规则
    input = hou.ui.readInput("enter the regular pattern")
    if input[1]:
        pattern = input[1]
    else:
        hou.ui.displayMessage("no regular pattern has been assigned")
        sys.exit(1)
        
    # 对符合条件的文件移动到temp目录下
    if pattern[1]:
        file_count=0
        for file in files:
            l = re.findall(pattern, file)
            # 只有文件才会被移动，目录不会
            if l and os.path.isfile(dir+l[0]):
                shutil.move(dir+l[0], new_dir)
                file_count+=1
        print "%d files have been moved" % file_count
        



exclude_node = ["explodedview", "pointjitter", "popsolver::2.0", "rigidbodysolver", "flipobject", "popgrains", "oceanspectrum", "oceansource::2.0"]
def stickyText(node):
    return_sticky = {}
    notes = node.stickyNotes()
    for index, note in enumerate(notes):
        content = "path: " + node.path() + "\n" + "content: "+ note.text().encode("utf-8") + "\n\n\n\n"    
        # bug : 这里return就是找到一次，马上返回结果，函数停止运行       
        return_sticky[index] = content
    return return_sticky



        
def loop_through_node(node=hou.root(), write_to_file=True):
    children = node.children()
    if children or node.type().isManager() and not re.findall("^rop_.*$", node.type().name()):
        content_dic = stickyText(node)
        for child in children:
            if child.type().name() not in exclude_node and child.name() != "export_tangent_normals1":
                loop_through_node(child)
        if content_dic and write_to_file:
            for content in content_dic.values():
                f.write(content)
            f.flush()

             


def write_sticky_to_file():
    global f 
    file_name = os.path.dirname(hou.hipFile.path())+ "/" + hou.expandString("$HIPNAME") + "_sticky.txt"
    if os.path.exists(file_name):
        os.remove(file_name)
    f = file(file_name, "a+")
    loop_through_node()
    f.close()
    



def loop_through_dir(dir):
    sub_dirs = os.listdir(dir)
    for sub_dir in sub_dirs:
        path = dir + sub_dir
        if os.path.isdir(path) and not re.findall(".*?(?:bak|temp|back).*$", path):
            loop_through_dir(path+"/")
        elif re.findall(".*?hip$", sub_dir):
            print "loaded: " + path
            hou.hipFile.load(path, suppress_save_prompt=False, ignore_load_warnings=True)
            hou.setSimulationEnabled(0)
            hou.setUpdateMode(hou.updateMode.Manual)
            write_sticky_to_file()




def export_sticky():
    '''
    把hip文件里面的sticky_note内容写出来
    '''
    kind = int(hou.ui.readInput("1 means loop through current file\n2 means loop through all the selected directory")[1])
    if kind == 1:
        write_sticky_to_file()

    if kind == 2:        
        dir = hou.ui.selectFile()
        t=loop_through_dir(dir)




def findALLPrefix(name):
    '''
    查找多重命名前缀
    '''
    split_name = name.split("_")
    length = len(split_name)
    prefix = ""
    for i in range(length-1):
        prefix += split_name[i] + "_"
    return prefix       




def findALLSuffix(name):
    '''
    查找多重命名后缀
    '''
    basename = name.split(".")[0]
    split_name = basename.split("_")
    length = len(split_name)
    suffix = ""
    for i in range(1,length):
        suffix += "_" + split_name[i]
    return suffix




def viewportComment():
    '''
    视窗添加帧数
    '''
    node = hou.node(hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.ObjCamera))
    cam_list = []
    try:
        extra_pos = int(hou.ui.readInput("extra_pos")[1])
    except ValueError:
        return

    for node in node.allNodes():
        if node.type().name() != "cam":
            continue
        else:
            cam = node
            cam_list.append(cam)
    for c in cam_list:
        if not c.parm("vcomment"):
            t = hou.StringParmTemplate("vcomment","Viewport Comment",1)
            c.addSpareParmTuple(t)
        c.parm("vcomment").set("$FF".rjust(extra_pos))




def validateCache():        # geo缓存路径若是有缓存路径就得单独查找，待实现; 待增加其他的格式查找
    '''
    写一个可以查找当前houdini节点使用的缓存路径,即清理缓存
    最好是有个ui,标出哪段缓存是无效缓存,由用户来决定哪一个要删除
    可以整合到hqTool,查找未使用,并做清理
    输出log：
       区分有效缓存和无效缓存
       询问是不是需要把不使用的文件放到temp dir里面，输出log，大小，帧数
       有效缓存标出是哪个节点在使用 + 绝对路径 + 序列缓存大小 + 序列帧数
    先打开hip文件在执行脚本           
    '''
    dir = hou.expandString(hou.ui.selectFile(title="select directory",
                                             collapse_sequences=1,
                                             file_type=hou.fileType.Directory
                                             ))
    new_dir = dir+"temp_dir" 
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        
    pattern_list = []
    node_list = []
    pattern_to_node_index_list=[]
    root = hou.root()
    for node in root.allNodes():
        if not node.type().name() in ["filecache", "file", "dopio"]:
            continue
        else:
            parm = node.parm("file")
            if not parm:
                continue    
            file_path = parm.unexpandedString()
            basename = os.path.basename(file_path)            
            if ("$F" or "$F4") in basename:                 #序列的情况
                pattern = basename.split("$F")[0]
            else:                                           #单帧的情况
                pattern = basename.split(".bgeo.sc")[0]                
                # pattern = basename                
            # 有$OS的情况需要全部把名字解释出来, $OS、`$OS`
            if "$OS" in file_path:
                OS = node.name()
                if "`$OS`" in file_path:
                    pattern = pattern.replace("`$OS`", OS)
                else:
                    pattern = pattern.replace("$OS", OS)
            # houdini默认的节点设置除了OS，还会有其他`
            if "`" in pattern:
                continue
            pattern_list.append(pattern)
            node_list.append(node.path())
    
    found=""
    invalid_count=0
    try:
        files = os.listdir(dir)
    except :
        return
        
    file_count = len(files)
    count=0
    
    with hou.InterruptableOperation("searching...", open_interrupt_dialog=1) as operation:
        for file in files:
            for pattern in pattern_list:
                found = re.findall(pattern+".*", file, re.S)
                if found:
                    index = pattern_list.index(pattern)
                    if index not in pattern_to_node_index_list:
                        pattern_to_node_index_list.append(index)
                    break
            if not found:
                # print file
                file_path = dir + file
                shutil.move(file_path, new_dir)
                invalid_count+=1    
            count+=1
            percent = float(count)/float(file_count)
            operation.updateProgress(percent)

    print "%d invalid files have been removed" % (invalid_count-1), pattern_to_node_index_list
    for idx in pattern_to_node_index_list:
        print pattern_list[idx], "\t", node_list[idx], "\n"




def abcCamTrack():
    '''
    abc摄影机跟踪，可以使用object merge把相机内的点提取，选择transform参数
    '''
    
    node = hou.node(hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.ObjCamera))
    
    
    try:
        for node in node.allNodes():
            if node.type().name() != "cam":
                continue
            else:
                cam = node
    except AttributeError:
        return

    # look for /obj and create null node       
    while not node.type().isManager():
        if node.type().name() == "alembicarchive":      #abcNode
            abcNode = node                          
        node = node.parent() 
        
    null = node.createNode("null", cam.name()+"_track")
    str_template1 = hou.StringParmTemplate("cam_path","cam_path",1)
    str_template2 = hou.StringParmTemplate("abc_path","abc_path",1)
    null.addSpareParmTuple(str_template1)
    null.addSpareParmTuple(str_template2)
    null.parm("cam_path").set(cam.path())
    null.parm("abc_path").set(abcNode.path())

    for i in range(2):
        if i == 0:
            mode = "t"
        if i == 1:
            mode = "r"
        for j in range(3):        
            expr =  ""
            expr += "import _alembic_hom_extensions as abc\n"
            expr += "abcPath = hou.node(hou.pwd().parm(\"abc_path\").eval()).parm(\"fileName\").eval()\n"
            expr += "objPath = hou.node(hou.pwd().parm(\"cam_path\").eval()).parent().parm(\"objectPath\").eval()\n"
            expr += "trans_tuple = abc.getWorldXform(abcPath, objPath, hou.time())[0]\n"
            expr += "cam_trans = hou.Matrix4()\n"
            expr += "cam_trans.setTo(trans_tuple)\n"
            if mode == "t":
                expr += "return cam_trans.extractTranslates()[%d]" % j
            if mode == "r":
                expr += "return cam_trans.extractRotates()[%d]" % j
            null.parmTuple(mode)[j].setExpression(expr, hou.exprLanguage.Python)    




def findLockedSop():
    '''
    查找有锁住内容的节点
    '''
    root = hou.root()
    for node in root.allSubChildren():
        if node.type().category().name() == "Sop" and node.type().isManager() != 1:
            if node.isHardLocked():
                print node.path()




def fix_H17_abc_cam():
    '''
    修正17.0.416及之前版本的abc相机问题
    '''
    camlist=[]
    cam_nodes_f=[]
    geonodelist = hou.selectedNodes()
    
    for xs in geonodelist:   
        camlist += xs.allSubChildren()
        
    camlist+=geonodelist
    cam_nodes_f+= [node for node in camlist if 'cam'==node.type().name()]

    if len(cam_nodes_f)<1:
		print 'please select least one camera'
    for caml in cam_nodes_f:    
        caml.parent().parm("frame").setExpression("$FF")




def isolateSelection():
    '''
    孤立选择
    '''
    view = toolutils.sceneViewer()
    selection = view.selectGeometry()
    cur_node = view.currentNode()
    blast_node = cur_node.parent().createNode("blast")
    if selection.geometryType() == hou.geometryType.Points:        
        blast_node.parm("grouptype").set(3)
    if selection.geometryType() == hou.geometryType.Edges:        
        blast_node.parm("grouptype").set(2)        
    if selection.geometryType() == hou.geometryType.Primitives:        
        blast_node.parm("grouptype").set(4)
    blast_node.parm("group").set(selection.selectionStrings()[0])
    blast_node.parm("negate").set(1)
    blast_node.setInput(0, cur_node)
    blast_node.moveToGoodPosition()    
    for flag in [hou.nodeFlag.Visible, hou.nodeFlag.Render]:
        blast_node.setGenericFlag(flag, True)
    blast_node.setCurrent(1,clear_all_selected=1)
        



