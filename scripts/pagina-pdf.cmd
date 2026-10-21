@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\pagina_pdf.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\pagina-pdf.cmd ^<pad\naar\index.md^> [--force]
echo          scripts\pagina-pdf.cmd --all-koormappen [--force]
echo.
echo Bouwt index.pagina.pdf naast de Markdown door catalogus-product-PDF's
echo van de bieb/muziek-shortcodes achter elkaar te plakken.
echo.
python scripts\pagina_pdf.py -h
endlocal
exit /b %ERRORLEVEL%
