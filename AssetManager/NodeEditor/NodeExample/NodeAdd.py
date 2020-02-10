from PySide2.QtWidgets import *
from PySide2.QtCore import *
import PySide2.QtUiTools as QLoader
import os
from NodeExample.node import BaseNode

#获取主文件目录
path = os.path.dirname(os.path.abspath("__file__"))

srcPath = path + r"\src"



class NodeAdd(BaseNode):

    """相加节点"""

    #输入信号
    addInputSignal_1 = Signal()
    addInputSignal_2 = Signal()
    #输出信号
    addOutPutSignal_3 = Signal()

    def __init__(self,parent,posX,posY):

        super(NodeAdd, self).__init__(parent, posX,posY,scaX=240,scaY=165)
        
        self.setParent(parent)

        self.nodeName = "nodeAdd"

        self.show()

        # 根据类型改变节点样式
        self.nodeType = "add"


        ## 传入的两个节点
        self.node1 = None
        self.node2 = None


        #端口号
        self.radioNum = 0

        #能否被计算
        self.canBeCounted = False 


        #input radio
        self.radioButton1 = self.ui.findChild(QRadioButton, "radioButton_1")
        self.radioButton2 = self.ui.findChild(QRadioButton, "radioButton_2")
        #output radio
        self.radioButton3 = self.ui.findChild(QRadioButton, "radioButton_3")

        self.label = self.ui.findChild(QLabel, "label")
        

        
        self.radioButton1.clicked.connect(self.on_radioButton1_Click)
        self.radioButton2.clicked.connect(self.on_radioButton2_Click)
        self.radioButton3.clicked.connect(self.on_radioButton3_Click)


        self.addInputSignal_1.connect(lambda: self.parent().selectSecond(self))
        self.addInputSignal_2.connect(lambda: self.parent().selectSecond(self))
        self.addOutPutSignal_3.connect(lambda: self.parent().selectFirst(self))

        
        # self.addInputSignal.connect(self.parent()printA)


        
    def setUI(self):
        self.uiPath = srcPath + r"\AddNode.ui"
        self.loader = QLoader.QUiLoader()
        self.ui = self.loader.load(self.uiPath)
        self.ui.setParent(self)


    #点击raioButton时，自定义信号发射
    def on_radioButton1_Click(self):
        self.radioNum = 0
        self.addInputSignal_1.emit()

    def on_radioButton2_Click(self):
        self.radioNum = 1
        self.addInputSignal_2.emit()

    def on_radioButton3_Click(self):
        self.radioNum = 3
        self.addOutPutSignal_3.emit()




    #获取输入端的位置
    def getInputPos(self,radioInputNum):
        self.radioNum = radioInputNum
        if self.radioNum == 0:
            return self.PosX + self.radioButton1.geometry().x(), self.PosY + self.radioButton1.geometry().y() + 65

        
        else:
            return self.PosX + self.radioButton2.geometry().x(), self.PosY + self.radioButton2.geometry().y() + 115

      
    #获取输出端的位置
    def getOutputPos(self, radioOutputNum):
        self.radioNum = radioOutputNum
        if self.radioNum == 3:
            return self.PosX + self.radioButton3.geometry().x()+180,self.PosY + self.radioButton3.geometry().y() +65

    

    
    def  setRadioReadonly(self,radioNum):
        """设置按钮只读"""
        if radioNum == 0:
            #断开连接
            self.radioButton1.clicked.disconnect(self.on_radioButton1_Click)
            self.radioButton1.clicked.connect(lambda: self.on_set_radioButton_Click(1))
        elif radioNum == 1:
            #断开连接
            self.radioButton2.clicked.disconnect(self.on_radioButton2_Click)
            self.radioButton2.clicked.connect(lambda: self.on_set_radioButton_Click(2))
        elif radioNum == 2:
            #断开连接
            self.radioButton3.clicked.disconnect(self.on_radioButton3_Click)
            self.radioButton3.clicked.connect(lambda: self.on_set_radioButton_Click(3))


    def on_set_radioButton_Click(self,radioNum):
        """
            设置按钮只可以显示已点击
        """
        if radioNum == 1:
            if self.radioButton1.isChecked() == False:

                self.radioButton1.setChecked(True)
        elif radioNum == 2:
            if self.radioButton2.isChecked() == False:

                self.radioButton2.setChecked(True)
        
        elif radioNum == 3:
            if self.radioButton3.isChecked() == False:

                self.radioButton3.setChecked(True)




    def setRadioFalse(self, radioNum):
        """
            设置按钮关闭
            radioNum ,按钮序号

        """
        

        if radioNum == 0:
            self.radioButton1.setChecked(False)

        elif radioNum ==1:
            self.radioButton2.setChecked(False)
            
        elif radioNum == 2:
            self.radioButton3.setChecked(False)


        

    def setRadioTrue(self, radioNum):
        """
            设置按钮开启
            radioNum ,按钮序号

        """
        if radioNum == 1:
            self.radioButton1.setChecked(True)
        elif radioNum == 2:
            self.radioButton2.setChecked(True)
        elif radioNum == 3:  
            self.radioButton3.setChecked(True)

    def setInputNode(self, node,radioNum):
        """设置两个传入的节点,两个节点均不为空，则可以进行计算"""
        if radioNum == 0:

            self.node1 = node

            self.setCanBeCounted()
        elif radioNum == 1 :
            self.node2 = node
            self.setCanBeCounted()
           

    def setNodeType(self, type):
        """设置节点类型"""
        self.nodeType = type
        if type == "add":
            self.label.setText("ADD NODE")
        elif type == "minus":
            self.label.setText("MINUS NODE")
        elif type == "multiply":
            self.label.setText("MULTIPLY NODE")
        elif type == "divide":
            self.label.setText("DIVIDE NODE")


    def setCanBeCounted(self):
        """两个节点均连入后设置为可以计算"""
        if self.node1 != None and self.node2 != None:
            self.canBeCounted = True

