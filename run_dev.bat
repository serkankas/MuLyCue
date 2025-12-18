@echo off
REM Development server launcher for MuLyCue (Windows)

echo Starting MuLyCue Development Server...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo Starting FastAPI server...
echo Access the app at: http://localhost:8000
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

