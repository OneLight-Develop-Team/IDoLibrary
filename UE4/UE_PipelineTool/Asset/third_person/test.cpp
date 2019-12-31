// Fill out your copyright notice in the Description page of Project Settings.


#include "test.h"
#include "D:\UE_4.22\Engine\Plugins\Experimental\PythonScriptPlugin\Source\PythonScriptPlugin\Private\PythonScriptPlugin.h"
void Utest::ExecutePython(FString snippet)

{
	FPythonScriptPlugin::Get()->ExecPythonCommand(*snippet);
}
