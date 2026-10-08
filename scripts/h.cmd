@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0.."

REM Overzicht van gebruikerscommando's, of doorverwijzen naar <cmd> -h.
REM   scripts\h.cmd
REM   scripts\h.cmd check
REM   scripts\h.cmd bieb hernoem
REM
REM Echo: alleen eenvoudige ASCII (cmd-codepage).

if /I "%~1"=="-h" goto usage_h
if /I "%~1"=="--help" goto usage_h
if "%~1"=="" goto catalog

REM Normaliseer: scripts\foo.cmd -> foo
set "CMD=%~1"
set "CMD=!CMD:scripts\=!"
set "CMD=!CMD:.cmd=!"

if /I "!CMD!"=="h" goto usage_h
if /I "!CMD!"=="help" goto usage_h

if /I "!CMD!"=="bieb" goto run_bieb_help
if not exist "scripts\!CMD!.cmd" goto unknown

REM Zelfde als: <command> -h
call "scripts\!CMD!.cmd" -h
exit /b %ERRORLEVEL%

:run_bieb_help
REM h bieb           -> bieb -h
REM h bieb hernoem   -> bieb hernoem -h
REM (Gebruik geen %%* na shift: %%* verandert niet op Windows-cmd.)
if "%~2"=="" (
  call scripts\bieb.cmd -h
) else (
  call scripts\bieb.cmd %~2 %~3 %~4 %~5 %~6 %~7 %~8 %~9 -h
)
exit /b %ERRORLEVEL%

:catalog
echo.
echo === bibliotheek-commando's ===
echo Meer hulp: h ^<naam^>   ^(zelfde als ^<naam^> -h^)
echo Voorbeelden: h check   ^|   h bieb   ^|   h bieb hernoem
echo.
call :row "h" "overzicht of hulp per commando"
call :row "validate" "vsa/mvsa validate op de catalogus"
call :row "check" "preflight / CI-spiegel (validate, producten, Hugo)"
call :row "build" "site bouwen naar generated\site"
call :row "serve" "lokale preview http://127.0.0.1:18732/"
call :row "products" "afgeleide producten (PDF/MXL/mp3/...) bouwen"
call :row "all-products" "alias: products --kinds all"
call :row "vsa-products" "Coria-.vsa.mxl + .vsa.pdf bij catalogus-.vsa"
call :row "mscz-products" "PDF + Coria-.mxl bij basispartituur-.mscz"
call :row "tekstblad-products" "PDF bij .tekstblad.md"
call :row "mvsa-products" "Coria-.mvsa.mxl + .mvsa.pdf bij .mvsa"
call :row "audio-products" "preview-.mp3 (Beluisteren)"
call :row "lyrics-products" "lyrics.txt (.vsa/.mvsa/.mscz)"
call :row "import-mvsa" "bewerkvorm .mscz.mvsa naast basis-.mscz"
call :row "layout" "basispartituur-layout op .mscz/.mxl"
call :row "ensure-bibliotheek-id" "colofon Bibliotheek-id: op .mscz"
call :row "opkuisen" "herkomstanalyse + inhoudsopkuis"
call :row "bieb" "multi-command: accepteer | hernoem"
call :row "update-werkvoorraad" "tabel input\werkvoorraad.md bijwerken"
call :row "werkbank-status" "open werkbank-cases"
call :row "lifecycle-grenzen" "grenzen werkbank vs catalogus"
call :row "oefenhoek-index" "bladermap-SVG uit .vsa"
echo.
echo Uitgebreide man-pages: content-source\handleiding\scripts\
echo Repo-lijst: scripts\README.md
echo.
goto end_ok

:row
echo   %~1
echo     %~2
goto :eof

:unknown
echo Onbekend commando: %CMD%
echo Typ "h" voor de lijst, of "h -h" voor uitleg.
exit /b 1

:usage_h
echo.
echo Gebruik:
echo   scripts\h.cmd                 korte catalogus
echo   scripts\h.cmd ^<naam^>          zelfde als ^<naam^> -h
echo   scripts\h.cmd bieb hernoem     zelfde als bieb hernoem -h
echo   scripts\h.cmd -h              deze uitleg
echo.
echo Met .\scripts op PATH: h   of   h check
echo.
goto end_ok

:end_ok
endlocal
exit /b 0
