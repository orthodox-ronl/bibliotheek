@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Multi-command CLI: bieb accepteer|hernoem|verwijder|kopieer
REM Engelse aliassen: accept|rename|delete|copy

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
if "%~1"=="" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\bieb.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\bieb.cmd ^<subcommando^> [args...]
echo.
echo   accepteer   partituur/tekstblad opnemen onder catalogus-id
echo   hernoem     catalogus-id hernoemen ^(zangstuk/variant/uitvoeringsvorm^)
echo   verwijder   catalogus-id wissen ^(dangling refs rapporteren^)
echo   kopieer     uitvoeringsvorm kopiëren naar nieuw id
echo.
echo Engelse aliassen: accept, rename, delete, copy.
echo.
echo Voorbeelden:
echo   scripts\bieb.cmd accepteer trisagion/8a-nederlands/hemelum pad\naar\x.mscz --dry-run
echo   scripts\bieb.cmd hernoem ektinia/vredes ektinia/litanie --dry-run
echo   scripts\bieb.cmd verwijder ektinia/vredes/hemelum --dry-run
echo   scripts\bieb.cmd kopieer ektinia/vredes/hemelum groningen --dry-run
echo.
echo Handleiding:
echo   content-source\handleiding\scripts\bieb-accepteer.md
echo   content-source\handleiding\scripts\bieb-hernoem.md
echo   content-source\handleiding\scripts\bieb-verwijder.md
echo   content-source\handleiding\scripts\bieb-kopieer.md
echo.
endlocal
exit /b 2
