#coding:utf-8
# 功能实现借用了GitHub库：20tab/unrealenginepython
import os
import unreal_engine as ue
from unreal_engine.classes import MediaPlayerFactoryNew, FileMediaSourceFactoryNew, MediaTextureFactoryNew, MaterialFactoryNew
from unreal_engine.structs import EdGraphPinType


config_path = "/Game/Movies/"

# -------------------------------------------------------------------------------------------------------------------------------------- #
def stereo_setup_media_assets(project_name, shot_name, video_dir, stereo=1):
	# 创建资产
	# ----------------------------------------------
	file_name = os.path.splitext(os.listdir(video_dir)[0])[0]
	ext       = os.path.splitext(os.listdir(video_dir)[0])[1]		
	file_name_pattern = file_name[:-2]
	
	# L	
	# ----------------------------------------------	
	factory = MediaPlayerFactoryNew()
	media_player_L = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MP_" + file_name_pattern + "_L")

	factory = FileMediaSourceFactoryNew()
	file_source_L = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MF_" + file_name_pattern + "_L")
	file_source_L.set_property("FilePath", video_dir + "\\" + file_name_pattern + "_L" + ext)

	factory = MediaTextureFactoryNew()
	media_texture_L = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MT_" + file_name_pattern + "_L")
	media_texture_L.set_property("MediaPlayer", media_player_L)
	
	# R
	# ----------------------------------------------
	factory = MediaPlayerFactoryNew()	
	media_player_R = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MP_" + file_name_pattern + "_R")

	factory = FileMediaSourceFactoryNew()
	file_source_R = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MF_" + file_name_pattern + "_R")
	file_source_R.set_property("FilePath", video_dir + "\\" + file_name_pattern + "_R" + ext)
	
	factory = MediaTextureFactoryNew()
	media_texture_R = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MT_" + file_name_pattern + "_R")
	media_texture_R.set_property("MediaPlayer", media_player_R)

	# 创建并开始编辑sheder
	# ----------------------------------------------
	factory = MaterialFactoryNew()
	material = factory.factory_create_new(config_path + project_name + "/" + shot_name + "/" + "MM_" + file_name_pattern)	
	material.modify() 

	# 创建材质节点
	# ----------------------------------------------
	from unreal_engine.classes import MaterialExpressionCustom, MaterialExpressionCustom, MaterialExpressionTextureSample, MaterialExpressionLinearInterpolate
	texture_sample_node_L = MaterialExpressionTextureSample('', material)
	texture_sample_node_R = MaterialExpressionTextureSample('', material)
	
	texture_sample_node_L.Texture = ue.get_asset(media_texture_L.get_path_name())
	texture_sample_node_R.Texture = ue.get_asset(media_texture_R.get_path_name())

	custom_node = MaterialExpressionCustom("", material)
	custom_node.Code = "return ResolvedView.StereoPassIndex;"
	custom_node.Desc = "0:right, 1:left"
	custom_node.OutputType = 0
	lerp_node = MaterialExpressionLinearInterpolate("", material)
	
	# 连接材质节点
	# ----------------------------------------------
	from unreal_engine.structs import ExpressionInput, ColorMaterialInput
	lerp_node.A = ExpressionInput(Expression = texture_sample_node_L)
	lerp_node.B = ExpressionInput(Expression = texture_sample_node_R)
	lerp_node.Alpha = ExpressionInput(Expression = custom_node)
	material.Expressions = [
								texture_sample_node_R, 
								texture_sample_node_L,
								custom_node,
								lerp_node
							]	
	# 判断是否需要做立体视频
	if stereo:
		material.EmissiveColor = ColorMaterialInput(Expression = lerp_node)
	else:
		material.EmissiveColor = ColorMaterialInput(Expression = texture_sample_node_L)

	# 结束材质编辑
	# ----------------------------------------------
	material.post_edit_change()
	material.save_package()

	return [media_player_L, media_player_R, file_source_L, file_source_R]



