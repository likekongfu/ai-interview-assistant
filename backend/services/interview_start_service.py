import logging
import re
from typing import Any

from fastapi import HTTPException

from chains.first_question_chain import first_question_chain, topic_chain
from db.crud import create_interview, create_message, get_resume_by_id, save_topics
from services.llm_output_parser import parse_json_response

logger = logging.getLogger(__name__)

INVALID_RESUME_MESSAGE = (
    "上传的文件不是有效简历，请上传包含教育经历、工作经历、项目经历或技能信息的简历。"
)


def start_interview_session(resume_id: int, user_id: int):
    """根据简历创建一场 AI 面试，并生成第一道面试题。

    这里会先校验简历归属和简历内容有效性，再生成 Topic。
    只有 Topic 生成成功后才会创建 interview，避免普通文档造成脏数据。
    """
    resume = get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该简历")

    resume_text = (resume.resume_text or "").strip()
    if not is_valid_resume_text(resume_text):
        logger.info(
            "invalid_resume_text resume_id=%s user_id=%s text_length=%s",
            resume_id,
            user_id,
            len(resume_text),
        )
        raise HTTPException(status_code=400, detail=INVALID_RESUME_MESSAGE)

    topic_list = generate_topics(resume_text, resume_id, user_id)

    interview = create_interview(user_id=user_id, resume_id=resume_id)
    saved_topics = [
        save_topics(interview_id=interview.id, topic=topic, topic_order=order)
        for order, topic in enumerate(topic_list)
    ]
    current_topic = saved_topics[0]

    question_text = generate_first_question(
        resume_text=resume_text,
        topic=current_topic.topic,
        interview_id=interview.id,
        resume_id=resume_id,
        user_id=user_id,
    )

    create_message(
        interview_id=interview.id,
        role="ai",
        content=question_text,
        topic_id=current_topic.id,
    )

    return {"interview_id": interview.id, "first_question": question_text}


def generate_topics(resume_text: str, resume_id: int, user_id: int) -> list[str]:
    """调用 LLM 从简历中提取本场面试要考察的 Topic 列表。"""
    try:
        raw_result = topic_chain.invoke({"resume": resume_text})
        topic_result = parse_json_response(raw_result)
    except Exception as exc:
        logger.exception(
            "generate_interview_topics_failed resume_id=%s user_id=%s error=%s",
            resume_id,
            user_id,
            exc,
        )
        raise HTTPException(status_code=400, detail=INVALID_RESUME_MESSAGE) from exc

    topics = normalize_topic_list(topic_result)
    if not topics:
        logger.warning(
            "empty_interview_topics resume_id=%s user_id=%s raw_result=%r",
            resume_id,
            user_id,
            raw_result,
        )
        raise HTTPException(status_code=400, detail=INVALID_RESUME_MESSAGE)

    return topics


def generate_first_question(
    resume_text: str,
    topic: str,
    interview_id: int,
    resume_id: int,
    user_id: int,
) -> str:
    """基于简历和当前 Topic 调用 LLM 生成第一道问题。"""
    try:
        question_text = first_question_chain.invoke({"resume": resume_text, "topic": topic})
    except Exception as exc:
        logger.exception(
            "generate_first_question_failed interview_id=%s resume_id=%s user_id=%s error=%s",
            interview_id,
            resume_id,
            user_id,
            exc,
        )
        raise HTTPException(status_code=502, detail="AI生成面试题失败，请稍后重试") from exc

    question_text = str(question_text or "").strip()
    if not question_text:
        logger.warning(
            "empty_first_question interview_id=%s resume_id=%s user_id=%s",
            interview_id,
            resume_id,
            user_id,
        )
        raise HTTPException(status_code=502, detail="AI生成面试题失败，请稍后重试")

    return question_text


def is_valid_resume_text(resume_text: str) -> bool:
    """判断解析出的文本是否像一份有效简历。

    主要依据：长度、教育/工作/项目/技能等简历关键词、技术关键词和联系方式。
    普通说明文档或空文本会被拦截为 400，避免进入 LLM 生成流程。
    """
    compact_text = re.sub(r"\s+", "", resume_text)
    if len(compact_text) < 80:
        return False

    lower_text = resume_text.lower()
    resume_markers = [
        "教育经历",
        "教育背景",
        "学历",
        "毕业院校",
        "本科",
        "硕士",
        "博士",
        "工作经历",
        "工作经验",
        "实习经历",
        "项目经历",
        "项目经验",
        "技术栈",
        "专业技能",
        "技能",
        "求职意向",
        "个人信息",
        "联系方式",
        "education",
        "experience",
        "work experience",
        "project",
        "projects",
        "skills",
        "technical skills",
        "resume",
        "curriculum vitae",
    ]
    marker_count = sum(1 for marker in resume_markers if marker in lower_text)

    technical_markers = [
        "java",
        "python",
        "go",
        "mysql",
        "redis",
        "spring",
        "springboot",
        "fastapi",
        "docker",
        "kafka",
        "rocketmq",
        "elasticsearch",
        "linux",
        "api",
        "sql",
    ]
    technical_count = sum(1 for marker in technical_markers if marker in lower_text)
    contact_like = bool(re.search(r"1[3-9]\d{9}|[\w.+-]+@[\w-]+\.[\w.-]+", resume_text))

    return marker_count >= 2 or (marker_count >= 1 and technical_count >= 2) or (
        contact_like and marker_count >= 1
    )


def normalize_topic_list(topic_result: Any) -> list[str]:
    """把 LLM 输出的 Topic 结果统一整理成去重后的字符串列表。"""
    if isinstance(topic_result, dict):
        topic_result = (
            topic_result.get("topics")
            or topic_result.get("topic")
            or topic_result.get("data")
            or []
        )

    if not isinstance(topic_result, list):
        return []

    topics = []
    for item in topic_result:
        if isinstance(item, dict):
            item = item.get("topic") or item.get("name") or item.get("title")
        topic = str(item or "").strip()
        if topic and topic not in topics:
            topics.append(topic[:255])

    return topics
