@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Multi-command CLI: bieb accepteer | (later zoek, hernoem, ...)

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
echo   accepteer   partituur/tekstblad opnemen onder bibliotheek-id
echo.
echo Voorbeeld:
echo   scripts\bieb.cmd accepteer 8-trisagion/8a-nederlands/hemelum pad\naar\x.mscz --dry-run
echo.
echo Handleiding: content-source\handleiding\scripts\bieb-accepteer.md
echo.
endlocal
exit /b 2
