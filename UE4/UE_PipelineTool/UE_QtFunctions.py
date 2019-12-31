#coding:utf-8
import unreal
import sys
sys.path.append('C:/Python27/Lib/site-packages')
from PySide import QtGui



# 第一次import的时候会执行
# UE线程里面的，只会随UE关闭，其余时间存在内存里
unreal_app = QtGui.QApplication.instance()
if not unreal_app:
	existing_windows = {}
	opened_windows = []
	unreal_app = QtGui.QApplication(sys.argv)
	# tick_handle = unreal.register_slate_post_tick_callback(__QtAppTick__)
	# unreal_app.aboutToQuit.connect(__QtAppQuit__)
print unreal_app


# 每次UE tick，执行UI里面的自定义event函数
def __QtAppTick__(delta_seconds):
	for window in opened_windows:
		window.eventTick(delta_seconds)


# UE关闭，tick停止，需要全局的tick_handle
def __QtAppQuit__():
	unreal.unregister_slate_post_tick_callback(tick_handle)


# 每次UI关闭的时候，从列表里面删除，但是内存里还存在着
def __QtWindowClosed__(window=None):
	if window in opened_windows:
		opened_windows.remove(window)


def spawnQtWindow(desired_window_class=None):
	# 如果创建过了，字典里会由对应的函数名应用，所以重复调用不会创建新的UI，会使用existing_windows里之前已经创建过的
	print "%d UI exist" % len(existing_windows)
	window = existing_windows.get(desired_window_class, None)
	# 如果没有创建过UI，创建一个，并加入existing字典，知道UE关闭，否则UI一直存在内存，并传入一个窗口关闭的函数应用
	if not window:
		window = desired_window_class()
		existing_windows[desired_window_class] = window  # { 函数应用： UI实例； }
		window.aboutToClose = __QtWindowClosed__
	# 加入opened列表，用来表示窗口的状态
	if window not in opened_windows:
		opened_windows.append(window)
	window.show()
	print "%d UI opened" % len(opened_windows)
	return window


def setup_asset_tool_UI():
	import UE_AssetTool_UI
	reload(UE_AssetTool_UI)
	spawnQtWindow(UE_AssetTool_UI.UE_AssetTool_UI)


def setup_assemble_tool_UI():
	import UE_AssembleTool_UI
	reload(UE_AssembleTool_UI)
	spawnQtWindow(UE_AssembleTool_UI.UE_AssembleTool_UI)


def setup_material_tool_UI():
	import UE_MaterialTool_UI
	reload(UE_MaterialTool_UI)
	spawnQtWindow(UE_MaterialTool_UI.UE_MaterialTool_UI)

	