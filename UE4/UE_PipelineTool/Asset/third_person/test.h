// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "test.generated.h"


/**
 * 
 */
UCLASS()
class THIRD_PERSON_API Utest : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

	UFUNCTION(BlueprintCallable)
		static void ExecutePython(FString string);
	
};
