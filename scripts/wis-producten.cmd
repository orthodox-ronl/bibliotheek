@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\wis_producten.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\wis-producten.cmd [map^|bestand ...] [--apply]
echo.
echo Wist alle gegenereerde bestanden uit catalogus en koormappen
echo ^(products, meta, index.md.pdf^), zodat alles opnieuw gemaakt kan worden.
echo.
echo Blijft staan: bronnen, map formules, handmatige mappen ^(manueel: true,
echo tekstbladen zoals dialoog-met-diaken^), .print.mscz en .mscz.mvsa.
echo.
echo Zonder --apply alleen tonen ^(dry-run^). Met --apply echt wissen.
echo.
python scripts\wis_producten.py -h
endlocal
exit /b %ERRORLEVEL%
