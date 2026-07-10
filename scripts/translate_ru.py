#!/usr/bin/env python3
"""
Перевод locales/en.json -> locales/ru.json через локальную модель Ollama.
Ключи и плейсхолдеры ({count}, {name} и т.п.) сохраняются, переводятся только значения.
Перевод идёт по верхним разделам, с проверкой структуры и откатом на английский при сбое.
"""
import json
import sys
import urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:14b-instruct"

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "locales" / "en.json"
RU = ROOT / "locales" / "ru.json"

SYS_PROMPT = (
    "Ты профессиональный переводчик интерфейсов. Тебе дают JSON-объект с английскими "
    "строками интерфейса. Переведи ЗНАЧЕНИЯ на естественный русский язык. "
    "СТРОГИЕ ПРАВИЛА:\n"
    "1. НЕ меняй ключи (имена полей) — только значения-строки.\n"
    "2. Сохраняй ВСЕ плейсхолдеры вида {name}, {count}, {id}, %s, {0} без изменений.\n"
    "3. Сохраняй структуру вложенности точь-в-точь.\n"
    "4. Технические токены, названия API-путей (/api/...), коды — не переводи.\n"
    "5. Верни ТОЛЬКО валидный JSON той же структуры, без пояснений."
)


def ollama_translate(obj: dict) -> dict:
    payload = {
        "model": MODEL,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.2},
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": json.dumps(obj, ensure_ascii=False)},
        ],
    }
    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return json.loads(data["message"]["content"])


def same_shape(a, b) -> bool:
    """Проверяет, что структура ключей совпадает."""
    if isinstance(a, dict):
        if not isinstance(b, dict) or set(a.keys()) != set(b.keys()):
            return False
        return all(same_shape(a[k], b[k]) for k in a)
    if isinstance(a, str):
        return isinstance(b, str)
    return True


def merge_fallback(en, ru):
    """Где перевод сломался/отсутствует — берём английский, чтобы не было пустот."""
    if isinstance(en, dict):
        out = {}
        for k, v in en.items():
            if isinstance(ru, dict) and k in ru:
                out[k] = merge_fallback(v, ru[k])
            else:
                out[k] = v
        return out
    if isinstance(en, str):
        return ru if isinstance(ru, str) and ru.strip() else en
    return en


def main():
    en = json.loads(EN.read_text(encoding="utf-8"))
    result = {}
    for section, content in en.items():
        sys.stdout.write(f"  переводим раздел '{section}' ... ")
        sys.stdout.flush()
        try:
            translated = ollama_translate({section: content})
            # модель может вернуть либо {section: {...}}, либо сразу {...}
            inner = translated.get(section, translated)
            if same_shape(content, inner):
                result[section] = inner
                print("ок")
            else:
                result[section] = merge_fallback(content, inner)
                print("структура частично разошлась — слили с англ.")
        except Exception as e:
            result[section] = content
            print(f"ошибка ({e}) — оставили англ.")

    RU.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    # финальная проверка валидности
    json.loads(RU.read_text(encoding="utf-8"))
    print(f"\nГотово: {RU}")


if __name__ == "__main__":
    main()
