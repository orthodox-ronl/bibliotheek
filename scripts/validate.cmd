@echo off
setlocal EnableExtensions EnableDelayedExpansion
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

REM Enkel bestand: alleen het juiste straat-commando (geen vsa op .mvsa).
set "IS_DIR=0"
if exist "%TARGET%\" set "IS_DIR=1"
if "!IS_DIR!"=="0" if exist "%TARGET%" (
  for %%I in ("%TARGET%") do set "EXT=%%~xI"
  if /I "!EXT!"==".mvsa" goto validate_mvsa_file
  if /I "!EXT!"==".vsa" goto validate_vsa_file
  call scripts\_msg.cmd hard "ERROR  validate verwacht .vsa, .mvsa of een map — kreeg: %TARGET%"
  exit /b 1
)

REM Map: vsa voor .vsa/.md; mvsa als er .mvsa onder staat.
call scripts\_msg.cmd section "=== validate: vsa %TARGET% ==="
vsa validate "%TARGET%"
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  vsa validate failed"
  exit /b 1
)

where mvsa >nul 2>&1
if errorlevel 1 goto validate_ok
dir /s /b "%TARGET%\*.mvsa" >nul 2>&1
if errorlevel 1 goto validate_ok
call scripts\_msg.cmd section "=== validate: mvsa %TARGET% ==="
mvsa validate "%TARGET%"
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  mvsa validate failed"
  exit /b 1
)
goto validate_ok

:validate_vsa_file
call scripts\_msg.cmd section "=== validate: vsa %TARGET% ==="
vsa validate "%TARGET%"
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  vsa validate failed"
  exit /b 1
)
goto validate_ok

:validate_mvsa_file
where mvsa >nul 2>&1
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  mvsa not on PATH after _ensure --vsa-tool"
  exit /b 1
)
call scripts\_msg.cmd section "=== validate: mvsa %TARGET% ==="
mvsa validate "%TARGET%"
if errorlevel 1 (
  call scripts\_msg.cmd hard "ERROR  mvsa validate failed"
  exit /b 1
)
goto validate_ok

:validate_ok
call scripts\_msg.cmd ok "OK  validate"
exit /b 0

:usage
echo.
echo Gebruik: scripts\validate.cmd [map^|bestand]
echo.
echo   Zonder argument: content-source\catalogus
echo   .vsa-bestand  → vsa validate
echo   .mvsa-bestand → mvsa validate
echo   Map           → vsa validate, plus mvsa validate als er .mvsa onder staat
echo   Korte paden: t.o.v. content-source, catalogus of koormappen
echo                ^(zelfde G2 als raw vsa/mvsa validate: alleluia, communievers, …^).
echo.
echo Handleiding: content-source\handleiding\scripts\validate.md
echo Contract:    VSA-tooling docs\reference\cli\input-pad.md
echo.
endlocal
exit /b 0
