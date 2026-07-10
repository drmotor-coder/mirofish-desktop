# MiroFish Electron App Setup

## Требования

- **Node.js**: >=18.0.0
- **Python**: 3.11 - 3.12 (для backend)
- **Ollama**: Локально на localhost:11434 (для LLM моделей)
- **V100 GPU**: Для ускорения LLM (опционально, но рекомендуется)
- **Дисковое пространство**: ~5GB на D:\ диск

## Установка шаг за шагом

### 1. Подготовка системы

```powershell
# Убедись что Node.js установлен
node --version
npm --version

# Убедись что Python установлен
python --version

# Убедись что Ollama запущена
curl http://localhost:11434/api/tags
```

### 2. Клонирование и установка зависимостей

```powershell
cd D:\FACTORY\MiroFish

# Установи все зависимости
npm run setup:all

# Или отдельно:
npm install
cd frontend && npm install
cd ../backend && uv sync
cd ..
```

### 3. Разработка (Development Mode)

```powershell
# Запусти в режиме разработки с hot reload
npm run electron-dev

# Это запустит:
# - Backend на http://localhost:5000 (Flask)
# - Frontend на http://localhost:5173 (Vite)
# - Electron окно с DevTools
```

### 4. Сборка для производства

```powershell
# Собери фронтенд
npm run build

# Собери Electron приложение
npm run electron-build-win

# Результат: MiroFish-0.1.0.exe в папке build/
```

### 5. Установка приложения

```powershell
# Скопируй .exe на D:\
copy build\MiroFish-0.1.0.exe D:\MiroFish\

# Или запусти инсталлятор
.\build\MiroFish-0.1.0.exe

# Это создаст:
# - C:\Users\<USER>\AppData\Local\Programs\MiroFish\ (приложение)
# - Ярлык на рабочем столе
# - Ярлык в Пуск меню
```

## Использование

### Первый запуск

1. Запусти MiroFish из ярлыка на рабочем столе
2. Убедись что Ollama запущена (http://localhost:11434)
3. В приложении появится список доступных моделей
4. Выбери модель из списка (например, `qwen3.5:35b`)
5. Начни создавать симуляции

### Обновление приложения

Приложение автоматически проверяет обновления:

1. Если есть новая версия → появится уведомление
2. Обновление загрузится в фоне
3. При следующем перезапуске установится новая версия

**Ручная проверка:** Menu → Help → Check for Updates

### Выбор модели Ollama

Список доступных моделей:
- `qwen3.5:35b` - Рекомендуется для симуляций
- `qwen3.6:35b` - Новая версия с улучшениями
- `gemma-4-e4b` - Быстрая, легкая модель
- `mistral-small:22b` - Альтернатива
- Любая другая модель из Ollama

**Как установить новую модель:**

```powershell
# В терминале:
ollama pull qwen3.5:35b

# Или через Ollama UI
# http://localhost:11434
```

## Архитектура

```
MiroFish.exe
├─ Frontend (Vue 3 + Vite)
│  └─ Renderer Process (порт 5173 в dev)
├─ Backend (Flask + Python)
│  └─ Main Process (порт 5000)
├─ Electron Main Process
│  ├─ Auto-updater
│  ├─ IPC (взаимодействие между процессами)
│  └─ System Integration
└─ Ollama (localhost:11434)
   └─ LLM Models (V100 GPU)
```

## Проблемы и решения

### Проблема: "Ollama не найдена"

**Решение:**
```powershell
# Убедись что Ollama запущена
ollama serve

# Проверь доступность
curl http://localhost:11434/api/tags

# Если не работает, перезагрузи Ollama
```

### Проблема: "Модели не загружаются"

**Решение:**
```powershell
# Скачай модель вручную
ollama pull qwen3.5:35b

# Проверь что модель установлена
ollama list
```

### Проблема: "Backend не запускается"

**Решение:**
```powershell
# Проверь Python версию
python --version  # Должна быть 3.11 или 3.12

# Попробуй запустить backend вручную
cd backend
uv run python run.py

# Должен вывести что-то типа:
# [04:26:10] INFO: MiroFish Backend 启动中...
# [04:26:10] INFO: MiroFish Backend 启动完成
```

### Проблема: "GPU не используется"

**Решение:**
```powershell
# Проверь что Ollama использует V100
ollama show qwen3.5:35b

# Убедись что CUDA доступна
nvidia-smi

# Если нет - переинсталлируй драйверы NVIDIA
```

## Запуск на V100

MiroFish автоматически использует первый доступный GPU если он найден.

**Проверка:**
```powershell
# В Ollama логах должно быть:
# "Nvidia GPU: NVIDIA H100 SXM2 (Compute Capability 9.0)"
# или
# "Nvidia GPU: Tesla V100-PCIE-32GB (Compute Capability 7.0)"
```

## Отключение обновлений

Если не хочешь автоматических обновлений:

```powershell
# В app config (опционально):
# Отключи в electron-updater конфиге
```

## Разработка и контрибьютинг

```powershell
# Исправить баг / добавить фичу
git checkout -b feature/my-feature

# Разработка
npm run electron-dev

# Тестирование
npm run electron-build

# Коммит
git commit -am "fix: description"

# Push и PR
git push origin feature/my-feature
```

## Логи приложения

Логи сохраняются в:
```
C:\Users\<USER>\AppData\Local\MiroFish\logs\
```

## Поддержка

Если что-то не работает:

1. Проверь логи в MiroFish/logs/
2. Проверь что Ollama запущена
3. Проверь что Python 3.11-3.12 установлен
4. Создай issue на GitHub с логами

---

**Версия:** 0.1.0  
**Последнее обновление:** 2026-07-10
