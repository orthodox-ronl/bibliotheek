@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\pagina_pdf.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\pagina-pdf.cmd ^<pad\naar\index.md^|map^> [--force]
echo          scripts\pagina-pdf.cmd --all-koormappen [--force]
echo.
echo Bouwt index.pagina.pdf naast de Markdown. Pad: één .md of een map
echo ^(recursief index.md^). --all-koormappen = content-source\koormappen.
echo Altijd kale blad-SVG's + koppen; bij pdf-bijelkaar: tooling --compact.
echo Geen catalogus-product-PDF's plakken.
echo.
python scripts\pagina_pdf.py -h
endlocal
exit /b %ERRORLEVEL%
