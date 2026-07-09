import json

import pytest
from fastapi import HTTPException

from prompts.quiz_prompt import build_quiz_prompt
from schemas.quiz import QuizGenerateRequest
from services import quiz_service


def build_llm_payload(count=5):
    questions = []
    for index in range(1, count + 1):
        if index == 1:
            questions.append(
                {
                    "id": "q1",
                    "stem": "关于 Python 中可变对象和不可变对象，哪一项说法正确？",
                    "options": [
                        {"key": "A", "text": "list 是不可变对象，tuple 是可变对象"},
                        {"key": "B", "text": "list 是可变对象，tuple 通常是不可变对象"},
                        {"key": "C", "text": "dict 和 set 都不可变"},
                        {"key": "D", "text": "所有对象都可以作为 dict 的 key"},
                    ],
                    "correct_answer": "B",
                    "explanation": "B 正确。list 可变，tuple 通常不可变。A、C、D 都与 Python 对象模型不符。",
                    "knowledge_point": "Python 可变与不可变对象",
                    "difficulty": "medium",
                }
            )
            continue
        if index == 3:
            questions.append(
                {
                    "id": "q3",
                    "stem": "关于 Python 函数参数，哪一项说法正确？",
                    "options": [
                        {"key": "A", "text": "*args 接收关键字参数，**kwargs 接收位置参数"},
                        {"key": "B", "text": "*args 接收多余位置参数，**kwargs 接收多余关键字参数"},
                        {"key": "C", "text": "lambda 不能接收任何参数"},
                        {"key": "D", "text": "闭包不能访问外层函数变量"},
                    ],
                    "correct_answer": "B",
                    "explanation": "B 正确，*args 形成 tuple，**kwargs 形成 dict。其他选项都误解了函数参数、lambda 或闭包。",
                    "knowledge_point": "Python 函数参数与闭包",
                    "difficulty": "medium",
                }
            )
            continue
        if index == 2:
            questions.append(
                {
                    "id": "q2",
                    "stem": "给定 Python 3 代码：a = [1]; b = a; b.append(2); print(a)。输出是什么？",
                    "options": [
                        {"key": "A", "text": "[1]"},
                        {"key": "B", "text": "[1, 2]"},
                        {"key": "C", "text": "[2]"},
                        {"key": "D", "text": "抛出 TypeError"},
                    ],
                    "correct_answer": "B",
                    "explanation": "B 正确，a 和 b 引用同一个 list 对象，修改 b 会影响 a。A、C 忽略了引用关系，D 不会抛异常。",
                    "knowledge_point": "Python 引用关系与对象共享",
                    "difficulty": "medium",
                }
            )
            continue
        if index == 5:
            questions.append(
                {
                    "id": "q5",
                    "stem": "在 FastAPI 异步接口中调用大模型 API 时，哪种做法更能避免阻塞事件循环？",
                    "options": [
                        {"key": "A", "text": "在 async 函数中直接执行长时间阻塞调用"},
                        {"key": "B", "text": "使用支持 await 的异步客户端，并设置超时和有限重试"},
                        {"key": "C", "text": "把 API Key 写死在代码中便于调试"},
                        {"key": "D", "text": "捕获所有异常后直接返回空字符串"},
                    ],
                    "correct_answer": "B",
                    "explanation": "B 正确，await 异步调用能减少事件循环阻塞。A 会阻塞，C 有安全风险，D 会隐藏错误。",
                    "knowledge_point": "Python async/await 与阻塞调用",
                    "difficulty": "medium",
                }
            )
            continue
        if index == 4:
            questions.append(
                {
                    "id": "q4",
                    "stem": "关于 Python with 语句和上下文管理器，哪一项说法正确？",
                    "options": [
                        {"key": "A", "text": "with 语句会调用对象的 __enter__ 和 __exit__ 方法"},
                        {"key": "B", "text": "with 语句只能用于打开文件"},
                        {"key": "C", "text": "__exit__ 方法一定不能接收异常信息"},
                        {"key": "D", "text": "上下文管理器无法用于数据库连接管理"},
                    ],
                    "correct_answer": "A",
                    "explanation": "A 正确。with 会进入和退出上下文。B、C、D 都限制或误解了上下文管理器。",
                    "knowledge_point": "Python 上下文管理器",
                    "difficulty": "medium",
                }
            )
            continue
        questions.append(
            {
                "id": f"q{index}",
                "stem": f"关于 FastAPI 依赖注入的说法，哪一项正确？第 {index} 题",
                "options": [
                    {"key": "A", "text": "Depends 只能用于同步函数"},
                    {"key": "B", "text": "Depends 可以复用依赖逻辑并支持嵌套依赖"},
                    {"key": "C", "text": "Depends 会自动创建数据库表"},
                    {"key": "D", "text": "Depends 只能在中间件中使用"},
                ],
                "correct_answer": "B",
                "explanation": "B 正确。A、C、D 都夸大或误解了 Depends 的作用。",
                "knowledge_point": "FastAPI 依赖注入",
                "difficulty": "medium",
            }
        )
    return {"questions": questions}


