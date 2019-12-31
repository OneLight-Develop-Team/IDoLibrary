// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "UE_CppHelpers.generated.h"

/**
 * 
 */
UCLASS()
class THIRD_PERSON_API UUE_CppHelpers : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static void ExecutePython(FString snippet);

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static void PythonLog(FString string);

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static TArray<FString> GetSelectedAssets();

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static TArray<FString> GetSelectedFolders();

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static void SetSelectedAssets(TArray<FString> Paths);

	UFUNCTION(BlueprintCallable, Category = "Unreal Python")
		static void SetSelectedFolders(TArray<FString> Paths);
};
