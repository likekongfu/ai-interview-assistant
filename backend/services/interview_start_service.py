from fastapi import HTTPException

from chains.first_question_chain import first_question_chain, topic_chain
from db.crud import create_interview, create_message, get_resume_by_id, save_topics
from services.llm_output_parser import parse_json_response


def start_interview_session(resume_id: int, user_id: int):
    resume = get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问该简历")

    interview = create_interview(user_id=user_id, resume_id=resume_id)
    topic_list = parse_json_response(topic_chain.invoke({"resume": resume.resume_text}))
    if not topic_list:
        raise HTTPException(status_code=500, detail="Failed to generate interview topics")

    saved_topics = [
        save_topics(interview_id=interview.id, topic=topic, topic_order=order)
        for order, topic in enumerate(topic_list)
    ]
    current_topic = saved_topics[0]

    question_text = first_question_chain.invoke(
        {"resume": resume.resume_text, "topic": current_topic.topic}
    )
    create_message(
        interview_id=interview.id,
        role="ai",
        content=question_text,
        topic_id=current_topic.id,
    )

    return {"interview_id": interview.id, "first_question": question_text}
