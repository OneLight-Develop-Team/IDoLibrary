#coding:utf-8
import unreal
import os
@unreal.uclass()
class GetEditorAssetLibrary(unreal.EditorAssetLibrary):
	pass
@unreal.uclass()
class GetEditorFilterLibrary(unreal.EditorFilterLibrary):
	pass
@unreal.uclass()
class GetEditorUtilityLibrary(unreal.EditorUtilityLibrary):
	pass


# --------------------------------------------------------------------------------------------------------- #
def set_two_sided():
	# UE里面暂时没有get_folder的选项，只能借助C++，但是对于编译版本的虚幻添加C++蓝图函数有问题
	# 所以暂时只能用这种方式来处理双面材质
	editorAssetLib = GetEditorAssetLibrary()
	editorUtil = GetEditorUtilityLibrary()
	editor_filter_lib = GetEditorFilterLibrary()
	workingPaths = os.path.dirname(editorUtil.get_selected_assets()[0].get_path_name()) + "/"
	
	if not workingPaths:
		return
	two_sided_count = 0
	allAssets = editorAssetLib.list_assets(workingPaths, False)
		
	for asset in allAssets:
		loaded_asset = unreal.load_asset(asset)		
		try:
			loaded_asset.get_editor_property("two_sided")
		except:
			continue
		loaded_asset.set_editor_property("two_sided", 1)
		editorAssetLib.save_asset(asset)
		two_sided_count += 1
	print "materials two sided"
	print two_sided_count

