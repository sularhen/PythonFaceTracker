param(
    [string]$InputPath = ".\media",
    [string]$OutputPath = ".\output"
)

Write-Host "1. Creating virtual environment"
python -m venv .venv

Write-Host "2. Activating virtual environment"
. .\.venv\Scripts\Activate.ps1

Write-Host "3. Installing FaceTrail in editable mode"
python -m pip install -e .

Write-Host "4. Running terminal scan"
facetrail scan $InputPath --output $OutputPath --engine auto --save-redacted --open-report

Write-Host "5. Launching desktop GUI"
facetrail
