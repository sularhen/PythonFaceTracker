@echo off
setlocal
for %%I in ("%~dp0.") do set "ROOT=%%~fI"

if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo [FaceTrail] Creating local virtual environment...
  python -m venv "%ROOT%\.venv"
)

echo [FaceTrail] Ensuring dependencies are installed...
"%ROOT%\.venv\Scripts\python.exe" -m pip install -e "%ROOT%"

echo [FaceTrail] Launching GUI...
"%ROOT%\.venv\Scripts\facetrail.exe" %*
