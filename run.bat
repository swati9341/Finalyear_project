@echo off
echo Starting Frontend and Backend...
echo.

REM Start Backend in a new window
echo Starting Backend on http://127.0.0.1:8000
start cmd /k "cd Backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start Frontend in a new window
echo Starting Frontend on http://localhost:8501
start cmd /k "cd Frontend && streamlit run frontend.py"

echo.
echo Both frontend and backend are starting...
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
