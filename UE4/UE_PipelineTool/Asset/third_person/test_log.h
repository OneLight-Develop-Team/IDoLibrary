// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "test_log.generated.h"

/**
 * 
 */
UCLASS()
class THIRD_PERSON_API Utest_log : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
	UFUNCTION(BlueprintCallable)
		static void PythonLog(FString string);
};
