#!/usr/bin/env python3
"""
MiroFish MCP Server
Позволяет агентам (Claude, Краб, OpenClaw) использовать MiroFish для проведения исследований

Использование:
  python mirofish_mcp_server.py

Интеграция:
  Добавь в claude_desktop_config.json:
  {
    "mcpServers": {
      "mirofish": {
        "command": "python",
        "args": ["D:\\FACTORY\\MiroFish\\mcp_server\\main.py"]
      }
    }
  }
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
MIROFISH_BACKEND_URL = "http://localhost:5000"
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:35b"


class MiroFishMCPServer:
    """MCP сервер для использования MiroFish в агентах"""

    def __init__(self):
        self.backend_url = MIROFISH_BACKEND_URL
        self.ollama_url = OLLAMA_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.tools = {
            "get_available_models": self._get_available_models,
            "create_simulation": self._create_simulation,
            "run_simulation": self._run_simulation,
            "get_simulation_results": self._get_simulation_results,
            "list_simulations": self._list_simulations,
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _get_available_models(self) -> Dict[str, Any]:
        """Получить список доступных LLM моделей из Ollama"""
        try:
            async with self.session.get(f"{self.ollama_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    return {
                        "status": "success",
                        "count": len(models),
                        "models": [
                            {
                                "name": m.get("name"),
                                "size": m.get("size"),
                                "modified_at": m.get("modified_at"),
                            }
                            for m in models
                        ],
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Ollama returned {response.status}",
                    }
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return {"status": "error", "message": str(e)}

    async def _create_simulation(
        self,
        graph: Dict[str, Any],
        name: str,
        description: str = "",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Создать новую симуляцию в MiroFish"""
        try:
            model = model or DEFAULT_MODEL

            payload = {
                "graph": graph,
                "name": name,
                "description": description,
                "model": model,
                "created_at": datetime.now().isoformat(),
            }

            async with self.session.post(
                f"{self.backend_url}/api/simulation/create", json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        "simulation_id": data.get("simulation_id"),
                        "project_id": data.get("project_id"),
                        "message": "Simulation created successfully",
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "message": f"Failed to create simulation: {error_text}",
                    }
        except Exception as e:
            logger.error(f"Error creating simulation: {e}")
            return {"status": "error", "message": str(e)}

    async def _run_simulation(
        self,
        simulation_id: str,
        simulation_prompt: str,
        time_horizon: int = 90,
        steps: int = 30,
    ) -> Dict[str, Any]:
        """Запустить симуляцию"""
        try:
            payload = {
                "simulation_id": simulation_id,
                "simulation_prompt": simulation_prompt,
                "time_horizon": time_horizon,
                "simulation_steps": steps,
            }

            async with self.session.post(
                f"{self.backend_url}/api/simulation/prepare", json=payload
            ) as response:
                if response.status in [200, 202]:
                    data = await response.json()
                    return {
                        "status": "success",
                        "message": "Simulation started",
                        "task_id": data.get("task_id"),
                        "status_url": f"{self.backend_url}/api/simulation/{simulation_id}/status",
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "message": f"Failed to run simulation: {error_text}",
                    }
        except Exception as e:
            logger.error(f"Error running simulation: {e}")
            return {"status": "error", "message": str(e)}

    async def _get_simulation_results(
        self, simulation_id: str
    ) -> Dict[str, Any]:
        """Получить результаты симуляции"""
        try:
            async with self.session.get(
                f"{self.backend_url}/api/simulation/{simulation_id}/results"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        "results": data,
                    }
                elif response.status == 202:
                    return {
                        "status": "in_progress",
                        "message": "Simulation is still running",
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Simulation not found or failed",
                    }
        except Exception as e:
            logger.error(f"Error getting results: {e}")
            return {"status": "error", "message": str(e)}

    async def _list_simulations(self) -> Dict[str, Any]:
        """Получить список всех симуляций"""
        try:
            async with self.session.get(
                f"{self.backend_url}/api/simulation/list"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        "simulations": data.get("simulations", []),
                        "count": len(data.get("simulations", [])),
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to list simulations",
                    }
        except Exception as e:
            logger.error(f"Error listing simulations: {e}")
            return {"status": "error", "message": str(e)}


async def main():
    """Запуск MCP сервера"""
    logger.info("🚀 MiroFish MCP Server starting...")
    logger.info(f"Backend URL: {MIROFISH_BACKEND_URL}")
    logger.info(f"Ollama URL: {OLLAMA_URL}")

    async with MiroFishMCPServer() as server:
        # Проверка доступности сервисов
        try:
            models = await server._get_available_models()
            if models.get("status") == "success":
                logger.info(f"✅ Ollama available ({models.get('count')} models)")
            else:
                logger.warning("⚠️ Ollama not available")
        except Exception as e:
            logger.warning(f"⚠️ Cannot connect to Ollama: {e}")

        logger.info("✅ MiroFish MCP Server ready")
        logger.info("Available tools:")
        for tool_name in server.tools.keys():
            logger.info(f"  - {tool_name}")

        # Для MCP протокола нужна основной loop
        # Здесь можно добавить STDIO обработчик для MCP
        try:
            # Keep server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
