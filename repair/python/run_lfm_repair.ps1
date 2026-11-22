$ErrorActionPreference = 'Stop'
$src = '<REPO>\repair\template'
$dst = '<REPO>\repair\lfm'
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse -Force

$hermes = '<USERPROFILE>\AppData\Local\hermes\bin\hermes.exe'
$prompt = @'
Fix the failing tests in this repository according to AGENTS.md. Do not modify anything under tests/. Keep the fixes small and local, standard library only. Run `python -m unittest discover -s tests -v` to verify before you finish.
'@
$start = Get-Date
Push-Location $dst
try {
    & $hermes -m lfm -z $prompt --yolo --reasoning none 2>&1 |
        Out-File '<REPO>\closed-qa\lfm25-baseline\lfm25-hermes-repair-output.txt' -Encoding utf8
} finally {
    Pop-Location
}
$elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
Write-Output "elapsed=$elapsed s"

Push-Location '<REPO>\repair'
try {
    & '<STRATA>\.venv\Scripts\python.exe' score.py $dst hidden 2>&1 |
        Out-File '<REPO>\closed-qa\lfm25-baseline\lfm25-hermes-repair-score.json' -Encoding utf8
} finally {
    Pop-Location
}
Get-Content '<REPO>\closed-qa\lfm25-baseline\lfm25-hermes-repair-score.json' -Tail 40
