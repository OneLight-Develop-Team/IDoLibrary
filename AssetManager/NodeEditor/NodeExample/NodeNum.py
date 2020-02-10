from PySide2.QtWidgets import *
from PySide2.QtCore import *
import PySide2.QtUiTools as QLoader
import os
from NodeExample.node import BaseNode

#获取主文件目录
path = os.path.dirname(os.path.abspath("__file__"))

srcPath = path+ r"\src"
class NodeNum(BaseNode):
    """相加节点"""

    #输出信号
    numOutputSignal = Signal()

    

    def __init__(self,parent,posX,posY):

        super(NodeNum, self).__init__(parent,posX,posY,scaX = 200,scaY = 120)
        
        self.setParent(parent)

        self.radioNum = 0

        self.nodeName = "nodeNum"

        

        #output radio
        self.radioButton = self.ui.findChild(QRadioButton, "radioButton")
        self.spinbox = self.ui.findChild(QSpinBox, "spinBox")
        
        self.number = self.spinbox.value() #数字值

        self.radioButton.clicked.connect(self.on_radioButton_Click)


        self.numOutputSignal.connect(lambda: self.parent().selectFirst(self))

        #设置最大值与最小值
        self.spinbox.setMaximum(10000)
        self.spinbox.setMinimum(-10000)

    def setUI(self):
        self.uiPath = srcPath + r"\NumNode.ui"
        self.loader = QLoader.QUiLoader()
        self.ui = self.loader.load(self.uiPath)
        self.ui.setParent(self)


    def on_radioButton_Click(self):
        self.numOutputSignal.emit()



    def getOutputPos(self, radioOutputNum):
        
        return self.PosX + self.radioButton.geometry().x(), self.PosY + self.radioButton.geometry().y() + 60
        

      
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
        