$ErrorActionPreference = 'Continue'
$fixture = '<REPO>\repair-cpp\v4'
$work = Join-Path $fixture 'run-qwen36'
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
Copy-Item -Recurse (Join-Path $fixture 'task') $work
Set-Location $work
$hermes = '<USERPROFILE>\AppData\Local\hermes\bin\hermes.exe'
$outLog = Join-Path $fixture 'run-qwen36-hermes-output.txt'
$timeLog = Join-Path $fixture 'run-qwen36-hermes-timing.txt'
$start = Get-Date
& $hermes -z 'Fix the C++ bugs in this repository according to AGENTS.md. All visible tests pass but the code is still wrong; read every contract carefully. You may compile and run tests locally. Do not modify anything under tests/ or include/. Standard C++ only. Keep fixes small and local.' --yolo --reasoning none *> $outLog
$code = $LASTEXITCODE
$end = Get-Date
$elapsed = ($end - $start).TotalSeconds
@("Start=$($start.ToString('o'))","End=$($end.ToString('o'))","ElapsedSeconds=$elapsed","ExitCode=$code") | Out-File -FilePath $timeLog -Encoding utf8
Write-Output "DONE exit=$code elapsed=$elapsed sec"
