@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\cleanup_chained_products.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\cleanup-chained-products.cmd [map^|bestand] [--apply]
echo.
echo Verwijdert ketting-afgeleiden en verkeerde siblings, bijvoorbeeld:
echo   {stam}.mvsa.mscz.mp3
echo   {stam}.mscz.mscz / {stam}.mscz.mscz.mp3
echo   {stam}.mscz.score-ir.json / {stam}.mscz.from-ir.musicxml
echo.
echo Laat geldige enkele producten staan, bijvoorbeeld:
echo   {stam}.mvsa.mscz
echo   {stam}.mvsa.mp3
echo   {stam}.mvsa.score-ir.json
echo   {stam}.mscz.mvsa
echo   {stam}.mscz-1.svg
echo.
echo Standaardmap: content-source\catalogus
echo Zonder --apply alleen tonen ^(dry-run^). Met --apply echt wissen.
echo.
python scripts\cleanup_chained_products.py -h
endlocal
exit /b %ERRORLEVEL%
