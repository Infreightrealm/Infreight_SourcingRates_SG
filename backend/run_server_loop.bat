@echo off
:: This script runs the backend server in a separate window and automatically checks for updates from GitHub when the server window is closed.
:loop
cls
echo ====================================================
echo [AUTO-UPDATE] Checking for latest code from GitHub...
echo ====================================================
git pull origin main

echo ====================================================
echo [SERVER] Starting Infreight Backend in a new window...
echo Close the new server window to trigger an auto-update/restart!
echo ====================================================
start /wait "Infreight Backend" ..\.venv\Scripts\python run_server.py

echo ====================================================
echo [SERVER] Server window closed. Restarting in 5 seconds...
echo Close this window to stop the loop completely.
echo ====================================================
timeout /t 5
goto loop
