@echo off
cd /d "%~dp0"
python "desktop\Tangliengim Website Editor.py"
if errorlevel 1 (
  echo.
  echo The editor could not start. Make sure Python is installed and available as "python".
  pause
)
