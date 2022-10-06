. ".\_Common.ps1"

Set-Location ".."

Write-Host "Checking flake8..."
poetry run flake8
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check flake8 by error: $LastExitCode" 1
}

Write-Host "Checking black..."
poetry run black --check --diff .
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check black by error: $LastExitCode" 1
}

Write-Host "Checking pytest..."
poetry run pytest
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check pytest by error: $LastExitCode" 1
}

Stop-Shell "Check was done" 0
