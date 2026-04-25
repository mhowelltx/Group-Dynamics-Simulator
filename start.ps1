$ErrorActionPreference = "Stop"
$VenvDir = ".venv"

if (-not (Test-Path "$VenvDir\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment. Is Python installed?"
        exit 1
    }
}

& "$VenvDir\Scripts\Activate.ps1"

Write-Host "Installing / verifying dependencies..."
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed."
    exit 1
}

Write-Host ""
Write-Host "Starting Group Dynamics Simulator at http://localhost:8000"
Write-Host "Press Ctrl+C to stop."
Write-Host ""
python run.py
