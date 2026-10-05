@echo off
setlocal
rem Migreer catalogus-.vsa/.mvsa-frontmatter naar het proefschema.
rem Spec: docs\specs\vsa-frontmatter.md
rem
rem   scripts\migrate-vsa-frontmatter.cmd
rem   scripts\migrate-vsa-frontmatter.cmd --dry-run

set ROOT=%~dp0..
python "%ROOT%\scripts\migrate_vsa_frontmatter.py" %*
exit /b %ERRORLEVEL%
