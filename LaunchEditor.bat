@echo off
rem Launch Blue Signal in the UE 5.8 editor with a safe local DDC (avoids the ZenServer DDC hang).
rem Set UE_ROOT if your engine is not in D:\UE_5.8
if "%UE_ROOT%"=="" set "UE_ROOT=D:\UE_5.8"
start "" "%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0FishGame.uproject" -ddc=InstalledNoZenLocalFallback -ModelContextProtocolPort=18765 %*
