import json
import logging
import re
from statistics import mean
from typing import Any

from fastapi import HTTPException

from db.crud import (
    get_ai_interview_by_id,
    get_interview_context,
    get_messages_by_interview,
    get_report_by_interview_id,
    get_topics_by_interview,
    save_interview_report,
)
from prompts.report_prompt import build_interview_report_prompt
from services.llm_service import invoke_llm_text
from services.llm_output_parser import parse_json_response

logger = logging.getLogger(__name__)

CANNOT_ANSWER_KEYWORDS = (
    "不会",
    "不知道",
    "不清楚",
    "不了解",
    "没接触过",
    "没用过",
    "不太懂",
    "没经验",
)
TECHNICAL_KEYWORDS = (
    "redis",
    "缓存",
    "数据库",
    "接口",
    "fastapi",
    "mysql",
    "kafka",
    "索引",
    "异步",
    "锁",
    "项目",
    "方案",
    "优化",
)


def generate_ai_interview_report(interview_id: int, user_id: int):
    """生成并保存指定 AI 面试的结构化报告。"""
    interview = get_ai_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="interview_id 不存在")
    if interview.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该面试")

    existing_report = get_report_by_interview_id(interview_id)
    if existing_report:
        logger.info("report already exists, regenerate and update interview_id=%s", interview_id)

    if interview.status != "finished":
        raise HTTPException(status_code=400, detail="面试未完成，不能生成报告")

    topics = get_topics_by_interview(interview_id)
    messages = get_messages_by_interview(interview_id)
    if not topics or not messages:
        raise HTTPException(status_code=400, detail="面试记录不足，不能生成报告")

    logger.info(
        "generate report start interview_id=%s topics=%s messages=%s",
        interview_id,
        len(topics),
        len(messages),
    )

    llm_report = build_report_with_llm(interview_id, topics, messages)
    normalized_report = normalize_report(llm_report, topics, messages)
    normalized_report["overall_score"] = calculate_overall_score(
        normalized_report["topic_scores"],
        topics,
        messages,
    )
    normalized_report["summary"] = apply_summary_policy(
        normalized_report["summary"],
        normalized_report["overall_score"],
        normalized_report["topic_scores"],
        messages,
    )
    normalized_report["strengths"] = apply_strength_display_policy(
        normalized_report["strengths"],
        normalized_report["overall_score"],
        normalized_report["topic_scores"],
        messages,
    )

    save_interview_report(
        interview_id=interview_id,
        overall_score=normalized_report["overall_score"],
        summary=normalized_report["summary"],
        strengths=json.dumps(normalized_report["strengths"], ensure_ascii=False),
        weaknesses=json.dumps(normalized_report["weaknesses"], ensure_ascii=False),
        topic_scores_json=json.dumps(
            normalized_report["topic_scores"], ensure_ascii=False
        ),
        improvement_suggestions=json.dumps(
            normalized_report["improvement_suggestions"], ensure_ascii=False
        ),
        study_plan=json.dumps(normalized_report["study_plan"], ensure_ascii=False),
    )

    logger.info(
        "generate report success interview_id=%s overall_score=%s",
        interview_id,
        normalized_report["overall_score"],
    )
    return {
        "interview_id": interview_id,
        **normalized_report,
    }


def get_ai_interview_report(interview_id: int, user_id: int):
    """查询当前用户指定面试的报告；未生成时返回 report_not_generated。"""
    interview = get_ai_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="interview_id 不存在")
    if interview.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该面试")

    status_payload = {
        "interview_status": interview.status,
        "finished": interview.status == "finished",
    }

    report = get_report_by_interview_id(interview_id)
    if not report:
        return {
            "status": "report_not_generated",
            "interview_id": interview_id,
            **status_payload,
        }

    return {**serialize_report(report), **status_payload}


def build_report_with_llm(interview_id: int, topics: list, messages: list):
    """调用 LLM 生成报告 JSON；失败时返回代码兜底报告。"""
    prompt = build_interview_report_prompt(
        interview_id=interview_id,
        topics_text=build_topics_text(topics),
        conversation_text=build_conversation_text(messages),
    )
    try:
        raw_result = invoke_llm_text(prompt)
        logger.info("report_llm_raw interview_id=%s raw=%s", interview_id, raw_result)
        return parse_json_response(raw_result)
    except Exception as exc:
        logger.warning(
            "report llm parse failed, fallback used: interview_id=%s error=%s",
            interview_id,
            exc,
        )
        return build_fallback_report(topics, messages)


