@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Steekproef: OSMD tekent speelplan-navigatie uit .from-ir.musicxml
REM (besluit 9 / docs/specs/schermpartituur.md) + S8 A1-adapter
REM (alleluia/9a-toon-8/groningen).

set "DIR=scripts\osmd-nav-check"
if not exist "%DIR%\package.json" (
  echo ERROR: %DIR%\package.json ontbreekt
  exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: node niet op PATH - OSMD-navigatiecheck
  exit /b 1
)

if not exist "%DIR%\node_modules\playwright" (
  echo === npm ci osmd-nav-check ===
  pushd "%DIR%"
  call npm ci
  if errorlevel 1 (
    popd
    exit /b 1
  )
  call npx playwright install chromium
  if errorlevel 1 (
    popd
    exit /b 1
  )
  popd
)

echo === OSMD-navigatie zichtbaar steekproef ===
pushd "%DIR%"
node check.mjs
set RC=%ERRORLEVEL%
if not "%RC%"=="0" (
  popd
  exit /b 1
)
echo === OSMD S8 A1-adapter steekproef ===
node s8-alleluia-hide-check.mjs
set RC=%ERRORLEVEL%
popd
if not "%RC%"=="0" exit /b 1
exit /b 0
