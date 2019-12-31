#coding:utf-8
import unreal
import sys
sys.path.append('C:/Python27/Lib/site-packages')
from PySide import QtGui, QtUiTools, QtCore
import UE_AssembleTool
reload(UE_AssembleTool)

UI_FILE_FULLNAME = r"\\ftdytool.hytch.com\FTDY\hq_tool\software\Unreal Engine\PythonProject\UE_PipelineTool\Assemble\UE_AssembleTool_UI.ui"
UI_OPTION_FULLNAME = r"\\ftdytool.hytch.com\FTDY\hq_tool\software\Unreal Engine\PythonProject\UE_PipelineTool\Assemble\UE_AssembleOption_UI.ui"

	
class UE_AssembleTool_UI(QtGui.QDialog):
	def __init__(self, parent=None):
		super(UE_AssembleTool_UI, self).__init__(parent)		
		self.aboutToClose = None # This is used to stop the tick when the window is closed
		self.widget = QtUiTools.QUiLoader().load(UI_FILE_FULLNAME)
		self.widget.setParent(self)			
		self.setGeometry(100,100,350,320)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.file_dialog = None
		self.option_window = None

		
		# layout
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.widget)
		layout.setSpacing(0)
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		
		self.button1 = self.widget.findChild(QtGui.QPushButton, "pushButton_1")
		self.button2 = self.widget.findChild(QtGui.QPushButton, "pushButton_2")
		self.button3 = self.widget.findChild(QtGui.QPushButton, "pushButton_3")
		self.button4 = self.widget.findChild(QtGui.QPushButton, "pushButton_4")
		
		self.button1.clicked.connect(self.path_pop_up)
		self.button2.setEnabled(0)	
		self.button3.setEnabled(0)
		self.button4.setEnabled(0)


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


	def path_pop_up(self):
		self.file_dialog = QtGui.QFileDialog()
		self.file_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)		
		self.file_dialog.setNameFilter("FBX files (*.fbx)")

		self.file_dialog.filesSelected.connect(self.option_pop_up)
		self.file_dialog.show()


	def option_pop_up(self, fbx_files):
		self.option_window = QtUiTools.QUiLoader().load(UI_OPTION_FULLNAME)		
		self.option_window.show()
		button = self.option_window.findChild(QtGui.QPushButton, "pushButton")
		button.clicked.connect(lambda: self.exec_assemble(fbx_files))
		

	def exec_assemble(self, fbx_files):	
		combo = self.option_window.findChild(QtGui.QComboBox, "comboBox")
		line  = self.option_window.findChild(QtGui.QLineEdit, "lineEdit")
		spin  = self.option_window.findChild(QtGui.QDoubleSpinBox, "doubleSpinBox")		
		type = combo.currentText()
		path = line.text()
		scale = spin.value()
		self.option_window.close()
		if not path:
			path = "/Game/NewFolder"
		UE_AssembleTool.assemble_fbx_asset(fbx_files, path, import_type=type, assemble_scale_factor=scale)		
		print fbx_files, path, type, scale

	