@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Basispartituur-standaard (layoutprofiel partituur) op .mscz of .mxl.
REM Dunne wrapper om VSA-tooling; zie scripts\apply_mscz_layout.py

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
if "%~1"=="" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\apply_mscz_layout.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\layout.cmd ^<bestand.mscz^|.mxl^> [-o doel.mscz] [--id ID] [--bron "…"]
echo.
echo   Past de basispartituur-standaard toe (normaliseren / layouten).
echo   .mxl: zet -o naar een .mscz zonder spaties (meestal input\_werk\STAM\).
echo   .mscz: zonder -o in-place (opnieuw na editslag in MuseScore).
echo   --bron: bronvermelding (MuseScore source + colofon); anders uit
echo           bron.uitgangspunt van een sibling .vsa/.mvsa indien aanwezig.
echo   Weigert *.print.mscz. MuseScore 4 nodig bij .mxl-invoer.
echo.
echo Handleiding: content-source\handleiding\scripts\layout.md
echo.
endlocal
exit /b 2
