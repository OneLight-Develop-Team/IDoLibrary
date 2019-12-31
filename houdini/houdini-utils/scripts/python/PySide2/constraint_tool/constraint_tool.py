#coding:utf-8
import sys
sys.path.append(r"D:\pcs-utils\scripts\Python\PySide2\constraint_tool")
import constraint_tool_ui
reload(constraint_tool_ui)
from PySide2.QtWidgets import *
import PySide2.QtCore as qc
import PySide2.QtGui as qg
import toolutils

# 实现可以拖放节点到pyside的功能
app = QApplication.instance()

class CustomFilter(qc.QObject):
    def __init__(self):
        super(CustomFilter, self).__init__()

    # 必须继承自QObject，然后重写该函数
    # return True表示事件被过滤掉了，相关的事件到这里就结束了(被拦截掉了)，不会继续进行
    # return False表示事件不过滤，继续进行
    def eventFilter(self, object, event):
        # 若是使用位置参数和关键字参数，那么需要制定event和obj
        # obj = args[0]
        # event = args[1]

        if event.type() == qc.QEvent.Drop:
            # source()必须写在类型判别之后，因为事件时时刻刻在产生，会不停执行该语句
            src = event.source()
            print 'drop event filter'
            return False

        if event.type() == qc.QEvent.KeyPress:
            if event.key() == qc.Qt.Key_Space:
                print 'space press event filter'
                # 返回真表示拦截了当前事件
                return False
        else:
            # pass the event on to the parent class
            return super(CustomFilter, self).eventFilter(object, event)


class ToolDialog(constraint_tool_ui.Ui_Dialog, QDialog):
    def __init__(self):
        super(ToolDialog, self).__init__()
        self.setupUi(self)   
        self.button_object1.setIcon(qg.QIcon(r"D:\pcs-utils\scripts\Python\PySide2\constraint_tool\f_open_folder.png"))
        self.button_object2.setIcon(qg.QIcon(r"D:\pcs-utils\scripts\Python\PySide2\constraint_tool\f_open_folder.png"))
        self.button_dopnet.setIcon(qg.QIcon(r"D:\pcs-utils\scripts\Python\PySide2\constraint_tool\f_open_folder.png"))
        self.constraint_type=0
        # slot
        self.buttonBox.accepted.connect(self.create_constraint)
        self.button_object1.clicked.connect(lambda: self.choose_node(self.lineEdit_object1))
        self.button_object2.clicked.connect(lambda: self.choose_node(self.lineEdit_object2))
        self.button_dopnet.clicked.connect(lambda: self.choose_node(self.lineEdit_dopnet))
        self.comboBox.currentIndexChanged.connect(self.change_con_type)        
        # drop
        self.setAcceptDrops(1)        
               
    def change_con_type(self, index):    
        self.constraint_type = index
                                   
    def choose_node(self, lineEdit):
        network = toolutils.networkEditor()
        curNode = network.currentNode()
        lineEdit.setText(curNode.path())     
    
    def create_constraint(self):    
        # 检查
        if not self.lineEdit_object1.text():
            raise IOError, "please choose one packed fragment node"            
        if not self.lineEdit_dopnet.text():
            raise IOError, "please choose dopnet"            
        geo1 = hou.node(self.lineEdit_object1.text()).geometry()        
        if not geo1.containsPrimType("PackedFragment"):
            raise TypeError, "input1 should contain only packed fragments"
        if self.lineEdit_object2.text():
            geo2 = hou.node(self.lineEdit_object2.text()).geometry()        
            if not geo2.containsPrimType("PackedFragment"):
                raise TypeError, "input2 should contain only packed fragments"            
            
        object1_node = hou.node(self.lineEdit_object1.text())
        dopnet_node = hou.node(self.lineEdit_dopnet.text())
        SOP_constraint_node =  object1_node.parent().createNode("SOP_generic_rbd_constraint")
        SOP_constraint_node.parm("Constraint_Type").set(self.constraint_type)
        if self.lineEdit_object2.text():
            object2_node = hou.node(self.lineEdit_object2.text())
            SOP_constraint_node.parm("Location").set(1)       
            SOP_constraint_node.setInput(1, object2_node)
        SOP_constraint_node.setInput(0, object1_node)                
        SOP_constraint_node.moveToGoodPosition()            
        dopnet_node = hou.node(self.lineEdit_dopnet.text())
        if self.constraint_type == 0:
            con_node = dopnet_node.createNode("DOP_pcs_glue_constraint")
        if self.constraint_type == 1:
            con_node = dopnet_node.createNode("DOP_pcs_pin_constraint")
            SOP_constraint_node.parm("center_or_surface").set(1)    
        if self.constraint_type == 2:
            pass      
        con_node.moveToGoodPosition()
            
    def closeEvent(self, event):
        self.setParent(None)
        #print "close"
        
    def dragEnterEvent(self, event):
        # The proposed drop actions can be filtered in a
        # widget's dragMoveEvent() function. However, it is
        # possible to accept all proposed actions in the
        # dragEnterEvent() and let the user decide which
        # they want to accept later:
        event.acceptProposedAction()
        print "dragEnter"
        
    def dropEvent(self, event):
        event.acceptProposedAction()
        print "drop"
    
    def mouseMoveEvent(self, event):
        print app.applicationName()
        
# tool_dialog = ToolDialog()
# tool_dialog.setParent(hou.qt.mainWindow(), qc.Qt.Window)
# tool_dialog.show()