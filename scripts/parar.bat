@echo off
chcp 65001 >nul
title Senhora Vera - Encerrando Serviços

echo ======================================================
echo          Encerrando o Ambiente da Senhora Vera
echo ======================================================
echo.

echo Encerrando Uvicorn/Backend (porta 8010)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8010 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Encerrando Frontend Next.js (porta 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Encerrando Ollama (porta 11434)...
taskkill /F /IM "ollama.exe" >nul 2>&1
taskkill /F /IM "ollama_llama_server.exe" >nul 2>&1

echo.
echo ✓ Todos os processos da Senhora Vera e do Ollama foram encerrados!
echo.
pause
