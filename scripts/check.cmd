@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo
if errorlevel 1 exit /b 1

echo === bibliotheek check ^(Hugo + Coria fingerprints^) ===
python scripts\fingerprint_coria_mxl.py
if errorlevel 1 exit /b 1

if exist generated\site rmdir /s /q generated\site
hugo ^
  --minify ^
  --cleanDestinationDir ^
  --destination generated\site ^
  --config hugo.toml
if errorlevel 1 (
  echo ERROR: hugo build failed
  exit /b 1
)
echo OK: hugo build
exit /b 0
