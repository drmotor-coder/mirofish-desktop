"""
Рантайм-настройки, изменяемые из интерфейса (без перезапуска и пересборки).
Хранятся в JSON на томе uploads, поэтому переживают перезапуск контейнера
и видны подпроцессам симуляции (они перечитывают файл).

Поддерживает выбор вычислительного режима (какая карта/движок считает):
  - v100     : всё на Ollama (V100)
  - lmstudio : всё на LM Studio (4070)
  - both     : тяжёлое (подготовка, анализ, отчёты) на Ollama/V100,
               лёгкое (посты симуляции) на LM Studio/4070
"""
import json
import os
from pathlib import Path

_OVERRIDE_FILE = Path(__file__).resolve().parent.parent / "uploads" / "runtime_config.json"

# Фиксированные эндпоинты движков (из контейнера)
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1")
LMSTUDIO_BASE = os.environ.get("LMSTUDIO_BASE_URL", "http://host.docker.internal:1234/v1")

DEFAULT_MODE = "v100"
DEFAULT_OLLAMA_MODEL = "qwen2.5:14b-instruct"


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


# --- Модель Ollama (обратная совместимость) ---
def get_model() -> str | None:
    model = _read().get("model")
    return model.strip() if isinstance(model, str) and model.strip() else None


def set_model(model: str) -> None:
    data = _read()
    data["model"] = model
    _write(data)


# --- Вычислительный режим ---
def get_mode() -> str:
    mode = _read().get("compute_mode")
    return mode if mode in ("v100", "lmstudio", "both") else DEFAULT_MODE


def set_mode(mode: str) -> None:
    if mode not in ("v100", "lmstudio", "both"):
        raise ValueError("mode must be v100 | lmstudio | both")
    data = _read()
    data["compute_mode"] = mode
    _write(data)


def get_lmstudio_model() -> str:
    # LM Studio обычно игнорирует имя и использует загруженную модель,
    # но передаём сохранённое/дефолтное для совместимости с OpenAI API
    return _read().get("lmstudio_model") or "local-model"


def set_lmstudio_model(model: str) -> None:
    data = _read()
    data["lmstudio_model"] = model
    _write(data)


def resolve_ollama_endpoint() -> dict:
    """Всегда возвращает Ollama/V100, независимо от выбранного режима.
    Используется как надёжный fallback (например, если модель на LM Studio
    'уплыла' в другой язык и нужно перегенерировать текст)."""
    return {"base_url": OLLAMA_BASE, "api_key": "ollama", "model": get_model() or DEFAULT_OLLAMA_MODEL, "engine": "ollama"}


def resolve_endpoint(task: str = "heavy") -> dict:
    """
    Возвращает {base_url, api_key, model} для задачи.
    task: 'heavy' (подготовка/анализ/отчёты) или 'light' (посты симуляции).

    Режим 'both' означает "использовать максимум мощности": и подготовка,
    и сама симуляция считаются на мощной V100. 4070/LM Studio при этом —
    надёжный резерв (используется только через force_ollama-подобный
    механизм для восстановления при сбоях, а не как основной движок).
    """
    mode = get_mode()
    ollama_model = get_model() or DEFAULT_OLLAMA_MODEL
    lm_model = get_lmstudio_model()

    ollama = {"base_url": OLLAMA_BASE, "api_key": "ollama", "model": ollama_model, "engine": "ollama"}
    lmstudio = {"base_url": LMSTUDIO_BASE, "api_key": "lm-studio", "model": lm_model, "engine": "lmstudio"}

    if mode == "lmstudio":
        return lmstudio
    if mode == "both":
        return ollama  # обе фазы — на V100, максимум мощности
    # v100 (по умолчанию)
    return ollama
