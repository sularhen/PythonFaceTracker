$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
    Write-Host "[FaceTrail] Creating local virtual environment..."
    python -m venv "$Root\.venv"
}

Write-Host "[FaceTrail] Ensuring dependencies are installed..."
& "$Root\.venv\Scripts\python.exe" -m pip install -e "$Root"

Write-Host "[FaceTrail] Launching GUI..."
& "$Root\.venv\Scripts\facetrail.exe" @args
