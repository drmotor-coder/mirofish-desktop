#!/usr/bin/env python3
"""
MiroFish MCP Server — даёт агентам (Claude, Краб) доступ к MiroFish.

Инструменты работают против запущенного бэкенд-сервиса MiroFish (по умолчанию
http://127.0.0.1:18500). Позволяют смотреть проекты/симуляции/отчёты и
переключать LLM-модель.

Запуск: python -m mcp_server.main   (или python mcp_server/main.py)
Регистрация в Claude Desktop / claude mcp — см. README ниже.
"""
import json
import os
import urllib.request
import urllib.error

from mcp.server.fastmcp import FastMCP

BACKEND = os.environ.get("MIROFISH_BACKEND", "http://127.0.0.1:18500")
OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")

mcp = FastMCP("mirofish")


def _get(url: str):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


def _post(url: str, payload: dict):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


@mcp.tool()
def health() -> dict:
    """Проверить, что бэкенд MiroFish доступен."""
    return _get(f"{BACKEND}/health")


@mcp.tool()
def list_ollama_models() -> dict:
    """Список доступных локальных LLM-моделей (Ollama)."""
    data = _get(f"{OLLAMA}/api/tags")
    if "models" in data:
        return {"models": [m.get("name") for m in data["models"]]}
    return data


@mcp.tool()
def get_active_model() -> dict:
    """Узнать, на какой LLM-модели сейчас считает MiroFish."""
    return _get(f"{BACKEND}/api/config/model")


@mcp.tool()
def set_active_model(model: str) -> dict:
    """Переключить LLM-модель MiroFish (например 'gemma4:31b', 'qwen3.6:35b')."""
    return _post(f"{BACKEND}/api/config/model", {"model": model})


@mcp.tool()
def list_projects() -> dict:
    """Список проектов (графов), созданных в MiroFish."""
    return _get(f"{BACKEND}/api/graph/project/list")


@mcp.tool()
def list_simulations() -> dict:
    """Список симуляций в MiroFish."""
    return _get(f"{BACKEND}/api/simulation/list")


@mcp.tool()
def list_reports() -> dict:
    """Список готовых отчётов по симуляциям."""
    return _get(f"{BACKEND}/api/report/list")


@mcp.tool()
def get_report(report_id: str) -> dict:
    """Получить содержимое отчёта по его ID (результаты исследования)."""
    return _get(f"{BACKEND}/api/report/{report_id}")


if __name__ == "__main__":
    mcp.run()
