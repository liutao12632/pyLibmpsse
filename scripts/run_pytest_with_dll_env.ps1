param(
    [Parameter(Mandatory = $false)]
    [string]$Ftd2xxDll = "ftd2xx.dll",

    [Parameter(Mandatory = $true)]
    [string]$LibMpsseDll,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$activateScript = Join-Path $repoRoot "venv_3_12_x86\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    . $activateScript
    Write-Host "Activated virtual environment: $activateScript"
}
else {
    Write-Warning "Virtual environment activation script not found: $activateScript"
}

$env:PYLIBMPSSE_FTD2XX_DLL = $Ftd2xxDll
$env:PYLIBMPSSE_LIBMPSSE_DLL = $LibMpsseDll

Write-Host "PYLIBMPSSE_FTD2XX_DLL=$env:PYLIBMPSSE_FTD2XX_DLL"
Write-Host "PYLIBMPSSE_LIBMPSSE_DLL=$env:PYLIBMPSSE_LIBMPSSE_DLL"

if (-not $PytestArgs -or $PytestArgs.Count -eq 0) {
    $PytestArgs = @("-m", "integration", "-s")
}

python -m pytest @PytestArgs
exit $LASTEXITCODE
