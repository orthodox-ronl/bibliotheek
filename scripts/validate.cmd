@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

where vsa >nul 2>&1
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  vsa not on PATH after _ensure --vsa-tool"
  exit /b 1
)

set "RAW=content-source\catalogus"
if not "%~1"=="" set "RAW=%~1"

set "RESOLVE_OUT=%TEMP%\bibliotheek-validate-target.txt"
python scripts\resolve_cli_path.py "%RAW%" > "%RESOLVE_OUT%"
if errorlevel 1 (
  del "%RESOLVE_OUT%" 2>nul
  exit /b 1
)
set /p TARGET=<"%RESOLVE_OUT%"
del "%RESOLVE_OUT%" 2>nul
if not defined TARGET (
  call scripts\_msg.cmd hard "FAIL  kon pad niet oplossen: %RAW%"
  exit /b 1
)

call scripts\_msg.cmd section "=== validate: vsa %TARGET% ==="
vsa validate "%TARGET%"
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  vsa validate failed"
  exit /b 1
)

where mvsa >nul 2>&1
if not errorlevel 1 (
  dir /s /b "%TARGET%\*.mvsa" >nul 2>&1
  if not errorlevel 1 (
    call scripts\_msg.cmd section "=== validate: mvsa %TARGET% ==="
    mvsa validate "%TARGET%"
    if errorlevel 1 (
      call scripts\_msg.cmd hard "ERROR  mvsa validate failed"
      exit /b 1
    )
  )
)

call scripts\_msg.cmd ok "OK  validate"
exit /b 0

:usage
echo.
echo Gebruik: scripts\validate.cmd [map]
echo.
echo   Zonder map: content-source\catalogus
echo   Korte paden: t.o.v. content-source, catalogus of koormappen.
echo   Draait vsa validate ^(en mvsa validate als er .mvsa staat^).
echo.
echo Handleiding: content-source\handleiding\scripts\validate.md
echo.
endlocal
exit /b 0
