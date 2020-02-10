from PySide2.QtWidgets import *
from PySide2.QtCore import *

class BaseNode(QFrame):
    """
    作用：
        节点基类
    参数：
        posX posY :位置
        scaX scaY :大小
    
    """
    def __init__(self,parent,posX,posY,scaX,scaY):
        super(BaseNode,self).__init__()
        self.isSelect = False  #是否被选中
      
        self.ui = None
        
        
        
        self.PosX = posX
        self.PosY = posY

        self.sizeX = scaX
        self.sizeY = scaY

        self.setTransform()

        self.setUI()
        self.setTransform()


    def setHighlight(self):
        """
        设置高亮
        """
        if isSelect == True:
            pass
    
    def setUI(self):
        """
        设置UI界面
        """ 
        pass

    def setTransform(self):
        """
        设置样式，位置
        """

        #加载不到ui，直接退出
        if self.ui == None:
            return


        self.move(self.PosX,self.PosY)


        
    #设置移动事件
    def mouseMoveEvent(self,event):
        if event.buttons() == Qt.LeftButton:
            self.PosX += event.x()
            self.PosX -= self.sizeX/2
            self.PosY += event.y()
            self.PosY -= self.sizeY/2
            self.move(self.PosX, self.PosY)

            #移动之后，重绘窗口
            if self.parent() != None:
                self.parent().updateWindow()
                



    def getInputPos(self):
        """获取节点上的radio上的输入位置"""
        pass
        
    def getOutputPos(self):
        """获取节点上的radio输出位置"""
        pass

    def setRadioReadOnly(self):
        """连接完成后设置radio为只读"""
        pass

    def setRadioFalse(self,radioNum):
        """设置按钮为关闭"""
        pass

    def setRadioTrue(self, radioNum):
        """设置按钮为开启"""
        pass
    def setInputNode(self, node):
        """设置传入节点"""
        pass