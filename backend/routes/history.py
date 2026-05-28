from fastapi import APIRouter, Depends
from db.database import SessionLocal
from models import Interview, InterviewAnswer
from utils.auth import verify_token

router = APIRouter()


"""历史记录"""


@router.get("")
def get_history(user=Depends(verify_token)):

    db = SessionLocal()

    user_id = user["user_id"]

    interviews = db.query(Interview).filter(Interview.user_id == user_id).all()

    result = []

    for item in interviews:

        answers = (
            db.query(InterviewAnswer)
            .filter(InterviewAnswer.interview_id == item.id)
            .all()
        )

        overall_score = 0
        feedback = "暂无评价"

        if answers:
            overall_score = answers[0].overall_score
            feedback = answers[0].feedback

        result.append(
            {
                "id": item.id,
                "jd": item.jd,
                "created_at": item.created_at,
                "overall_score": overall_score,
                "feedback": feedback,
            }
        )

    db.close()

    return result


"""查询某次面试详情"""


@router.get("/{interview_id}")
def get_interview_detail(interview_id: int, user=Depends(verify_token)):

    db = SessionLocal()

    answers = (
        db.query(InterviewAnswer)
        .filter(InterviewAnswer.interview_id == interview_id)
        .all()
    )

    result = []

    for item in answers:

        result.append(
            {
                "question": item.question,
                "answer": item.answer,
                "technical_score": item.technical_score,
                "logic_score": item.logic_score,
                "experience_score": item.experience_score,
                "communication_score": item.communication_score,
                "overall_score": item.overall_score,
                "feedback": item.feedback,
            }
        )

    db.close()

    return result


"""删除单条面试记录"""


@router.delete("/{interview_id}")
def delete_history(interview_id: int, user=Depends(verify_token)):

    db = SessionLocal()

    # 查找面试记录
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == user["user_id"])
        .first()
    )

    if not interview:
        db.close()
        return {"message": "记录不存在"}

    # 先删除回答
    db.query(InterviewAnswer).filter(
        InterviewAnswer.interview_id == interview_id
    ).delete()

    # 再删除面试记录
    db.delete(interview)

    db.commit()

    db.close()

    return {"message": "删除成功"}
