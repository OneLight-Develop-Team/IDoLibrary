# coding:utf-8
import PySide2.QtUiTools as QLoader
from PySide2 import QtWidgets,QtGui,QtCore
import os

#获取C:\Users\用户名的路径
path = os.getcwd() 


#获取资源文件路径
file_path = path + r"\Documents\houdini17.0\python2.7libs\src"
aboutDialog_ui = file_path + "\AboutDialog.ui"

ico_path = file_path + r"\aLight.jpg"

class AboutDialogWin(QtWidgets.QWidget):
    """关于窗口类"""
    def __init__(self):
        super(AboutDialogWin,self).__init__()

        #加载ui,并设置ui界面
        loader = QLoader.QUiLoader()
        self.ui = loader.load(aboutDialog_ui)
        self.ui.setParent(self)
        
        #设置窗口名称
        self.setWindowTitle(u"一灯")

        #设置布局
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.ui)

        #设置样式
        self.setStyleSheet("background-color:rgb(42,42,42);color:rgb(255,255,255);font: 22pt '宋体';")

        #设置大小
        self.setMaximumSize(330,110)
        self.setMinimumSize(330,110)

        #加载图片,图片保持比例
        self.label_about = self.ui.findChild(QtWidgets.QLabel,"label")
        pixmap = QtGui.QPixmap()
        pixmap.load(ico_path)
        self.label_about.setPixmap(pixmap)

        #设置为模态对话框
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        #设置图片自适应背景
        self.label_about.setMaximumSize(80,80)
        self.label_about.setScaledContents(True)
