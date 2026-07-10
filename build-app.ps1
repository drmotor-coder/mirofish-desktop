#!/usr/bin/env pwsh
# MiroFish Electron Build Script
# Использование: .\build-app.ps1

Write-Host "🚀 MiroFish Electron Build" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Проверка Node.js
Write-Host "📋 Проверяю Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version
if ($null -eq $nodeVersion) {
    Write-Host "❌ Node.js не найден! Скачай: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js: $nodeVersion`n" -ForegroundColor Green

# Проверка Python
Write-Host "📋 Проверяю Python..." -ForegroundColor Yellow
$pythonVersion = python --version
if ($null -eq $pythonVersion) {
    Write-Host "❌ Python не найден! Требуется Python 3.11-3.12" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion`n" -ForegroundColor Green

# Проверка Ollama
Write-Host "📋 Проверяю Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    Write-Host "✅ Ollama доступна`n" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama не запущена на localhost:11434" -ForegroundColor Yellow
    Write-Host "   Запусти: ollama serve`n" -ForegroundColor Yellow
}

# Установка зависимостей
Write-Host "📦 Установка NPM зависимостей..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при установке NPM зависимостей" -ForegroundColor Red
    exit 1
}
Write-Host "✅ NPM зависимости установлены`n" -ForegroundColor Green

# Frontend зависимости
Write-Host "📦 Установка Frontend зависимостей..." -ForegroundColor Yellow
Push-Location frontend
npm install
Pop-Location
Write-Host "✅ Frontend зависимости установлены`n" -ForegroundColor Green

# Python зависимости
Write-Host "📦 Установка Backend зависимостей..." -ForegroundColor Yellow
Push-Location backend
if (Test-Path "venv") {
    Write-Host "   Используется существующий venv" -ForegroundColor Gray
} else {
    Write-Host "   Создаю новый venv..." -ForegroundColor Gray
    python -m venv venv
}

if ($IsWindows) {
    & ".\venv\Scripts\Activate.ps1"
} else {
    & "./venv/bin/Activate.ps1"
}

pip install -r requirements.txt --quiet
Pop-Location
Write-Host "✅ Backend зависимости установлены`n" -ForegroundColor Green

# Сборка Frontend
Write-Host "🔨 Собираю Frontend..." -ForegroundColor Yellow
Push-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при сборке Frontend" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "✅ Frontend собран`n" -ForegroundColor Green

# Сборка Electron
Write-Host "🔨 Собираю Electron приложение..." -ForegroundColor Yellow
npm run electron-build-win
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при сборке Electron" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Electron приложение собрано`n" -ForegroundColor Green

# Результаты
Write-Host "🎉 Сборка завершена успешно!" -ForegroundColor Green
Write-Host "`n📍 Результат:" -ForegroundColor Cyan
Write-Host "   build/MiroFish*.exe`n" -ForegroundColor Cyan

Write-Host "📦 Установка:" -ForegroundColor Cyan
Write-Host "   1. Запусти build/MiroFish*.exe" -ForegroundColor Cyan
Write-Host "   2. Следуй инструкциям инсталлятора" -ForegroundColor Cyan
Write-Host "   3. Приложение установится на D:\ диск`n" -ForegroundColor Cyan

Write-Host "🚀 Запуск:" -ForegroundColor Cyan
Write-Host "   - Кликни ярлык на рабочем столе" -ForegroundColor Cyan
Write-Host "   - Или найди MiroFish в Пуск меню`n" -ForegroundColor Cyan

Write-Host "📚 Документация:" -ForegroundColor Cyan
Write-Host "   Читай ELECTRON_SETUP.md для подробных инструкций`n" -ForegroundColor Cyan
