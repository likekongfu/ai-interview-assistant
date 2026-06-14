from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from main import app
from models import Interview, InterviewAnswer
from utils.auth import verify_token


@pytest.fixture(autouse=True)
def auth_override():
    app.dependency_overrides[verify_token] = lambda: {"user_id": 1, "username": "zhangsan"}
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def make_score(score=82):
    return {
        "technical_score": score,
        "logic_score": score,
        "experience_score": score,
        "communication_score": score,
        "overall_score": score,
        "feedback": "回答能覆盖关键技术点",
    }


def test_generate_questions_creates_practice_and_returns_question_list(client, monkeypatch):
    import routes.generate as generate_route

    monkeypatch.setattr(
        generate_route,
        "create_practice",
        lambda user_id, jd: SimpleNamespace(id=1001, user_id=user_id, jd=jd),
    )
    monkeypatch.setattr(
        generate_route,
        "question_chain",
        SimpleNamespace(
            invoke=lambda jd: '{"questions":["Redis 缓存击穿是什么？","如何优化慢查询？"]}'
        ),
    )

    response = client.post(
        "/generate_questions",
        json={"jd": "题库：后端；题型：简答；技术方向：Redis"},
    )

    assert response.status_code == 200
    assert response.json()["interview_id"] == 1001
    assert "Redis 缓存击穿是什么？" in response.json()["questions"]


def test_generate_questions_rejects_empty_jd(client):
    response = client.post("/generate_questions", json={"jd": "   "})

    assert response.status_code == 400


def test_generate_questions_returns_502_when_llm_fails(client, monkeypatch):
    import routes.generate as generate_route

    monkeypatch.setattr(
        generate_route,
        "create_practice",
        lambda user_id, jd: SimpleNamespace(id=1001, user_id=user_id, jd=jd),
    )
    monkeypatch.setattr(
        generate_route,
        "question_chain",
        SimpleNamespace(
            invoke=lambda jd: (_ for _ in ()).throw(RuntimeError("llm down"))
        ),
    )

    response = client.post("/generate_questions", json={"jd": "Redis"})

    assert response.status_code == 502


def test_evaluate_answer_saves_score(client, monkeypatch):
    import routes.evaluate as evaluate_route

    saved = []
    monkeypatch.setattr(
        evaluate_route,
        "get_practice_by_id",
        lambda practice_id: SimpleNamespace(id=practice_id, user_id=1),
    )
    monkeypatch.setattr(
        evaluate_route,
        "evaluate_answer_with_ai",
        lambda question, answer: make_score(88),
    )
    monkeypatch.setattr(
        evaluate_route,
        "save_answer",
        lambda interview_id, question, answer, result: saved.append(
            (interview_id, question, answer, result)
        ),
    )

    response = client.post(
        "/evaluate_answer",
        json={
            "interview_id": 1001,
            "question": "Redis 缓存击穿是什么？",
            "answer": "热点 key 过期后大量请求打到数据库，可以用互斥锁和逻辑过期处理。",
        },
    )

    assert response.status_code == 200
    assert response.json()["result"]["overall_score"] == 88
    assert len(saved) == 1


def test_evaluate_answer_rejects_empty_answer(client, monkeypatch):
    import routes.evaluate as evaluate_route

    monkeypatch.setattr(
        evaluate_route,
        "get_practice_by_id",
        lambda practice_id: SimpleNamespace(id=practice_id, user_id=1),
    )

    response = client.post(
        "/evaluate_answer",
        json={"interview_id": 1001, "question": "Redis？", "answer": "   "},
    )

    assert response.status_code == 400


def test_evaluate_answer_rejects_missing_practice(client, monkeypatch):
    import routes.evaluate as evaluate_route

    monkeypatch.setattr(evaluate_route, "get_practice_by_id", lambda practice_id: None)

    response = client.post(
        "/evaluate_answer",
        json={"interview_id": 404, "question": "Redis？", "answer": "答案"},
    )

    assert response.status_code == 400


def test_evaluate_answer_returns_502_when_ai_scoring_fails(client, monkeypatch):
    import routes.evaluate as evaluate_route

    monkeypatch.setattr(
        evaluate_route,
        "get_practice_by_id",
        lambda practice_id: SimpleNamespace(id=practice_id, user_id=1),
    )
    monkeypatch.setattr(
        evaluate_route,
        "evaluate_answer_with_ai",
        lambda question, answer: (_ for _ in ()).throw(RuntimeError("llm down")),
    )

    response = client.post(
        "/evaluate_answer",
        json={"interview_id": 1001, "question": "Redis？", "answer": "有效回答"},
    )

    assert response.status_code == 502


def test_evaluate_answer_allows_repeat_submit_without_crash(client, monkeypatch):
    import routes.evaluate as evaluate_route

    saved = []
    monkeypatch.setattr(
        evaluate_route,
        "get_practice_by_id",
        lambda practice_id: SimpleNamespace(id=practice_id, user_id=1),
    )
    monkeypatch.setattr(
        evaluate_route,
        "evaluate_answer_with_ai",
        lambda question, answer: make_score(70),
    )
    monkeypatch.setattr(
        evaluate_route,
        "save_answer",
        lambda interview_id, question, answer, result: saved.append(result),
    )

    payload = {"interview_id": 1001, "question": "Redis？", "answer": "有效回答"}

    first = client.post("/evaluate_answer", json=payload)
    second = client.post("/evaluate_answer", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(saved) == 2


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items

    def delete(self, synchronize_session=False):
        count = len(self.items)
        self.items.clear()
        return count


class FakeHistoryDb:
    def __init__(self, practice=None, answers=None):
        self.practice = practice
        self.answers = answers or []
        self.committed = False
        self.closed = False
        self.deleted = []

    def query(self, model):
        if model is Interview or getattr(model, "key", None) == "id":
            return FakeQuery([self.practice] if self.practice else [])
        if model is InterviewAnswer:
            return FakeQuery(self.answers)
        return FakeQuery([])

    def delete(self, item):
        self.deleted.append(item)

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


def test_history_detail_returns_saved_answer(client, monkeypatch):
    import routes.history as history_route

    db = FakeHistoryDb(
        practice=SimpleNamespace(id=1001, user_id=1),
        answers=[
            SimpleNamespace(
                question="Redis？",
                answer="缓存击穿处理",
                technical_score=80,
                logic_score=80,
                experience_score=75,
                communication_score=82,
                overall_score=80,
                feedback="回答较完整",
            )
        ],
    )
    monkeypatch.setattr(history_route, "SessionLocal", lambda: db)

    response = client.get("/history/1001")

    assert response.status_code == 200
    assert response.json()[0]["overall_score"] == 80


def test_history_detail_returns_404_when_question_record_missing(client, monkeypatch):
    import routes.history as history_route

    monkeypatch.setattr(history_route, "SessionLocal", lambda: FakeHistoryDb())

    response = client.get("/history/404")

    assert response.status_code == 404


def test_delete_missing_history_returns_404(client, monkeypatch):
    import routes.history as history_route

    monkeypatch.setattr(history_route, "SessionLocal", lambda: FakeHistoryDb())

    response = client.delete("/history/single_delete/404")

    assert response.status_code == 404
