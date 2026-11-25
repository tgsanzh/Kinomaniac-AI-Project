"""Проверяет, насколько модель помнит годы и длительности без каталога.

Запуск: uv run memory_probe.py
В запрос модели отправляются только ID и названия выбранных фильмов — не год,
не длительность и не остальные поля из films.json.
"""

import json
import random
from datetime import datetime
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from kino import BASE_DIR, FILMS_FILE, LIMIT, MODEL

load_dotenv(BASE_DIR / ".env", override=True)
OUTPUT = BASE_DIR / "memory_probe_result.json"


class MemoryFilm(BaseModel):
    id: str
    year: int
    minutes: int


class MemoryAnswer(BaseModel):
    items: list[MemoryFilm]


def main():
    films = json.loads(FILMS_FILE.read_text(encoding="utf-8"))
    sample = random.Random(42).sample(films, min(10, len(films)))

    # В модель отправляем только ID и названия; год и минуты в prompt отсутствуют.
    titles = [{"id": film["id"], "title": film["title"]} for film in sample]
    prompt = (
        "Для каждого фильма укажи год первого выхода и длительность в минутах. "
        "Не угадывай по другим данным; если не уверен, всё равно укажи наиболее "
        "вероятные значения. Верни каждый переданный id ровно один раз.\n"
        "Список фильмов:\n"
        + json.dumps(titles, ensure_ascii=False)
    )

    if OpenAI is None:
        print("Не установлен пакет openai. Выполни: uv sync")
        return 1

    try:
        client = OpenAI()
        completion = client.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты отвечаешь только структурированными данными."},
                {"role": "user", "content": prompt},
            ],
            response_format=MemoryAnswer,
            max_completion_tokens=LIMIT,
        )
    except openai.OpenAIError as error:
        print(f"Не удалось провести эксперимент: {error}")
        return 1

    message = completion.choices[0].message
    if message.refusal or message.parsed is None:
        print("Модель отказалась или вернула неразбираемый ответ.")
        return 1

    actual = {str(film["id"]): film for film in sample}
    predicted = {str(item.id): item for item in message.parsed.items}
    rows = []
    for film in sample:
        guess = predicted.get(str(film["id"]))
        if guess is None:
            rows.append({
                "id": film["id"], "title": film["title"],
                "catalog_year": film["year"], "catalog_minutes": film["minutes"],
                "model_year": None, "model_minutes": None,
                "year_match": False, "minutes_match": False,
            })
            continue
        rows.append({
            "id": film["id"], "title": film["title"],
            "catalog_year": film["year"], "catalog_minutes": film["minutes"],
            "model_year": guess.year, "model_minutes": guess.minutes,
            "year_match": guess.year == film["year"],
            "minutes_match": guess.minutes == film["minutes"],
        })

    extra_ids = sorted(set(predicted) - set(actual))
    year_errors = sum(not row["year_match"] for row in rows)
    minute_errors = sum(not row["minutes_match"] for row in rows)
    result = {
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model": MODEL,
        "method": "Модели отправлены только id и названия; каталоговые год и minutes не отправлялись.",
        "films": rows,
        "summary": {
            "checked": len(rows),
            "year_mismatches": year_errors,
            "minutes_mismatches": minute_errors,
            "extra_ids": extra_ids,
        },
        "usage": completion.usage.model_dump() if completion.usage else None,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Фильм | каталог | память модели")
    for row in rows:
        print(
            f"{row['title']}: {row['catalog_year']}, {row['catalog_minutes']} мин."
            f" | {row['model_year']}, {row['model_minutes']} мин."
        )
    print("\nОшибок в годах:", year_errors, "из", len(rows))
    print("Ошибок в длительности:", minute_errors, "из", len(rows))
    print("Лишние ID:", extra_ids)
    print("Подробный результат:", OUTPUT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
