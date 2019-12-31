# coding:utf-8
import PySide2.QtUiTools as QLoader
from PySide2 import QtWidgets,QtGui,QtCore
import hou 
import os,json,re,shutil
import sys


import AboutDialog
reload(AboutDialog)


#获取C:\Users\用户名的路径
path = os.getcwd()

#获取资源文件路径
file_path = path + r"\Documents\houdini17.0\python2.7libs\src"

#暂无截图图标路径
not_screenshot_path = file_path + r"\not_screenshot.jpg"
#储存截图文件夹路径
screenshot_path = file_path + r"\screenshot"

#加载ui
manager_ui = path + r"\Documents\houdini17.0\python2.7libs\src\MainWindow.ui"
pic_info_ui = file_path + "\pic_info.ui"

model_info_ui = file_path + "\model_info.ui"
confirm_screenshot_ui = file_path + "\confirm_screenshot.ui"

#图片总字典，用于保存图片类型
image_dir = {}

#图片描述字典
image_describe_dir = {}

#模型总字典
model_dir = {}
#模型描述字典
model_describe_dir = {}
#模型截图字典
model_screenshot_dir = {}

#获取当前Qt应用程序实例
app = QtWidgets.QApplication.instance()

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

        self.widget_source = self.ui.findChild(QtWidgets.QWidget,"widget_source")

        self.btn_pic_men = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_men")
        self.btn_pic_sence = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_sence")
        self.btn_pic_goods = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_goods")
        self.btn_pic_texture = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_texture")
        self.btn_pic_other = self.ui.findChild(QtWidgets.QPushButton,"btn_pic_other")

        self.btn_model_men = self.ui.findChild(QtWidgets.QPushButton,"btn_model_men")
        self.btn_model_scene = self.ui.findChild(QtWidgets.QPushButton, "btn_model_scene")
        self.btn_model_object = self.ui.findChild(QtWidgets.QPushButton, "btn_model_object")
        self.btn_model_other = self.ui.findChild(QtWidgets.QPushButton, "btn_model_other")


        #资源浏览器布局
        self.widget_source.setLayout(QtWidgets.QVBoxLayout())

        #初次打开，加载人物图片界面
        self.childWidget = PicWidget("men")
        #self.childWidget = ModelWidget("model_men")
        self.widget_source.layout().addWidget(self.childWidget)
        
        #为ui控件添加动作
        self.actionOpen = self.fileMenu.addAction(u"打开")
        self.actionAbout = self.helpMenu.addAction(u"关于")

        #连接信号与槽
        self.actionOpen.triggered.connect(self.openFile)
        self.actionAbout.triggered.connect(self.openAbout)

        self.btn_pic_men.clicked.connect(lambda: self.loadPicWin("men"))
        self.btn_pic_sence.clicked.connect(lambda: self.loadPicWin("sence"))
        self.btn_pic_goods.clicked.connect(lambda: self.loadPicWin("goods"))
        self.btn_pic_texture.clicked.connect(lambda: self.loadPicWin("texture"))
        self.btn_pic_other.clicked.connect(lambda: self.loadPicWin("other"))

        self.btn_model_men.clicked.connect(lambda: self.loadModelWin("model_men"))
        self.btn_model_scene.clicked.connect(lambda: self.loadModelWin("model_scene"))
        self.btn_model_object.clicked.connect(lambda: self.loadModelWin("model_object"))
        self.btn_model_other.clicked.connect(lambda: self.loadModelWin("model_other"))
        
    #加载人物图片浏览器
    def loadPicWin(self,windowName):

        #实例化图片窗口
        self.widget_source.layout().removeWidget(self.childWidget)
        self.childWidget.close()

        #打开图片
        self.childWidget = PicWidget(windowName)
        self.widget_source.layout().addWidget(self.childWidget)

        # if(windowName=="model_man"):
        #     self.childWidget = ModelWidget(windowName)
        #     self.widget_source.layout().addWidget(self.childWidget)
        # else:
        #     self.childWidget = PicWidget(windowName)
        #     self.widget_source.layout().addWidget(self.childWidget)

    #打开文件浏览器，返回文件路径
    def openFile(self): 

        dialog = QtWidgets.QFileDialog() 

        #加载对应的文件
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)


        if dialog.exec_():
            fileNames = dialog.selectedFiles()

            #Todo:弹出窗口，判断文件类型，加载资源到文件栏
            #Todo:一次加载多个文件
        
        #判断当前所在资源窗口
        if(self.childWidget.windowName == "men"):
            self.childWidget.openPicture(fileNames[0],"men")
        elif(self.childWidget.windowName == "sence"):
            self.childWidget.openPicture(fileNames[0],"sence")
        elif(self.childWidget.windowName == "goods"):
            self.childWidget.openPicture(fileNames[0],"goods")
        elif(self.childWidget.windowName == "texture"):
            self.childWidget.openPicture(fileNames[0],"texture")
        elif(self.childWidget.windowName == "other"):
            self.childWidget.openPicture(fileNames[0],"other")

        elif (self.childWidget.windowName == "model_men"):
            self.childWidget.openModel(fileNames[0],"model_men")
        elif (self.childWidget.windowName == "model_sence"):
            self.childWidget.openModel(fileNames[0],"model_scene")
        elif (self.childWidget.windowName == "model_object"):
            self.childWidget.openModel(fileNames[0],"model_object")
        elif (self.childWidget.windowName == "model_other"):
            self.childWidget.openModel(fileNames[0],"model_other")

    #加载模型图片浏览器
    def loadModelWin(self,windowName):
        # 实例化图片窗口
        self.widget_source.layout().removeWidget(self.childWidget)
        self.childWidget.close()
        # 打开图片
        self.childWidget = ModelWidget(windowName)
        self.widget_source.layout().addWidget(self.childWidget)

    #打开关于对话框
    def openAbout(self):
        self.about_win = AboutDialog.AboutDialogWin()
        self.about_win.show()
        
