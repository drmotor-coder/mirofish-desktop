#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MiroFish Electron Application Installer

.DESCRIPTION
    Автоматический установщик MiroFish desktop приложения

.EXAMPLE
    .\INSTALL.ps1
#>

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          MiroFish Electron Application Installer          ║" -ForegroundColor Cyan
Write-Host "║                    Version 0.1.0 (Electron)               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Проверка .exe файла
$exePath = Join-Path $PSScriptRoot "build\MiroFish-0.1.0.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "❌ Ошибка: MiroFish-0.1.0.exe не найден!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Необходимо сначала собрать приложение:" -ForegroundColor Yellow
    Write-Host "   1. Запусти: .\build-app.ps1" -ForegroundColor Gray
    Write-Host "   2. Дождись завершения (~30 минут)" -ForegroundColor Gray
    Write-Host "   3. Потом запусти: .\INSTALL.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Инсталлятор найден: $exePath" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Требования:" -ForegroundColor Yellow
Write-Host "   ✓ Windows 10/11" -ForegroundColor Gray
Write-Host "   ✓ Ollama запущена (ollama serve)" -ForegroundColor Gray
Write-Host "   ✓ ~350MB свободного места на диске" -ForegroundColor Gray
Write-Host ""

# Проверка Ollama
Write-Host "🔍 Проверяю Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction Stop -TimeoutSec 2
    Write-Host "✅ Ollama доступна на localhost:11434" -ForegroundColor Green
    $ollamaOk = $true
} catch {
    Write-Host "⚠️  Ollama НЕ запущена на localhost:11434" -ForegroundColor Yellow
    Write-Host "   Нужно запустить в отдельном терминале:" -ForegroundColor Gray
    Write-Host "   > ollama serve" -ForegroundColor Gray
    $ollamaOk = $false
}

Write-Host ""
Write-Host "🚀 Запускаю инсталлятор..." -ForegroundColor Cyan
Write-Host ""

# Запуск инсталлятора
& $exePath

Write-Host ""
Write-Host "✅ Установка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Ярлык приложения:" -ForegroundColor Cyan
Write-Host "   Desktop/MiroFish.lnk" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Запуск:" -ForegroundColor Cyan
Write-Host "   Кликни ярлык на рабочем столе или найди в Пуск меню" -ForegroundColor Gray
Write-Host ""
Write-Host "⚙️  Первый запуск:" -ForegroundColor Cyan
Write-Host "   1. Приложение стартует" -ForegroundColor Gray
Write-Host "   2. Нажми кнопку ⚙️ внизу справа" -ForegroundColor Gray
Write-Host "   3. Выбери модель LLM из списка (qwen3.5:35b)" -ForegroundColor Gray
Write-Host "   4. Начини использовать приложение!" -ForegroundColor Gray
Write-Host ""

if (-not $ollamaOk) {
    Write-Host "⚠️  Помни: Ollama должна работать при каждом запуске MiroFish" -ForegroundColor Yellow
    Write-Host "   Запусти: ollama serve" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📚 Документация:" -ForegroundColor Cyan
Write-Host "   - QUICK_START_ELECTRON.md" -ForegroundColor Gray
Write-Host "   - ELECTRON_SETUP.md" -ForegroundColor Gray
Write-Host "   - vault/MIROFISH_COMPLETE_SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Готово! Наслаждайся MiroFish!" -ForegroundColor Green
