import logging
import re
from typing import Any

from fastapi import HTTPException

from chains.first_question_chain import first_question_chain, judge_chain
from chains.follow_up_chain import followup_chain
from core.config import MAX_FOLLOW_UP
from db.crud import (
    create_message,
    finish_ai_interview,
    finish_topic,
    get_ai_interview_by_id,
    get_current_topic,
    get_messages_by_topic,
    get_next_topic,
    get_resume_by_id,
    update_follow_up_count,
)
from schemas import FollowUpRequest
from services.llm_output_parser import parse_json_response

logger = logging.getLogger(__name__)

# Topic 追问流程中的动作枚举。LLM 和代码兜底逻辑都会围绕这两个动作做判断。
FOLLOW_UP = "follow_up"
SWITCH_TOPIC = "switch_topic"
CANNOT_ANSWER_SCORE = 20
INVALID_ANSWER_SCORE = 20
CANNOT_ANSWER_MAX_LENGTH = 20
CANNOT_ANSWER_KEYWORDS = (
    "不会",
    "不知道",
    "不清楚",
    "不了解",
    "没接触过",
    "没用过",
    "不太懂",
    "不会说",
    "没经验",
)
TECHNICAL_KEYWORDS = (
    "redis",
    "缓存",
    "数据库",
    "接口",
    "过期时间",
    "项目",
    "方案",
    "优化",
    "锁",
    "互斥锁",
    "请求",
    "查库",
    "缓存击穿",
    "缓存穿透",
    "缓存雪崩",
    "mysql",
    "kafka",
    "消息队列",
    "异步",
    "线程",
    "事务",
    "索引",
    "架构",
    "高并发",
    "队列",
    "异步处理",
    "非阻塞",
    "事件驱动",
    "模块化",
    "数据校验",
    "持久化",
    "扩容",
    "调优",
    "部署",
    "性能",
    "可用",
    "解耦",
    "批量",
)


def handle_follow_up(req: FollowUpRequest, user_id: int):
    """处理用户每次回答后的追问流程。

    主要步骤：
    1. 校验当前用户是否有权访问该面试和简历。
    2. 保存用户回答。
    3. 判断回答是否是“不会”或无效回答。
    4. 调用 LLM 判断当前 Topic 是否继续追问。
    5. 根据 LLM 判断和代码兜底规则决定继续追问、切换 Topic 或结束面试。
    """
    validate_interview_access(req.interview_id, req.resume_id, user_id)

    current_topic = get_current_topic(req.interview_id)
    if not current_topic:
        raise HTTPException(status_code=400, detail="No active topic found")

    create_message(
        interview_id=req.interview_id,
        role="human",
        content=req.answer,
        topic_id=current_topic.id,
    )

    cannot_answer, cannot_answer_reason = detect_cannot_answer(req.answer)
    invalid_answer, invalid_answer_reason = detect_invalid_answer(req.answer)
    history = get_messages_by_topic(req.interview_id, current_topic.id)
    history_text = build_history_text(history)

    if invalid_answer:
        decision = build_invalid_answer_decision(invalid_answer_reason)
    elif cannot_answer:
        decision = build_cannot_answer_decision()
    else:
        decision = judge_topic_action(
            topic=current_topic.topic,
            answer=req.answer,
            history=history_text,
            follow_up_count=current_topic.follow_up_count,
        )
        decision = normalize_decision_by_answer(
            decision=decision,
            answer=req.answer,
            cannot_answer=cannot_answer,
        )

    should_switch, switch_reason = should_switch_topic(
        decision=decision,
        follow_up_count=current_topic.follow_up_count,
        cannot_answer=cannot_answer,
        invalid_answer=invalid_answer,
    )

    log_topic_decision(
        topic=current_topic.topic,
        candidate_answer=req.answer,
        follow_up_count=current_topic.follow_up_count,
        cannot_answer=cannot_answer,
        cannot_answer_reason=cannot_answer_reason,
        invalid_answer=invalid_answer,
        invalid_answer_reason=invalid_answer_reason,
        decision=decision,
        should_switch=should_switch,
        switch_reason=switch_reason,
    )

    if should_switch:
        return switch_to_next_topic(
            req=req,
            current_topic=current_topic,
            decision=decision,
            switch_reason=switch_reason,
        )

    return continue_follow_up(
        req=req,
        current_topic=current_topic,
        history=history,
        decision=decision,
    )


