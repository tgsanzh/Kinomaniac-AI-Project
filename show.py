import json
from collections import Counter, defaultdict
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "calls.jsonl"


def main():
    if not LOG_FILE.exists():
        print("Журнал calls.jsonl пока пуст или не создан.")
        return

    rows = []
    with open(LOG_FILE, encoding="utf-8") as file:
        for line in file:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print("Пропускаю повреждённую строку журнала.")

    outcomes = Counter(row.get("outcome", "unknown") for row in rows)
    by_model = defaultdict(lambda: {"input": 0, "output": 0, "usd": 0.0, "priced": 0})
    total_seconds = 0.0

    for row in rows:
        model = row.get("model", "unknown")
        usage = row.get("usage") or {}
        by_model[model]["input"] += usage.get("prompt_tokens", 0)
        by_model[model]["output"] += usage.get("completion_tokens", 0)
        total_seconds += row.get("seconds", 0)
        if isinstance(row.get("usd"), (int, float)):
            by_model[model]["usd"] += row["usd"]
            by_model[model]["priced"] += 1

    print(f"Всего вызовов: {len(rows)}")
    print("Исходы:")
    for outcome, count in sorted(outcomes.items()):
        print(f"  {outcome}: {count}")

    print("\nТокены и цена:")
    for model, data in by_model.items():
        print(f"  {model}")
        print(f"    входные токены: {data['input']}")
        print(f"    выходные токены: {data['output']}")
        if data["priced"]:
            print(f"    цена: ${data['usd']:.6f}")
        else:
            print("    цена: не задан тариф для этой модели")

    rejected = sum(len(row.get("rejected", [])) for row in rows)
    print(f"\nЧужих ID отклонено: {rejected}")
    print(f"Суммарное время запросов: {total_seconds:.1f} сек.")


if __name__ == "__main__":
    main()
