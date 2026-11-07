# Upload blad-PDF's naar Cloudflare R2.
# Laadt eerst scripts/r2-env.ps1 (of .cmd) als die bestaat.
# Voorbeeld:  .\scripts\r2-pdf-upload.ps1 --env preview --dry-run

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$envCmd = Join-Path $PSScriptRoot "r2-env.cmd"
$envPs1 = Join-Path $PSScriptRoot "r2-env.ps1"

if (Test-Path -LiteralPath $envPs1) {
    . $envPs1
} elseif (Test-Path -LiteralPath $envCmd) {
    cmd.exe /d /c "call `"$envCmd`""
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    # cmd-set blijft niet in deze PowerShell-sessie; Python laadt r2-env.cmd zelf.
} else {
    Write-Host "Let op: geen scripts\r2-env.ps1 of r2-env.cmd. Zie r2-env.*.example"
}

python (Join-Path $PSScriptRoot "r2_pdf_upload.py") @args
exit $LASTEXITCODE
