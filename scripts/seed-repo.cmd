@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\seed_repo.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\seed-repo.cmd ^<doelmap^> [opties]
echo.
echo Kopieert deze bibliotheek-repo kaal naar een map buiten de repo:
echo bronnen, scripts, docs, homepage, tekstblad-schermproducten -
echo zonder regenereerbare catalogus-/koormap-afgeleiden.
echo.
echo Opties o.a.: --dry-run  --force  --configure  --git-init
echo   --initial-commit  --ensure  --repo-name  --site-title
echo.
echo Handleiding: content-source\handleiding\scripts\seed-repo.md
echo.
python scripts\seed_repo.py -h
endlocal
exit /b %ERRORLEVEL%