class PicWidget(QtWidgets.QWidget):
    """图片浏览器类"""
    def __init__(self,windowName):
        super(PicWidget,self).__init__()

        #获取窗口类型
        self.windowName = windowName

        #资源浏览器的行数与列数
        self.columnNum = 0
        self.rowNum = 0

        self.tool_button = ToolButton("name",self.windowName)

        #加载初始界面图片
        self.loadPicture(self.windowName)
 
    
    #用于初始加载所有图片,以及重新排序所有图片
    def loadPicture(self,windowName):
        #加载保存数据到字典
        with open(file_path + "\picture.json") as js:
            image_dir = json.load(js)

        #获取字典里的子字典
        image_child_dir = image_dir[windowName]

        #设置布局
        self.setLayout(QtWidgets.QGridLayout())

        #从json文件中加载初始图片，并在窗口中显示出来
        for key in image_child_dir:

            #获取文件名
            self.name = (image_child_dir[key].split("/"))[-1]

            #实例化一个图标按钮
            self.tool_button = ToolButton(image_child_dir[key],windowName)

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
    def openPicture(self,name,windowName):


        #加载保存数据到字典
        with open(file_path + "\picture.json") as js:
            image_child_dir = (json.load(js))[windowName]

        #获取文件名
        file_name = (name.split("/"))[-1]

        #如果文件名已存在，弹出MessaBox,否则加载到资源浏览器中
        if file_name in image_child_dir.keys():


            msg = QtWidgets.QMessageBox()
            msg.setText(u"文件名重复，请重命名后再加载")
            msg.setParent(self)
            msg.setStyleSheet("background-color:rgb(128,128,128);color:rgb(255,255,255);")
            msg.setWindowModality(QtCore.Qt.ApplicationModal)
            msg.show()

        else:

            #保存文件，下次打开时自动初始化
            self.savePicture(name,windowName)

            #重新加载图片数据
            self.loadPicture(windowName)

   
    #保存图片到json文件中
    def savePicture(self,fileName,windowName):
        

        #获取文件名
        name = (fileName.split("/"))[-1]        


        #加载保存数据到字典
        with open(file_path + "\picture.json") as js:
            image_dir = json.load(js)

        
        #写入到字典中
        image_dir[windowName][name] = fileName

        #写入数据到json文件中
        with open(file_path + "\picture.json", 'w') as json_file:
            json.dump(image_dir,json_file,indent=4)
    
class ToolButton(QtWidgets.QToolButton):
    """资源浏览器加载进来后的图标按钮"""
    def __init__(self,image_path,windowName):
        super(ToolButton,self).__init__()
        self.image_path = image_path

        #获取文件名
        self.name = (image_path.split("/"))[-1]   
        
        #获取窗口名
        self.windowName = windowName

        #设置样式
        self.setAutoRaise(True)
        self.setMaximumSize(400,400)
        self.setMinimumSize(100,100)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.defaultMap = file_path + "\defaultMap.jpg"

        #加载并设置图标
        pixmap = QtGui.QPixmap(self.image_path)
        self.setIcon(pixmap)
        self.setIconSize(self.size())
  
        #设置图片名称
        self.setText(self.name)

        self.pic_win = InfoWidget(self.image_path,self.windowName)

        #点击图标，弹出描述对话框
        self.clicked.connect(lambda: self.openInfoWin(self.image_path))

        #接受删除信号
        self.pic_win.del_signal.connect(self.SetDefaultMap)

    #加载并设置默认图标,并断开信号与槽连接，防止再按到  
    def SetDefaultMap(self):
        self.clicked.disconnect()
       
        pixmap = QtGui.QPixmap(self.defaultMap)
        self.setIcon(pixmap)
        self.setIconSize(self.size())

    #弹出图片描述对话框
    def openInfoWin(self,image_path):
        self.pic_win.show()

