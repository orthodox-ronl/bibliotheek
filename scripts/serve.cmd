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

REM Poort 18732: niet 1313 (lokaal gereserveerd), niet 18731 (VSA-demo).
hugo server ^
  --disableFastRender ^
  --cleanDestinationDir ^
  --bind 127.0.0.1 ^
  --port 18732 ^
  --config hugo.toml
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\serve.cmd
echo.
echo   Lokale Hugo-preview op http://127.0.0.1:18732/
echo   ^(niet poort 1313, niet 18731^).
echo.
echo Handleiding: content-source\handleiding\scripts\serve.md
echo.
endlocal
exit /b 0
