@echo off
REM Detiene los servidores del Tracker Dinamico
echo Deteniendo Tracker Dinamico...

REM Mata cualquier proceso de uvicorn (backend) y vite (frontend)
taskkill /F /FI "WINDOWTITLE eq Tracker - Backend*" >nul 2>nul
taskkill /F /FI "WINDOWTITLE eq Tracker - Frontend*" >nul 2>nul

REM Tambien por puerto, por si acaso
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>nul

echo Servicios detenidos.
timeout /t 2 /nobreak >nul
