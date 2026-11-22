param(
  [string]$Label = '',
  [string]$Model = 'qwen3.6-35b-a3b-ud-q3_k_m',
  [string]$BaseUrl = 'http://127.0.0.1:8080/v1/chat/completions',
  [string]$Categories = 'swe,aime,mmlu,gpqa,open_ended,traps',
  [string]$Compare = '',
  [int]$Timeout = 300,
  [string]$Resume = '',
  [int]$Limit = 0
)

$py = '<USERPROFILE>\AppData\Local\Programs\Python\Python311\python.exe'
$runner = '<REPO>\open-ended\unified-suite-91\run_suite.py'

Write-Output '=== server health ==='
try {
  $h = Invoke-RestMethod 'http://127.0.0.1:8080/health' -TimeoutSec 5
  Write-Output "8080 loaded=$($h.loaded) model=$($h.model)"
} catch {
  Write-Output 'WARNING: 8080 health check failed'
}

$args = @($runner, '--model', $Model, '--base-url', $BaseUrl,
          '--categories', $Categories, '--timeout', "$Timeout")
if ($Label)    { $args += @('--label', $Label) }
if ($Compare)  { $args += @('--compare', $Compare) }
if ($Resume)   { $args += @('--resume', $Resume) }
if ($Limit)    { $args += @('--limit', "$Limit") }

& $py @args
exit $LASTEXITCODE
