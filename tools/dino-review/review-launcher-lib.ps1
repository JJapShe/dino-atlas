function Get-DinoReviewConfig {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ReviewRoot
    )

    $portText = if ($env:DINO_REVIEW_PORT) { $env:DINO_REVIEW_PORT } else { "8792" }
    $reviewPort = 0
    if (-not [int]::TryParse($portText, [ref]$reviewPort) -or $reviewPort -lt 1024 -or $reviewPort -gt 65535) {
        throw "DINO_REVIEW_PORT must be an integer between 1024 and 65535."
    }

    $dataDir = Join-Path $ReviewRoot "data"
    [System.IO.Directory]::CreateDirectory($dataDir) | Out-Null
    $keyPath = Join-Path $dataDir "review-key"
    $reviewKey = if ($env:DINO_REVIEW_KEY) {
        $env:DINO_REVIEW_KEY.Trim()
    } elseif (Test-Path -LiteralPath $keyPath) {
        ([System.IO.File]::ReadAllText($keyPath)).Trim()
    } else {
        [guid]::NewGuid().ToString("N")
    }

    if ($reviewKey -notmatch '^[A-Za-z0-9._~-]{16,128}$') {
        throw "DINO_REVIEW_KEY must contain 16-128 URL-safe characters (letters, numbers, dot, underscore, tilde or hyphen)."
    }

    $env:DINO_REVIEW_KEY = $reviewKey
    $env:DINO_REVIEW_PORT = [string]$reviewPort
    $encodedKey = [uri]::EscapeDataString($reviewKey)

    [pscustomobject]@{
        Port = $reviewPort
        Key = $reviewKey
        EncodedKey = $encodedKey
        Url = "http://127.0.0.1:$reviewPort/?key=$encodedKey"
        HealthUrl = "http://127.0.0.1:$reviewPort/api/health"
        DataDir = $dataDir
        KeyPath = $keyPath
    }
}

function Save-DinoReviewKey {
    param(
        [Parameter(Mandatory = $true)]$Config
    )

    $currentKey = if (Test-Path -LiteralPath $Config.KeyPath) {
        ([System.IO.File]::ReadAllText($Config.KeyPath)).Trim()
    } else { "" }
    if ($currentKey -eq $Config.Key) { return }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Config.KeyPath, $Config.Key, $utf8NoBom)
}

function Test-DinoReviewHealth {
    param(
        [Parameter(Mandatory = $true)]$Config
    )

    try {
        $health = Invoke-RestMethod -Method Get -Uri $Config.HealthUrl `
            -Headers @{ "x-dino-review-key" = $Config.Key } -TimeoutSec 2
        return $health.ok -eq $true -and $health.service -eq "dino-review" -and $health.database -eq "sqlite"
    } catch {
        return $false
    }
}

function Get-DinoReviewNode {
    $candidates = New-Object System.Collections.Generic.List[string]
    $primaryRuntimeNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
    if (Test-Path -LiteralPath $primaryRuntimeNode) { $candidates.Add($primaryRuntimeNode) }

    $runtimeRoot = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\runtimes\cua_node"
    Get-ChildItem -LiteralPath $runtimeRoot -Recurse -Filter "node.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        ForEach-Object { $candidates.Add($_.FullName) }

    $pathNode = Get-Command node -ErrorAction SilentlyContinue
    if ($pathNode) { $candidates.Add($pathNode.Source) }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        $probe = New-Object System.Diagnostics.ProcessStartInfo
        $probe.FileName = $candidate
        $probe.Arguments = "--no-warnings -e `"require('node:sqlite')`""
        $probe.UseShellExecute = $false
        $probe.CreateNoWindow = $true
        $probe.RedirectStandardOutput = $true
        $probe.RedirectStandardError = $true
        $probeProcess = $null
        try {
            $probeProcess = [System.Diagnostics.Process]::Start($probe)
            $probeProcess.WaitForExit()
            if ($probeProcess.ExitCode -eq 0) { return $candidate }
        } catch {
            continue
        } finally {
            if ($probeProcess) { $probeProcess.Dispose() }
        }
    }

    throw "No Node.js runtime with node:sqlite support was found. Use the bundled Node 24 runtime."
}

function Get-DinoReviewListener {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
}

function Get-DinoReviewListenerDescription {
    param(
        [Parameter(Mandatory = $true)]$Listener
    )

    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($Listener.OwningProcess)" -ErrorAction SilentlyContinue
    if (-not $process) { return "PID $($Listener.OwningProcess)" }
    $executable = if ($process.ExecutablePath) { $process.ExecutablePath } else { "executable unavailable" }
    return "PID $($process.ProcessId) $($process.Name) ($executable)"
}

function Test-DinoAtlasHealth {
    param(
        [string]$Url = "http://127.0.0.1:8020/index.html"
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
        return $response.StatusCode -eq 200 `
            -and $response.Content -match '<title>Dino Atlas' `
            -and $response.Content -match '<body data-app-mode="public"'
    } catch {
        return $false
    }
}

function Start-DinoReviewBackgroundServer {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ReviewRoot,
        [Parameter(Mandatory = $true)]$Config
    )

    $node = Get-DinoReviewNode
    $stdoutLog = Join-Path $Config.DataDir "review-server.stdout.log"
    $stderrLog = Join-Path $Config.DataDir "review-server.stderr.log"
    $process = Start-Process -FilePath $node -ArgumentList @("server.js") `
        -WorkingDirectory $ReviewRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog

    for ($attempt = 0; $attempt -lt 40; $attempt += 1) {
        Start-Sleep -Milliseconds 250
        $process.Refresh()
        if ($process.HasExited) {
            $details = if (Test-Path -LiteralPath $stderrLog) {
                (Get-Content -LiteralPath $stderrLog -Encoding UTF8 -Tail 20 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
            } else { "No stderr log was written." }
            throw "Dino review server exited with code $($process.ExitCode).`n$details"
        }
        if (Test-DinoReviewHealth -Config $Config) { return $process }
    }

    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
    $details = if (Test-Path -LiteralPath $stderrLog) {
        (Get-Content -LiteralPath $stderrLog -Encoding UTF8 -Tail 20 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
    } else { "No stderr log was written." }
    throw "Dino review server did not become healthy on port $($Config.Port).`n$details"
}
