@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo
if errorlevel 1 exit /b 1
python scripts\fingerprint_coria_mxl.py
if errorlevel 1 exit /b 1

REM Poort 18732: niet 1313 (lokaal gereserveerd), niet 18731 (VSA-demo).
hugo server ^
  --disableFastRender ^
  --cleanDestinationDir ^
  --bind 127.0.0.1 ^
  --port 18732 ^
  --config hugo.toml
exit /b %ERRORLEVEL%
