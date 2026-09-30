@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
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
