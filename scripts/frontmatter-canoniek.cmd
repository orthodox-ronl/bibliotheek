@echo off
setlocal
rem Canonieke-vorm-gate voor VSA/MVSA-frontmatter (stript leeg + ongedocumenteerd).
rem Spec: docs\specs\vsa-frontmatter.md
rem
rem   scripts\frontmatter-canoniek.cmd pad\naar\bestand.vsa
rem   scripts\frontmatter-canoniek.cmd --check pad\*.vsa
rem   scripts\frontmatter-canoniek.cmd --in-place pad\bestand.vsa

set ROOT=%~dp0..
python "%ROOT%\scripts\frontmatter_canoniek.py" %*
exit /b %ERRORLEVEL%
