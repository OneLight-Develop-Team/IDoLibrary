#coding:utf-8
import unreal
import sys
sys.path.append('C:/Python27/Lib/site-packages')
from PySide import QtGui, QtUiTools, QtCore
import UE_AssetTool
reload(UE_AssetTool)

UI_FILE_FULLNAME = r"\\ftdytool.hytch.com\FTDY\hq_tool\software\Unreal Engine\PythonProject\UE_PipelineTool\Asset\UE_AssetTool_UI.ui"
UI_Structure = r"\\ftdytool.hytch.com\FTDY\hq_tool\software\Unreal Engine\PythonProject\UE_PipelineTool\Asset\UE_Structure_Option_UI.ui"
	
class UE_AssetTool_UI(QtGui.QDialog):
	def __init__(self, parent=None):
		super(UE_AssetTool_UI, self).__init__(parent)		
		self.aboutToClose = None # This is used to stop the tick when the window is closed
		self.widget = QtUiTools.QUiLoader().load(UI_FILE_FULLNAME)
		self.widget.setParent(self)			
		self.setGeometry(100,100,350,300)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.structure_option = None
		
		# layout
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.widget)
		layout.setSpacing(0)
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		
		self.button1 = self.widget.findChild(QtGui.QPushButton, "pushButton")
		self.button2 = self.widget.findChild(QtGui.QPushButton, "pushButton_2")
		self.button3 = self.widget.findChild(QtGui.QPushButton, "pushButton_3")
		self.button4 = self.widget.findChild(QtGui.QPushButton, "pushButton_4")
		
		self.button1.clicked.connect(UE_AssetTool.delete_unused_assets)
		self.button2.clicked.connect(UE_AssetTool.prefix_all_assets)
		self.button3.clicked.connect(UE_AssetTool.report_unused_assets)		
		self.button4.clicked.connect(self.create_structure_UI)		


	def closeEvent(self, event):
		# 把自身传入函数引用从opened列表里面删除并关闭UI，但是并没有从内存中删除？？
		if self.aboutToClose:
			self.aboutToClose(self)
		print "UI deleted"
		event.accept()


	def eventTick(self, delta_seconds):
		self.myTick(delta_seconds)


	def myTick(self, delta_seconds):
		print delta_seconds


	def create_structure_UI(self):
		self.structure_option = QtUiTools.QUiLoader().load(UI_Structure)
		button = self.structure_option.findChild(QtGui.QPushButton, "pushButton")
		line = self.structure_option.findChild(QtGui.QLineEdit, "lineEdit")
		spin = self.structure_option.findChild(QtGui.QSpinBox, "spinBox")
		spin2 = self.structure_option.findChild(QtGui.QSpinBox, "spinBox_2")
		self.structure_option.show()		
		button.clicked.connect(lambda: UE_AssetTool.create_project_structure(line.text(), spin2.value(), spin.value()))		
		button.clicked.connect(self.structure_option.close)

	
		