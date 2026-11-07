@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

if exist "scripts\r2-env.cmd" (
  call "scripts\r2-env.cmd"
  if errorlevel 1 exit /b %ERRORLEVEL%
)

python scripts\r2_pdf_opschonen.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\r2-pdf-opschonen.cmd [--apply] [pad ...]
echo          scripts\r2-pdf-opschonen.cmd --fail-if-tracked-on-main
echo.
echo Wis lokale blad-PDF's die SHA-256-gelijk zijn aan R2 production/.
echo Zonder --apply: alleen tonen ^(dry-run^).
echo.
echo Na stabiele upload: r2-pdf-upload, daarna dit met --apply.
echo.
python scripts\r2_pdf_opschonen.py -h
endlocal
exit /b %ERRORLEVEL%