def normalize_report(report: Any, topics: list, messages: list):
    """规范化 LLM 报告字段，缺失或格式异常时使用兜底内容补齐。"""
    if not isinstance(report, dict):
        report = build_fallback_report(topics, messages)

    fallback = build_fallback_report(topics, messages)
    topic_names = [topic.topic for topic in topics]

    topic_scores = normalize_topic_scores(
        report.get("topic_scores"),
        topic_names,
        fallback["topic_scores"],
    )

    return {
        "summary": clean_text(report.get("summary")) or fallback["summary"],
        "strengths": normalize_string_list(
            report.get("strengths"), fallback["strengths"], min_count=2
        ),
        "weaknesses": normalize_string_list(
            report.get("weaknesses"), fallback["weaknesses"], min_count=2
        ),
        "topic_scores": topic_scores,
        "improvement_suggestions": normalize_string_list(
            report.get("improvement_suggestions"),
            fallback["improvement_suggestions"],
            min_count=2,
        ),
        "study_plan": normalize_string_list(
            report.get("study_plan"), fallback["study_plan"], min_count=3
        )[:3],
    }


def normalize_topic_scores(value: Any, topic_names: list[str], fallback: list[dict]):
    """规范化每个 Topic 的得分，保证 Topic 顺序和数据库中的 Topic 一致。"""
    fallback_by_topic = {item["topic"]: item for item in fallback}
    by_topic = {}

    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue
            topic = clean_text(item.get("topic"))
            if topic not in topic_names:
                continue
            by_topic[topic] = {
                "topic": topic,
                "score": fallback_by_topic[topic]["score"],
                "comment": (
                    fallback_by_topic[topic]["comment"]
                    if fallback_by_topic[topic]["score"] <= 40
                    else clean_text(item.get("comment"))
                    or fallback_by_topic[topic]["comment"]
                ),
            }

    return [
        by_topic.get(topic_name) or fallback_by_topic[topic_name]
        for topic_name in topic_names
    ]


def calculate_overall_score(topic_scores: list[dict], topics: list, messages: list):
    """按 Topic 平均分、完成度和回答稳定性计算综合分。"""
    topic_average = mean([item["score"] for item in topic_scores]) if topic_scores else 60
    completeness = calculate_completeness(topics)
    stability = calculate_answer_stability(messages)
    score = topic_average * 0.7 + completeness * 0.15 + stability * 0.15
    return clamp_score(score)


def calculate_completeness(topics: list):
    """计算面试完成度，已完成 Topic 占全部 Topic 的比例。"""
    if not topics:
        return 0
    finished_count = sum(1 for topic in topics if topic.finished)
    return round(finished_count / len(topics) * 100)


def calculate_answer_stability(messages: list):
    """根据无效回答、不会回答和过短回答比例计算回答稳定性。"""
    answers = [message.content for message in messages if message.role == "human"]
    if not answers:
        return 30

    invalid_count = sum(1 for answer in answers if is_invalid_answer(answer))
    invalid_penalty = invalid_count / len(answers) * 70
    cannot_count = sum(1 for answer in answers if is_short_cannot_answer(answer))
    cannot_penalty = cannot_count / len(answers) * 45
    short_count = sum(1 for answer in answers if len(answer.strip()) < 20)
    short_penalty = short_count / len(answers) * 20
    return clamp_score(100 - invalid_penalty - cannot_penalty - short_penalty)


def apply_summary_policy(
    summary: str,
    overall_score: int,
    topic_scores: list[dict],
    messages: list,
):
    """根据最终分数和无效回答比例修正综合评价，避免低质量回答被过度夸奖。"""
    answers = [message.content for message in messages if message.role == "human"]
    invalid_ratio = calculate_invalid_answer_ratio(answers)
    short_ratio = calculate_short_answer_ratio(answers)
    topic_average = (
        mean([item["score"] for item in topic_scores]) if topic_scores else overall_score
    )

    if invalid_ratio >= 0.7:
        return (
            "本次面试中候选人的回答大量为纯数字、重复字符或无明确语义内容，"
            "无法证明其对相关 Topic 的理解和项目实践能力，整体表现较弱。"
        )

    if overall_score < 60 or topic_average < 60 or short_ratio >= 0.6:
        return (
            "本次面试中候选人的回答有效信息不足，技术细节、项目场景和解决方案描述不充分，"
            "暂未体现出稳定的岗位胜任力，需要优先补齐基础知识和项目表达。"
        )

    return summary


