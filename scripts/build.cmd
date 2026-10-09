@echo off
setlocal
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

call scripts\_ensure.cmd --hugo --vsa-tool
if errorlevel 1 exit /b 1
python scripts\update_werkvoorraad.py
if errorlevel 1 exit /b 1
python scripts\fingerprint_coria_mxl.py
if errorlevel 1 exit /b 1
python scripts\sync_oefenhoek_index.py --svg
if errorlevel 1 exit /b 1
python scripts\write_build_stamp.py
if errorlevel 1 exit /b 1
if exist generated\site rmdir /s /q generated\site
hugo ^
  --minify ^
  --cleanDestinationDir ^
  --destination generated\site ^
  --config hugo.toml
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\build.cmd
echo.
echo   Bouwt de site naar generated\site ^(Hugo^).
echo   Roept eerst werkvoorraad, Coria-fingerprints en bladermap-SVG bij.
echo.
echo Handleiding: content-source\handleiding\scripts\build.md
echo.
endlocal
exit /b 0
