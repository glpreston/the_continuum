@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ----------------------------------------
REM Optional port argument (default 2000)
REM ----------------------------------------
SET PORT=2000
IF NOT "%~1"=="" SET PORT=%~1

echo Starting The Continuum on port %PORT%

REM ----------------------------------------
REM Activate virtual environment
REM ----------------------------------------
IF EXIST ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) ELSE (
    echo ERROR: .venv not found. Please create it first.
    pause
    exit /b 1 )

REM ----------------------------------------
REM Start UVicorn in a new window
REM ----------------------------------------
echo Launching UVicorn backend...
start "Continuum Backend" cmd /k "cd /d E:\the_continuum && python -m uvicorn continuum.app:app"

REM ----------------------------------------
REM Start Streamlit in this window
REM ----------------------------------------
echo Launching Streamlit UI...
python -m streamlit run "E:\the_continuum\continuum\ui\streamlit_app.py" --server.port %PORT%

echo Streamlit exited. Press any key to close this window.
pause >nul
ENDLOCAL