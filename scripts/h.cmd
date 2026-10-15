@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0.."

REM Overzicht van gebruikerscommando's, of doorverwijzen naar <cmd> -h.
REM   scripts\h.cmd
REM   scripts\h.cmd check
REM   scripts\h.cmd bieb hernoem
REM
REM Echo: alleen eenvoudige ASCII (cmd-codepage).
REM Geen "call :row" met beschrijvingen die haakjes bevatten: dat breekt
REM de cmd-parser en kan oneindige recursie geven (BATCH RECURSION).

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
echo   h
echo     overzicht of hulp per commando
echo   validate
echo     vsa/mvsa validate op de catalogus
echo   check
echo     preflight / CI-spiegel ^(validate, producten, Hugo^)
echo   build
echo     site bouwen naar generated\site
echo   serve
echo     lokale preview http://127.0.0.1:18732/
echo   products
echo     afgeleide producten ^(PDF/MXL/mp3/...^) bouwen
echo   all-products
echo     alias: products --kinds all
echo   vsa-products
echo     Coria-.vsa.mxl + .vsa.pdf bij catalogus-.vsa
echo   mscz-products
echo     PDF + Coria-.mxl bij basispartituur-.mscz
echo   tekstblad-products
echo     PDF bij .tekstblad.md
echo   mvsa-products
echo     Coria-.mvsa.mxl + .mvsa.pdf bij .mvsa
echo   audio-products
echo     preview-.mp3 ^(Beluisteren^)
echo   lyrics-products
echo     lyrics.txt ^(.vsa/.mvsa/.mscz^)
echo   import-mvsa
echo     bewerkvorm .mscz.mvsa naast basis-.mscz
echo   layout
echo     basispartituur-layout op .mscz/.mxl
echo   ensure-bibliotheek-id
echo     colofon Bibliotheek-id: op .mscz
echo   bump-vsa-tooling-pin
echo     productie-pin vsa-tooling.pin bijwerken
echo   opkuisen
echo     herkomstanalyse + inhoudsopkuis
echo   bieb
echo     multi-command: accepteer^|hernoem^|verwijder^|kopieer ^(EN: accept^|rename^|delete^|copy^)
echo   update-werkvoorraad
echo     tabel input\werkvoorraad.md bijwerken
echo   werkbank-status
echo     open werkbank-cases
echo   lifecycle-grenzen
echo     grenzen werkbank vs catalogus
echo   oefenhoek-index
echo     bladermap-SVG uit .vsa
echo.
echo Uitgebreide man-pages: content-source\handleiding\scripts\
echo Repo-lijst: scripts\README.md
echo.
goto end_ok

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
