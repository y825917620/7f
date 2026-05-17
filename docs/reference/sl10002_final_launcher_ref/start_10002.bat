@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title SL10002 SL10002 V45 ControlOnly ResourcePreload Launcher
set "LOGFILE=%~dp0SL10002_launcher_console_v45.log"
set "ONELOG=%~dp0SL10002_ONE_LOG.txt"

:MENU
cls
echo ======================================================
echo  SL10002 SL10002 V45 ControlOnly ResourcePreload Launcher
echo ======================================================
echo  1. Single loopback / local host test [default]
echo  2. LAN host
echo  3. LAN client join host
echo  4. Generate SL10002_ONE_LOG.txt only
echo  5. Stop port 29002
echo  0. Exit
echo ======================================================
echo  Send only this file after testing: SL10002_ONE_LOG.txt
echo.
set "CHOICE="
set /p "CHOICE=Choose number and press Enter: "
if "%CHOICE%"=="" set "CHOICE=1"

if "%CHOICE%"=="1" goto SINGLE
if "%CHOICE%"=="2" goto HOST
if "%CHOICE%"=="3" goto CLIENT
if "%CHOICE%"=="4" goto ONLYLOG
if "%CHOICE%"=="5" goto STOPPORT
if "%CHOICE%"=="0" exit /b 0
goto MENU

:SINGLE
cls
echo Starting: single loopback / local host test...
echo Console log: %LOGFILE%
echo One log will be generated after game exits: %ONELOG%
> "%ONELOG%" echo SL10002 ONE LOG V45 prestart. Mode=Single. resource-preload controlonly baseline.
>> "%ONELOG%" echo If the game blocks before exit, V45 auto-refreshes this log after 35 seconds.
start "" /B powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 35; & '%~dp0SL10002_MakeOneLog.ps1' -VersionTag V45" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0SL10002_FinalLauncher.ps1" -Mode Single -HostIP 127.0.0.1 -PlayerName Player1 -PlayerSlot 1 -ProtocolVariant ControlOnly >> "%LOGFILE%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
call :MAKEONELOG
if not "%EXITCODE%"=="0" goto ERR
echo Game exited. Send only: SL10002_ONE_LOG.txt
pause
exit /b 0

:HOST
cls
set "HOSTIP="
echo LAN host mode.
echo Leave Host IP empty for auto select. If wrong, enter 192.168.x.x manually.
set /p "HOSTIP=Host IP optional: "
echo Starting: LAN host...
> "%ONELOG%" echo SL10002 ONE LOG V45 prestart. Mode=Host. resource-preload controlonly baseline.
start "" /B powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 35; & '%~dp0SL10002_MakeOneLog.ps1' -VersionTag V45" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0SL10002_FinalLauncher.ps1" -Mode Host -HostIP "%HOSTIP%" -PlayerName Player1 -PlayerSlot 1 -ProtocolVariant ControlOnly >> "%LOGFILE%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
call :MAKEONELOG
if not "%EXITCODE%"=="0" goto ERR
echo Game exited. Send only: SL10002_ONE_LOG.txt
pause
exit /b 0

:CLIENT
cls
set "HOSTIP="
set "PLAYERNAME="
set "PLAYERSLOT="
set /p "HOSTIP=Host LAN IP required: "
set /p "PLAYERNAME=Player name default Player2: "
if "%PLAYERNAME%"=="" set "PLAYERNAME=Player2"
set /p "PLAYERSLOT=Player slot 1-24 default 2: "
if "%PLAYERSLOT%"=="" set "PLAYERSLOT=2"
echo Starting: client join %HOSTIP% ...
> "%ONELOG%" echo SL10002 ONE LOG V45 prestart. Mode=Client. LAN core client baseline.
start "" /B powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 35; & '%~dp0SL10002_MakeOneLog.ps1' -VersionTag V45" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0SL10002_FinalLauncher.ps1" -Mode Client -HostIP "%HOSTIP%" -PlayerName "%PLAYERNAME%" -PlayerSlot %PLAYERSLOT% -ProtocolVariant ControlOnly >> "%LOGFILE%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
call :MAKEONELOG
if not "%EXITCODE%"=="0" goto ERR
echo Game exited. Send only: SL10002_ONE_LOG.txt
pause
exit /b 0

:ONLYLOG
call :MAKEONELOG
echo Generated: SL10002_ONE_LOG.txt
echo Send only this file.
pause
exit /b 0

:STOPPORT
echo Stopping processes listening on port 29002...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":29002"') do taskkill /F /PID %%p >nul 2>nul
call :MAKEONELOG
echo Done.
pause
exit /b 0

:MAKEONELOG
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0SL10002_MakeOneLog.ps1" -VersionTag V45 >nul 2>nul
exit /b 0

:ERR
echo.
echo Launcher or game exited abnormally. Send only: SL10002_ONE_LOG.txt
pause
exit /b 1