def validate_interview_access(interview_id: int, resume_id: int, user_id: int):
    """校验面试、简历和当前登录用户之间的归属关系。"""
    interview = get_ai_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    if interview.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该面试")
    if interview.resume_id != resume_id:
        raise HTTPException(status_code=400, detail="面试与简历不匹配")

    resume = get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该简历")


def detect_cannot_answer(answer: str) -> tuple[bool, str]:
    """判断候选人是否主要表达“不会/不知道/没接触过”。

    这里故意不是简单 includes("不会")，因为“不会一直查库”这类回答
    是正常技术表达，不能误判为候选人不会。
    """
    compact_answer = re.sub(r"\s+", "", answer.strip().lower())
    if not compact_answer:
        return True, "回答为空"

    if has_technical_details(compact_answer):
        return False, "回答包含技术关键词或具体方案"

    matched_keyword = next(
        (keyword for keyword in CANNOT_ANSWER_KEYWORDS if keyword in compact_answer),
        None,
    )
    if matched_keyword and len(compact_answer) <= CANNOT_ANSWER_MAX_LENGTH:
        return True, f"短回答中包含无法回答关键词：{matched_keyword}"

    return False, "未命中无法回答规则"


def has_technical_details(compact_answer: str) -> bool:
    """判断回答中是否出现技术关键词或具体实现线索。"""
    return any(keyword in compact_answer for keyword in TECHNICAL_KEYWORDS)


def detect_invalid_answer(answer: str) -> tuple[bool, str]:
    """识别纯数字、纯符号、重复字符等没有明确语义的无效回答。"""
    compact_answer = re.sub(r"\s+", "", answer.strip().lower())
    if not compact_answer:
        return True, "empty answer"

    if has_technical_details(compact_answer):
        return False, "answer contains technical details"

    if re.fullmatch(r"\d+", compact_answer):
        return True, "answer is numbers only"

    if re.fullmatch(r"[\W_]+", compact_answer, flags=re.UNICODE):
        return True, "answer is symbols only"

    if len(compact_answer) <= 12 and len(set(compact_answer)) <= 2:
        return True, "answer is short repeated characters"

    if len(compact_answer) <= 8 and not re.search(r"[a-zA-Z\u4e00-\u9fff]", compact_answer):
        return True, "answer has no semantic characters"

    return False, "valid answer"


def build_cannot_answer_decision() -> dict:
    """构造“候选人明确不会”时的固定低分切换决策。"""
    return {
        "action": SWITCH_TOPIC,
        "score": CANNOT_ANSWER_SCORE,
        "reason": "候选人明确表示不会，当前 Topic 无需继续追问",
        "next_question": "",
        "parse_failed": False,
        "cannot_answer": True,
    }


def build_invalid_answer_decision(reason: str) -> dict:
    """构造无效回答时的固定低分切换决策。"""
    return {
        "action": SWITCH_TOPIC,
        "score": INVALID_ANSWER_SCORE,
        "reason": f"Candidate answer is invalid: {reason}",
        "next_question": "",
        "parse_failed": False,
        "invalid_answer": True,
    }


def normalize_decision_by_answer(
    decision: dict,
    answer: str,
    cannot_answer: bool,
) -> dict:
    """修正 LLM 对“不会”类表达的误判。

    如果回答里包含技术细节，但 LLM 仍判断为“明确不会”，这里会把决策
    拉回继续追问，避免误杀正常答案。
    """
    if cannot_answer:
        return decision

    compact_answer = re.sub(r"\s+", "", answer.strip().lower())
    reason = str(decision.get("reason") or "")
    score = decision.get("score")
    looks_like_cannot_answer_judgement = (
        "明确表示不会" in reason
        or "无需继续追问" in reason
        or score == CANNOT_ANSWER_SCORE
    )

    if has_technical_details(compact_answer) and looks_like_cannot_answer_judgement:
        logger.info(
            "normalize_llm_cannot_answer_false_positive answer=%s original_action=%s "
            "original_score=%s original_reason=%s",
            answer,
            decision.get("action"),
            score,
            reason,
        )
        return {
            **decision,
            "action": FOLLOW_UP,
            "score": max(score or 0, 60),
            "reason": "回答包含技术细节，不按无法回答处理，继续追问具体实现",
        }

    return decision


