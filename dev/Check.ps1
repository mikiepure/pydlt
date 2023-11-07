. ".\_Common.ps1"

Set-Location ".."

Write-Host "Checking ruff check..."
poetry run ruff check .
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check ruff check by error: $LastExitCode" 1
}

Write-Host "Checking ruff format..."
poetry run ruff format . --check
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check ruff format by error: $LastExitCode" 1
}

Write-Host "Checking pytest..."
poetry run pytest
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to check pytest by error: $LastExitCode" 1
}

Stop-Shell "Check was done" 0
