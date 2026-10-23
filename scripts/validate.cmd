@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

where vsa >nul 2>&1
if errorlevel 1 (
  echo ERROR: vsa not on PATH after _ensure --vsa-tool
  exit /b 1
)

set "TARGET=content-source\catalogus"
if not "%~1"=="" set "TARGET=%~1"

echo === bibliotheek validate: vsa validate %TARGET% ===
vsa validate "%TARGET%"
if errorlevel 1 (
  echo ERROR: vsa validate failed
  exit /b 1
)

where mvsa >nul 2>&1
if not errorlevel 1 (
  dir /s /b "%TARGET%\*.mvsa" >nul 2>&1
  if not errorlevel 1 (
    echo === bibliotheek validate: mvsa validate %TARGET% ===
    mvsa validate "%TARGET%"
    if errorlevel 1 (
      echo ERROR: mvsa validate failed
      exit /b 1
    )
  )
)

echo OK: validate
exit /b 0

:usage
echo.
echo Gebruik: scripts\validate.cmd [map]
echo.
echo   Zonder map: content-source\catalogus
echo   Draait vsa validate ^(en mvsa validate als er .mvsa staat^).
echo.
echo Handleiding: content-source\handleiding\scripts\validate.md
echo.
endlocal
exit /b 0
