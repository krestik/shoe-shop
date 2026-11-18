param([string]$Python = (Join-Path $PSScriptRoot '.venv\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Create .venv with Python 3.10 and install requirements-build.lock.txt first.' }
$taskOldPath = $env:PATH
$taskOldLocation = Get-Location
try {
    $taskBasePython = & $Python -c 'import sys; print(sys.base_prefix)'
    if ($LASTEXITCODE -ne 0) { throw 'Cannot identify Python base directory.' }
    # Foreign Poppler/ICU DLLs on PATH must not replace the Windows ICU used by Qt.
    $env:PATH = @((Split-Path -Parent $Python), $taskBasePython, (Join-Path $env:WINDIR 'System32'), $env:WINDIR) -join ';'
    Set-Location -LiteralPath $PSScriptRoot
    & $Python -m PyInstaller --noconfirm --clean ShoeStore.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed. Read the console log.' }
} finally {
    $env:PATH = $taskOldPath
    Set-Location -LiteralPath $taskOldLocation.Path
}