class InfoWidget(QtWidgets.QWidget):
    """图片信息窗口类"""
    #自定义信号
    del_signal = QtCore.Signal()
    
    def __init__(self,image_path,windowName):
        super(InfoWidget,self).__init__()
        #设置窗口名称
        self.setWindowTitle("图片预览窗口")
        self.windowName = windowName
        self.image_path = image_path

        #获取文件名
        self.file_name = (self.image_path.split("/"))[-1]  

        #加载ui,并设置ui界面
        loader = QLoader.QUiLoader()
        self.ui = loader.load(pic_info_ui)
        self.ui.setParent(self)

        #设置布局
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.ui)

        #设置样式
        self.setStyleSheet("background-color:rgb(128,128,128);color:rgb(255,255,255);")

        #加载控件
        self.btn_close = self.ui.findChild(QtWidgets.QPushButton, "img_btn_close")
        self.btn_del = self.ui.findChild(QtWidgets.QPushButton,"img_btn_del")
        self.label_pic = self.ui.findChild(QtWidgets.QLabel,"label_pic")
        self.label_name = self.ui.findChild(QtWidgets.QLabel,"label_name")
        self.textEdit_describe = self.ui.findChild(QtWidgets.QTextEdit,"textEdit_describe")

        #设置文本编辑框样式
        self.textEdit_describe.setStyleSheet("background-color:rgb(64,64,64);font: 16pt 'Agency FB';color:rgb(255,255,255);")

        self.label_name.setText(self.file_name)

        #关闭窗口按钮的信号连接
        self.btn_close.clicked.connect(self.close)
        
        #删除图片
        self.btn_del.clicked.connect(lambda : self.delPic(self.file_name,windowName))

        #写入图片描述信号连接
        self.textEdit_describe.textChanged.connect(lambda:self.saveDescribe(self.file_name,windowName))

        #加载图片,图片保持比例
        pixmap = QtGui.QPixmap()
        pixmap.load(self.image_path)
        self.label_pic.setPixmap(pixmap)
        
        #设置图片自适应背景
        self.label_pic.setMaximumSize(600,600)
        self.label_pic.setScaledContents(True)

        self.loadDescribe(self.file_name,windowName)
        

    #加载图片描述
    def loadDescribe(self,filename,windowName):
        #加载数据到字典
        with open(file_path + "\pic_describe.json") as js:
            image_describe_dir = json.load(js)

        image_describe_child_dir = image_describe_dir[windowName]

        #如果字典里能找得到描述内容，则加载到描述对话框
        if(filename in image_describe_child_dir.keys()):
            self.textEdit_describe.setText(image_describe_child_dir[filename])

    #保存图片描述到json文件
    def saveDescribe(self,filename,windowName):

        #加载数据到字典
        with open(file_path + "\pic_describe.json") as js:
            image_describe_dir = json.load(js)

        #获取文件名
        name = (filename.split("/"))[-1]        

        #写入到字典中
        image_describe_dir[windowName][name] = self.textEdit_describe.toPlainText()

        #写入数据到json文件中
        with open(file_path + "\pic_describe.json", 'w') as json_file:
            json.dump(image_describe_dir,json_file,indent=4)

    #删除图片
    def delPic(self,filename,windowName):
        
        #获取文件名
        name = (filename.split("/"))[-1] 

        #删除json里的图片，然后重新加载布局
        with open(file_path + "\picture.json") as js:
            image_dir = json.load(js)
          
        del image_dir[windowName][name]

        #重新写入json文件
        with open(file_path + "\picture.json", 'w') as json_file:
            json.dump(image_dir,json_file,indent=4)

        
        #删除json里的文字描述，然后重新加载布局
        with open(file_path + "\pic_describe.json") as js_des:
            image_describe_dir = json.load(js_des)
        
        image_describe_child_dir = image_describe_dir[windowName]

        #删除json文件里的描述
        if name in image_describe_child_dir.keys():
            del image_describe_dir[windowName][name]

        #重新写入json文件
        with open(file_path + "\pic_describe.json", 'w') as json_desfile:
            json.dump(image_describe_dir,json_desfile,indent=4)

        #删除完关闭窗口
        self.close()

        #发送信号到资产浏览器，进行窗口按钮重绘
        self.del_signal.emit()

