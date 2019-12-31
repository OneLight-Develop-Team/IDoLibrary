#coding:utf-8
import unreal
import sys
sys.path.append('C:/Python27/Lib/site-packages')
from PySide import QtGui, QtUiTools, QtCore
import UE_MaterialTool
reload(UE_MaterialTool)

UI_FILE_FULLNAME = r"\\ftdytool.hytch.com\FTDY\hq_tool\software\Unreal Engine\PythonProject\UE_PipelineTool\Material\UE_MaterialTool_UI.ui"

	
class UE_MaterialTool_UI(QtGui.QDialog):
	def __init__(self, parent=None):
		super(UE_MaterialTool_UI, self).__init__(parent)		
		self.aboutToClose = None # This is used to stop the tick when the window is closed
		self.widget = QtUiTools.QUiLoader().load(UI_FILE_FULLNAME)
		self.widget.setParent(self)			
		self.setGeometry(100,100,350,300)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		
		# layout
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.widget)
		layout.setSpacing(0)
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		
		self.button1 = self.widget.findChild(QtGui.QPushButton, "pushButton")
		self.button2 = self.widget.findChild(QtGui.QPushButton, "pushButton_2")
				
		self.button1.clicked.connect(UE_MaterialTool.set_two_sided)
		self.button2.setEnabled(0)
		

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