def apply_strength_display_policy(
    strengths: list[str],
    overall_score: int,
    topic_scores: list[dict],
    messages: list,
):
    """决定是否展示优点；低分或无效回答过多时隐藏优点。"""
    answers = [message.content for message in messages if message.role == "human"]
    invalid_ratio = calculate_invalid_answer_ratio(answers)
    short_ratio = calculate_short_answer_ratio(answers)
    topic_average = (
        mean([item["score"] for item in topic_scores]) if topic_scores else overall_score
    )

    should_hide_strengths = (
        overall_score < 60
        or topic_average < 60
        or invalid_ratio >= 0.4
        or short_ratio >= 0.6
    )

    if should_hide_strengths:
        logger.info(
            "report strengths hidden overall_score=%s topic_average=%.2f invalid_ratio=%.2f short_ratio=%.2f",
            overall_score,
            topic_average,
            invalid_ratio,
            short_ratio,
        )
        return []

    return strengths


def calculate_invalid_answer_ratio(answers: list[str]):
    """计算无效回答和短“不会”回答在全部回答中的占比。"""
    if not answers:
        return 1
    invalid_count = sum(
        1
        for answer in answers
        if is_invalid_answer(answer) or is_short_cannot_answer(answer)
    )
    return invalid_count / len(answers)


def calculate_short_answer_ratio(answers: list[str]):
    """计算过短回答在全部回答中的占比。"""
    if not answers:
        return 1
    short_count = sum(1 for answer in answers if len(answer.strip()) < 20)
    return short_count / len(answers)


def build_fallback_report(topics: list, messages: list):
    """在 LLM 失败或返回非法 JSON 时，根据面试记录生成兜底报告。"""
    topic_scores = [
        build_fallback_topic_score(topic.topic, get_topic_answers(topic.id, messages))
        for topic in topics
    ]
    cannot_answers = [
        message.content
        for message in messages
        if message.role == "human" and is_short_cannot_answer(message.content)
    ]

    weakness = "部分回答缺少具体实现细节，需要补充项目中的参数、链路和取舍。"
    if cannot_answers:
        weakness = "存在多次不会或不了解的回答，需要优先补齐对应 Topic 的知识盲区。"

    return {
        "summary": "本次面试已完成，候选人能够覆盖部分项目和技术点，但回答深度与稳定性仍有提升空间。",
        "strengths": [
            "能够围绕项目经历展开回答。",
            "部分回答能提到接口、缓存或数据库等工程实践。",
        ],
        "weaknesses": [
            weakness,
            "部分 Topic 的回答缺少量化结果、异常场景和落地细节。",
        ],
        "topic_scores": topic_scores,
        "improvement_suggestions": [
            "按 Topic 整理每个技术点的原理、项目用法、常见问题和优化方案。",
            "准备 2 个项目难点案例，补充背景、方案、结果和取舍。",
        ],
        "study_plan": [
            "第1天：复盘本次低分 Topic，补齐核心概念和常见面试题。",
            "第2天：整理项目中的接口、缓存、数据库和异常处理案例。",
            "第3天：按 STAR 结构练习项目介绍和技术追问回答。",
        ],
    }


def build_fallback_topic_score(topic: str, answers: list[str]):
    """根据某个 Topic 下的候选人回答生成兜底 Topic 得分。"""
    if not answers:
        return {
            "topic": topic,
            "score": 20,
            "comment": "该 Topic 缺少有效回答，需要系统复习基础概念和项目应用。",
        }

    invalid_ratio = sum(1 for answer in answers if is_invalid_answer(answer)) / len(answers)
    cannot_ratio = sum(1 for answer in answers if is_short_cannot_answer(answer)) / len(answers)
    technical_hits = sum(count_technical_keywords(answer) for answer in answers)
    average_length = mean([len(answer.strip()) for answer in answers])

    if invalid_ratio >= 0.5:
        return {
            "topic": topic,
            "score": 20,
            "comment": "该 Topic 的回答多为纯数字、重复字符或无语义内容，无法证明掌握程度。",
        }

    score = 35 + min(30, technical_hits * 5) + min(20, average_length / 15)
    score -= invalid_ratio * 50
    score -= cannot_ratio * 45
    score = clamp_score(score)

    if score >= 80:
        comment = "回答覆盖了较多工程细节，可以继续加强边界场景和取舍分析。"
    elif score >= 60:
        comment = "具备一定理解，但原理、异常场景或项目量化结果仍需补充。"
    else:
        comment = "回答偏弱，需要优先复习基础概念和常见实践问题。"

    return {"topic": topic, "score": score, "comment": comment}