class ModelWidget(QtWidgets.QWidget):
    """模型浏览器类"""
    def __init__(self,windowName):
        super(ModelWidget,self).__init__()
        #获取窗口类型
        self.windowName = windowName
        #资源浏览器的行数与列数
        self.columnNum = 0
        self.rowNum = 0
        self.tool_button = ModelToolButton("name",self.windowName)
        #加载初始界面图片
        self.loadModel(self.windowName)

    #加载、排列模型的图片
    def loadModel(self, windowName):
        # 加载保存数据到字典
        with open(file_path + "\model.json") as js:
            model_dir = json.load(js)
        # 获取字典里的子字典
        model_child_dir = model_dir[windowName]
        # 设置布局
        self.setLayout(QtWidgets.QGridLayout())
        # 从json文件中加载初始图片，并在窗口中显示出来
        for key in model_child_dir:
            # 获取文件名
            self.name = (model_child_dir[key].split("/"))[-1]
            # 实例化一个图标按钮
            self.tool_button = ModelToolButton(model_child_dir[key], windowName)
            # 添加按钮
            self.layout().addWidget(self.tool_button, self.rowNum, self.columnNum)
            # 设置布局为5列n行
            if (self.columnNum >= 4):
                self.rowNum += 1
                self.columnNum = 0
            else:
                self.columnNum += 1

        # 重置资源浏览器的行数与列数
        self.columnNum = 0
        self.rowNum = 0

    # 加载模型按钮到资源浏览器
    def openModel(self, name, windowName):
        # 加载保存数据到字典
        with open(file_path + "\model.json") as js:
            model_child_dir = (json.load(js))[windowName]
        # 获取文件名
        file_name = (name.split("/"))[-1]

        # 如果文件名已存在，弹出MessaBox,否则加载到资源浏览器中
        if file_name in model_child_dir.keys():
            msg = QtWidgets.QMessageBox()
            msg.setText(u"文件名重复，请重命名后再加载")
            msg.setParent(self)
            msg.setStyleSheet("background-color:rgb(128,128,128);color:rgb(255,255,255);")
            msg.setWindowModality(QtCore.Qt.ApplicationModal)
            msg.show()

        else:
            # 保存文件，下次打开时自动初始化
            self.saveModel(name, windowName)
            # 重新加载图片数据
            self.loadModel(windowName)

    # 保存模型到json文件中
    def saveModel(self, fileName, windowName):
        # 获取文件名
        name = (fileName.split("/"))[-1]
        # 加载保存数据到字典
        with open(file_path + "\model.json") as js:
            model_dir = json.load(js)
        # 写入到字典中
        model_dir[windowName][name] = fileName
        # 写入数据到json文件中
        with open(file_path + "\model.json", 'w') as json_file:
           json.dump(model_dir, json_file, indent=4)

        #加载模型截图字典
        with open(file_path + "\model_screenshot.json") as jsc:
            model_screenshot_dir = json.load(jsc)

        #各个视图截图设置为0，即未截图。
        model_screenshot_dir[windowName][name + "_free"] = 0
        model_screenshot_dir[windowName][name + "_front"] = 0
        model_screenshot_dir[windowName][name + "_left"] = 0
        model_screenshot_dir[windowName][name + "_vertical"] = 0

        #写入数据到模型截图字典
        with open(file_path + "\model_screenshot.json",'w') as jsc_file:
            json.dump(model_screenshot_dir,jsc_file,indent=4)

