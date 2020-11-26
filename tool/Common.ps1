function Stop-Shell ([string]$msg, [int]$code) {
    if ($code -eq 0) {
        Write-Host $msg
    }
    else {
        Write-Host $msg -ForegroundColor Red
    }
    Write-Host -NoNewLine "Press any key to exit..."
    $null = $host.ui.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit $code
}

function Remove-Dir([string]$path) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
    }
}
