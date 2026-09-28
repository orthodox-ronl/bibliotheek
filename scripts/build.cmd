@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo --vsa-tool
if errorlevel 1 exit /b 1
python scripts\update_werkvoorraad.py
if errorlevel 1 exit /b 1
python scripts\fingerprint_coria_mxl.py
if errorlevel 1 exit /b 1
if exist generated\site rmdir /s /q generated\site
hugo ^
  --minify ^
  --cleanDestinationDir ^
  --destination generated\site ^
  --config hugo.toml
exit /b %ERRORLEVEL%
