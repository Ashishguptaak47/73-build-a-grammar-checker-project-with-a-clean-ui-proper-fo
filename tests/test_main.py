import pytest
from grammar_checker.engine import GrammarEngine
from grammar_checker.models import Category
from main import app


@pytest.fixture
def engine():
    return GrammarEngine()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_repeated_words(engine):
    res = engine.analyze("This is the the best result.")
    assert any(i.category == Category.GRAMMAR and "the the" in i.matched_text for i in res.issues)


def test_subject_verb_agreement(engine):
    res = engine.analyze("He don't like it.")
    assert any(i.matched_text.lower() == "he don't" for i in res.issues)
    fixed = engine.apply_all_replacements("He don't like it.")
    assert "He doesn't like it." == fixed


def test_homophones(engine):
    res1 = engine.analyze("Your welcome to join.")
    assert any("your welcome" in i.matched_text.lower() for i in res1.issues)

    res2 = engine.analyze("Better then before.")
    assert any("then" in i.matched_text.lower() for i in res2.issues)


def test_capitalization_and_i(engine):
    res = engine.analyze("i think so. another sentence.")
    assert any(i.matched_text == "i" for i in res.issues)
    assert any(i.matched_text == "a" for i in res.issues)


def test_readability_metrics(engine):
    text = "The quick brown fox jumps over the lazy dog. It was a sunny and pleasant day."
    res = engine.analyze(text)
    assert res.metrics.word_count == 15
    assert res.metrics.sentence_count == 2
    assert res.metrics.flesch_reading_ease > 0
    assert res.metrics.flesch_kincaid_grade >= 0


def test_api_check_endpoint(client):
    response = client.post("/api/check", json={"text": "He don't know."})
    assert response.status_code == 200
    data = response.get_json()
    assert "issues" in data
    assert "metrics" in data
    assert len(data["issues"]) > 0


def test_api_fix_all_endpoint(client):
    payload = {"text": "in order to proceed, he don't go."}
    response = client.post("/api/fix-all", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "to proceed" in data["fixed_text"]
    assert "doesn't go" in data["fixed_text"]


def test_empty_string_handling(engine):
    res = engine.analyze("")
    assert len(res.issues) == 0
    assert res.metrics.word_count == 0
