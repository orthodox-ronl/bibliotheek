@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

REM Credentials: lokale r2-env (gitignore). Python laadt ze ook zelf als nodig.
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
echo Gebruik: scripts\r2-pdf-upload.cmd --env production^|preview [--dry-run] [pad ...]
echo.
echo Upload blad-PDF's ^(index.md.pdf / translit^) naar Cloudflare R2.
echo Object-sleutel: {env}/{pad-onder-content-source}/{bestandsnaam}
echo Productie en preview zijn strikt gescheiden mappen.
echo.
echo Zonder pad: hele content-source. Met --dry-run: alleen sleutels tonen
echo ^(geen credentials nodig^).
echo.
echo Credentials: dit script roept eerst scripts\r2-env.cmd aan als die bestaat
echo ^(lokaal, in .gitignore; sjabloon: r2-env.*.example^).
echo Python: pip install boto3
echo Diagnose: scripts\r2-pdf-upload.cmd --list-buckets
echo.
echo Plan/terugkeer: docs\plans\pdf-r2.md
echo.
python scripts\r2_pdf_upload.py -h
endlocal
exit /b %ERRORLEVEL%
