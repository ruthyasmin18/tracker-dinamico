@echo off
REM ============================================================
REM   Tracker Dinamico - Arranque automatico
REM   Doble click para levantar backend + frontend
REM ============================================================

setlocal
cd /d "%~dp0"
title Tracker Dinamico - Launcher

echo.
echo ========================================
echo   Tracker Dinamico - Iniciando...
echo ========================================
echo.

REM ---------- Verificar requisitos ----------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Descargalo desde https://www.python.org/downloads/
    pause
    exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado o no esta en el PATH.
    echo Descargalo desde https://nodejs.org/
    pause
    exit /b 1
)

REM ---------- Setup backend si hace falta ----------
if not exist "backend\.venv\Scripts\python.exe" (
    echo [Backend] Creando entorno virtual...
    pushd backend
    python -m venv .venv
    if errorlevel 1 ( echo [ERROR] No se pudo crear el entorno virtual. & popd & pause & exit /b 1 )
    echo [Backend] Instalando dependencias Python...
    call .venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 ( echo [ERROR] Fallo la instalacion de dependencias Python. & popd & pause & exit /b 1 )
    popd
    echo [Backend] Setup completo.
    echo.
)

REM ---------- Setup frontend si hace falta ----------
if not exist "frontend\node_modules" (
    echo [Frontend] Instalando dependencias Node...
    pushd frontend
    call npm install
    if errorlevel 1 ( echo [ERROR] Fallo la instalacion de dependencias Node. & popd & pause & exit /b 1 )
    popd
    echo [Frontend] Setup completo.
    echo.
)

REM ---------- Arrancar backend en nueva ventana ----------
echo [Backend]  Iniciando en http://127.0.0.1:8000 ...
start "Tracker - Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

REM Esperar a que el backend arranque
timeout /t 4 /nobreak >nul

REM ---------- Arrancar frontend en nueva ventana ----------
echo [Frontend] Iniciando en http://localhost:5173 ...
start "Tracker - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM Esperar y abrir navegador
timeout /t 6 /nobreak >nul
start "" http://localhost:5173

echo.
echo ========================================
echo   Listo!
echo ========================================
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://127.0.0.1:8000
echo   API docs:  http://127.0.0.1:8000/docs
echo.
echo Para detener: cierra las ventanas "Tracker - Backend"
echo y "Tracker - Frontend" o ejecuta stop.bat.
echo.
echo Puedes cerrar esta ventana cuando quieras.
pause
