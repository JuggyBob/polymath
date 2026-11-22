$ErrorActionPreference = 'Stop'
$fixture = '<REPO>\repair-rust\v6'
$runDir  = Join-Path $fixture 'run-qwen36-v6'
$outTxt  = Join-Path $fixture 'run-qwen36-v6-hermes-output.txt'
$errTxt  = Join-Path $fixture 'run-qwen36-v6-stderr.txt'
$timeTxt = Join-Path $fixture 'run-qwen36-v6-timing.txt'
$hermes  = '<USERPROFILE>\AppData\Local\hermes\bin\hermes.exe'
# Guard: a previous C++ run read a parent README and edited task/ instead of the
# candidate copy. Pin the absolute workspace for this run too.
$prompt = @'
Fix the bugs in this repository. Your workspace is EXACTLY this directory and nothing else: <REPO>\repair-rust\v6\run-qwen36-v6 . Work only inside that directory. Do NOT list, read, write or patch any path outside it — in particular do NOT use <REPO>\repair-rust\v6\task\ or any parent directory. Ignore any README.md you may find above your workspace; the only specification is the README.md and the examples in examples/ INSIDE your workspace. DISTINCT is a feature to add across the lexer, parser, compiler, VM, disassembler and serialiser; its examples intentionally fail on the broken code. You may compile and run tests locally with rustc. Keep fixes small and local. Do not modify anything under tests/, include/ or the examples/. The visible tests and examples are the only specification.
'@

if (Test-Path $runDir) { Remove-Item $runDir -Recurse -Force }
Copy-Item (Join-Path $fixture 'task') $runDir -Recurse -Force

$launchCwd = (Get-Location).Path
if ($launchCwd -ine $runDir) { Set-Location -LiteralPath $runDir; $launchCwd = (Get-Location).Path }
if ($launchCwd -ine $runDir) { throw "Launch CWD mismatch: $launchCwd != $runDir" }

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $hermes
$psi.WorkingDirectory = $runDir
$psi.ArgumentList.Add('-z')
$psi.ArgumentList.Add($prompt.Trim())
$psi.ArgumentList.Add('--yolo')
$psi.ArgumentList.Add('--reasoning')
$psi.ArgumentList.Add('none')
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$start = Get-Date
$proc = [System.Diagnostics.Process]::Start($psi)
$outTask = $proc.StandardOutput.ReadToEndAsync()
$errTask = $proc.StandardError.ReadToEndAsync()
$capped = $false
if (-not $proc.WaitForExit(1800000)) {
    $capped = $true
    try { $proc.Kill($true) } catch { }
    $proc.WaitForExit(10000) | Out-Null
}
$out = $outTask.Result
$err = $errTask.Result
$end = Get-Date
$elapsed = [math]::Round(($end - $start).TotalSeconds, 1)
$exit = if ($capped) { 'CAPPED_1800s' } else { $proc.ExitCode }

[System.IO.File]::WriteAllText($outTxt, $out, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($errTxt, $err, [System.Text.UTF8Encoding]::new($false))
$timing = "start=$($start.ToString('o'))`nend=$($end.ToString('o'))`nelapsed_seconds=$elapsed`nexit_code=$exit`ncapped=$capped`nhermes_pid=$($proc.Id)`nrun_dir=$runDir`nlaunch_cwd_verified=$launchCwd`n"
[System.IO.File]::WriteAllText($timeTxt, $timing, [System.Text.UTF8Encoding]::new($false))
Write-Output "elapsed=$elapsed exit=$exit bytes_out=$($out.Length) bytes_err=$($err.Length)"
