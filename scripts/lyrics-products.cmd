@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\sync_lyrics_products.py %*
exit /b %ERRORLEVEL%