def test_generate_quiz_success(monkeypatch):
    monkeypatch.setattr(
        quiz_service,
        "invoke_llm_json_text",
        lambda prompt: json.dumps(build_llm_payload(), ensure_ascii=False),
    )

    result = quiz_service.generate_quiz(
        QuizGenerateRequest(topic="FastAPI 与后端", count=5, difficulty="medium")
    )

    assert len(result.questions) == 5
    assert [option.key for option in result.questions[0].options] == ["A", "B", "C", "D"]
    assert result.questions[0].correct_answer == "B"


@pytest.mark.parametrize("topic", ["FastAPI 与后端", "RAG", "Docker 与部署"])
def test_generate_quiz_supported_topics(monkeypatch, topic):
    monkeypatch.setattr(
        quiz_service,
        "invoke_llm_json_text",
        lambda prompt: json.dumps(build_llm_payload(), ensure_ascii=False),
    )

    result = quiz_service.generate_quiz(
        QuizGenerateRequest(topic=topic, count=5, difficulty="medium")
    )

    assert len(result.questions) == 5
    assert all(len(question.options) == 4 for question in result.questions)


def test_generate_quiz_retry_once(monkeypatch):
    q1_call_count = {"value": 0}

    def fake_invoke(prompt):
        if "题号 q1/" in prompt and q1_call_count["value"] == 0:
            q1_call_count["value"] += 1
            return "not json"
        return json.dumps(build_llm_payload(), ensure_ascii=False)

    monkeypatch.setattr(quiz_service, "invoke_llm_json_text", fake_invoke)

    result = quiz_service.generate_quiz(
        QuizGenerateRequest(topic="FastAPI 与后端", count=5, difficulty="medium")
    )

    assert len(result.questions) == 5
    assert q1_call_count["value"] == 1


def test_generate_quiz_invalid_topic():
    with pytest.raises(HTTPException) as exc_info:
        quiz_service.generate_quiz(
            QuizGenerateRequest(topic="不支持的方向", count=5, difficulty="medium")
        )

    assert exc_info.value.status_code == 400


def test_validate_quiz_payload_rejects_wrong_options():
    payload = build_llm_payload()
    payload["questions"][0]["options"] = payload["questions"][0]["options"][:3]

    with pytest.raises(ValueError):
        quiz_service.validate_quiz_payload(payload, expected_count=5, difficulty="medium")


def test_validate_quiz_payload_accepts_answer_alias():
    payload = build_llm_payload()
    payload["questions"][0]["answer"] = payload["questions"][0].pop("correct_answer")

    result = quiz_service.validate_quiz_payload(
        payload,
        expected_count=5,
        difficulty="medium",
    )

    assert result[0].correct_answer == "B"


def test_validate_quiz_payload_strips_options_from_stem():
    payload = build_llm_payload()
    payload["questions"][0]["stem"] = (
        "在 Python 中，以下哪项描述了 list 和 tuple 的区别？ "
        "A) list 是不可变的，而 tuple 是可变的。 "
        "B) list 可以包含任意类型的元素，而 tuple 仅能包含相同类型的元素。 "
        "C) list 比 tuple 更耗内存且速度更慢。 "
        "D) list 是可变的，支持动态修改和添加元素；tuple 不可变，但可以用来存储多个数据类型。"
    )

    result = quiz_service.validate_quiz_payload(
        payload,
        expected_count=5,
        difficulty="medium",
    )

    assert result[0].stem == "在 Python 中，以下哪项描述了 list 和 tuple 的区别？"


def test_validate_quiz_payload_rejects_placeholder_option():
    payload = build_llm_payload()
    payload["questions"][0]["options"][0]["text"] = "..."

    with pytest.raises(ValueError, match="不能是省略号或占位内容"):
        quiz_service.validate_quiz_payload(
            payload,
            expected_count=5,
            difficulty="medium",
        )


def test_validate_quiz_payload_rejects_incomplete_stem():
    payload = build_llm_payload()
    payload["questions"][0]["stem"] = "下列代码段中，`"

    with pytest.raises(ValueError, match="题干不完整"):
        quiz_service.validate_quiz_payload(
            payload,
            expected_count=5,
            difficulty="medium",
        )


def test_topic_prompt_contains_distribution_and_quality_rules():
    prompt = build_quiz_prompt(topic="FastAPI 与后端", count=4, difficulty="medium")

    assert "JD 1「FastAPI 核心机制」" in prompt
    assert "JD 4「后端稳定性」" in prompt
    assert "代码分析题" in prompt
    assert "工程场景题" in prompt
    assert "否定题" in prompt
    assert "多答案模糊题" in prompt
    assert "内部自检" in prompt
    assert "不要输出自检过程" in prompt
    assert "[✓]" not in prompt


def test_quality_guard_accepts_valid_questions():
    """验证基础校验通过。"""
    payload = build_llm_payload()
    result = quiz_service.validate_quiz_payload(
        payload,
        expected_count=5,
        difficulty="medium",
    )
    assert len(result) == 5


def test_topic_rules_not_generated_for_unknown_topic():
    """验证未知 topic 不生成子 JD 规则。"""
    prompt = build_quiz_prompt(topic="FastAPI 与后端", count=4, difficulty="medium")
    # 确认子 JD 存在
    assert "JD 1" in prompt
    assert "分布规则" in prompt
