// Fill out your copyright notice in the Description page of Project Settings.


#include "test_log.h"

void Utest_log::PythonLog(FString string)
{
	UE_LOG(LogTemp, Error, TEXT("%s"), *string);
}
