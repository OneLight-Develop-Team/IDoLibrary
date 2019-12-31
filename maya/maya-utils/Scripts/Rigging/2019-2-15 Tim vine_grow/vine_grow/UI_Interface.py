# -*- coding:utf-8 -*-
import os
import json
from functools import partial
from maya import OpenMayaUI as omui
import maya.mel as mel
import maya.cmds as cmds
import plugin.Qt as Qt
# 识别当前的使用的Qt库 从而导入正确的库
if Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
elif Qt.__binding__ == 'PySide':
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
    from PySide.QtCore import *
    from PySide.QtGui import *
    import pysideuic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    import pyside2uic as uic
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO

def loadUiType(uiFile):
    """
    Pyside "loadUiType" command like PyQt4 has one, so we have to convert the 
    ui file to py code in-memory first and then execute it in a special frame
    to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type
        # in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('%s'%widget_class)

    return form_class, base_class

DIR_PATH = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR_PATH,"ui","vine_grow.ui")
GUI_STATE_PATH = os.path.join(DIR_PATH,"json",'GUI_STATE.json')
COLOR_INDEX_PATH = os.path.join(DIR_PATH,"json",'COLOR_INDEX.json')
form_class , base_class = loadUiType(UI_PATH)

# UI功能编写
class Interface(base_class,form_class):
    def __init__(self,dock="dock"):
        self.DOCK = dock
        # 读取当前DOCK属性
        if os.path.exists(GUI_STATE_PATH):
            GUI_STATE = {}
            with open(GUI_STATE_PATH,'r') as f:
                GUI_STATE = json.load(f)
            self.DOCK = GUI_STATE["DOCK"]
        
        # 如果2017以下的版 将workspace转换为dock
        if mel.eval("getApplicationVersionAsFloat;")<2017:
            if self.DOCK == "workspace":
                self.DOCK = "dock"

        ptr = self.Dock_Win_Management()
        
        super(Interface,self).__init__(parent=ptr)

        self.parent().layout().addWidget(self)
        self.setupUi(self)

        # 设置字体
        self.Bold_Font = QFont()
        self.Bold_Font.setBold(True)
        self.Normal_Font = QFont()
        self.Normal_Font.setBold(False)

        # 隐藏标签功能
        self.Rig_Obj_Toggle_Check = True
        self.Rig_Obj_Toggle.clicked.connect(self.Rig_Obj_Toggle_Fun)

        self.Loc_Generate_Toggle_Check = True
        self.Loc_Generate_Toggle.clicked.connect(self.Loc_Generate_Toggle_Fun)

        self.JNT_Setting_Toggle_Check = True
        self.JNT_Setting_Toggle.clicked.connect(self.JNT_Setting_Toggle_Fun)

        self.Rig_Generate_Toggle_Check = True
        self.Rig_Generate_Toggle.clicked.connect(self.Rig_Generate_Toggle_Fun)

        self.Namespace_Toggle_Check = True
        self.Namespace_Toggle.clicked.connect(self.Namespace_Toggle_Fun)

        self.Window_Setting_Toggle_Check = True
        self.Window_Setting_Toggle.clicked.connect(self.Window_Setting_Toggle_Fun)

        self.Attribute_Setting_Toggle_Check = True
        self.Attribute_Setting_Toggle.clicked.connect(self.Attribute_Setting_Toggle_Fun)
        
        # 隐藏选择按钮
        self.Rig_Obj_GetBtn.setVisible(False)
        self.Start_JNT_GetBtn.setVisible(False)
        self.End_JNT_GetBtn.setVisible(False)

        # 添加按钮功能
        self.Rig_Obj_Btn.clicked.connect(self.Get_Rig_Obj)
        self.Start_JNT_Btn.clicked.connect(self.Get_Start_JNT)
        self.End_JNT_Btn.clicked.connect(self.Get_End_JNT)

        # 限制数字输入
        self.Main_JNT_Num.setValidator(QIntValidator(3,1000))
        self.IK_JNT_Num.setValidator(QIntValidator(3,1000))
        self.Curve_Span_Num.setValidator(QIntValidator(3,1000))

        # 滑竿操作
        self.Main_JNT_Slider.valueChanged.connect(self.Main_JNT_Change)
        self.IK_JNT_Slider.valueChanged.connect(self.IK_JNT_Change)
        self.Curve_Span_Slider.valueChanged.connect(self.Curve_Span_Change)

        # 设置按钮不启用
        self.Loc_Generate_Btn.setEnabled(False)
        self.Rig_Generate_Btn.setEnabled(False)
        self.Switch_Btn.setEnabled(False)

        # 一键生成检测
        self.Rig_Obj_Text.textChanged.connect(self.Rig_Generate_Check)
        self.IK_JNT_Num.textChanged.connect(self.Rig_Generate_Check)
        self.End_JNT_Text.textChanged.connect(self.Rig_Generate_Check)

        # 设置默认命名
        self.Geo_Name_Text.setText("TengMan")
        self.Main_JNT_Name_Text.setText("gan_joint")
        self.IK_JNT_Name_Text.setText("ganJoint")
        self.Curve_Name_Text.setText("gan")
        self.IK_CTRL_Name_Text.setText("gan_ctrl")
        self.Start_Ctrl_Text.setText("main2")
        self.End_IK_Text.setText("main")
        self.Character_Ctrl_Text.setText("Character")

        # 设置按钮颜色
        self.IK_CTRL_ColorBtn.clicked.connect(partial(self.setColor,self.IK_CTRL_ColorBtn))
        self.Start_Ctrl_ColorBtn.clicked.connect(partial(self.setColor,self.Start_Ctrl_ColorBtn))
        self.End_IK_ColorBtn.clicked.connect(partial(self.setColor,self.End_IK_ColorBtn))
        self.Character_Ctrl_ColorBtn.clicked.connect(partial(self.setColor,self.Character_Ctrl_ColorBtn))

        self.IK_CTRL_ColorSlider.valueChanged.connect(partial(self.Slider_Change_Color,self.IK_CTRL_ColorBtn))
        self.Start_Ctrl_ColorSlider.valueChanged.connect(partial(self.Slider_Change_Color,self.Start_Ctrl_ColorBtn))
        self.End_IK_ColorSlider.valueChanged.connect(partial(self.Slider_Change_Color,self.End_IK_ColorBtn))
        self.Character_Ctrl_ColorSlider.valueChanged.connect(partial(self.Slider_Change_Color,self.Character_Ctrl_ColorBtn))

        if mel.eval("getApplicationVersionAsFloat;")<2017:
            self.IK_CTRL_ColorBtn.setEnabled(False)
            self.Start_Ctrl_ColorBtn.setEnabled(False)
            self.End_IK_ColorBtn.setEnabled(False)
            self.Character_Ctrl_ColorBtn.setEnabled(False)
        
        # 设置记录窗口
        self.Save_Path_GetBtn.setVisible(False)
        self.Load_Path_GetBtn.setVisible(False)
        self.Pick_Save_Path_Btn.clicked.connect(self.Browse_Save_File_Path)
        self.Pick_Load_Path_Btn.clicked.connect(self.Browse_Load_File_Path)
        self.Save_Path_Btn.clicked.connect(self.Save_File_Fun)
        self.Load_Path_Btn.clicked.connect(self.Load_File_Fun)

        # 添加修改保存
        self.Rig_Obj_Text.textChanged.connect(self.Text_Change_Fun)
        self.Start_JNT_Text.textChanged.connect(self.Text_Change_Fun)
        self.End_JNT_Text.textChanged.connect(self.Text_Change_Fun)
        self.Main_JNT_Num.textChanged.connect(self.Text_Change_Fun)
        self.IK_JNT_Num.textChanged.connect(self.Text_Change_Fun)
        self.Curve_Span_Num.textChanged.connect(self.Text_Change_Fun)
        self.Geo_Name_Text.textChanged.connect(self.Text_Change_Fun)
        self.Main_JNT_Name_Text.textChanged.connect(self.Text_Change_Fun)
        self.IK_JNT_Name_Text.textChanged.connect(self.Text_Change_Fun)
        self.Curve_Name_Text.textChanged.connect(self.Text_Change_Fun)
        self.IK_CTRL_Name_Text.textChanged.connect(self.Text_Change_Fun)
        self.Start_Ctrl_Text.textChanged.connect(self.Text_Change_Fun)
        self.End_IK_Text.textChanged.connect(self.Text_Change_Fun)
        self.Character_Ctrl_Text.textChanged.connect(self.Text_Change_Fun)
        
        self.Load_File()
    
    def Text_Change_Fun(self):
        self.Save_Json_File()

    def Load_File(self,path=GUI_STATE_PATH,load=False):
        if os.path.exists(path):
            GUI_STATE = {}
            with open(path,'r') as f:
                GUI_STATE = json.load(f)
            self.X_RadioButton.setChecked(GUI_STATE['X_RadioButton'])
            self.Y_RadioButton.setChecked(GUI_STATE['Y_RadioButton'])
            self.Z_RadioButton.setChecked(GUI_STATE['Z_RadioButton'])

            # 获取上次打开的text信息
            self.Rig_Obj_Text.setText(GUI_STATE['Rig_Obj_Text'])
            self.Start_JNT_Text.setText(GUI_STATE['Start_JNT_Text'])
            self.End_JNT_Text.setText(GUI_STATE['End_JNT_Text'])
            
            self.Main_JNT_Slider.setValue(int(GUI_STATE['Main_JNT_Num']))
            self.Main_JNT_Num.setText(GUI_STATE['Main_JNT_Num'])
            self.IK_JNT_Slider.setValue(int(GUI_STATE['IK_JNT_Num']))
            self.IK_JNT_Num.setText(GUI_STATE['IK_JNT_Num'])
            self.Curve_Span_Slider.setValue(int(GUI_STATE['Curve_Span_Num']))
            self.Curve_Span_Num.setText(GUI_STATE['Curve_Span_Num'])

            self.Tab_Widget.setCurrentIndex(int(GUI_STATE['Tab_Widget'])) 

            self.Geo_Name_Text.setText(GUI_STATE['Geo_Name_Text'])
            self.Main_JNT_Name_Text.setText(GUI_STATE['Main_JNT_Name_Text'])
            self.Curve_Name_Text.setText(GUI_STATE['Curve_Name_Text'])
            self.IK_JNT_Name_Text.setText(GUI_STATE['IK_JNT_Name_Text'])
            self.Delete_CheckBox.setChecked(GUI_STATE['Delete_CheckBox'])
            self.IK_CTRL_Name_Text.setText(GUI_STATE['IK_CTRL_Name_Text']) 
            self.Start_Ctrl_Text.setText(GUI_STATE['Start_Ctrl_Text']) 
            self.End_IK_Text.setText(GUI_STATE['End_IK_Text']) 
            self.Character_Ctrl_Text.setText(GUI_STATE['Character_Ctrl_Text']) 

            if self.Rig_Obj_Text.text() != "":
                try:
                    cmds.select(self.Rig_Obj_Text.text())
                except Exception:
                    pass
                self.Get_Rig_Obj()
                cmds.select(cl=True)


            if self.Start_JNT_Text.text() != "":
                try:
                    cmds.select(self.Start_JNT_Text.text())
                except Exception:
                    pass
                self.Get_Start_JNT()
                cmds.select(cl=True)

            if self.End_JNT_Text.text() != "":
                try:
                    cmds.select(self.End_JNT_Text.text())
                except Exception:
                    pass
                self.Get_End_JNT()
                cmds.select(cl=True)

            self.Rig_Generate_Check()

            # 设置颜色滑竿
            self.IK_CTRL_ColorSlider.setValue(int(GUI_STATE['IK_CTRL_ColorSlider']))
            self.Start_Ctrl_ColorSlider.setValue(int(GUI_STATE['Start_Ctrl_ColorSlider']))
            self.End_IK_ColorSlider.setValue(int(GUI_STATE['End_IK_ColorSlider']))
            self.Character_Ctrl_ColorSlider.setValue(int(GUI_STATE['Character_Ctrl_ColorSlider']))

            # 设置按钮颜色
            if mel.eval("getApplicationVersionAsFloat;")>=2017:

                r = GUI_STATE['IK_CTRL_ColorBtn'][0]
                g = GUI_STATE['IK_CTRL_ColorBtn'][1]
                b = GUI_STATE['IK_CTRL_ColorBtn'][2]
                self.IK_CTRL_ColorBtn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))

                r = GUI_STATE['Start_Ctrl_ColorBtn'][0]
                g = GUI_STATE['Start_Ctrl_ColorBtn'][1]
                b = GUI_STATE['Start_Ctrl_ColorBtn'][2]
                self.Start_Ctrl_ColorBtn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))

                r = GUI_STATE['End_IK_ColorBtn'][0]
                g = GUI_STATE['End_IK_ColorBtn'][1]
                b = GUI_STATE['End_IK_ColorBtn'][2]
                self.End_IK_ColorBtn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))

                r = GUI_STATE['Character_Ctrl_ColorBtn'][0]
                g = GUI_STATE['Character_Ctrl_ColorBtn'][1]
                b = GUI_STATE['Character_Ctrl_ColorBtn'][2]
                self.Character_Ctrl_ColorBtn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))

            else:
                # 设置滑竿颜色
                self.Slider_Change_Color(self.IK_CTRL_ColorBtn,self.IK_CTRL_ColorSlider.value())
                self.Slider_Change_Color(self.Start_Ctrl_ColorBtn,self.Start_Ctrl_ColorSlider.value())
                self.Slider_Change_Color(self.End_IK_ColorBtn,self.End_IK_ColorSlider.value())
                self.Slider_Change_Color(self.Character_Ctrl_ColorBtn,self.Character_Ctrl_ColorSlider.value())

            # 根据上次打开的记录expand 或者 collapse 标签
            self.Rig_Obj_Toggle_Check = GUI_STATE['Rig_Obj_Toggle_Check']
            self.Loc_Generate_Toggle_Check = GUI_STATE['Loc_Generate_Toggle_Check']
            self.JNT_Setting_Toggle_Check = GUI_STATE['JNT_Setting_Toggle_Check']
            self.JNT_Setting_Toggle_Check = GUI_STATE['JNT_Setting_Toggle_Check']
            self.Rig_Generate_Toggle_Check = GUI_STATE['Rig_Generate_Toggle_Check']
            self.Namespace_Toggle_Check = GUI_STATE['Namespace_Toggle_Check']
            self.Window_Setting_Toggle_Check = GUI_STATE['Window_Setting_Toggle_Check']

            self.Window_Setting_Toggle_Fun()
            self.Rig_Obj_Toggle_Fun()
            self.Loc_Generate_Toggle_Fun()
            self.JNT_Setting_Toggle_Fun()
            self.Rig_Generate_Toggle_Fun()
            self.Namespace_Toggle_Fun()

            self.Window_Setting_Toggle_Fun()
            self.Rig_Obj_Toggle_Fun()
            self.Loc_Generate_Toggle_Fun()
            self.JNT_Setting_Toggle_Fun()
            self.Rig_Generate_Toggle_Fun()
            self.Namespace_Toggle_Fun()
            
            return True
        else:

            if load==True:
                QMessageBox.warning(self, "Warning", "加载失败\n检查路径是否正确")
                return False

            # 设置默认属性
            self.IK_JNT_Slider.setValue(5)
            self.Main_JNT_Slider.setValue(20)
            self.Curve_Span_Slider.setValue(15)
            
            self.Slider_Change_Color(self.IK_CTRL_ColorBtn,17)
            self.Slider_Change_Color(self.Start_Ctrl_ColorBtn,18)
            self.Slider_Change_Color(self.End_IK_ColorBtn,13)
            self.Slider_Change_Color(self.Character_Ctrl_ColorBtn,14)
    
    def Save_File_Fun(self):
        Save_Path = self.Save_Path_Text.text()
        try:
            self.closeEvent(self.event,path=Save_Path)
        except:
            QMessageBox.warning(self, "Warning", "保存失败")
            traceback.print_exc()
            return
        QMessageBox.information(self, "保存成功", "保存成功")

    def Load_File_Fun(self):
        
        Load_Path = self.Load_Path_Text.text()
        check = self.Load_File(path=Load_Path,load=True)
        if check:
            QMessageBox.information(self, "加载成功", "加载成功")
        

    def Browse_Save_File_Path(self):
        save_file = QFileDialog.getSaveFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(save_file) is tuple:
            save_file = save_file[0]
        self.Save_Path_Text.setText(QDir.toNativeSeparators(save_file))
        self.Save_Path_Label.setVisible(False)
        self.Save_Path_GetBtn.setVisible(True)
        try :
            self.Save_Path_GetBtn.clicked.disconnect()
        except:
            pass
        self.Save_Path_GetBtn.clicked.connect(partial(self.Open_Directory,self.Save_Path_Text))

    def Browse_Load_File_Path(self):
        save_file = QFileDialog.getOpenFileName(self, caption=u"保存文件到", directory=".",filter="json (*.json)")
        if type(save_file) is tuple:
            save_file = save_file[0]
        self.Load_Path_Text.setText(QDir.toNativeSeparators(save_file))
        self.Load_Path_Label.setVisible(False)
        self.Load_Path_GetBtn.setVisible(True)
        try :
            self.Load_Path_GetBtn.clicked.disconnect()
        except:
            pass
        self.Load_Path_GetBtn.clicked.connect(partial(self.Open_Directory,self.Load_Path_Text))

    def Open_Directory(self,LineEdit):
        Save_Location = LineEdit.text()
        if Save_Location == "":
            Save_Location = os.getcwd()
        else:
            Save_Location_temp = Save_Location.split('.')[0]
            if Save_Location_temp != Save_Location:
                Save_Location = os.path.split(Save_Location)[0]
        
        if os.path.exists(Save_Location):
            subprocess.call("explorer %s" % Save_Location, shell=True)
        else:
            QMessageBox.warning(self, "警告", "路径不存在\n检查路径是否正确")

    def Dock_Win_Management(self):
        Title_Name = u"藤蔓生长快速绑定工具"
        def mayaToQT( name ):
            # Maya -> QWidget
            ptr = omui.MQtUtil.findControl( name )
            if ptr is None:         ptr = omui.MQtUtil.findLayout( name )
            if ptr is None:         ptr = omui.MQtUtil.findMenuItem( name )
            if ptr is not None:     return wrapInstance( long( ptr ), QWidget )

        if self.DOCK == "undock":
            # undock 窗口
            # win = omui.MQtUtil_mainWindow()
            if mel.eval("getApplicationVersionAsFloat;")>=2017:
                self.undockWindow = cmds.window( title=Title_Name,cc=partial(self.closeEvent,self.event))
            else:
                self.undockWindow = cmds.window( title=Title_Name,rc=partial(self.closeEvent,self.event))
            cmds.paneLayout()
            cmds.showWindow(self.undockWindow)
            ptr = mayaToQT(self.undockWindow)
            return ptr

        elif self.DOCK == "dock":
            
            window = cmds.window( title=Title_Name)
            cmds.paneLayout()
            self.dockControl = cmds.dockControl( area='right', content=window, label=Title_Name,floatChangeCommand=self.Win_Size_Adjustment,vcc=self.closeEvent)
            dock = mayaToQT(window)
            return dock

        elif self.DOCK == "workspace":
            name='VineGrowDock'
            if cmds.workspaceControl(name,query=True,exists=True) :
                cmds.deleteUI(name)
            self.workspaceCtrl = cmds.workspaceControl(name,fl=True,label=Title_Name,vcc=self.closeEvent)
            cmds.paneLayout()
            workspace = mayaToQT(self.workspaceCtrl)
            return workspace

    # 原本用来调整窗口大小的
    # 现在发现了Qt Spacer 的真正用法
    # 就不需要调节大小了，只需要保存UI即可。
    def Win_Size_Adjustment(self):
        self.closeEvent(self.event)
        # if self.DOCK=="undock":
        #     self.adjustSize()

        # elif self.DOCK=="workspace":
        #     try:
        #         self.adjustSize()
        #         cmds.window( self.workspaceCtrl, edit=True, rtf=True,widthHeight=(400,500) )
        #     except Exception:
        #         pass
        # elif self.DOCK=="dock":
            
        #     try:
        #         self.adjustSize()
        #         cmds.window( self.dockControl, edit=True, rtf=True,widthHeight=(400,500) )
        #     except Exception:
        #         pass

    def Rig_Generate_Check(self):
        if len(self.End_JNT_Text.text()) > 0 and len(self.Start_JNT_Text.text()) > 0 and len(self.Rig_Obj_Text.text()) > 0:
            self.Rig_Generate_Btn.setEnabled(True)
        else:
            self.Rig_Generate_Btn.setEnabled(False)

    def Main_JNT_Change(self):
        self.Main_JNT_Num.setText(str(self.Main_JNT_Slider.value()))

    def IK_JNT_Change(self):
        self.IK_JNT_Num.setText(str(self.IK_JNT_Slider.value()))
        
    def Curve_Span_Change(self):
        self.Curve_Span_Num.setText(str(self.Curve_Span_Slider.value()))

    # toggle UI
    
    def Rig_Obj_Toggle_Fun(self):
        if self.Rig_Obj_Toggle_Check:
            self.Rig_Obj_Toggle_Check = False
            self.Rig_Obj_Layout.setVisible(False)
            self.Rig_Obj_Toggle.setText(u"■获取绑定物体")
            self.Rig_Obj_Toggle.setFont(self.Bold_Font)
        else:
            self.Rig_Obj_Toggle_Check = True
            self.Rig_Obj_Layout.setVisible(True)
            self.Rig_Obj_Toggle.setText(u"▼获取绑定物体")
            self.Rig_Obj_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def Loc_Generate_Toggle_Fun(self):
        if self.Loc_Generate_Toggle_Check:
            self.Loc_Generate_Toggle_Check = False
            self.Auto_Generate_Layout.setVisible(False)
            self.Loc_Generate_Toggle.setText(u"■自动生成绑定参考节点")
            self.Loc_Generate_Toggle.setFont(self.Bold_Font)
        else:
            self.Loc_Generate_Toggle_Check = True
            self.Auto_Generate_Layout.setVisible(True)
            self.Loc_Generate_Toggle.setText(u"▼自动生成绑定参考节点")
            self.Loc_Generate_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def JNT_Setting_Toggle_Fun(self):
        if self.JNT_Setting_Toggle_Check:
            self.JNT_Setting_Toggle_Check = False
            self.JNT_Setting_Layout.setVisible(False)
            self.JNT_Setting_Toggle.setText(u"■设置绑定参考节点")
            self.JNT_Setting_Toggle.setFont(self.Bold_Font)
        else:
            self.JNT_Setting_Toggle_Check = True
            self.JNT_Setting_Layout.setVisible(True)
            self.JNT_Setting_Toggle.setText(u"▼设置绑定参考节点")
            self.JNT_Setting_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def Rig_Generate_Toggle_Fun(self):
        if self.Rig_Generate_Toggle_Check:
            self.Rig_Generate_Toggle_Check = False
            self.Rig_Generate_Layout.setVisible(False)
            self.Rig_Generate_Toggle.setText(u"■生成设置")
            self.Rig_Generate_Toggle.setFont(self.Bold_Font)
        else:
            self.Rig_Generate_Toggle_Check = True
            self.Rig_Generate_Layout.setVisible(True)
            self.Rig_Generate_Toggle.setText(u"▼生成设置")
            self.Rig_Generate_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def Window_Setting_Toggle_Fun(self):
        if self.Window_Setting_Toggle_Check:
            self.Window_Setting_Toggle_Check = False
            self.Window_Setting_Layout.setVisible(False)
            self.Window_Setting_Toggle.setText(u"■窗口设置")
            self.Window_Setting_Toggle.setFont(self.Bold_Font)
        else:
            self.Window_Setting_Toggle_Check = True
            self.Window_Setting_Layout.setVisible(True)
            self.Window_Setting_Toggle.setText(u"▼窗口设置")
            self.Window_Setting_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def Namespace_Toggle_Fun(self):
        if self.Namespace_Toggle_Check:
            self.Namespace_Toggle_Check = False
            self.Namespace_Toggle_Layout.setVisible(False)
            self.Namespace_Toggle.setText(u"■绑定节点命名")
            self.Namespace_Toggle.setFont(self.Bold_Font)
        else:
            self.Namespace_Toggle_Check = True
            self.Namespace_Toggle_Layout.setVisible(True)
            self.Namespace_Toggle.setText(u"▼绑定节点命名")
            self.Namespace_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    def Attribute_Setting_Toggle_Fun(self):
        if self.Attribute_Setting_Toggle_Check:
            self.Attribute_Setting_Toggle_Check = False
            self.Attribute_Setting_Layout.setVisible(False)
            self.Attribute_Setting_Toggle.setText(u"■设置记录")
            self.Attribute_Setting_Toggle.setFont(self.Bold_Font)
        else:
            self.Attribute_Setting_Toggle_Check = True
            self.Attribute_Setting_Layout.setVisible(True)
            self.Attribute_Setting_Toggle.setText(u"▼设置记录")
            self.Attribute_Setting_Toggle.setFont(self.Normal_Font)
        self.Win_Size_Adjustment()

    # 获取物体功能
    def Get_Rig_Obj(self):
        self.Rig_Obj = cmds.ls(sl=True)
        if len(self.Rig_Obj) > 0:
            self.Rig_Obj_Text.setText(self.Rig_Obj[0])
        else :
            self.Rig_Obj_Text.setText("")
        
        if self.Rig_Obj_Text.text() != "":
            self.Rig_Obj_Label.setVisible(False)
            self.Rig_Obj_GetBtn.setVisible(True)
            self.Loc_Generate_Btn.setEnabled(True)
        else:
            self.Rig_Obj_GetBtn.setVisible(False)
            self.Rig_Obj_Label.setVisible(True)
            self.Loc_Generate_Btn.setEnabled(False)
        self.Rig_Obj_GetBtn.clicked.connect(partial(self.selectObj,self.Rig_Obj))

    def Get_Start_JNT(self):
        self.Start_JNT = cmds.ls(sl=True)
        if len(self.Start_JNT) > 0:
            self.Start_JNT_Text.setText(self.Start_JNT[0])
        else :
            self.Start_JNT_Text.setText("")
        
        if self.Start_JNT_Text.text() != "":
            self.Start_JNT_Label.setVisible(False)
            self.Start_JNT_GetBtn.setVisible(True)
            if self.End_JNT_Text.text() != "":
                self.Switch_Btn.setEnabled(True)
            else:
                self.Switch_Btn.setEnabled(False)
        else:
            self.Start_JNT_GetBtn.setVisible(False)
            self.Start_JNT_Label.setVisible(True)
            self.Switch_Btn.setEnabled(False)
        self.Start_JNT_GetBtn.clicked.connect(partial(self.selectObj,self.Start_JNT))
        
    def Get_End_JNT(self):
        self.End_JNT = cmds.ls(sl=True)
        if len(self.End_JNT) > 0:
            self.End_JNT_Text.setText(self.End_JNT[0])
        else :
            self.End_JNT_Text.setText("")
        
        if self.End_JNT_Text.text() != "":
            self.End_JNT_Label.setVisible(False)
            self.End_JNT_GetBtn.setVisible(True)
            if self.Start_JNT_Text.text() != "":
                self.Switch_Btn.setEnabled(True)
            else:
                self.Switch_Btn.setEnabled(False)
        else:
            self.End_JNT_GetBtn.setVisible(False)
            self.End_JNT_Label.setVisible(True)
            self.Switch_Btn.setEnabled(False)
        self.End_JNT_GetBtn.clicked.connect(partial(self.selectObj,self.End_JNT))
        
    # 选取物体
    def selectObj(self,selectTarget):
        if selectTarget != "":
            cmds.select(selectTarget)

    # 关闭窗口时保存当前视窗选择
    def closeEvent(self, event,path=GUI_STATE_PATH):
        self.Save_Json_File(path=path)

    def Save_Json_File(self,path=GUI_STATE_PATH):
        
        GUI_STATE = {}
        # 判断物体是否存在，存在就存储
        try:
            GUI_STATE['Rig_Obj_Text'] = self.Rig_Obj_Text.text() if len(cmds.ls(self.Rig_Obj_Text.text()))>0 else ""
        except:
            return
        GUI_STATE['Start_JNT_Text'] = self.Start_JNT_Text.text() if len(cmds.ls(self.Start_JNT_Text.text()))>0 else ""
        GUI_STATE['End_JNT_Text'] = self.End_JNT_Text.text() if len(cmds.ls(self.End_JNT_Text.text()))>0 else ""
        GUI_STATE['Main_JNT_Num'] = self.Main_JNT_Num.text()
        GUI_STATE['IK_JNT_Num'] = self.IK_JNT_Num.text()
        GUI_STATE['Curve_Span_Num'] = self.Curve_Span_Num.text()
        GUI_STATE['IK_CTRL_ColorSlider'] = self.IK_CTRL_ColorSlider.value()
        GUI_STATE['Start_Ctrl_ColorSlider'] = self.Start_Ctrl_ColorSlider.value()
        GUI_STATE['End_IK_ColorSlider'] = self.End_IK_ColorSlider.value()
        GUI_STATE['Character_Ctrl_ColorSlider'] = self.Character_Ctrl_ColorSlider.value()

        GUI_STATE['Geo_Name_Text'] = self.Geo_Name_Text.text()
        GUI_STATE['Main_JNT_Name_Text'] = self.Main_JNT_Name_Text.text()
        GUI_STATE['Curve_Name_Text'] = self.Curve_Name_Text.text()
        GUI_STATE['IK_JNT_Name_Text'] = self.IK_JNT_Name_Text.text()
        GUI_STATE['IK_CTRL_Name_Text'] = self.IK_CTRL_Name_Text.text()
        GUI_STATE['Start_Ctrl_Text'] = self.Start_Ctrl_Text.text()
        GUI_STATE['End_IK_Text'] = self.End_IK_Text.text()
        GUI_STATE['Character_Ctrl_Text'] = self.Character_Ctrl_Text.text()
        GUI_STATE['X_RadioButton'] = self.X_RadioButton.isChecked()
        GUI_STATE['Y_RadioButton'] = self.Y_RadioButton.isChecked()
        GUI_STATE['Z_RadioButton'] = self.Z_RadioButton.isChecked()
        GUI_STATE['Delete_CheckBox'] = self.Delete_CheckBox.isChecked()
        GUI_STATE['Rig_Obj_Toggle_Check'] = self.Rig_Obj_Toggle_Check 
        GUI_STATE['Loc_Generate_Toggle_Check'] = self.Loc_Generate_Toggle_Check 
        GUI_STATE['JNT_Setting_Toggle_Check'] = self.JNT_Setting_Toggle_Check 
        GUI_STATE['Rig_Generate_Toggle_Check'] = self.Rig_Generate_Toggle_Check 
        GUI_STATE['Namespace_Toggle_Check'] = self.Namespace_Toggle_Check 
        GUI_STATE['Window_Setting_Toggle_Check'] = self.Window_Setting_Toggle_Check 
        GUI_STATE['Tab_Widget'] = self.Tab_Widget.currentIndex() 


        styleSheet = self.IK_CTRL_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])
        g = float(styleSheet[1])
        b = float(styleSheet[2].split(")")[0])
        color = (r,g,b)
        GUI_STATE['IK_CTRL_ColorBtn'] = (color[0],color[1],color[2])
        
        styleSheet = self.Start_Ctrl_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])
        g = float(styleSheet[1])
        b = float(styleSheet[2].split(")")[0])
        color = (r,g,b)
        GUI_STATE['Start_Ctrl_ColorBtn'] = (color[0],color[1],color[2])

        styleSheet = self.End_IK_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])
        g = float(styleSheet[1])
        b = float(styleSheet[2].split(")")[0])
        color = (r,g,b)
        GUI_STATE['End_IK_ColorBtn'] = (color[0],color[1],color[2])

        styleSheet = self.Character_Ctrl_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])
        g = float(styleSheet[1])
        b = float(styleSheet[2].split(")")[0])
        color = (r,g,b)
        GUI_STATE['Character_Ctrl_ColorBtn'] = (color[0],color[1],color[2])

        GUI_STATE['DOCK'] = self.DOCK
        try:
            with open(path,'w') as f:
                json.dump(GUI_STATE,f,indent=4)
        except:
            QMessageBox.warning(self, "Warning", "保存失败")
            

    def setColor(self,Btn=None):
        # 获取灯光的颜色
        styleSheet = self.IK_CTRL_ColorBtn.styleSheet().split("(")[1].split(",")
        r = float(styleSheet[0])/255
        g = float(styleSheet[1])/255
        b = float(styleSheet[2].split(")")[0])/255
        Btn_Color = (r,g,b)

        # 打开 Maya 的颜色编辑器
        color = cmds.colorEditor(rgbValue=Btn_Color)
        
        # Maya 返回了字符串
        # 我们需要手动将其转换为可用的变量
        r,g,b,a = [float(c) for c in color.split()]

        # 设置新的颜色值
        Btn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r*255,g*255,b*255))
        self.Save_Json_File()

    def Slider_Change_Color(self,Btn,Index):

        COLOR_INDEX = {}
        with open(COLOR_INDEX_PATH,'r') as f:
            COLOR_INDEX = json.load(f)
        r = COLOR_INDEX[str(Index)][0]
        g = COLOR_INDEX[str(Index)][1]
        b = COLOR_INDEX[str(Index)][2]

        Btn.setStyleSheet('background-color:rgb(%s,%s,%s)'%(r,g,b))
        self.Save_Json_File()
