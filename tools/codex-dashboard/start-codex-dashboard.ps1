$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$node = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\runtimes\cua_node\1b23c930bdf84ed6\bin\node.exe"

if (-not (Test-Path -LiteralPath $node)) {
    $node = "node"
}

Set-Location -LiteralPath $scriptDir
& $node .\server.js
