// Fill out your copyright notice in the Description page of Project Settings.


#include "UE_CppHelpers.h"
#include "Runtime/Core/Public/Misc/ConfigCacheIni.h"
//PublicDependencyModuleNames-> "UnrealEd"
#include "Editor/UnrealEd/Public/Editor.h" 
#include "Editor/UnrealEd/Public/Toolkits/AssetEditorManager.h"
#include "Editor/UnrealEd/Public/LevelEditorViewport.h"
// PublicDependencyModuleNames -> "ContentBrowser"
#include "Editor/ContentBrowser/Public/ContentBrowserModule.h"
#include "Editor/ContentBrowser/Private/SContentBrowser.h"
// PublicDependencyModuleNames -> "AssetRegistry"
#include "Runtime/AssetRegistry/Public/AssetRegistryModule.h"
// PublicDependencyModuleNames -> "PythonScriptPlugin" && "Python"
#include "D:/UE_4.22/Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/PythonScriptPlugin.h"


void UUE_CppHelpers::ExecutePython(FString snippet)
{
	FPythonScriptPlugin::Get()->ExecPythonCommand(*snippet);
}

void UUE_CppHelpers::PythonLog(FString string)
{
	UE_LOG(LogTemp, Error, TEXT("%s"), *string);
}

TArray<FString> UUE_CppHelpers::GetSelectedAssets()
{
	FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
	TArray<FAssetData> SelectedAssets;
	ContentBrowserModule.Get().GetSelectedAssets(SelectedAssets);
	TArray<FString> Result;
	for (FAssetData& AssetData : SelectedAssets) {
		Result.Add(AssetData.PackageName.ToString());
	}
	return Result;
}

TArray<FString> UUE_CppHelpers::GetSelectedFolders()
{
	FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
	TArray<FString> SelectedFolders;
	ContentBrowserModule.Get().GetSelectedFolders(SelectedFolders);
	return SelectedFolders;
}

void UUE_CppHelpers::SetSelectedAssets(TArray<FString> Paths)
{
	FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
	TArray<FName> PathsName;
	for (FString Path : Paths) {
		PathsName.Add(*Path);
	}
	FARFilter AssetFilter;
	AssetFilter.PackageNames = PathsName;
	TArray<FAssetData> AssetDatas;
	AssetRegistryModule.Get().GetAssets(AssetFilter, AssetDatas);
	ContentBrowserModule.Get().SyncBrowserToAssets(AssetDatas);
}

void UUE_CppHelpers::SetSelectedFolders(TArray<FString> Paths)
{
	FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
	ContentBrowserModule.Get().SyncBrowserToFolders(Paths);
}
