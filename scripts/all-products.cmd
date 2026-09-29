@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo === all-products: ontbrekende/stale bibliotheek-producten ===
call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

echo.
echo --- vsa-products ---
call scripts\vsa-products.cmd %*
if errorlevel 1 exit /b 1

echo.
echo --- mscz-products ---
call scripts\mscz-products.cmd %*
if errorlevel 1 exit /b 1

echo.
echo --- tekstblad-products ---
call scripts\tekstblad-products.cmd %*
if errorlevel 1 exit /b 1

echo.
echo --- mvsa-products ---
call scripts\mvsa-products.cmd %*
if errorlevel 1 exit /b 1

echo.
echo --- import-mvsa ^(alleen bestaande siblings^) ---
call scripts\import-mvsa.cmd %*
if errorlevel 1 exit /b 1

echo.
echo --- audio-products ---
call scripts\audio-products.cmd %*
if errorlevel 1 exit /b 1

echo.
echo OK: all-products klaar
exit /b 0
