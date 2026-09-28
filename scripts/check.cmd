@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo --vsa-tool
if errorlevel 1 exit /b 1

echo === bibliotheek check ^(validate + Hugo + Coria fingerprints^) ===
where vsa >nul 2>&1
if errorlevel 1 (
  echo ERROR: vsa not on PATH after _ensure --vsa-tool
  exit /b 1
)
vsa --version
if errorlevel 1 exit /b 1

call scripts\validate.cmd content-source\bibliotheek
if errorlevel 1 exit /b 1

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
