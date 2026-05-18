@echo off
echo Starting Infreight Sourcing Rates Stack...

:: Start Backend in a new terminal
start "Infreight Backend" cmd /k "cd backend && ..\.venv\Scripts\python.exe run_server.py"

:: Start Frontend in a new terminal
start "Infreight Frontend" cmd /k "cd frontend && npm run dev"

echo Stack started! Keep the opened terminal windows running.
