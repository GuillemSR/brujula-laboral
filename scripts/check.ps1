$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

Push-Location $repoRoot
try {
    & $python -m ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m ruff format --check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m pytest
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
