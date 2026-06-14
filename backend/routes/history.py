from fastapi import APIRouter, Depends, HTTPException

from db.database import SessionLocal
from models import Interview, InterviewAnswer
from schemas import BatchDeleteRequest
from utils.auth import verify_token

router = APIRouter()


@router.get("")
def get_history(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        interviews = (
            db.query(Interview)
            .filter(Interview.user_id == user["user_id"])
            .order_by(Interview.id.desc())
            .all()
        )

        result = []
        for item in interviews:
            answer = (
                db.query(InterviewAnswer)
                .filter(InterviewAnswer.interview_id == item.id)
                .order_by(InterviewAnswer.id.asc())
                .first()
            )

            result.append(
                {
                    "id": item.id,
                    "jd": item.jd,
                    "created_at": item.created_at,
                    "overall_score": answer.overall_score if answer else 0,
                    "feedback": answer.feedback if answer else "暂无评价",
                }
            )

        return result
    finally:
        db.close()


@router.get("/{interview_id}")
def get_interview_detail(interview_id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        practice = (
            db.query(Interview)
            .filter(Interview.id == interview_id, Interview.user_id == user["user_id"])
            .first()
        )
        if not practice:
            raise HTTPException(status_code=404, detail="刷题记录不存在")

        answers = (
            db.query(InterviewAnswer)
            .filter(InterviewAnswer.interview_id == interview_id)
            .order_by(InterviewAnswer.id.asc())
            .all()
        )

        return [
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
            for item in answers
        ]
    finally:
        db.close()


@router.delete("/single_delete/{interview_id}")
def delete_history(interview_id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        interview = (
            db.query(Interview)
            .filter(Interview.id == interview_id, Interview.user_id == user["user_id"])
            .first()
        )
        if not interview:
            raise HTTPException(status_code=404, detail="刷题记录不存在")

        db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_id == interview_id
        ).delete()
        db.delete(interview)
        db.commit()

        return {"message": "删除成功"}
    finally:
        db.close()


@router.delete("/batch_delete/batch_delete")
def batch_delete(req: BatchDeleteRequest, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        owned_ids = [
            item.id
            for item in db.query(Interview.id)
            .filter(Interview.id.in_(req.ids), Interview.user_id == user["user_id"])
            .all()
        ]
        if not owned_ids:
            raise HTTPException(status_code=404, detail="刷题记录不存在")

        db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_id.in_(owned_ids)
        ).delete(synchronize_session=False)
        db.query(Interview).filter(Interview.id.in_(owned_ids)).delete(
            synchronize_session=False
        )
        db.commit()

        return {"message": "批量删除成功"}
    finally:
        db.close()
