#coding:utf-8
import toolutils
import hou

# 待增加按数量比例copy
def setup():
    v=toolutils.sceneViewer()
    try:
        times = int(hou.ui.readInput("how many instancce node")[1])
    except:
        return
    print times
    node_list = []
    for t in range(times):
        t+=1
        node = hou.node(hou.ui.selectNode())
        node_list.append(node)
        print t

    template_node = hou.node(hou.ui.selectNode())
    print node_list[0]
    copy_node = node_list[0].parent().createNode("copy","my_copy1")
    switch_node = node_list[0].parent().createNode("switch", "copy_switch1")
    trans_node = node_list[0].parent().createNode("xform", "copy_transform1")  

    template_obj = template_node.geometry()
    id = template_obj.findPointAttrib("id")
    id_or_name = "$ID"
    if not id:
        id_or_name = "$PT"

    for t in range(times):
        switch_node.setInput(t, node_list[t])
    
    trans_node.setInput(0, switch_node)
    copy_node.setInput(0, trans_node)
    copy_node.setInput(1, template_node)
    
    trans = "fit01(rand(%s),0,0)" % id_or_name
    rot = "fit01(rand(%s),-1080,1080)" % id_or_name
    scale = "fit01(rand(%s),0.1,1)" % id_or_name
    model = "floor(fit01(rand(%s),0,%d))" % (id_or_name, times)
    
    copy_node.setParms({"stamp":1})
    copy_node.setParmExpressions(
                       {
                       "param1":"trans", "val1":trans,
                       "param2":"rot",  "val2":rot,
                       "param3":"scale", "val3":scale,
                       "param4":"model", "val4":model
                       },
                       hou.exprLanguage.Hscript)                       
    switch_node.setParmExpressions(
                                    {"input":"stamp(\"%s\",\"model\",0)" % copy_node.path() },                
                                    hou.exprLanguage.Hscript
                                  )
    trans_node.setParmExpressions(
                                    {"tx":"stamp(\"%s\",\"trans\",0)" % copy_node.path(),
                                     "ty":"stamp(\"%s\",\"trans\",0)" % copy_node.path(),
                                     "tz":"stamp(\"%s\",\"trans\",0)" % copy_node.path(),
                                     "rx":"stamp(\"%s\",\"rot\",0)" % copy_node.path(),
                                     "ry":"stamp(\"%s\",\"rot\",0)" % copy_node.path(),
                                     "rz":"stamp(\"%s\",\"rot\",0)" % copy_node.path(),
                                     "sx":"stamp(\"%s\",\"scale\",0)" % copy_node.path(),
                                     "sy":"stamp(\"%s\",\"scale\",0)" % copy_node.path(),
                                     "sz":"stamp(\"%s\",\"scale\",0)" % copy_node.path()                                     
                                    },                       
                                    hou.exprLanguage.Hscript
                                  )
                                  
    for node in [switch_node, trans_node, copy_node]:
        node.moveToGoodPosition()

    #node_list[0].parent().layoutChildren()
    copy_node.setDisplayFlag(1)
    copy_node.setRenderFlag(1)