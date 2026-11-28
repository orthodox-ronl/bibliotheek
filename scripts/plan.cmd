@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Leesbaar plan van alle productstraten (alleen lezen).
REM   scripts\plan.cmd            samenvatting per straat
REM   scripts\plan.cmd --lijst    ook elk te maken product

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

python scripts\plan.py %*
if errorlevel 1 exit /b 1
