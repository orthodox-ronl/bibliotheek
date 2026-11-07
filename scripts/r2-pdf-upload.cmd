@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

if exist "scripts\r2-env.cmd" (
  call "scripts\r2-env.cmd"
  if errorlevel 1 exit /b %ERRORLEVEL%
) else if exist "scripts\r2-env.ps1" (
  echo Geen scripts\r2-env.cmd — Python probeert r2-env.ps1 te laden.
) else (
  echo Let op: geen scripts\r2-env.cmd of r2-env.ps1. Zie r2-env.*.example
)

python scripts\r2_pdf_upload.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\r2-pdf-upload.cmd [--env production] [--dry-run] [pad ...]
echo          scripts\r2-pdf-upload.cmd --list-buckets
echo          scripts\r2-pdf-upload.cmd --purge-prefix preview [--apply-purge]
echo          scripts\r2-pdf-upload.cmd --restamp-metadata [--only-missing-sha]
echo.
echo Upload blad-PDF's naar R2 production/ ^(één set^). Zet SHA-256-metadata.
echo --restamp-metadata: vingerafdrukken op bestaande R2-PDF's.
echo --env preview mag niet meer.
echo.
echo Credentials: scripts\r2-env.cmd ^(gitignore^).
echo Plan: docs\plans\pdf-r2.md
echo.
python scripts\r2_pdf_upload.py -h
endlocal
exit /b %ERRORLEVEL%