def continue_follow_up(req: FollowUpRequest, current_topic, history: list, decision: dict):
    """继续当前 Topic 的追问，并保存 AI 的下一道问题。"""
    next_question = decision.get("next_question") or generate_follow_up_question(
        topic=current_topic.topic,
        answer=req.answer,
        history=history,
    )
    next_count = current_topic.follow_up_count + 1
    update_follow_up_count(current_topic.id, next_count)

    create_message(
        interview_id=req.interview_id,
        role="ai",
        content=next_question,
        topic_id=current_topic.id,
    )

    return {
        "next_question": next_question,
        "topic": current_topic.topic,
        "follow_up_count": next_count,
        "finished": False,
        "message": None,
        "action": decision.get("action", FOLLOW_UP),
        "score": decision.get("score"),
        "reason": decision.get("reason"),
    }


def switch_to_next_topic(
    req: FollowUpRequest,
    current_topic,
    decision: dict,
    switch_reason: str,
):
    """结束当前 Topic，并切换到下一个 Topic。

    如果已经没有下一个 Topic，则标记整场 AI 面试结束。
    """
    finish_topic(current_topic.id)
    next_topic = get_next_topic(req.interview_id, current_topic.topic_order)
    if not next_topic:
        finish_ai_interview(req.interview_id)
        return {
            "next_question": None,
            "topic": current_topic.topic,
            "follow_up_count": current_topic.follow_up_count,
            "finished": True,
            "message": "面试结束",
            "action": SWITCH_TOPIC,
            "score": decision.get("score"),
            "reason": switch_reason,
        }

    resume = get_resume_by_id(req.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    next_question = generate_topic_question(resume.resume_text, next_topic.topic)
    update_follow_up_count(next_topic.id, 0)

    create_message(
        interview_id=req.interview_id,
        role="ai",
        content=next_question,
        topic_id=next_topic.id,
    )

    return {
        "next_question": next_question,
        "topic": next_topic.topic,
        "follow_up_count": 0,
        "finished": False,
        "message": None,
        "action": SWITCH_TOPIC,
        "score": decision.get("score"),
        "reason": switch_reason,
    }


def judge_topic_action(
    topic: str,
    answer: str,
    history: str,
    follow_up_count: int,
) -> dict:
    """调用 LLM 判断当前回答是否需要继续追问或切换 Topic。"""
    try:
        raw_result = judge_chain.invoke(
            {
                "topic": topic,
                "answer": answer,
                "history": history,
                "follow_up_count": follow_up_count,
                "max_follow_up": MAX_FOLLOW_UP,
            }
        )
        logger.info(
            "topic_decision_raw topic=%s follow_up_count=%s raw=%s",
            topic,
            follow_up_count,
            raw_result,
        )
        parsed = parse_json_response(raw_result)
        return normalize_decision(parsed, answer)
    except Exception as exc:
        logger.warning(
            "topic decision parse failed, fallback to follow_up: topic=%s follow_up_count=%s error=%s",
            topic,
            follow_up_count,
            exc,
        )
        fallback_score = estimate_answer_score(answer)
        return {
            "action": FOLLOW_UP,
            "score": fallback_score,
            "reason": f"LLM 输出解析失败，使用代码兜底评分 {fallback_score} 并继续追问：{exc}",
            "next_question": "",
            "parse_failed": True,
        }


def normalize_decision(parsed: Any, answer: str = "") -> dict:
    """规范化 LLM 返回的决策 JSON，保证 action/score 等字段可用。"""
    if not isinstance(parsed, dict):
        raise ValueError("LLM decision must be a JSON object")

    action = parsed.get("action", FOLLOW_UP)
    if action not in {FOLLOW_UP, SWITCH_TOPIC}:
        action = FOLLOW_UP

    score = parsed.get("score")
    if score is not None:
        score = int(score)
        score = max(0, min(score, 100))
    elif answer:
        score = estimate_answer_score(answer)

    return {
        "action": action,
        "score": score,
        "reason": str(parsed.get("reason") or ""),
        "next_question": str(parsed.get("next_question") or "").strip(),
        "parse_failed": False,
    }


def estimate_answer_score(answer: str) -> int:
    """在 LLM 输出解析失败时，根据回答长度和技术关键词估算保守分数。"""
    invalid_answer, _ = detect_invalid_answer(answer)
    if invalid_answer:
        return 20

    cannot_answer, _ = detect_cannot_answer(answer)
    if cannot_answer:
        return 20

    compact_answer = re.sub(r"\s+", "", answer.strip().lower())
    technical_hits = sum(
        1 for keyword in TECHNICAL_KEYWORDS if keyword in compact_answer
    )
    length_score = min(25, len(compact_answer) // 8)
    technical_score = min(35, technical_hits * 7)
    structure_score = 0
    for marker in ("首先", "其次", "然后", "最后", "比如", "例如", "方案", "问题", "优化"):
        if marker in answer:
            structure_score += 4

    score = 35 + length_score + technical_score + min(20, structure_score)
    return max(20, min(85, score))


def should_switch_topic(decision: dict, follow_up_count: int, cannot_answer: bool, invalid_answer: bool = False):
    """根据 LLM 决策、分数、追问次数和兜底规则判断是否切换 Topic。"""
    score = decision.get("score")

    if invalid_answer:
        return True, "invalid answer, force switch topic"

    if cannot_answer:
        return True, "候选人明确表示不会，强制切换 Topic"

    if follow_up_count >= MAX_FOLLOW_UP:
        return True, f"达到最大追问次数 {MAX_FOLLOW_UP}"

    if decision.get("action") == SWITCH_TOPIC:
        return True, decision.get("reason") or "LLM 判断应切换 Topic"

    if score is not None and score >= 85:
        return True, f"回答评分 {score} >= 85，提前切换 Topic"

    if score is not None and score <= 55 and follow_up_count >= 1:
        return True, f"回答评分 {score} <= 55 且已追问 {follow_up_count} 次"

    return False, "继续追问"


def log_topic_decision(
    topic: str,
    candidate_answer: str,
    follow_up_count: int,
    cannot_answer: bool,
    cannot_answer_reason: str,
    invalid_answer: bool,
    invalid_answer_reason: str,
    decision: dict,
    should_switch: bool,
    switch_reason: str,
):
    """记录 Topic 判断过程，便于排查线上追问和切换行为。"""
    logger.info(
        (
            "topic_decision topic=%s candidate_answer=%s follow_up_count=%s "
            "cannot_answer=%s cannot_answer_reason=%s invalid_answer=%s "
            "invalid_answer_reason=%s score=%s action=%s final_decision=%s "
            "switch_reason=%s"
        ),
        topic,
        candidate_answer,
        follow_up_count,
        cannot_answer,
        cannot_answer_reason,
        invalid_answer,
        invalid_answer_reason,
        decision.get("score"),
        decision.get("action"),
        SWITCH_TOPIC if should_switch else FOLLOW_UP,
        switch_reason,
    )


def build_history_text(history: list):
    """把当前 Topic 的历史消息拼成 Prompt 可读的对话文本。"""
    return "\n".join(
        [
            f"{'面试官' if message.role == 'ai' else '候选人'}：{message.content}"
            for message in history
        ]
    )


def generate_follow_up_question(topic: str, answer: str, history: list):
    """调用追问链，为当前 Topic 生成下一道追问问题。"""
    history_text = build_history_text(history)
    return followup_chain.invoke(
        {
            "topic": topic,
            "answer": answer,
            "history": history_text,
        }
    )


def generate_topic_question(resume_text: str, topic: str):
    """切换 Topic 后，基于简历和新 Topic 生成第一道问题。"""
    return first_question_chain.invoke(
        {
            "resume": resume_text,
            "topic": topic,
        }
    )
