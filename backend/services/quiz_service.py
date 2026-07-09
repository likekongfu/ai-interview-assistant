import logging
import re
import time
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from prompts.quiz_prompt import SUPPORTED_QUIZ_TOPICS, build_quiz_prompt
from schemas.quiz import QuizGenerateRequest, QuizGenerateResponse, QuizQuestion
from services.llm_output_parser import parse_json_response
from services.llm_service import LLMProviderError, invoke_llm_json_text

logger = logging.getLogger(__name__)

EXPECTED_OPTION_KEYS = ["A", "B", "C", "D"]
MAX_GENERATE_ATTEMPTS = 2


def generate_quiz(req: QuizGenerateRequest) -> QuizGenerateResponse:
    """生成 AI 应用开发选择题，并对 LLM 输出进行校验和必要重试。"""

    topic = req.topic.strip()
    if topic not in SUPPORTED_QUIZ_TOPICS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的知识方向，请选择：{'、'.join(SUPPORTED_QUIZ_TOPICS)}",
        )

    started_at = time.perf_counter()
    base_prompt = build_quiz_prompt(
        topic=topic,
        count=req.count,
        difficulty=req.difficulty,
        jd=req.jd,
    )
    last_error = ""
    for attempt in range(1, MAX_GENERATE_ATTEMPTS + 1):
        try:
            prompt = append_retry_feedback(base_prompt, last_error) if last_error else base_prompt
            llm_started_at = time.perf_counter()
            raw_result = invoke_llm_json_text(prompt)
            logger.info(
                "quiz_llm_call_done topic=%s difficulty=%s count=%s attempt=%s prompt_chars=%s elapsed=%.2fs",
                topic,
                req.difficulty,
                req.count,
                attempt,
                len(prompt),
                time.perf_counter() - llm_started_at,
            )
            parsed = parse_json_response(raw_result)
            questions = validate_quiz_payload(
                payload=parsed,
                expected_count=req.count,
                difficulty=req.difficulty
            )
            logger.info(
                "quiz_generate_success topic=%s difficulty=%s count=%s attempt=%s elapsed=%.2fs",
                topic,
                req.difficulty,
                len(questions),
                attempt,
                time.perf_counter() - started_at,
            )
            return QuizGenerateResponse(questions=questions)
        except HTTPException:
            raise
        except (ValidationError, ValueError, LLMProviderError) as exc:
            last_error = str(exc)
            logger.warning(
                "quiz_generate_failed topic=%s difficulty=%s count=%s attempt=%s error=%s",
                topic,
                req.difficulty,
                req.count,
                attempt,
                exc,
            )
        except Exception as exc:
            last_error = str(exc)
            logger.exception(
                "quiz_generate_unexpected_error topic=%s difficulty=%s count=%s attempt=%s",
                topic,
                req.difficulty,
                req.count,
                attempt,
            )

    raise HTTPException(
        status_code=502,
        detail=f"选择题生成失败，模型返回格式不稳定，请稍后重试。原因：{last_error}",
    )


def append_retry_feedback(prompt: str, last_error: str) -> str:
    """重试时把失败原因反馈给模型。"""

    return (
        f"{prompt}\n"
        f"上一轮校验失败：{last_error}\n"
        "请重新生成完整 JSON，不要复用不合格题目，检查子 JD 覆盖和 A/B/C/D 选项完整性。"
    )