def get_topic_answers(topic_id: int, messages: list):
    """从整场面试消息中提取某个 Topic 下的候选人回答。"""
    return [
        message.content
        for message in messages
        if message.topic_id == topic_id and message.role == "human"
    ]


def build_topics_text(topics: list):
    """把 Topic 状态整理成 LLM 报告 Prompt 使用的文本。"""
    return "\n".join(
        [
            f"- {topic.topic}：追问次数 {topic.follow_up_count}，"
            f"是否完成 {'是' if topic.finished else '否'}"
            for topic in topics
        ]
    )


def build_conversation_text(messages: list):
    """把面试消息整理成 LLM 报告 Prompt 使用的对话文本。"""
    role_map = {"ai": "面试官", "human": "候选人"}
    return "\n".join(
        [
            f"{role_map.get(message.role, message.role)}：{message.content}"
            for message in messages
        ]
    )


def serialize_report(report):
    """把数据库中的报告对象转换成接口返回的 JSON 结构。"""
    return {
        "interview_id": report.interview_id,
        "overall_score": report.overall_score,
        "summary": report.summary,
        "strengths": parse_json_list(report.strengths),
        "weaknesses": parse_json_list(report.weaknesses),
        "topic_scores": parse_json_list(report.topic_scores_json),
        "improvement_suggestions": parse_json_list(report.improvement_suggestions),
        "study_plan": parse_json_list(report.study_plan),
    }


def normalize_string_list(value: Any, fallback: list[str], min_count: int):
    """规范化字符串列表字段，并用 fallback 保证最小条数。"""
    if isinstance(value, list):
        result = [clean_text(item) for item in value if clean_text(item)]
    else:
        result = []

    if len(result) < min_count:
        result.extend(fallback)

    deduped = []
    for item in result:
        if item not in deduped:
            deduped.append(item)
    return deduped


def parse_json_list(value: str):
    """解析数据库中以 JSON 字符串保存的列表字段。"""
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def clean_text(value: Any):
    """把任意值转换成去除首尾空白的字符串。"""
    if value is None:
        return ""
    return str(value).strip()


def clamp_score(value: Any):
    """把分数限制在 0 到 100 之间，异常时返回默认分 60。"""
    try:
        return max(0, min(100, round(float(value))))
    except Exception:
        return 60


def is_short_cannot_answer(answer: str):
    """判断回答是否是短文本形式的“不会/不知道/没经验”。"""
    compact = re.sub(r"\s+", "", answer.strip().lower())
    if len(compact) > 20:
        return False
    if count_technical_keywords(compact) > 0:
        return False
    return any(keyword in compact for keyword in CANNOT_ANSWER_KEYWORDS)


def is_invalid_answer(answer: str):
    """判断回答是否为纯数字、重复字符、纯符号等无效内容。"""
    compact = re.sub(r"\s+", "", answer.strip().lower())
    if not compact:
        return True
    if count_technical_keywords(compact) > 0:
        return False
    if re.fullmatch(r"\d+", compact):
        return True
    if re.fullmatch(r"[\W_]+", compact, flags=re.UNICODE):
        return True
    if len(compact) <= 12 and len(set(compact)) <= 2:
        return True
    if len(compact) <= 8 and not re.search(r"[a-zA-Z\u4e00-\u9fff]", compact):
        return True
    return False


def count_technical_keywords(answer: str):
    """统计回答中命中的技术关键词数量。"""
    lower_answer = answer.lower()
    return sum(1 for keyword in TECHNICAL_KEYWORDS if keyword in lower_answer)


def calculate_scores(interview_id):
    """计算刷题模式下历史评分记录的平均分。"""
    history = get_interview_context(interview_id)
    if not history:
        raise HTTPException(status_code=404, detail="没有找到已评分的回答记录")

    count = len(history)
    return {
        "technical_avg": round(sum(item.technical_score for item in history) / count, 2),
        "logic_avg": round(sum(item.logic_score for item in history) / count, 2),
        "experience_avg": round(sum(item.experience_score for item in history) / count, 2),
        "communication_avg": round(
            sum(item.communication_score for item in history) / count, 2
        ),
        "overall_avg": round(sum(item.overall_score for item in history) / count, 2),
    }


def generate_report(interview_id: int):
    """生成刷题模式下的简单汇总报告。"""
    history = get_interview_context(interview_id)
    scores = calculate_scores(interview_id)
    return {
        **scores,
        "summary": f"共完成 {len(history)} 道练习题，平均分 {scores['overall_avg']}。",
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
    }
