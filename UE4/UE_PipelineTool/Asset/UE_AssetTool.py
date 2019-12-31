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
def report_unused_assets():
	editorAssetLib = GetEditorAssetLibrary()
	workingPath = "/Game"
	allAssets = editorAssetLib.list_assets(workingPath, True, False)
	if (len(allAssets) > 0):
		for asset in allAssets:
			deps = editorAssetLib.find_package_referencers_for_asset(asset, False)
			if (len(deps) == 0):
				print ">>>%s" % asset


# --------------------------------------------------------------------------------------------------------- #
def delete_unused_assets():
	editorAssetLib = GetEditorAssetLibrary()
	workingPath = "/Game"
	allAssets = editorAssetLib.list_assets(workingPath, True, False)
	processingAssetPath = ""
	allAssetsCount = len(allAssets)
	if ( allAssetsCount > 0):
		with unreal.ScopedSlowTask(allAssetsCount, processingAssetPath) as slowTask:
			slowTask.make_dialog(True)
			for asset in allAssets:
				processingAssetPath = asset
				deps = editorAssetLib.find_package_referencers_for_asset(asset, False)
				if (len(deps) <= 0):
					print ">>> Deleting >>> %s" % asset
					editorAssetLib.delete_asset(asset)
				if slowTask.should_cancel():
					break
				slowTask.enter_progress_frame(1, processingAssetPath)
			

# --------------------------------------------------------------------------------------------------------- #
def prefix_all_assets():
	#You can set the prefix of your choice here
	prefixAnimationBlueprint    = "Anim_BP"
	prefixAnimationSequence     = "Seq"
	prefixAnimation             = "Anim"
	prefixBlendSpace            = "BS"
	prefixBlueprint             = "BP"
	prefixCurveFloat            = "crvF"
	prefixCurveLinearColor      = "crvL"
	prefixLevel                 = "Lv"
	prefixMaterial              = "M"
	prefixMaterialFunction      = "MF"
	prefixMaterialInstance      = "MI"
	prefixParticleSystem        = "FX"
	prefixPhysicsAsset          = "Phy"
	prefixSkeletalMesh          = "SKM"
	prefixSkeleton              = "SK"
	prefixSoundCue              = "Cue"
	prefixSoundWave             = "wv"
	prefixStaticMesh            = "SM"
	prefixTexture2D             = "T"
	prefixTextureCube           = "HDRI"

	def GetProperPrefix(className):
		_prefix = ""
		if className == "AnimBlueprint":
			_prefix = prefixAnimationBlueprint
		elif className == "AnimSequence":
			_prefix = prefixAnimationSequence
		elif className == "Animation":
			_prefix = prefixAnimation
		elif className == "BlendSpace1D":
			_prefix = prefixBlendSpace
		elif className == "Blueprint":
			_prefix = prefixBlueprint
		elif className == "CurveFloat":
			_prefix = prefixCurveFloat
		elif className == "CurveLinearColor":
			_prefix = prefixCurveLinearColor
		elif className == "Material":
			_prefix = prefixMaterial
		elif className == "MaterialFunction":
			_prefix = prefixMaterialFunction
		elif className == "MaterialInstance":
			_prefix = prefixMaterialInstance
		elif className == "ParticleSystem":
			_prefix = prefixParticleSystem
		elif className == "PhysicsAsset":
			_prefix = prefixPhysicsAsset
		elif className == "SkeletalMesh":
			_prefix = prefixSkeletalMesh
		elif className == "Skeleton":
			_prefix = prefixSkeleton
		elif className == "SoundCue":
			_prefix = prefixSoundCue
		elif className == "SoundWave":
			_prefix = prefixSoundWave
		elif className == "StaticMesh":
			_prefix = prefixStaticMesh
		elif className == "Texture2D":
			_prefix = prefixTexture2D
		elif className == "TextureCube":
			_prefix = prefixTextureCube
		else:
			_prefix = ""
		return _prefix

	editorAssetLib = GetEditorAssetLibrary()
	workingPath = "/Game"
	allAssets = editorAssetLib.list_assets(workingPath, True, False)
	allAssetsCount = len(allAssets)
	selectedAssetPath = workingPath

	with unreal.ScopedSlowTask(allAssetsCount, selectedAssetPath) as slowTask:
		slowTask.make_dialog(True)
		for asset in allAssets:
			_assetData = editorAssetLib.find_asset_data(asset)
			_assetName = _assetData.get_asset().get_name()
			_assetPathName = _assetData.get_asset().get_path_name()
			_assetPathOnly = _assetPathName.replace((_assetName + "." + _assetName), "")
			_assetClassName = _assetData.get_asset().get_class().get_name()
			_assetPrefix = GetProperPrefix(_assetClassName)

			if _assetPrefix in _assetName:
				continue
			elif _assetPrefix == "":
				continue
			else:
				_targetPathName = _assetPathOnly + ("%s%s%s%s%s%s%s" % (_assetPrefix, "_", _assetName, ".", _assetPrefix, "_", _assetName))

				editorAssetLib.rename_asset(_assetPathName, _targetPathName)
				print ">>> Renaming [%s] to [%s]" % (_assetPathName, _targetPathName)

			if slowTask.should_cancel():
				break
			slowTask.enter_progress_frame(1, asset)



# --------------------------------------------------------------------------------------------------------- #
def create_project_structure(project_name="TEST", start_from=0, shots=3):	
	dir_list = ['anim', 'cam', 'audio', 'scenes', 'fx', 'geometry', 'blueprints', 'HDRI', 'sourceimages', 'materials']
	editorAssetLib = GetEditorAssetLibrary()
	for shot in range(shots):
		shot_number = str(shot+start_from).zfill(2)
		shot_path = "/Game/%s_SC%s" % (project_name, shot_number)
		dir_shot = editorAssetLib.make_directory(shot_path)
		for dir in dir_list:
			editorAssetLib.make_directory(shot_path + "/" + dir)
	print "project structure generated"