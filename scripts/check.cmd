@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

set "STRICT="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--strict" set "STRICT=1" & shift & goto parse_args
if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
echo Onbekende optie: %~1
goto usage

:args_done

call scripts\_ensure.cmd --hugo --vsa-tool
if errorlevel 1 exit /b 1

echo === bibliotheek check ^(validate + producten + Hugo + Coria^) ===
where vsa >nul 2>&1
if errorlevel 1 (
  echo ERROR: vsa not on PATH after _ensure --vsa-tool
  exit /b 1
)
vsa --version
if errorlevel 1 exit /b 1

call scripts\validate.cmd content-source\catalogus
if errorlevel 1 exit /b 1

python scripts\update_werkvoorraad.py
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_vsa_products.py --fail
) else (
  python scripts\check_vsa_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_mscz_products.py --fail
) else (
  python scripts\check_mscz_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_tekstblad_products.py --fail
) else (
  python scripts\check_tekstblad_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_import_mvsa.py --fail
) else (
  python scripts\check_import_mvsa.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_mvsa_products.py --fail
) else (
  python scripts\check_mvsa_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_audio_products.py --fail
) else (
  python scripts\check_audio_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_lyrics_products.py --fail
) else (
  python scripts\check_lyrics_products.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\check_mxl_playback_contract.py --fail
) else (
  python scripts\check_mxl_playback_contract.py
)
if errorlevel 1 exit /b 1

if defined STRICT (
  python scripts\ensure_bibliotheek_id.py --check-only --fail
) else (
  python scripts\ensure_bibliotheek_id.py --check-only
)
if errorlevel 1 exit /b 1

REM Relatieve TOC-links moeten bestaan (anders Hugo-404 na hernoem).
python scripts\check_koormap_slot_links.py --fail
if errorlevel 1 exit /b 1

python scripts\fingerprint_coria_mxl.py
if errorlevel 1 exit /b 1

python scripts\sync_oefenhoek_index.py --svg
if errorlevel 1 exit /b 1

python scripts\build_zoek_index.py
if errorlevel 1 exit /b 1

if exist generated\site rmdir /s /q generated\site
hugo ^
  --minify ^
  --cleanDestinationDir ^
  --destination generated\site ^
  --config hugo.toml
if errorlevel 1 (
  echo ERROR: hugo build failed
  exit /b 1
)
echo OK: hugo build
exit /b 0

:usage
echo.
echo Gebruik: scripts\check.cmd [--strict]
echo.
echo   --strict   faal op stale/missing producten of bibliotheek-id ^(CI-spiegel^)
echo.
echo Zonder --strict: product-/id-checks waarschuwen lokaal maar falen niet
echo ^(behalve op main / BIBLIOTHEEK_PRODUCTS_STRICT=1^). CI faalt altijd.
echo.
endlocal
exit /b 2
