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
echo Gebruik: scripts\r2-pdf-upload.cmd [--env production^|development] [--dry-run] [pad ...]
echo          scripts\r2-pdf-upload.cmd --list-buckets
echo          scripts\r2-pdf-upload.cmd --purge-prefix development [--apply-purge]
echo          scripts\r2-pdf-upload.cmd --restamp-metadata [--only-missing-sha]
echo          scripts\r2-pdf-upload.cmd --write-manifest-from-r2
echo --env development = alleen diff t.o.v. production/. --env preview mag niet.
echo.
echo Upload blad-PDF's naar R2. production/ = volledige set; development/ = diff.
echo --restamp-metadata: vingerafdrukken op bestaande production-PDF's.
echo Na merge naar main: scripts\r2-pdf-promote.cmd
echo.
echo Credentials: scripts\r2-env.cmd ^(gitignore^).
echo Plan: docs\plans\pdf-r2.md
echo.
python scripts\r2_pdf_upload.py -h
endlocal
exit /b %ERRORLEVEL%
