@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\sync_lyrics_products.py %*
if errorlevel 1 exit /b %ERRORLEVEL%

REM Zoekindex vernieuwen (tenzij dry-run: lyrics ongewijzigd, index toch ok).
echo.
echo --- zoekindex (static/zoek/index.json) ---
python scripts\build_zoek_index.py
exit /b %ERRORLEVEL%