def validate_quiz_payload(
    payload: Any,
    expected_count: int,
    difficulty: str,
) -> list[QuizQuestion]:
    """校验 LLM 返回结构，确保题目、选项、答案和解析都满足固定格式。"""

    if isinstance(payload, list):
        payload = {"questions": payload}

    if not isinstance(payload, dict):
        raise ValueError("LLM 返回结果必须是 JSON 对象")

    raw_questions = payload.get("questions") or payload.get("data") or payload.get("items")
    if not isinstance(raw_questions, list):
        raise ValueError("questions 必须是数组")

    if len(raw_questions) != expected_count:
        raise ValueError(f"题目数量不正确，期望 {expected_count}，实际 {len(raw_questions)}")

    questions = []
    seen_stems = set()
    for index, item in enumerate(raw_questions, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 题不是对象")

        normalized_item = normalize_question_item(item, index, difficulty)
        question = QuizQuestion.model_validate(normalized_item)
        validate_question(question, index)

        stem_key = question.stem.strip()
        if stem_key in seen_stems:
            raise ValueError(f"第 {index} 题与前面题目重复")
        seen_stems.add(stem_key)
        questions.append(question)

    return questions


def normalize_question_item(item: dict, index: int, difficulty: str) -> dict:
    """补齐题目 ID 和难度字段，降低模型遗漏非关键字段时的失败率。"""

    normalized = dict(item)
    normalized["id"] = str(normalized.get("id") or f"q{index}")
    normalized["difficulty"] = str(normalized.get("difficulty") or difficulty)
    normalized["stem"] = clean_markdown_code_fence(
        normalized.get("stem") or normalized.get("question") or normalized.get("title")
    )
    normalized["options"] = normalize_options(normalized.get("options"))
    normalized["stem"] = strip_options_from_stem(normalized["stem"], normalized["options"])

    if "correct_answer" not in normalized:
        normalized["correct_answer"] = (
            normalized.get("answer")
            or normalized.get("correctAnswer")
            or normalized.get("correct_option")
            or normalized.get("correctOption")
            or normalized.get("correct")
        )
    normalized["correct_answer"] = normalize_answer_key(normalized.get("correct_answer"))

    if "knowledge_point" not in normalized:
        normalized["knowledge_point"] = (
            normalized.get("knowledgePoint")
            or normalized.get("point")
            or normalized.get("topic")
        )
    normalized["explanation"] = clean_markdown_code_fence(normalized.get("explanation"))
    normalized["knowledge_point"] = clean_markdown_code_fence(normalized.get("knowledge_point"))
    return normalized


def clean_markdown_code_fence(value: Any) -> str:
    """去掉模型偶尔返回的 Markdown 代码围栏，避免小程序端直接展示 ``` 标记。"""

    if value is None:
        return ""
    return str(value).replace("```python", "").replace("```", "").strip()


def strip_options_from_stem(stem: str, options: list[dict]) -> str:
    """模型偶尔会把 A/B/C/D 选项混进题干，这里按选项边界清理掉。"""

    cleaned = clean_markdown_code_fence(stem)
    if not cleaned:
        return ""

    # 最常见情况：题干后面直接拼了 A) ... B) ... C) ... D) ...
    option_marker_match = re.search(r"(?<![A-Za-z0-9])A\s*[\)\.、:：]", cleaned)
    if option_marker_match:
        cleaned = cleaned[: option_marker_match.start()].strip()

    # 兜底：如果模型先写了题干，再重复完整选项文本，则从第一个选项文本处截断。
    first_positions = []
    for option in options:
        option_text = clean_markdown_code_fence(option.get("text"))
        if option_text:
            position = cleaned.find(option_text)
            if position > 0:
                first_positions.append(position)
    if first_positions:
        cleaned = cleaned[: min(first_positions)].strip()

    return cleaned.rstrip("。；;，,：:")


def normalize_options(raw_options: Any) -> list[dict]:
    """把模型可能返回的选项对象或字符串数组统一整理成列表结构。"""

    if isinstance(raw_options, dict):
        return [
            {"key": key, "text": get_option_text_from_dict(raw_options, key)}
            for key in EXPECTED_OPTION_KEYS
        ]

    if isinstance(raw_options, list):
        normalized_options = []
        for index, option in enumerate(raw_options):
            key = EXPECTED_OPTION_KEYS[index] if index < len(EXPECTED_OPTION_KEYS) else ""
            if isinstance(option, dict):
                normalized_options.append(
                    {
                        "key": str(option.get("key") or option.get("label") or key).strip(),
                        "text": clean_markdown_code_fence(
                            option.get("text")
                            or option.get("content")
                            or option.get("value")
                            or ""
                        ),
                    }
                )
            else:
                normalized_options.append({"key": key, "text": clean_markdown_code_fence(option)})
        return sort_and_complete_options(normalized_options)

    return []


def normalize_answer_key(value: Any) -> str:
    """把模型返回的答案统一清洗成 A-D。"""

    if value is None:
        return ""
    answer = str(value).strip().upper()
    for key in EXPECTED_OPTION_KEYS:
        if answer == key or answer.startswith(f"{key}.") or answer.startswith(f"{key}、"):
            return key
    return answer[:1] if answer[:1] in EXPECTED_OPTION_KEYS else answer


def normalize_option_key(value: Any, fallback: str) -> str:
    """兼容 A.、A、选项A 等选项 key 写法。"""

    raw_key = str(value or fallback).strip().upper()
    for key in EXPECTED_OPTION_KEYS:
        if raw_key == key or raw_key.startswith(f"{key}.") or raw_key.startswith(f"{key}、"):
            return key
        if key in raw_key and len(raw_key) <= 4:
            return key
    return raw_key


def sort_and_complete_options(options: list[dict]) -> list[dict]:
    """按 A-D 重排模型返回的选项，避免因为顺序乱导致整组题失败。"""

    keyed_options: dict[str, str] = {}
    for index, option in enumerate(options):
        fallback = EXPECTED_OPTION_KEYS[index] if index < len(EXPECTED_OPTION_KEYS) else ""
        key = normalize_option_key(option.get("key"), fallback)
        text = clean_markdown_code_fence(option.get("text"))
        if key in EXPECTED_OPTION_KEYS and text:
            keyed_options[key] = text

    if set(keyed_options) == set(EXPECTED_OPTION_KEYS):
        return [{"key": key, "text": keyed_options[key]} for key in EXPECTED_OPTION_KEYS]

    return options


def get_option_text_from_dict(raw_options: dict, key: str) -> str:
    """从对象形式的 options 中兼容提取 A-D 选项文本。"""

    candidates = (
        key,
        key.lower(),
        f"选项{key}",
        f"{key}.",
        f"{key}、",
    )
    for candidate in candidates:
        value = raw_options.get(candidate)
        if value:
            return clean_markdown_code_fence(value)

    for raw_key, value in raw_options.items():
        normalized_key = str(raw_key).strip().upper()
        if normalized_key.startswith(key) and value:
            return clean_markdown_code_fence(value)
    return ""


def validate_question(question: QuizQuestion, index: int) -> None:
    """校验单道题必须有 A-D 四个选项且正确答案存在。"""

    option_keys = [option.key for option in question.options]
    if option_keys != EXPECTED_OPTION_KEYS:
        raise ValueError(f"第 {index} 题选项必须按 A、B、C、D 顺序返回")

    if len(question.options) != 4:
        raise ValueError(f"第 {index} 题必须包含四个选项")

    option_texts = [option.text.strip() for option in question.options]
    if len(set(option_texts)) != 4:
        raise ValueError(f"第 {index} 题选项内容不能重复")

    if question.correct_answer not in option_keys:
        raise ValueError(f"第 {index} 题正确答案不在选项中")