# -------------------------------------------------------------------------------------------------------------------------------------- #
def stereo_setup_level_bp_variable(player_sets=[]):		
	from unreal_engine.classes import KismetMathLibrary, K2Node_Timeline, K2Node_ExecutionSequence, K2Node_IfThenElse

	world = ue.get_editor_world()
	level_bp = world.CurrentLevel.get_level_script_blueprint()
	left_channel = player_sets[0]
	if len(player_sets==4):
		right_channel = player_sets[1]
	else:
		right_channel = None
		
	pin = EdGraphPinType(PinCategory='object', PinSubCategoryObject=MediaPlayer)
	left_media = ue.blueprint_add_member_variable(level_bp, left_channel.get_name(), pin, None, left_channel.get_path_name())
	right_media = ue.blueprint_add_member_variable(level_bp, right_channel.get_name(), pin, None, right_channel.get_path_name())

	uber_page = level_bp.UberGraphPages[0]

	# 添加media player节点
	# ----------------------------------------------
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_left_media = uber_page.graph_add_node_variable_get(left_channel.get_name(), None, x, y)
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_right_media = uber_page.graph_add_node_variable_get(right_channel.get_name(), None, x, y)

	# 添加open source节点
	# ----------------------------------------------
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_open_source_L = uber_page.graph_add_node_call_function(MediaPlayer.OpenSource, x, y)
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_open_source_R = uber_page.graph_add_node_call_function(MediaPlayer.OpenSource, x, y)

	# 连接media source，没办法单独的设置资源，只能通过变量来设置
	# ----------------------------------------------
	pin = EdGraphPinType(PinCategory='object', PinSubCategoryObject=FileMediaSource)
	ue.blueprint_add_member_variable(level_bp, player_sets[2].get_name(), pin, None, player_sets[2].get_path_name())
	pin = EdGraphPinType(PinCategory='object', PinSubCategoryObject=FileMediaSource)
	ue.blueprint_add_member_variable(level_bp, player_sets[3].get_name(), pin, None, player_sets[3].get_path_name())

	c = uber_page.graph_add_node_variable_get(player_sets[2].get_name(), None, x, y)
	d = uber_page.graph_add_node_variable_get(player_sets[3].get_name(), None, x, y)

	pin1=c.node_find_pin(player_sets[2].get_name())
	pin2=node_open_source_L.node_find_pin("MediaSource")
	pin1.make_link_to(pin2)
	pin1=d.node_find_pin(player_sets[3].get_name())
	pin2=node_open_source_R.node_find_pin("MediaSource")
	pin1.make_link_to(pin2)

	# 添加>=节点, call_function的函数名可以大写也可以小写，直接按照C++文档的来就可以
	# ----------------------------------------------
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_greater = uber_page.graph_add_node_call_function(KismetMathLibrary.EqualEqual_FloatFloat, x, y)
	
	# 添加branch节点
	# ----------------------------------------------
	i = K2Node_IfThenElse()
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_branch = uber_page.graph_add_node(i, x, y)

	# 连接节点
	# ----------------------------------------------
	pin1 = node_greater.node_find_pin("ReturnValue")
	pin2 = node_branch.node_find_pin("Condition")
	pin1.make_link_to(pin2)

	pin1 = node_left_media.node_find_pin(left_channel.get_name())
	pin2 = node_open_source_L.node_find_pin('self')
	pin1.make_link_to(pin2)

	pin1 = node_right_media.node_find_pin(right_channel.get_name())
	pin2 = node_open_source_R.node_find_pin('self')
	pin1.make_link_to(pin2)

	pin1 = node_open_source_L.node_find_pin("then")
	pin2 = node_open_source_R.node_find_pin("execute")
	pin1.make_link_to(pin2)

	pin1 = node_branch.node_find_pin("Then")
	pin2 = node_open_source_L.node_find_pin("execute")
	pin1.make_link_to(pin2)

	# compile the blueprint
	ue.compile_blueprint(level_bp)

	# open related editor
	ue.open_editor_for_asset(level_bp)
	return node_branch.node_find_pin, node_greater.node_find_pin("A")



# -------------------------------------------------------------------------------------------------------------------------------------- #
def stereo_setup_level_blurprint(video_asset_dir, project_name, shot_name, video_dir):
	sc_num = len(os.listdir(video_asset_dir))

	world = ue.get_editor_world()
	level_bp = world.CurrentLevel.get_level_script_blueprint()
	uber_page = level_bp.UberGraphPages[0]

	from unreal_engine.classes import KismetMathLibrary, K2Node_Timeline, K2Node_ExecutionSequence, K2Node_IfThenElse
	n = K2Node_ExecutionSequence()
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_sequence = uber_page.graph_add_node(n, x, y)

	t = K2Node_Timeline()
	y, x = uber_page.graph_get_good_place_for_new_node()
	node_timeline = uber_page.graph_add_node(t, x, y)

	pin1 = node_timeline.get_update_pin()	
	pin2 = node_sequence.node_find_pin("execute")
	pin1.make_link_to(pin2)
	
	# 开始程序化操作
	for idx, num in enumerate(sc_num):	
		if len(os.listdir(video_dir))>1:
			stereo = 1
		else：
			stereo = 0			
		# 创建asset和相对应的level bp
		player_sets = stereo_setup_media_assets(project_name,shot_name,video_dir,stereo)
		pin_branch_exec, pin_greaterA = stereo_setup_level_bp_variable(player_sets)
		if idx < 2:
			pin1 = node_sequence.node_find_pin("Then%d",idx)
			pin1.make_link_to(pin_branch_exec)
			# 连接timeline节点，暂时只能手动，因为timeline节点不能添加轨迹
			##########
		else:				
			seq_num_pin = node_sequence.add_pin()
			seq_num_pin.make_link_to(pin_branch_exec)

		

		
# -------------------------------------------------------------------------------------------------------------------------------------- #		
import unreal_engine as ue
import sys
sys.path.append(r"C:\Python36\Lib\site-packages")
import PySide2
from PySide2 import QtGui
from PySide2 import QtWidgets


assets = ue.get_selected_assets()
property_list = []
for asset in assets:
	asset_properties = asset.properties()
	for p in asset_properties:
		if p not in property_list:
			property_list.append(p)


app = QtWidgets.QApplication.instance()
if not app:
	app = QtWidgets.QApplication()        

class widget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(widget, self).__init__(parent)	
		self.layout = QtWidgets.QVBoxLayout()
		self.setLayout(self.layout)
		self.list_widget = QtWidgets.QListWidget()
		self.layout.addWidget(self.list_widget)
		for p in sorted(property_list):
			item = QtWidgets.QListWidgetItem(p)
			self.list_widget.addItem(item)
			
		self.spin = QtWidgets.QDoubleSpinBox()
		self.layout.addWidget(self.spin)
		self.spin.setMaximum(10000000)
		
		self.button = QtWidgets.QPushButton("CHANGE")
		self.layout.addWidget(self.button)
		
		self.button.clicked.connect(self.change_property)

	def change_property(self):
		for asset in assets:
			property_name = self.list_widget.currentItem().text()
			value = self.spin.value()
			asset.set_property(property_name, value)
		self.close()
		

a=widget()
a.show()
		
