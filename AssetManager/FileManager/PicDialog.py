# coding:utf-8
import PySide2.QtUiTools as QLoader
from PySide2 import QtWidgets,QtGui,QtCore
import hou 
import os,json
import sys



#获取当前文件所在文件目录
path = os.path.dirname(os.path.abspath(__file__))


file_path = path + r"\src"

pic_info_ui = file_path + r"\pic_info.ui"


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
    def openPicture(self,fileNames,windowName):
        

        #加载保存数据到字典
        with open(file_path + "\picture.json") as js:
            image_child_dir = (json.load(js))[windowName]

        for file_name in fileNames:
            #获取文件名
            name = (file_name.split("/"))[-1]  
            
            #如果文件名已存在，弹出MessaBox,否则加载到资源浏览器中
            if name in image_child_dir.keys():

                print name + " has exited"
                
                # msg = QtWidgets.QMessageBox()
                # msg.setText(u"文件名重复，请重命名后再加载")
                # msg.setParent(self)
                # msg.setStyleSheet("background-color:rgb(128,128,128);color:rgb(255,255,255);")
                # msg.setWindowModality(QtCore.Qt.ApplicationModal)
                # msg.show()

            else:  
                        
                #保存文件，下次打开时自动初始化
                self.savePicture(file_name,windowName)

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
        self.btn_close =  self.ui.findChild(QtWidgets.QPushButton, "img_btn_close")
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
