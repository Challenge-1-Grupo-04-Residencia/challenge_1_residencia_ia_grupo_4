@echo off
chcp 65001 >nul
title Senhora Vera - Launcher (Windows)

:: Garante que o script roda a partir da raiz do repositório
cd /d "%~dp0\.."

echo ======================================================
echo          Iniciando o Ambiente da Senhora Vera
echo ======================================================
echo.

set "PATH=%USERPROFILE%\.local\bin;%LOCALAPPDATA%\Programs\Ollama;C:\Program Files\nodejs;%PATH%"
set "OLLAMA_TIMEOUT=120"

set /p "OLLAMA_CHOICE=Deseja iniciar o Ollama [Llama 3]? [S/N] (padrao S): "
if not defined OLLAMA_CHOICE set "OLLAMA_CHOICE=S"

if /i "%OLLAMA_CHOICE%"=="S" goto :start_ollama
goto :skip_ollama

:start_ollama
echo [1/3] Iniciando o Ollama (Llama 3)...
start "Vera - Ollama (Llama 3)" cmd /k "title Vera - Ollama && ollama serve"
goto :start_services

:skip_ollama
echo [1/3] Pulando o Ollama. A camada N4 saira indisponivel (comportamento normal).
goto :start_services

:start_services
echo.
echo [2/3] Iniciando o Backend FastAPI na porta 8010...
start "Vera - Backend (FastAPI)" cmd /k "title Vera - Backend && cd /d "%~dp0\.." && set PATH=%USERPROFILE%\.local\bin;%PATH% && set OLLAMA_TIMEOUT=120 && uv run uvicorn src.main:app --app-dir backend --reload --port 8010"

echo.
echo [3/3] Iniciando o Frontend Next.js na porta 3000...
start "Vera - Frontend (Next.js)" cmd /k "title Vera - Frontend && cd /d "%~dp0\..\frontend" && set PATH=C:\Program Files\nodejs;%PATH% && npm run dev"

echo.
echo ======================================================
echo Tudo pronto! As janelas foram abertas separadamente:
echo  - Frontend: http://localhost:3000
echo  - Backend:  http://localhost:8010/docs
echo  - Ollama:   http://localhost:11434
echo.
echo Para fechar tudo, feche as janelas abertas ou execute scripts\parar.bat.
echo ======================================================
echo.
pause
