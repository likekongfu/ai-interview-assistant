from contextlib import contextmanager
from datetime import datetime

from db.database import SessionLocal
from models import (
    AIInterviewInfo,
    Interview,
    InterviewAnswer,
    InterviewMessage,
    InterviewReport,
    InterviewTopic,
    Resume,
    User,
)


@contextmanager
def session_scope(commit: bool = False):
    db = SessionLocal()
    try:
        yield db
        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _create_record(record):
    with session_scope() as db:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


def create_practice(user_id: int, jd: str):
    return _create_record(Interview(jd=jd, user_id=user_id))


def get_practice_by_id(interview_id: int):
    with session_scope() as db:
        return db.query(Interview).filter(Interview.id == interview_id).first()


def create_interview(user_id: int, resume_id: int):
    return _create_record(AIInterviewInfo(user_id=user_id, resume_id=resume_id))


def get_ai_interview_by_id(interview_id: int):
    with session_scope() as db:
        return (
            db.query(AIInterviewInfo)
            .filter(AIInterviewInfo.id == interview_id)
            .first()
        )


def finish_ai_interview(interview_id: int):
    with session_scope(commit=True) as db:
        interview = (
            db.query(AIInterviewInfo)
            .filter(AIInterviewInfo.id == interview_id)
            .first()
        )
        if interview:
            interview.status = "finished"
            interview.finished_at = datetime.now()


def save_answer(interview_id: int, question: str, answer: str, scores: dict):
    return _create_record(
        InterviewAnswer(
            interview_id=interview_id,
            question=question,
            answer=answer,
            technical_score=scores["technical_score"],
            logic_score=scores["logic_score"],
            experience_score=scores["experience_score"],
            communication_score=scores["communication_score"],
            overall_score=scores["overall_score"],
            feedback=scores["feedback"],
        )
    )


def get_interview_context(interview_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewAnswer)
            .filter(InterviewAnswer.interview_id == interview_id)
            .all()
        )


def finish_interview(interview_id: int):
    with session_scope(commit=True) as db:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            interview.status = "finished"
            interview.finished_at = datetime.now()


def create_message(interview_id: int, role: str, content: str, topic_id: int):
    return _create_record(
        InterviewMessage(
            interview_id=interview_id,
            role=role,
            content=content,
            topic_id=topic_id,
        )
    )


def get_current_topic(interview_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(
                InterviewTopic.interview_id == interview_id,
                InterviewTopic.finished == False,
            )
            .order_by(InterviewTopic.topic_order.asc())
            .first()
        )


def get_next_topic(interview_id: int, current_order: int):
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(
                InterviewTopic.interview_id == interview_id,
                InterviewTopic.topic_order > current_order,
            )
            .order_by(InterviewTopic.topic_order.asc())
            .first()
        )


def update_follow_up_count(topic_id: int, count: int):
    with session_scope(commit=True) as db:
        topic = db.query(InterviewTopic).filter(InterviewTopic.id == topic_id).first()
        if topic:
            topic.follow_up_count = count


def finish_topic(topic_id: int):
    with session_scope(commit=True) as db:
        topic = db.query(InterviewTopic).filter(InterviewTopic.id == topic_id).first()
        if topic:
            topic.finished = True


def save_resume(user_id: int, file_name: str, resume_text: str):
    return _create_record(
        Resume(user_id=user_id, file_name=file_name, resume_text=resume_text)
    )


def get_resume_by_id(resume_id: int) -> Resume:
    with session_scope() as db:
        return db.query(Resume).filter(Resume.id == resume_id).first()


def get_messages_by_topic(interview_id: int, topic_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewMessage)
            .filter(
                InterviewMessage.interview_id == interview_id,
                InterviewMessage.topic_id == topic_id,
            )
            .order_by(InterviewMessage.id.asc())
            .all()
        )


def get_messages_by_interview(interview_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewMessage)
            .filter(InterviewMessage.interview_id == interview_id)
            .order_by(InterviewMessage.id.asc())
            .all()
        )


def get_topics_by_interview(interview_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(InterviewTopic.interview_id == interview_id)
            .order_by(InterviewTopic.topic_order.asc())
            .all()
        )


def get_report_by_interview_id(interview_id: int):
    with session_scope() as db:
        return (
            db.query(InterviewReport)
            .filter(InterviewReport.interview_id == interview_id)
            .first()
        )


def save_interview_report(
    interview_id: int,
    overall_score: int,
    summary: str,
    strengths: str,
    weaknesses: str,
    topic_scores_json: str,
    improvement_suggestions: str,
    study_plan: str,
):
    with session_scope(commit=True) as db:
        report = (
            db.query(InterviewReport)
            .filter(InterviewReport.interview_id == interview_id)
            .first()
        )
        if not report:
            report = InterviewReport(interview_id=interview_id)
            db.add(report)

        report.overall_score = overall_score
        report.summary = summary
        report.strengths = strengths
        report.weaknesses = weaknesses
        report.topic_scores_json = topic_scores_json
        report.improvement_suggestions = improvement_suggestions
        report.study_plan = study_plan
        report.updated_at = datetime.now()
        db.flush()
        db.refresh(report)
        return report


def save_topics(interview_id: int, topic: str, topic_order: int):
    return _create_record(
        InterviewTopic(
            interview_id=interview_id,
            topic=topic,
            topic_order=topic_order,
        )
    )


def get_user_by_username(username: str):
    with session_scope() as db:
        return db.query(User).filter(User.username == username).first()


def create_user(username: str, password: str):
    return _create_record(User(username=username, password=password))


def update_user_password(user_id: int, password: str):
    with session_scope(commit=True) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.password = password
