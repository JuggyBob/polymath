$ErrorActionPreference = 'Stop'
$fixture = '<REPO>\repair\v6'
$runDir  = Join-Path $fixture 'run-qwen36-v6'
$outTxt  = Join-Path $fixture 'run-qwen36-v6-hermes-output.txt'
$errTxt  = Join-Path $fixture 'run-qwen36-v6-stderr.txt'
$timeTxt = Join-Path $fixture 'run-qwen36-v6-timing.txt'
$hermes  = '<USERPROFILE>\AppData\Local\hermes\bin\hermes.exe'
$prompt = @'
Fix the bugs in this repository according to README.md and the programs in examples/ (each has a .expected file). You may compile and run tests locally, e.g. python tests/test_visible.py. Keep fixes small and local. Do not modify anything under tests/, include/ or the examples/. The visible tests and examples are the only specification.
'@

if (Test-Path $runDir) { Remove-Item $runDir -Recurse -Force }
Copy-Item (Join-Path $fixture 'task') $runDir -Recurse -Force

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
$timing = "start=$($start.ToString('o'))`nend=$($end.ToString('o'))`nelapsed_seconds=$elapsed`nexit_code=$exit`ncapped=$capped`nhermes_pid=$($proc.Id)`nrun_dir=$runDir`n"
[System.IO.File]::WriteAllText($timeTxt, $timing, [System.Text.UTF8Encoding]::new($false))
Write-Output "elapsed=$elapsed exit=$exit bytes_out=$($out.Length) bytes_err=$($err.Length)"
