from PySide2.QtWidgets import *
from PySide2 import QtCore
from NodeExample import NodeAdd, NodeNum, NodeOutput
import PySide2.QtUiTools as QLoader
import os

# 储存节点数据
nodeDate = {}

#获取主文件目录
path = os.path.dirname(os.path.abspath("__file__"))

srcPath = path + r"\src"

class NodeDialog(QDialog):
    """节点选择窗口"""    

    def __init__(self,x,y):
        super(NodeDialog, self).__init__()
        
        self.x = x
        self.y = y
         
        self.setObjectName("节点选择器")
        
        self.uiPath = srcPath + r"\NodeSelectDialog.ui"
        self.loader = QLoader.QUiLoader()
        self.ui = self.loader.load(self.uiPath)
        self.ui.setParent(self)

        #获取子控件
        self.btnNum = self.ui.findChild(QPushButton, "btn_NumNode")
        self.btnAdd = self.ui.findChild(QPushButton, "btn_AddNode")        
        self.btnMinus = self.ui.findChild(QPushButton, "btn_MinusNode")     
        self.btnMultiply = self.ui.findChild(QPushButton, "btn_MultiplyNode")     
        self.btnDivide = self.ui.findChild(QPushButton, "btn_DivideNode")     
        self.btnOutput = self.ui.findChild(QPushButton, "btn_OutputNode")
        self.btnCancel = self.ui.findChild(QPushButton, "btn_Cancel")

        #节点信号连接
        self.btnNum.clicked.connect(self.createNodeNum)
        self.btnAdd.clicked.connect(self.createNodeAdd)
        self.btnMinus.clicked.connect(self.createNodeMinus)
        self.btnMultiply.clicked.connect(self.createNodeMultiply)
        self.btnDivide.clicked.connect(self.createNodeDivide)
        
        self.btnOutput.clicked.connect(self.createNodeOutput)

        self.btnNum.clicked.connect(self.close)
        self.btnAdd.clicked.connect(self.close)
        self.btnMinus.clicked.connect(self.close)
        self.btnMultiply.clicked.connect(self.close)
        self.btnDivide.clicked.connect(self.close)
        self.btnOutput.clicked.connect(self.close)
        
        self.btnCancel.clicked.connect(self.close)

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        
    #创建数字节点
    def createNodeNum(self):
        node = NodeNum.NodeNum(self.parent(),self.x,self.y)



        node.show()
        return node
        #self.parent().setFocus()


    #创建相加节点
    def createNodeAdd(self):
        node = NodeAdd.NodeAdd(self.parent(), self.x, self.y)
        node.setNodeType("add")
        
        node.show()
    
    #创建相加节点
    def createNodeMinus(self):
        node = NodeAdd.NodeAdd(self.parent(), self.x, self.y)
        node.setNodeType("minus")
        
        node.show()
    
    #创建相加节点
    def createNodeMultiply(self):
        node = NodeAdd.NodeAdd(self.parent(), self.x, self.y)
        node.setNodeType("multiply")
        
        node.show()
    
    #创建相加节点
    def createNodeDivide(self):
        node = NodeAdd.NodeAdd(self.parent(), self.x, self.y)
        node.setNodeType("divide")
        
        node.show()
    


    #创建输出节点
    def createNodeOutput(self):
        node = NodeOutput.NodeOutput(self.parent(),self.x,self.y)


        node.show()
        return node

    