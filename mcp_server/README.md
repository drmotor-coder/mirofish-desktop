# MiroFish MCP Server

Даёт агентам (Claude, Краб, любой MCP-клиент) доступ к MiroFish.

## Что умеет (инструменты)

| Инструмент | Что делает |
|-----------|-----------|
| `health` | Проверить, что бэкенд MiroFish жив |
| `list_ollama_models` | Список локальных моделей (Ollama) |
| `get_active_model` | Какая модель сейчас у MiroFish |
| `set_active_model` | Переключить модель (напр. `qwen3.6:35b`) |
| `list_projects` | Проекты/графы |
| `list_simulations` | Симуляции |
| `list_reports` | Готовые отчёты |
| `get_report` | Содержимое отчёта по ID (результаты исследования) |

## Требования

- Запущенный бэкенд MiroFish (Docker-контейнер `mirofish` на `127.0.0.1:18500`)
- Python с пакетом `mcp` (уже установлен на заводе)

## Подключение к Claude Code / Claude Desktop

### Вариант 1 — через CLI (безопасно, не ломает конфиг):
```powershell
claude mcp add mirofish -- python D:\FACTORY\MiroFish\mcp_server\main.py
```

### Вариант 2 — вручную в claude_desktop_config.json:
```json
{
  "mcpServers": {
    "mirofish": {
      "command": "python",
      "args": ["D:\\FACTORY\\MiroFish\\mcp_server\\main.py"]
    }
  }
}
```

## Переменные окружения (необязательно)

- `MIROFISH_BACKEND` — адрес бэкенда (по умолчанию `http://127.0.0.1:18500`)
- `OLLAMA_URL` — адрес Ollama (по умолчанию `http://localhost:11434`)

## Пример использования агентом

> «Покажи последние отчёты MiroFish и переключи модель на qwen3.6:35b»

Агент вызовет `list_reports`, затем `set_active_model("qwen3.6:35b")`.

## Что пока НЕ входит

Запуск **новой** симуляции с нуля (загрузка документов → граф → симуляция →
отчёт) — это многошаговый асинхронный процесс. Пока MCP даёт доступ на чтение
результатов и управление моделью. Полный запуск через MCP — следующий шаг.
