. ".\_Common.ps1"

Set-Location ".."

Get-Command py *> $null
if (!$?) {
    Stop-Shell "'py' is required to use the script; Please install it" 1
}
Get-Command poetry *> $null
if (!$?) {
    Stop-Shell "'poetry' is required to use the script; Please install it" 1
}

if (Test-Path ".venv") {
    Write-Host "Python virtual environment is already created"
    $yesno = Read-Host "Do you want to re-create it? [y/N]"
    switch ($yesno) {
        "y" {
            Write-Host "Removing python virtual environment..."
            Remove-Dir ".venv"
            if (Test-Path ".venv") {
                Stop-Shell "Failed to remove python virtual environment" 1
            }
        }
        default {
            exit 0
        }
    }
}

Write-Host "Creating python virtual environment..."
py -m venv ".venv"
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to create python virtual environment by error: $LastExitCode" 1
}

Write-Host "Installing python required packages..."
poetry install
if ($LastExitCode -ne 0) {
    Stop-Shell "Failed to install python required packages by error: $LastExitCode" 1
}

Stop-Shell "Setup was done" 0
