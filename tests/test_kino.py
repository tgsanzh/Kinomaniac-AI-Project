"""Unit-тесты pick() без реального вызова API."""

import json
from types import SimpleNamespace

import kino


class FakeClient:
    """Минимальная заглушка под client.chat.completions.parse()."""

    def __init__(self, payload):
        self.payload = payload
        self.chat = SimpleNamespace(completions=self)
        self.last_arguments = None

    def parse(self, **kwargs):
        self.last_arguments = kwargs
        picks = [
            SimpleNamespace(film_id=item["film_id"], why=item["why"])
            for item in self.payload.get("picks", [])
        ]
        parsed = SimpleNamespace(
            status=self.payload["status"],
            reason=self.payload.get("reason", ""),
            picks=picks,
        )
        message = SimpleNamespace(refusal=None, parsed=parsed)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
            usage=None,
            id="stub-completion",
        )


def one_film_catalog():
    return [{
        "id": "film-1",
        "title": "Тестовый фильм",
        "year": 2020,
        "minutes": 100,
        "genres": ["драма"],
        "countries": ["Казахстан"],
        "languages": ["казахский"],
        "description": "Краткое описание из тестового каталога.",
    }]


def read_log(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_foreign_id_is_rejected_and_logged(tmp_path, monkeypatch, capsys):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setattr(kino, "LOG_FILE", log_path)
    client = FakeClient({
        "status": "ok",
        "picks": [{"film_id": "not-in-catalog", "why": "Подходит."}],
    })

    outcome, ids = kino.pick(client, "test-model", "любой фильм", one_film_catalog())

    assert outcome == "invalid"
    assert ids == []
    assert "not-in-catalog" in capsys.readouterr().out
    row = read_log(log_path)[0]
    assert row["outcome"] == "invalid"
    assert row["model"] == "test-model"
    assert row["rejected"] == ["not-in-catalog"]


def test_repeated_id_is_rejected(tmp_path, monkeypatch):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setattr(kino, "LOG_FILE", log_path)
    film = one_film_catalog()[0]
    client = FakeClient({
        "status": "ok",
        "picks": [
            {"film_id": film["id"], "why": "Первый раз."},
            {"film_id": film["id"], "why": "Второй раз."},
        ],
    })

    outcome, ids = kino.pick(client, "test-model", "драма", [film])

    assert outcome == "invalid"
    assert ids == []
    row = read_log(log_path)[0]
    assert row["outcome"] == "invalid"
    assert "Повторяющиеся" in row["invalid_reason"]


def test_no_match_returns_empty_ids(tmp_path, monkeypatch, capsys):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setattr(kino, "LOG_FILE", log_path)
    client = FakeClient({"status": "no_match", "reason": "В каталоге нет такого фильма.", "picks": []})

    outcome, ids = kino.pick(client, "test-model", "фильм про Аватар 7", one_film_catalog())

    assert outcome == "no_match"
    assert ids == []
    assert "Подходящих фильмов" in capsys.readouterr().out
    assert read_log(log_path)[0]["outcome"] == "no_match"


def test_valid_result_prints_catalog_data_inside_pick(tmp_path, monkeypatch, capsys):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setattr(kino, "LOG_FILE", log_path)
    film = one_film_catalog()[0]
    client = FakeClient({
        "status": "ok",
        "picks": [{"film_id": film["id"], "why": "Подходит по жанру."}],
    })

    outcome, ids = kino.pick(client, "test-model", "драма", [film])
    printed = capsys.readouterr().out

    assert outcome == "ok"
    assert ids == [film["id"]]
    assert film["title"] in printed
    assert str(film["year"]) in printed
    assert str(film["minutes"]) in printed
    assert film["description"] in printed
    assert read_log(log_path)[0]["outcome"] == "ok"


def test_prompt_contains_catalog_and_query_tags(tmp_path, monkeypatch):
    monkeypatch.setattr(kino, "LOG_FILE", tmp_path / "calls.jsonl")
    film = one_film_catalog()[0]
    client = FakeClient({"status": "no_match", "reason": "нет", "picks": []})

    kino.pick(client, "test-model", "покажи драму", [film])

    prompt = client.last_arguments["messages"][1]["content"]
    assert "<каталог>" in prompt and "</каталог>" in prompt
    assert "<запрос>покажи драму</запрос>" in prompt
    assert json.dumps(film["title"], ensure_ascii=False) in prompt
