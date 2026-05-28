from db.database import SessionLocal
from models import Interview, InterviewAnswer


def create_interview(user_id: int, jd: str):
    db = SessionLocal()
    interview = Interview(jd=jd, user_id=user_id)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    db.close()
    return interview


def save_answer(interview_id: int, question: str, answer: str, scores: dict):
    db = SessionLocal()
    answer_record = InterviewAnswer(
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
    db.add(answer_record)
    db.commit()
    db.close()
    return answer_record
