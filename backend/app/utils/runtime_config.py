"""
Рантайм-настройки, изменяемые из интерфейса (без перезапуска и пересборки).
Хранятся в JSON на томе uploads, поэтому переживают перезапуск контейнера
и видны подпроцессам симуляции (они перечитывают файл при создании LLMClient).
"""
import json
from pathlib import Path

# uploads смонтирован как том -> значение сохраняется между перезапусками
_OVERRIDE_FILE = Path(__file__).resolve().parent.parent / "uploads" / "runtime_config.json"


def _read() -> dict:
    try:
        if _OVERRIDE_FILE.exists():
            return json.loads(_OVERRIDE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write(data: dict) -> None:
    _OVERRIDE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _OVERRIDE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_model() -> str | None:
    """Выбранная в интерфейсе модель (или None, если не задана)."""
    model = _read().get("model")
    return model.strip() if isinstance(model, str) and model.strip() else None


def set_model(model: str) -> None:
    data = _read()
    data["model"] = model
    _write(data)
