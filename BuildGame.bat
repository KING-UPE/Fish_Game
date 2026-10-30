@echo off
rem Compile the C++ game module (close the editor first).
rem Set UE_ROOT if your engine is not in D:\UE_5.8
if "%UE_ROOT%"=="" set "UE_ROOT=D:\UE_5.8"
call "%UE_ROOT%\Engine\Build\BatchFiles\Build.bat" FishGameEditor Win64 Development "-Project=%~dp0FishGame.uproject" -WaitMutex
pause
