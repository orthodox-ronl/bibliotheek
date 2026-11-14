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

python scripts\r2_pdf_promote.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\r2-pdf-promote.cmd [--dry-run]
echo.
echo Kopieert R2 development/ naar production/, wist development/,
echo en maakt data\pdf-r2-development.json leeg.
echo.
echo Credentials: scripts\r2-env.cmd ^(gitignore^).
echo Plan: docs\plans\pdf-r2.md
echo.
python scripts\r2_pdf_promote.py -h
endlocal
exit /b %ERRORLEVEL%
