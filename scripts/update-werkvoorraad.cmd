@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\update_werkvoorraad.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\update-werkvoorraad.cmd
echo.
echo   Vult de tabel in content-source\input\werkvoorraad.md uit bestanden op schijf.
echo   Doel-id en notities in bestaande rijen blijven staan.
echo   Vernieuwt data\werkbank-status.json (special page Werkbank).
echo   Verwijdert generated\content\input (geen Hugo-pagina's voor inputs).
echo   check / build / serve doen dit ook.
echo.
echo Handleiding: content-source\handleiding\scripts\update-werkvoorraad.md
echo.
endlocal
exit /b 2
