import json

from fastapi.testclient import TestClient

from main import app
from services import quiz_service


client = TestClient(app)


def test_quiz_generate_api(monkeypatch):
    payload = {
        "questions": [
            {
                "id": f"q{index}",
                    "stem": (
                        "关于 Python 函数参数和闭包，哪一项说法正确？"
                        if index == 3
                        else (
                            "在 FastAPI 异步接口中调用大模型 API 时，如何避免阻塞事件循环？"
                            if index == 5
                            else (
                            "关于 Python with 语句和上下文管理器，哪一项说法正确？"
                            if index == 4
                            else (
                                "给定 Python 3 代码：a = [1]; b = a; b.append(2); print(a)。输出是什么？"
                                if index == 2
                                else f"Python 中 == 和 is 的区别是什么？第 {index} 题"
                            )
                        )
                    )
                ),
                "options": [
                    {"key": "A", "text": "[1]" if index == 2 else "== 比较对象身份，is 比较值"},
                    {"key": "B", "text": "[1, 2]" if index == 2 else "== 通常比较值，is 比较对象身份"},
                    {"key": "C", "text": "抛出 TypeError" if index == 2 else "二者完全相同"},
                    {"key": "D", "text": "None" if index == 2 else "is 只能用于字符串"},
                ],
                "correct_answer": "B",
                "explanation": "B 正确。== 通常走值比较，is 比较对象身份。",
                "knowledge_point": (
                    "AI 应用中的超时与重试"
                    if index == 5
                    else (
                        "Python 上下文管理器"
                        if index == 4
                        else ("Python 引用关系与对象共享" if index == 2 else ("Python 函数参数与闭包" if index == 3 else "Python 对象模型"))
                    )
                ),
                "difficulty": "medium",
            }
            for index in range(1, 6)
        ]
    }
    monkeypatch.setattr(
        quiz_service,
        "invoke_llm_json_text",
        lambda prompt: json.dumps(payload, ensure_ascii=False),
    )

    response = client.post(
        "/api/quiz/generate",
        json={"topic": "Python", "count": 5, "difficulty": "medium", "jd": ""},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) == 5
    assert data["questions"][0]["correct_answer"] == "B"
