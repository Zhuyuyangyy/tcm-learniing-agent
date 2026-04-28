@echo off
chcp 65001 >nul
title TCM Mind-RAG v2.2 - 中医智能诊疗系统

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   TCM Mind-RAG v2.2 启动脚本            ║
echo  ║   中医智能诊疗系统 · 互联网+大赛参赛作品  ║
echo  ╚══════════════════════════════════════════╝
echo.

:: 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 https://nodejs.org/
    pause
    exit /b 1
)

:: 启动后端（后台）
echo [1/2] 启动后端服务 (端口 8000) ...
cd /d "%~dp0"
start "TCM-Backend" cmd /c "cd .. && .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端服务 (端口 5173) ...
npm run dev

echo.
echo 系统已启动！
echo   前端：http://localhost:5173
echo   后端：http://localhost:8000
echo   API文档：http://localhost:8000/docs
echo.
pause
