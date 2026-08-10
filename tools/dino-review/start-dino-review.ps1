$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "review-launcher-lib.ps1")

$config = Get-DinoReviewConfig -ReviewRoot $scriptDir
$listener = Get-DinoReviewListener -Port $config.Port

if ($listener) {
    if (-not (Test-DinoReviewHealth -Config $config)) {
        $description = Get-DinoReviewListenerDescription -Listener $listener
        throw "Port $($config.Port) is occupied, but it is not the authenticated Dino review server for this local key. $description"
    }
    Save-DinoReviewKey -Config $config
    Write-Host "Dino review is already healthy at http://127.0.0.1:$($config.Port)/."
} else {
    Save-DinoReviewKey -Config $config
    $process = Start-DinoReviewBackgroundServer -ReviewRoot $scriptDir -Config $config
    Write-Host "Dino review started (PID $($process.Id)) at http://127.0.0.1:$($config.Port)/."
}

Start-Process $config.Url
