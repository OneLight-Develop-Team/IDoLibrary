from PySide2.QtWidgets import *
from PySide2.QtCore import *

class NodeOutput(QFrame):
    """输出节点"""
    def __init__(self, x, y):

        super(NodeOutput, self).__init__()
        
        self.setAcceptDrops(True)

        self.setStyleSheet("background-color: rgb(80, 50, 203);border-radius: 15px; border-color: rgb(0,0,0);" )
        
        #初始位置
        self.x = x
        self.y = y
        self.move(self.x, self.y)
        
        #初始大小
        self.sizeX = 120
        self.sizeY = 70
        self.resize(self.sizeX,self.sizeY)

        #创建子控件
        self.label = QLabel()
        self.label.setText("OUTPUT")
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setStyleSheet('font: 16pt "Arial";')

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setText("NONE")
        self.lineEdit.setStyleSheet('font: italic 14pt "微软雅黑";')
        self.lineEdit.setAlignment(Qt.AlignHCenter)



        #设置布局
        self.layout = QVBoxLayout()
        self.layout.setMargin(10)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineEdit)


        self.setLayout(self.layout)

    #设置移动事件
    def mouseMoveEvent(self,event):
        if event.buttons() == Qt.LeftButton:
            self.x += event.x()
            self.x -= self.sizeX/2
            self.y += event.y()
            self.y -= self.sizeY/2
            self.move(self.x,self.y)

    