class ModelToolButton(QtWidgets.QToolButton):
    def __init__(self, model_path, windowName):
        super(ModelToolButton, self).__init__()
        self.model_path = model_path
        # 获取文件名
        self.name = (model_path.split("/"))[-1]
        # 获取窗口名
        self.windowName = windowName
        # 设置样式
        self.setAutoRaise(True)
        self.setMaximumSize(400, 400)
        self.setMinimumSize(100, 100)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.defaultMap = file_path + "\defaultMap.jpg"

        #加载模型预览图
        self.loadModelView(self.windowName)

        self.model_win = ModelInfoWidget(self.model_path, self.windowName)

        # 点击图标，弹出描述对话框
        self.clicked.connect(lambda: self.openInfoWin(self.model_path))

        # 接受删除信号
        self.model_win.del_signal.connect(self.SetDefaultMap)

        #接受截图信号
        self.model_win.screenshot_signal.connect(lambda :self.loadModelView(self.windowName))

    def SetDefaultMap(self):
        self.clicked.disconnect()
        pixmap = QtGui.QPixmap(self.defaultMap)
        self.setIcon(pixmap)
        self.setIconSize(self.size())

    def openInfoWin(self,model_path):
        self.model_win.show()

    #加载模型浏览图
    def loadModelView(self,windowName):

        # 加载模型截图字典
        with open(file_path + "\model_screenshot.json") as jsc:
            model_screenshot_dir = json.load(jsc)
        model_screenshot_child_dir = model_screenshot_dir[windowName]

        # 如果截图字典里存在该模型
        if (model_screenshot_child_dir.has_key('%s' % self.name + "_free")):
            # 如果该模型不存在截图
            if (model_screenshot_child_dir[self.name + "_free"] == 0):
                # 加载并设置图标
                pixmap = QtGui.QPixmap(not_screenshot_path)
            else:
                model_name = self.name.split(".")[0]
                pixmap = QtGui.QPixmap(screenshot_path + r"\%s" % model_name + "_free" + ".jpg")
        else:
            pixmap = QtGui.QPixmap(not_screenshot_path)

        self.setIcon(pixmap)
        self.setIconSize(self.size())
        self.setText(self.name)


