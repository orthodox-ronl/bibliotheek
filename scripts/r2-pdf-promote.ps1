# Promoveer R2 development/ → production/ en leeg development/.
# Voorbeeld:  .\scripts\r2-pdf-promote.ps1 --dry-run

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$envPs1 = Join-Path $PSScriptRoot "r2-env.ps1"
$envCmd = Join-Path $PSScriptRoot "r2-env.cmd"
if (Test-Path -LiteralPath $envPs1) {
    . $envPs1
} elseif (Test-Path -LiteralPath $envCmd) {
    cmd.exe /d /c "call `"$envCmd`""
}

python (Join-Path $PSScriptRoot "r2_pdf_promote.py") @args
exit $LASTEXITCODE
