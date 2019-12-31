# coding:utf-8
import PySide2.QtUiTools as QLoader
from PySide2 import QtWidgets,QtGui,QtCore
import hou 
import os,json
import sys
import AboutDialog
import PicDialog
import ModelDialog
reload(ModelDialog)


#获取当前文件所在文件目录
path = os.path.dirname(os.path.abspath(__file__))


#获取资源文件路径
file_path = path + r"\src"

#加载ui
manager_ui = file_path + r"\MainWindow.ui"



# #图片总字典，用于保存图片类型
# image_dir = {}



# #图片描述字典
# image_describe_dir = {}



class ManagerWindow(QtWidgets.QWidget):
    """主窗口类"""
    def __init__(self):
        super(ManagerWindow,self).__init__()
        
        #加载ui,并设置ui界面
        loader = QLoader.QUiLoader()
        self.ui = loader.load(manager_ui)
        self.ui.setParent(self)
        
        #设置窗口名称
        self.setWindowTitle("资产浏览器")

        #设置布局
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.ui)


        #获取ui控件
        self.fileMenu = self.ui.findChild(QtWidgets.QMenu, "menu")
        self.helpMenu = self.ui.findChild(QtWidgets.QMenu, "menu_help")

        self.toolBox = self.ui.findChild(QtWidgets.QToolBox,"toolBox")

        self.widget_source = self.ui.findChild(QtWidgets.QWidget,"widget_source")

        self.btn_pic_men = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_men")
        self.btn_pic_sence = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_sence")   
        self.btn_pic_goods = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_goods")
        self.btn_pic_texture = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_texture")
        self.btn_pic_other = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_other")  


        self.btn_mod_men = self.ui.findChild(QtWidgets.QPushButton,"btn_mod_men")  
        self.btn_mod_sence = self.ui.findChild(QtWidgets.QPushButton, "btn_mod_sence")
        self.btn_mod_goods = self.ui.findChild(QtWidgets.QPushButton, "btn_mod_goods")
        self.btn_mod_other = self.ui.findChild(QtWidgets.QPushButton, "btn_mod_other")
      
        

        #资源浏览器布局
        self.widget_source.setLayout(QtWidgets.QVBoxLayout())

        #初次打开，加载人物图片界面
        self.childWidget = PicDialog.PicWidget("pic_men")
        self.widget_source.layout().addWidget(self.childWidget)
        
        #为ui控件添加动作
        self.actionOpen = self.fileMenu.addAction(u"打开")
        self.actionAbout = self.helpMenu.addAction(u"关于")

        #连接信号与槽
        self.actionOpen.triggered.connect(self.openFile)
        self.actionAbout.triggered.connect(self.openAbout)

        #图片按钮点击
        self.btn_pic_men.clicked.connect(lambda: self.loadPicWin("pic_men"))
        self.btn_pic_sence.clicked.connect(lambda: self.loadPicWin("pic_sence"))
        self.btn_pic_goods.clicked.connect(lambda: self.loadPicWin("pic_goods"))
        self.btn_pic_texture.clicked.connect(lambda: self.loadPicWin("pic_texture"))
        self.btn_pic_other.clicked.connect(lambda: self.loadPicWin("pic_other"))

        #模型按钮点击
        self.btn_mod_men.clicked.connect(lambda: self.loadModWin("mod_men"))
        self.btn_mod_sence.clicked.connect(lambda: self.loadModWin("mod_sence"))
        self.btn_mod_goods.clicked.connect(lambda: self.loadModWin("mod_goods"))
        self.btn_mod_other.clicked.connect(lambda: self.loadModWin("mod_other"))


        
    #加载人物图片浏览器
    def loadPicWin(self,windowName):

        #实例化图片窗口
        self.widget_source.layout().removeWidget(self.childWidget)
        self.childWidget.close()

        #打开图片
        self.childWidget = PicDialog.PicWidget(windowName)
        self.widget_source.layout().addWidget(self.childWidget)


    def loadModWin(self,windowName):
         #实例化图片窗口
        self.widget_source.layout().removeWidget(self.childWidget)
        self.childWidget.close()

        #打开图片
        self.childWidget = ModelDialog.ModalWidget(windowName)
        self.widget_source.layout().addWidget(self.childWidget)


    #打开文件浏览器，返回文件路径
    def openFile(self): 

        dialog = QtWidgets.QFileDialog() 
        
        
        #根据当前所在文件目录，设置默认打开文件格式
        if self.toolBox.currentIndex() == 0:
            dialog.setNameFilter("全部文件 (*);;图片文件(*.jpg *.png)")
        elif self.toolBox.currentIndex() == 1:
            dialog.setNameFilter("模型文件(*.obj)")

        #加载对应的文件
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)

        # #用于储存图片数据
        # self.fileNames = []
        
        if dialog.exec_():
            self.fileNames = dialog.selectedFiles()


        #判断当前所在资源窗口
        if(self.childWidget.windowName == "pic_men"):
            self.childWidget.openPicture(self.fileNames,"pic_men")
        elif(self.childWidget.windowName == "pic_sence"):
            self.childWidget.openPicture(self.fileNames,"pic_sence")
        elif(self.childWidget.windowName == "pic_goods"):
            self.childWidget.openPicture(self.fileNames,"pic_goods")
        elif(self.childWidget.windowName == "pic_texture"):
            self.childWidget.openPicture(self.fileNames,"pic_texture")
        elif(self.childWidget.windowName == "pic_other"):
            self.childWidget.openPicture(self.fileNames,"pic_other")

        elif (self.childWidget.windowName == "mod_men"):
            self.childWidget.openModal(self.fileNames, "mod_men")
        elif (self.childWidget.windowName == "mod_goods"):
            self.childWidget.openModal(self.fileNames, "mod_goods")
        elif (self.childWidget.windowName == "mod_sence"):
            self.childWidget.openModal(self.fileNames, "mod_sence")
        elif (self.childWidget.windowName == "mod_other"):
            self.childWidget.openModal(self.fileNames, "mod_other")


    #打开关于对话框
    def openAbout(self):
        self.about_win = AboutDialog.AboutDialogWin()
        self.about_win.show()




MyWin = ManagerWindow()
MyWin.show()