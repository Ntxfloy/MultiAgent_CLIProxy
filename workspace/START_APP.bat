@echo off
chcp 65001 >nul
title 🚀 Cyberpunk AI Chat - Launcher

REM Сохраняем путь к скрипту
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ═══════════════════════════════════════════════════════════
echo    🔥 CYBERPUNK AI CHAT - STARTING UP 🔥
echo ═══════════════════════════════════════════════════════════
echo.

REM Определяем какая команда Python работает
set PYTHON_CMD=
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    echo ✅ Найден Python: py
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
        echo ✅ Найден Python: python
    ) else (
        echo ❌ Python не найден! Установите Python 3.9+
        echo    Скачать: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Проверка Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js не найден! Установите Node.js 18+
    echo    Скачать: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Найден Node.js
echo.

REM Установка зависимостей Backend
echo [1/4] 📦 Установка Backend зависимостей...
if not exist "%SCRIPT_DIR%backend\requirements.txt" (
    echo ❌ Файл backend\requirements.txt не найден!
    echo    Текущая папка: %SCRIPT_DIR%
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%backend"
echo    Устанавливаю Python пакеты...
%PYTHON_CMD% -m pip install --quiet --upgrade pip
%PYTHON_CMD% -m pip install --quiet -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ошибка установки Python зависимостей
    echo    Попробуйте вручную: %PYTHON_CMD% -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo    ✅ Backend зависимости установлены

REM Установка зависимостей Frontend
echo.
echo [2/4] 📦 Установка Frontend зависимостей...
cd /d "%SCRIPT_DIR%frontend"
if not exist "node_modules" (
    echo    Устанавливаю npm пакеты (это может занять минуту)...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка установки npm зависимостей
        pause
        exit /b 1
    )
) else (
    echo    ✅ npm пакеты уже установлены
)
echo    ✅ Frontend зависимости готовы

REM Запуск Backend в фоне
echo.
echo [3/4] 🚀 Запускаю Backend (FastAPI)...
cd /d "%SCRIPT_DIR%backend"
start "Backend - FastAPI" cmd /k "%PYTHON_CMD% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Ждем пока Backend запустится
echo    Ожидание запуска Backend (5 сек)...
timeout /t 5 /nobreak >nul

REM Запуск Frontend
echo.
echo [4/4] 🚀 Запускаю Frontend (React + Vite)...
cd /d "%SCRIPT_DIR%frontend"
start "Frontend - Vite" cmd /k "npm run dev"

REM Ждем пока Frontend запустится
echo.
echo    Ожидание запуска Frontend (3 сек)...
timeout /t 3 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════
echo    ✅ ПРИЛОЖЕНИЕ ЗАПУЩЕНО!
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 Backend:  http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo.
echo 📝 Откроется автоматически через 2 секунды...
echo.
echo ⚠️  Не закрывайте это окно!
echo    Для остановки приложения нажмите любую клавишу
echo ═══════════════════════════════════════════════════════════
echo.

REM Открываем браузер
timeout /t 2 /nobreak >nul
start http://localhost:5173

REM Держим окно открытым
cd /d "%SCRIPT_DIR%"
pause >nul

REM Убиваем процессы при выходе
echo.
echo 🛑 Останавливаю приложение...
taskkill /FI "WindowTitle eq Backend - FastAPI*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend - Vite*" /T /F >nul 2>&1

echo ✅ Приложение остановлено
timeout /t 2 /nobreak >nul
