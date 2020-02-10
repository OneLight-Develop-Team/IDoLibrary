from PySide2.QtWidgets import *
from PySide2.QtCore import *
import PySide2.QtUiTools as QLoader
import os
from NodeExample.node import BaseNode

#获取主文件目录
path = os.path.dirname(os.path.abspath("__file__"))

srcPath = path+ r"\src"
class NodeOutput(BaseNode):
    """输出节点"""

    outputInputSignal = Signal()
    def __init__(self,parent,posX,posY):

        super(NodeOutput, self).__init__(parent,posX,posY,scaX=200,scaY=130)
        
        self.setParent(parent)
        self.show()

        self.nodeName = "nodeOutput"

        self.InputNode = None

        #传入的是什么节点
        self.getNodeAdd = False
        self.getNodeNum = False


        self.radioNum = 0
        
        self.radioButton = self.ui.findChild(QRadioButton, "radioButton")
        self.lineEdit = self.ui.findChild(QLineEdit, "lineEdit")
        self.btn = self.ui.findChild(QPushButton, "pushButton")
        
        self.radioButton.clicked.connect(self.on_radioButton_Click)

        self.btn.clicked.connect(self.count)
        
        self.outputInputSignal.connect(lambda: self.parent().selectSecond(self))

 
    def setUI(self):
        self.uiPath = srcPath + r"\OutputNode.ui"
        self.loader = QLoader.QUiLoader()
        self.ui = self.loader.load(self.uiPath)
        self.ui.setParent(self)

    def on_radioButton_Click(self):
        self.radioNum = 0
        self.outputInputSignal.emit()


    def getInputPos(self,radioInputNum):

        return self.PosX + self.radioButton.geometry().x(), self.PosY + self.radioButton.geometry().y() + 62
   
    def  setRadioReadonly(self,radioNum):
        """设置按钮只读"""

        #断开连接
        self.radioButton.clicked.disconnect(self.on_radioButton_Click)
        self.radioButton.clicked.connect(self.on_set_radioButton_Click)

    def on_set_radioButton_Click(self):
        """
            设置按钮只可以显示已点击
        """
        if self.radioButton.isChecked() == False:

            self.radioButton.setChecked(True)


    def setRadioFalse(self, radioNum):
        """
            设置按钮关闭
            radioNum ,按钮序号

        """
        self.radioButton.setChecked(False)

    def setRadioTrue(self, radioNum):
        """
            设置按钮开启
            radioNum ,按钮序号

        """
        self.radioButton.setChecked(True)
        


    def setInputNode(self, node):
        """保存传入的节点,并储存其类型"""
        self.InputNode = node
        if node.nodeName == "nodeNum":
            self.getNodeNum = True
        elif node.nodeName == "nodeAdd":
            self.getNodeAdd = True

    def count(self):
        """计算结果"""
        
        if self.getNodeAdd and self.InputNode.canBeCounted:  ## 连接的是add节点，并且add节点已经连接了两个num节点
            if self.InputNode.nodeType == "add":
                outputNumber = self.InputNode.node1.spinbox.value() + self.InputNode.node2.spinbox.value()

                self.lineEdit.setText(str(outputNumber))

            elif self.InputNode.nodeType == "minus":
                outputNumber = self.InputNode.node1.spinbox.value() - self.InputNode.node2.spinbox.value()
                self.lineEdit.setText(str(outputNumber))

            elif self.InputNode.nodeType == "multiply":
                outputNumber = self.InputNode.node1.spinbox.value() * self.InputNode.node2.spinbox.value()
                self.lineEdit.setText(str(outputNumber))

            elif self.InputNode.nodeType == "divide":
                if self.InputNode.node2.spinbox.value() == 0:
                    self.lineEdit.setText("除数不可以为零")
                else:
                    outputNumber = self.InputNode.node1.spinbox.value() / self.InputNode.node2.spinbox.value()
                    self.lineEdit.setText(str(outputNumber))


        elif self.getNodeNum:
            outputNumber = self.InputNode.spinbox.value()
            self.lineEdit.setText(str(outputNumber))
