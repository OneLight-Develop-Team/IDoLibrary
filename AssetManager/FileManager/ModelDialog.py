# coding:utf-8
import PySide2.QtUiTools as QLoader
from PySide2 import QtWidgets,QtGui,QtCore
import hou 
import os,json
import sys
import ModelInfoDialog
reload(ModelInfoDialog)

#获取当前文件所在文件目录
path = os.path.dirname(os.path.abspath(__file__))
file_path = path + r"\src"

class ModalWidget(QtWidgets.QWidget):
    """模型浏览器类"""
    def __init__(self,windowName):
        super(ModalWidget, self).__init__()
        
        #获取窗口类型
        self.windowName = windowName

        print windowName

        #资源浏览器的行数与列数
        self.columnNum = 0
        self.rowNum = 0

        self.tool_button = ToolButton("mame", self.windowName)
        
        #加载初始界面模型
        self.loadModal(self.windowName)

        

    #加载初始图片
    def loadModal(self,windowName):
        #加载保存数据到字典
        with open(file_path + "\modal.json") as js:
            image_dir = json.load(js)
            
        #获取字典里的子字典
        modal_child_dir = image_dir[windowName]

        #设置布局
        self.setLayout(QtWidgets.QGridLayout())
        
        #从json文件中加载初始图片，并在窗口中显示出来
        for key in modal_child_dir:
            
            #获取文件名
            self.name = (modal_child_dir[key].split("/"))[-1]

            #实例化一个图标按钮
            self.tool_button = ToolButton(modal_child_dir[key],windowName)

            #添加按钮
            self.layout().addWidget(self.tool_button,self.rowNum,self.columnNum)

            #设置布局为5列n行
            if(self.columnNum >= 4 ):
                self.rowNum += 1
                self.columnNum = 0
            else:
                self.columnNum += 1


        #重置资源浏览器的行数与列数
        self.columnNum = 0
        self.rowNum = 0
        
    #加载图片按钮到资源浏览器   
    def openModal(self, fileNames, windowName):
        
        #加载保存数据到字典
        with open(file_path + "\modal.json") as js:
            mod_child_dir = (json.load(js))[windowName]

        

        for file_name in fileNames:
            #获取文件名
            name = (file_name.split("/"))[-1]  
            
            #如果文件名已存在，弹出MessaBox,否则加载到资源浏览器中
            if name in mod_child_dir.keys():

                print name + " has exited"

            else:
                #保存文件，下次打开时自动初始化
                self.saveModal(file_name, windowName)
                #重新加载图片数据
                self.loadModal(windowName)

    def saveModal(self, fileName, windowName):
        
        #获取文件名
        name = (fileName.split("/"))[-1]

        #加载保存数据到字典
        with open(file_path + "\modal.json") as js:
            modal_dir = json.load(js)

        #写入到字典中
        modal_dir[windowName][name] = fileName

        #写入数据到json
        with open(file_path + "\modal.json", 'w') as json_file:
            json.dump(modal_dir,json_file,indent=4)  

class ToolButton(QtWidgets.QToolButton):
        """资源浏览器加载进来后的图标按钮"""
        def __init__(self,mod_path,windowName):
            super(ToolButton, self).__init__()

            self.mod_path = mod_path

            #获取文件名
            self.name = (mod_path.split("/"))[-1] 
            
            #获取窗口名
            self.windowName = windowName

            #设置样式
            self.setAutoRaise(True)
            self.setMaximumSize(400,400)
            self.setMinimumSize(100,100)
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

            #加载图片
            self.obj_img = file_path + "\objimg.jpg"


            #加载并设置图标
            pixmap = QtGui.QPixmap(self.obj_img)
            self.setIcon(pixmap)
            self.setIconSize(self.size())
     

            #设置图片名称
            self.setText(self.name)

            # self.pic_win = InfoWidget(self.image_path,self.windowName)

            #点击图标，弹出描述对话框
            self.clicked.connect(lambda: self.openInfoWin(self.mod_path))

            #接受删除信号
            # self.pic_win.del_signal.connect(self.SetDefaultMap)



        def openInfoWin(self, filePath):
            ModelInfoDialog.createObj(filePath)

            