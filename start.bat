@echo off
title PMI Launcher
color 0A

echo ============================================
echo   Predictive Manufacturing Intelligence
echo   Starting Development Servers...
echo ============================================
echo.

echo [1/2] Starting Backend (FastAPI - Port 8000)...
start "PMI Backend" cmd /k "cd /d "c:\Intership\Predictive Manufacturing Intelligence" && uvicorn api:app --reload --port 8000 --host 0.0.0.0"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend (Vite - Port 3000)...
start "PMI Frontend" cmd /k "cd /d "c:\Intership\Predictive Manufacturing Intelligence\frontend" && npm run dev -- --port 3000 --host 0.0.0.0"

echo.
echo ============================================
echo   Both servers are starting!
echo   Backend  : http://localhost:8000
echo   Frontend : http://localhost:3000
echo ============================================
echo.
pause
