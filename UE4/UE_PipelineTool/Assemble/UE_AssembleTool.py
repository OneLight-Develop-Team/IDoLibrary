# coding:utf-8
import unreal
import os


@unreal.uclass()
class GetEditorAssetLibrary(unreal.EditorAssetLibrary):
	pass
@unreal.uclass()
class GetEditorUtility(unreal.GlobalEditorUtilityBase):
	pass	
@unreal.uclass()
class GetEditorLevelLibrary(unreal.EditorLevelLibrary):	
	pass
@unreal.uclass()
class GetEditorFilterLibrary(unreal.EditorFilterLibrary):
	pass


# --------------------------------------------------------------------------------------------------------- #
def create_directory(path=''):
	editorAssetLib = GetEditorAssetLibrary()
	return editorAssetLib.make_directory(directory_path=path)	


# --------------------------------------------------------------------------------------------------------- #
def directory_exists(path=''):
	editorAssetLib = GetEditorAssetLibrary()
	return editorAssetLib.does_directory_exist(directory_path=path)


# --------------------------------------------------------------------------------------------------------- #
def build_import_task(filename='', destination_path='', options=None):
	task = unreal.AssetImportTask()
	task.set_editor_property('automated', True)
	task.set_editor_property('destination_name', '')
	task.set_editor_property('destination_path', destination_path)
	task.set_editor_property('filename', filename)
	task.set_editor_property('replace_existing', True)
	task.set_editor_property('save', True)
	task.set_editor_property('options', options)
	filename = os.path.basename(os.path.splitext(filename)[0])
	return task, filename


# --------------------------------------------------------------------------------------------------------- #
def build_static_mesh_import_options(scale=1.0):
	options = unreal.FbxImportUI()
	# unreal.FbxImportUI
	options.set_editor_property('import_mesh', True)
	options.set_editor_property('import_textures', True)
	options.set_editor_property('import_materials', True)
	options.set_editor_property('import_as_skeletal', False)  # Static Mesh
	# unreal.FbxMeshImportData
	options.static_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
	options.static_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
	options.static_mesh_import_data.set_editor_property('import_uniform_scale', scale)
	# unreal.FbxStaticMeshImportData
	options.static_mesh_import_data.set_editor_property('combine_meshes', False) 	# !!!!!!!!!!!!!
	options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', True)
	options.static_mesh_import_data.set_editor_property('auto_generate_collision', True)
	return options


# --------------------------------------------------------------------------------------------------------- #
def build_skeletal_mesh_import_options(scale=1.0):
	options = unreal.FbxImportUI()
	# unreal.FbxImportUI
	options.set_editor_property('import_mesh', True)
	options.set_editor_property('import_textures', True)
	options.set_editor_property('import_materials', True)
	options.set_editor_property('import_as_skeletal', True)  # Skeletal Mesh
	# unreal.FbxMeshImportData
	options.skeletal_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
	options.skeletal_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
	options.skeletal_mesh_import_data.set_editor_property('import_uniform_scale', scale)
	# unreal.FbxSkeletalMeshImportData
	options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
	options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', False)
	return options


# --------------------------------------------------------------------------------------------------------- #
# skeleton_path: str : Skeleton asset path of the skeleton that will be used to bind the animation
def build_animation_import_options(skeleton_path='',scale=1.0):
	options = unreal.FbxImportUI()
	# unreal.FbxImportUI
	options.set_editor_property('import_animations', True)
	options.skeleton = unreal.load_asset(skeleton_path)
	# unreal.FbxMeshImportData
	options.anim_sequence_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
	options.anim_sequence_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
	options.anim_sequence_import_data.set_editor_property('import_uniform_scale', scale)
	# unreal.FbxAnimSequenceImportData
	options.anim_sequence_import_data.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
	options.anim_sequence_import_data.set_editor_property('remove_redundant_keys', False)
	return options


# --------------------------------------------------------------------------------------------------------- #
def execute_import_task(task):
	# 只接受列表传参
	tasks = [task]
	unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
	# 返回所有的单独的asset 路径
	# imported_asset_paths = []	
	# for path in task.get_editor_property('imported_object_paths'):
	# 	imported_asset_paths.append(path)
	# return imported_asset_paths



# --------------------------------------------------------------------------------------------------------- #
def assemble_fbx_asset(fbx_files=[], dest_path="/Game/new_folder", import_type="static_mesh", assemble_scale_factor=1):	

	# --------------------------------------------
	# 判断类型，生成option
	# 尺寸缩放在这个时候（导入之前）进行
	if import_type=="static_mesh":
		option = build_static_mesh_import_options(assemble_scale_factor)
	if import_type=="misc":
		option = None	
	
	# --------------------------------------------
	# 一个FBX对应一个task， 一个FBX可以包含若干个asset
	# 一个FBX对应一个actor，一个actor包含若干个asset

	# --------------------------------------------
	# opertion start， with slow task ！！！
	for idx, fbx in enumerate(fbx_files):		

		# --------------------------------------------
		# create folder
		dest_path = dest_path + str("_%d" % (idx+1))
		if not directory_exists():
			create_directory(dest_path)

		# --------------------------------------------
		# 对每个fbx新建一个task，导入到content browser
		fbx_task, spawn_actor_name = build_import_task(fbx, dest_path, option)
		execute_import_task(fbx_task)
		print "CB imported"				
		editor_asset_lib = GetEditorAssetLibrary()
		editor_filter_lib = GetEditorFilterLibrary()
		asset_paths = editor_asset_lib.list_assets(dest_path)		
		print asset_paths

		# --------------------------------------------
		# 针对导入的fbx里每个单独的asset，spawn（导入的时候不要combine mesh!!!，build option里设置）
		# 做了一个过滤，只会spawn static mesh
		editor_level_lib = GetEditorLevelLibrary()
		actor_in_asset_list = []		
		for asset in asset_paths:	
			loaded_asset = unreal.load_asset(asset)
			temp_list = []
			temp_list.append(loaded_asset)
			temp_list = editor_filter_lib.by_class(temp_list, unreal.StaticMesh.static_class())	
			if not temp_list:
				continue
			actor = editor_level_lib.spawn_actor_from_object(loaded_asset, (0,0,0), (0,0,0))
			actor_in_asset_list.append(actor)
		print "assets spawned"

		# --------------------------------------------
		# join to a new actor
		join_options = unreal.EditorScriptingJoinStaticMeshActorsOptions()
		join_options.new_actor_label = spawn_actor_name
		join_options.destroy_source_actors = True
		join_options.rename_components_from_source = True
		new_actor = editor_level_lib.join_static_mesh_actors(actor_in_asset_list, join_options)
		print "actors joined"

		# --------------------------------------------
		# join to a new group
		new_actor.set_folder_path("new_group")
		print "group created"


