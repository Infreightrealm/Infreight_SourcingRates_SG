@echo off
title Infreight Maersk worker
cd /d "%~dp0"
rem Run this PC as the Maersk worker: the cloud server hands Maersk searches to it
rem through the shared database (DATABASE_URL in backend\.env). No tunnel needed.
rem Restarts and pulls the latest code from GitHub on every restart (run_live_loop.bat).
set WORKER_CARRIERS=MAERSK
call run_live_loop.bat