class ModelInfoWidget(QtWidgets.QWidget):
    """模型信息窗口类"""
    # 自定义信号
    del_signal = QtCore.Signal()#删除信号
    screenshot_signal = QtCore.Signal()#截图信号

    def __init__(self, model_path, windowName):
        super(ModelInfoWidget, self).__init__()
        # 设置窗口名称
        self.setWindowTitle("图片预览窗口")
        self.windowName = windowName
        self.model_path = model_path
        # 获取文件名
        self.file_name = (self.model_path.split("/"))[-1]
        # 加载ui,并设置ui界面
        loader = QLoader.QUiLoader()
        self.ui = loader.load(model_info_ui)
        self.ui.setParent(self)
        # 设置布局
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.ui)
        # 设置样式
        self.setStyleSheet("background-color:rgb(128,128,128);color:rgb(255,255,255);")
        # 加载控件
        self.btn_screenshot = self.ui.findChild(QtWidgets.QPushButton,"btn_screenshot")
        self.btn_see_model = self.ui.findChild(QtWidgets.QPushButton,"btn_see_model")
        self.btn_close = self.ui.findChild(QtWidgets.QPushButton, "model_btn_close")
        self.btn_del = self.ui.findChild(QtWidgets.QPushButton, "model_btn_del")

        self.label_model_freeView = self.ui.findChild(QtWidgets.QLabel, "label_model_freeView")
        self.label_model_frontView = self.ui.findChild(QtWidgets.QLabel, "label_model_frontView")
        self.label_model_leftView = self.ui.findChild(QtWidgets.QLabel, "label_model_leftView")
        self.label_model_verticalView = self.ui.findChild(QtWidgets.QLabel, "label_model_verticalView")

        self.label_name = self.ui.findChild(QtWidgets.QLabel, "label_name")
        self.textEdit_describe = self.ui.findChild(QtWidgets.QTextEdit, "model_describe")
        self.textEdit_modelPath = self.ui.findChild(QtWidgets.QTextEdit,"model_file_path")

        self.rbtn_freeView = self.ui.findChild(QtWidgets.QRadioButton,"rbtn_freeView")
        self.rbtn_frontView = self.ui.findChild(QtWidgets.QRadioButton, "rbtn_frontView")
        self.rbtn_leftView = self.ui.findChild(QtWidgets.QRadioButton, "rbtn_leftView")
        self.rbtn_verticalView = self.ui.findChild(QtWidgets.QRadioButton, "rbtn_verticalView")

        #默认选中
        #self.rbtn_freeView.setDefault(True)

        #显示模型路径
        self.textEdit_modelPath.setReadOnly(True)
        self.textEdit_modelPath.setText(self.model_path)
        self.textEdit_modelPath.setStyleSheet(
            "background-color:rgb(64,64,64);font: 12pt 'Agency FB';color:rgb(255,255,255);")

        # 设置文本编辑框样式
        self.textEdit_describe.setStyleSheet(
            "background-color:rgb(64,64,64);font: 16pt 'Agency FB';color:rgb(255,255,255);")
        self.label_name.setText(self.file_name)
        # 关闭窗口按钮的信号连接
        self.btn_close.clicked.connect(self.close)
        # 删除模型
        self.btn_del.clicked.connect(lambda: self.delModel(self.file_name, windowName))
        # 写入图片描述信号连接
        self.textEdit_describe.textChanged.connect(lambda: self.saveDescribe(self.file_name, windowName))

        #单选按钮与截图信号连接
        self.rbtn_freeView.toggled.connect(lambda : self.screenshot_freeView())
        self.rbtn_frontView.toggled.connect(lambda : self.screenshot_frontView())
        self.rbtn_leftView.toggled.connect(lambda: self.screenshot_leftView())
        self.rbtn_verticalView.toggled.connect(lambda: self.screenshot_verticalView())

        #加载模型视图
        self.loadModelView("_free")
        self.loadModelView("_left")
        self.loadModelView("_front")
        self.loadModelView("_vertical")

        #浏览模型信号连接
        self.btn_see_model.clicked.connect(lambda: self.browseModel(self.model_path,self.file_name))

        self.loadDescribe(self.file_name, windowName)

    def loadDescribe(self, filename, windowName):
        # 加载数据到字典
        with open(file_path + "\model_describe.json") as js:
            model_describe_dir = json.load(js)
        model_describe_child_dir = model_describe_dir[windowName]
        # 如果字典里能找得到描述内容，则加载到描述对话框
        if (filename in model_describe_child_dir.keys()):
            self.textEdit_describe.setText(model_describe_child_dir[filename])

    # 删除模型
    def delModel(self, filename, windowName):
        # 获取文件名
        name = (filename.split("/"))[-1]
        # 删除json里的模型，然后重新加载布局
        with open(file_path + "\model.json") as js:
            model_dir = json.load(js)
        del model_dir[windowName][name]
        # 重新写入json文件
        with open(file_path + "\model.json", 'w') as json_file:
            json.dump(model_dir, json_file, indent=4)

        # 删除json里的文字描述
        with open(file_path + "\model_describe.json") as js_des:
            model_describe_dir = json.load(js_des)
        model_describe_child_dir = model_describe_dir[windowName]
        if (name) in model_describe_child_dir.keys():
            del model_describe_dir[windowName][name]
        # 重新写入json文件
        with open(file_path + "\model_describe.json", 'w') as json_desfile:
            json.dump(model_describe_dir, json_desfile, indent=4)

        # 删除截图字典里相应数据
        with open(file_path + "\model_screenshot.json") as jsc:
            model_screenshot_dir = json.load(jsc)

        #删除截图
        pixname = name.split(".")[0]
        if(model_screenshot_dir[windowName][name + "_free"] == 1):
            os.remove(screenshot_path + r"\%s" % pixname + "_free" + ".jpg")
        if (model_screenshot_dir[windowName][name + "_front"] == 1):
            os.remove(screenshot_path + r"\%s" % pixname + "_front" + ".jpg")
        if (model_screenshot_dir[windowName][name + "_left"] == 1):
            os.remove(screenshot_path + r"\%s" % pixname + "_left" + ".jpg")
        if (model_screenshot_dir[windowName][name + "_vertical"] == 1):
            os.remove(screenshot_path + r"\%s" % pixname + "_vertical" + ".jpg")

        del model_screenshot_dir[windowName][name + "_free"]
        del model_screenshot_dir[windowName][name + "_front"]
        del model_screenshot_dir[windowName][name + "_left"]
        del model_screenshot_dir[windowName][name + "_vertical"]
        # 写入数据到模型截图字典
        with open(file_path + "\model_screenshot.json", 'w') as jsc_file:
            json.dump(model_screenshot_dir, jsc_file, indent=4)

        # 删除完关闭窗口
        self.close()
        # 发送信号到资产浏览器，进行窗口按钮重绘
        self.del_signal.emit()

    def saveDescribe(self, filename, windowName):
        # 加载数据到字典
        with open(file_path + "\model_describe.json") as js:
            model_describe_dir = json.load(js)
        # 获取文件名
        name = (filename.split("/"))[-1]
        # 写入到字典中
        model_describe_dir[windowName][name] = self.textEdit_describe.toPlainText()
        # 写入数据到json文件中
        with open(file_path + "\model_describe.json", 'w') as json_file:
            json.dump(model_describe_dir, json_file, indent=4)

    #执行截图函数
    def do_screenshot(self,model_path,windowName,screenshot_name):

        screenshot = Screenshot()#截图类实例
        screenshot.pixmap  = grab_window()#截图函数
        screenshot.showFullScreen()#以全屏模式显示

        screenshot.icon_signal.connect(lambda :self.buildIcon(screenshot.sel_image,screenshot_name))

        # 获取文件名
        file_name = (model_path.split("/"))[-1]
        #将模型截图字典改成以截图（1）
        # 加载模型截图字典
        with open(file_path + "\model_screenshot.json") as jsc:
            model_screenshot_dir = json.load(jsc)
        model_screenshot_dir[windowName][file_name + screenshot_name] = 1
        # 写入数据到模型截图字典
        with open(file_path + "\model_screenshot.json", 'w') as jsc_file:
            json.dump(model_screenshot_dir, jsc_file, indent=4)

        #发射已截图信号，进行刷新
        self.screenshot_signal.emit()
        self.loadModelView(screenshot_name)

    # 建立图标,并保存起来
    def buildIcon(self,icon,screenshot_name):
        name = (self.file_name.split("."))[0]
        # 将传进来的图片保存起来，不然执行完函数就会被资源回收
        icon.save(screenshot_path + r"\%s"%name + screenshot_name + ".jpg")


    # 将图像转化为byte_array
    def encode_pixmap(self, pixmap):
        # byteArray + buffer 通过Base64将图片编码为二进制格式，MIMEDATA相关
        pix_bytes = QtCore.QByteArray()
        buffer = QtCore.QBuffer(pix_bytes)
        # buffer使用需要打开和关闭
        buffer.open(QtCore.QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG")
        return pix_bytes.toBase64().data()
        # return pix_bytes.toBase64().data()
        # pixmap有loadFromData（）可以加载bytearray数组

    #截浏览图
    def screenshot_freeView(self):
        self.screenshot_name = "_free"
        self.btn_screenshot.clicked.connect(lambda: self.do_screenshot(self.model_path, self.windowName,self.screenshot_name))

    #截主视图
    def screenshot_frontView(self):
        self.screenshot_name = "_front"
        self.btn_screenshot.clicked.connect(lambda: self.do_screenshot(self.model_path, self.windowName,self.screenshot_name))

    #截左视图
    def screenshot_leftView(self):
        self.screenshot_name = "_left"
        self.btn_screenshot.clicked.connect(lambda: self.do_screenshot(self.model_path, self.windowName,self.screenshot_name))

    #截俯视图
    def screenshot_verticalView(self):
        self.screenshot_name = "_vertical"
        self.btn_screenshot.clicked.connect(lambda: self.do_screenshot(self.model_path, self.windowName,self.screenshot_name))

    #加载模型视图
    def loadModelView(self,screenshot_name):
        # 加载模型截图字典
        pixmap = QtGui.QPixmap()
        with open(file_path + "\model_screenshot.json") as jsc:
            model_screenshot_dir = json.load(jsc)
        model_screenshot_child_dir = model_screenshot_dir[self.windowName]

        # 如果截图字典里存在该模型
        if (model_screenshot_child_dir.has_key('%s' % self.file_name + screenshot_name)):
            # 如果该模型不存在截图
            if (model_screenshot_child_dir[self.file_name + screenshot_name] == 0):
                # 加载并设置图标
                pixmap.load(not_screenshot_path)
            else:
                model_name = self.file_name.split(".")[0]
                pixmap.load(screenshot_path + r"\%s" % model_name + screenshot_name + ".jpg")
        else:
            pixmap.load(not_screenshot_path)

        if(screenshot_name == "_free"):
            self.label_model_freeView.setPixmap(pixmap)
            self.label_model_freeView.setMaximumSize(600, 600)
            self.label_model_freeView.setScaledContents(True)
        if (screenshot_name == "_front"):
            self.label_model_frontView.setPixmap(pixmap)
            self.label_model_frontView.setMaximumSize(600, 600)
            self.label_model_frontView.setScaledContents(True)
        if (screenshot_name == "_left"):
            self.label_model_leftView.setPixmap(pixmap)
            self.label_model_leftView.setMaximumSize(600, 600)
            self.label_model_leftView.setScaledContents(True)
        if (screenshot_name == "_vertical"):
            self.label_model_verticalView.setPixmap(pixmap)
            self.label_model_verticalView.setMaximumSize(600, 600)
            self.label_model_verticalView.setScaledContents(True)


    def browseModel(self,file_path,file_name):
        #self.run_ogl(file_path,file_name)
        pass

#确认截图窗口类
class confirmScreenshot(QtWidgets.QWidget):
    con_yes_signal = QtCore.Signal()
    con_cancel_signal = QtCore.Signal()
    def __init__(self):
        super(confirmScreenshot,self).__init__()
        self.setWindowTitle("确认截图")
        loader = QLoader.QUiLoader()
        self.ui = loader.load(confirm_screenshot_ui)
        self.ui.setParent(self)

        self.btn_Yes = self.ui.findChild(QtWidgets.QPushButton,"btn_Yes")
        self.btn_Cancel = self.ui.findChild(QtWidgets.QPushButton,"btn_Cancel")

        self.btn_Yes.clicked.connect(lambda :self.yes())
        self.btn_Cancel.clicked.connect(lambda :self.cancel())

    def yes(self):
        self.con_yes_signal.emit()


    def cancel(self):
        self.con_cancel_signal.emit()
        self.close()



#截图类
class Screenshot(QtWidgets.QWidget):
    # 截图的图片容器是self.label，label父级是self
    # 自定义一个信号，在选取截图区域之后发送信号
    icon_signal = QtCore.Signal()

    def __init__(self):
        super(Screenshot, self).__init__()
        # 跟踪鼠标
        self.setMouseTracking(True)

        # 将widget设置为屏幕大小
        # 额外设置一个独立的layout和label用来作为接收截图的容器
        self.vLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)

        # 用一个label来做一个截图容器
        self.label = QtWidgets.QLabel()
        self.vLayout.addWidget(self.label)

        # 声明两个成员变量，用来记录鼠标按下起始点和记录rubberBand选区
        self.origin = None
        self.rubberBand = None
        self.sel_image = None

        #确认窗口实例
        self.con_screenshot_win = confirmScreenshot()

    #键盘按下,.ESC关闭，SHIFT的时候，宽、高，哪个小取哪个。
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == QtCore.Qt.Key_Shift and self.rubberBand.height()>self.rubberBand.width():
            self.rubberBand.setMaximumHeight(self.rubberBand.width())
        if event.key() == QtCore.Qt.Key_Shift and self.rubberBand.height()<self.rubberBand.width():
            self.rubberBand.setMaximumWidth(self.rubberBand.height())

        # 松开SHIFT,设置最大值

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.rubberBand.setMaximumWidth(10000)
            self.rubberBand.setMaximumHeight(10000)

    # 把函数当做属性使用，可以get和set
    @property
    def pixmap(self):
        return self.label.pixmap()

    # 使用实例化的GrabThumbnail然后当成属性调用
    # self.ins_widget.pixmap = foo, foo自动对应到newpixmap参数
    @pixmap.setter
    def pixmap(self, newpixmap):
        self.label.setPixmap(newpixmap)

    #鼠标点下
    def mousePressEvent(self, event):
        # 鼠标事件特有的信息
        self.origin = event.pos()#点下的位置
        if not self.rubberBand:
            # RubberBand是选区类
            # 必须指定父类，不然需要单独销毁
            self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    # 鼠标移动
    def mouseMoveEvent(self, event):
        # 因为像素是一个像素，没有半个像素的说法，所以必须转化为整型变量
        cur_pos = event.pos()
        geoF = QtCore.QRectF(self.origin, cur_pos)
        geo = geoF.toRect()
        # 只能接收int rectangle
        self.rubberBand.setGeometry(geo)
        self.rubberBand.show()

    # 鼠标松开
    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        # 鼠标释放之后才会执行缩放
        # 把截图做个copy，然后缩放为100*100
        self.sel_image = self.pixmap.copy(self.rubberBand.geometry())
        self.sel_image = self.sel_image.scaled(QtCore.QSize(300, 300), aspectMode=QtCore.Qt.IgnoreAspectRatio,
                                                   mode=QtCore.Qt.SmoothTransformation)

        self.con_screenshot_win.show()
        self.con_screenshot_win.con_yes_signal.connect(lambda :self.icon_signal.emit())
        self.con_screenshot_win.con_yes_signal.connect(lambda: self.close())

        self.con_screenshot_win.con_cancel_signal.connect(lambda :self.close())

        # 单纯的信号发射，代表着现在鼠标已经松开了，需要做某些事情
        #self.icon_signal.emit()
        #self.close()  # 松开后关闭


# 函数返回当前鼠标的坐标所处对应屏幕的geometry
def monitor_geometry():
    return app.desktop().screenGeometry(QtGui.QCursor.pos())

# 截图函数
def grab_window():
    # 获取屏幕区域几何体
    rect = monitor_geometry()
    # WinID（）Returns the window system identifier of the widget.
    # grabWindow是类的静态方法，必须有类自身来调用
    # QPixmap实例化时传入图片路径即可使用图片资源
    pix = QtGui.QPixmap.grabWindow(app.desktop().winId(), rect.left(), rect.top(), rect.width(), rect.height())
    return pix

