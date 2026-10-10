@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0.."

REM Schrijf vsa-tooling.pin naar de tip van VSA-tooling (default: main).
REM Commit/PR doe je zelf — dit script wijzigt alleen het pin-bestand.

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

set "DRY="
set "REF=main"
set "REPO=orthodox-ronl/VSA-tooling"

:parse
if "%~1"=="" goto run
if /I "%~1"=="--dry-run" (
  set "DRY=1"
  shift
  goto parse
)
if /I "%~1"=="--ref" (
  if "%~2"=="" (
    echo ERROR: --ref vereist een waarde ^(bijv. main of 0.2.0^)
    exit /b 2
  )
  set "REF=%~2"
  shift
  shift
  goto parse
)
REM Positionele ref: bump-vsa-tooling-pin 0.2.0
set "REF=%~1"
shift
goto parse

:run
where gh >nul 2>&1
if errorlevel 1 (
  echo ERROR: gh ^(GitHub CLI^) niet op PATH
  echo Installeer https://cli.github.com/ en log in met: gh auth login
  exit /b 1
)

set "PIN=vsa-tooling.pin"
set "OLD="
if exist "%PIN%" (
  set /p OLD=<"%PIN%"
)

echo === bump vsa-tooling.pin ===
echo Repo: %REPO%
echo Ref:  %REF%
if defined OLD (
  echo Oud:  !OLD!
) else (
  echo Oud:  ^(bestand ontbreekt^)
)

set "NEW="
for /f "usebackq delims=" %%S in (`gh api "repos/%REPO%/commits/%REF%" --jq .sha 2^>nul`) do set "NEW=%%S"
if not defined NEW (
  echo ERROR: kon SHA niet ophalen voor %REPO%@%REF%
  echo Controleer of gh ingelogd is en de ref bestaat.
  exit /b 1
)

echo Nieuw: %NEW%

if /I "!OLD!"=="!NEW!" (
  echo Pin wijst al naar deze commit. Niets te doen.
  exit /b 0
)

if defined DRY (
  echo Dry-run: %PIN% wordt niet geschreven.
  echo Zonder --dry-run schrijft het script het bestand; commit/PR naar main zelf.
  exit /b 0
)

> "%PIN%" echo %NEW%
if errorlevel 1 (
  echo ERROR: kon %PIN% niet schrijven
  exit /b 1
)

echo Geschreven: %PIN%
echo.
echo Volgende stap ^(productie op bibliotheek main^):
echo   git add vsa-tooling.pin
echo   git commit -m "chore: bump vsa-tooling.pin"
echo   git push
echo   ^(PR naar main van bibliotheek^)
echo.
echo Lokaal daarna met pin-mode:
echo   set BIBLIOTHEEK_TOOLING_MODE=pin
echo   scripts\_ensure.cmd --vsa-tool
exit /b 0

:usage
echo.
echo Gebruik: scripts\bump-vsa-tooling-pin.cmd [ref] [--dry-run]
echo          scripts\bump-vsa-tooling-pin.cmd --ref REF [--dry-run]
echo.
echo   Zet vsa-tooling.pin op de commit-SHA van orthodox-ronl/VSA-tooling.
echo   Zonder ref: tip van branch main.
echo   ref mag een branch, tag of SHA zijn ^(via gh api^).
echo.
echo   --dry-run   Toon oud/nieuw, schrijf het bestand niet.
echo.
echo   Commit en PR naar bibliotheek-main doe je zelf na een geslaagde bump.
echo   Preview-branch development floatt al op tooling-main ^(geen pin nodig^).
echo.
echo Handleiding: content-source\handleiding\scripts\bump-vsa-tooling-pin.md
echo Afspraken:   docs\tooling-koppeling.md
echo.
endlocal
exit /b 0
