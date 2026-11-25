import json
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI

from kino import BASE_DIR, MODEL, load_films, pick

load_dotenv(override=True)
QUERIES_FILE = BASE_DIR / "queries.json"
LOG_FILE = BASE_DIR / "calls.jsonl"


def read_new_log_lines(start_line_count):
    """Читает только новые строки журнала, добавленные во время проверки."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, encoding="utf-8") as file:
        lines = file.readlines()
    return [json.loads(line) for line in lines[start_line_count:] if line.strip()]


def main():
    try:
        films = load_films()
        with open(QUERIES_FILE, encoding="utf-8") as file:
            queries = json.load(file)
        client = OpenAI()
    except (OSError, json.JSONDecodeError, ValueError, openai.OpenAIError) as error:
        print("Не удалось запустить проверку:", error)
        return

    if not isinstance(queries, list) or len(queries) != 15:
        print("В queries.json должно быть ровно 15 запросов.")
        return

    if LOG_FILE.exists():
        with open(LOG_FILE, encoding="utf-8") as file:
            start_line_count = sum(1 for _ in file)
    else:
        start_line_count = 0
    passed = 0
    counts = {"ok": 0, "no_match": 0, "invalid": 0}

    for number, item in enumerate(queries, 1):
        query = item["query"]
        expected = item.get("expect", {})
        print(f"\n{'=' * 15} Запрос {number}/15 {'=' * 15}")
        print(query)

        outcome, ids = pick(client, MODEL, query, films)
        counts[outcome] = counts.get(outcome, 0) + 1

        if expected.get("no_match"):
            ok = outcome == "no_match"
        else:
            must = set(expected.get("must", []))
            forbid = set(expected.get("forbid", []))
            ok = outcome == "ok" and bool(set(ids) & must) and not (set(ids) & forbid)

        if ok:
            passed += 1
            print("Ожидание: пройдено")
        else:
            print("Ожидание: НЕ пройдено")

    new_rows = read_new_log_lines(start_line_count)
    foreign_ids = sum(len(row.get("rejected", [])) for row in new_rows)

    print("\n========== ИТОГ ==========")
    print("ok:", counts.get("ok", 0))
    print("no_match:", counts.get("no_match", 0))
    print("invalid:", counts.get("invalid", 0))
    print("Чужих ID поймано проверкой:", foreign_ids)
    print(f"Запросов с пройденным ожиданием: {passed}/15")


if __name__ == "__main__":
    main()
