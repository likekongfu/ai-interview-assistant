from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func

from db.database import SessionLocal
from models import (
    AIInterviewInfo,
    InterviewMessage,
    InterviewReport,
    InterviewTopic,
    Resume,
)
from schemas import BatchDeleteRequest
from utils.auth import verify_token

router = APIRouter()


@router.get("/interviews")
def get_ai_interview_records(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        user_id = user["user_id"]
        topic_count_subquery = (
            db.query(
                InterviewTopic.interview_id.label("interview_id"),
                func.count(InterviewTopic.id).label("topic_count"),
            )
            .group_by(InterviewTopic.interview_id)
            .subquery()
        )
        rows = (
            db.query(
                AIInterviewInfo,
                Resume.file_name,
                InterviewReport.overall_score,
                InterviewReport.summary,
                topic_count_subquery.c.topic_count,
            )
            .join(Resume, Resume.id == AIInterviewInfo.resume_id)
            .outerjoin(InterviewReport, InterviewReport.interview_id == AIInterviewInfo.id)
            .outerjoin(
                topic_count_subquery,
                topic_count_subquery.c.interview_id == AIInterviewInfo.id,
            )
            .filter(AIInterviewInfo.user_id == user_id)
            .order_by(AIInterviewInfo.created_at.desc())
            .all()
        )

        result = []
        for interview, resume_name, overall_score, summary, topic_count in rows:
            result.append(
                {
                    "id": interview.id,
                    "resume_name": resume_name,
                    "status": interview.status,
                    "overall_score": overall_score,
                    "summary": summary,
                    "topic_count": topic_count or 0,
                    "created_at": interview.created_at,
                    "finished_at": interview.finished_at,
                    "report_generated": overall_score is not None,
                }
            )

        return result
    finally:
        db.close()


@router.delete("/interviews/batch_delete")
def batch_delete_ai_interview_records(
    req: BatchDeleteRequest,
    user=Depends(verify_token),
):
    if not req.ids:
        return {"message": "未选择记录"}

    db = SessionLocal()
    try:
        owned_ids = [
            item.id
            for item in db.query(AIInterviewInfo.id)
            .filter(
                AIInterviewInfo.id.in_(req.ids),
                AIInterviewInfo.user_id == user["user_id"],
            )
            .all()
        ]

        if not owned_ids:
            raise HTTPException(status_code=404, detail="面试记录不存在")

        delete_ai_interview_rows(db, owned_ids)
        db.commit()
        return {"message": "批量删除成功", "deleted_count": len(owned_ids)}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.delete("/interviews/{interview_id}")
def delete_ai_interview_record(interview_id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        interview = (
            db.query(AIInterviewInfo)
            .filter(
                AIInterviewInfo.id == interview_id,
                AIInterviewInfo.user_id == user["user_id"],
            )
            .first()
        )
        if not interview:
            raise HTTPException(status_code=404, detail="面试记录不存在")

        delete_ai_interview_rows(db, [interview_id])
        db.commit()
        return {"message": "删除成功"}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_ai_interview_rows(db, interview_ids: list[int]):
    db.query(InterviewReport).filter(
        InterviewReport.interview_id.in_(interview_ids)
    ).delete(synchronize_session=False)

    db.query(InterviewMessage).filter(
        InterviewMessage.interview_id.in_(interview_ids)
    ).delete(synchronize_session=False)

    db.query(InterviewTopic).filter(
        InterviewTopic.interview_id.in_(interview_ids)
    ).delete(synchronize_session=False)

    db.query(AIInterviewInfo).filter(
        AIInterviewInfo.id.in_(interview_ids)
    ).delete(synchronize_session=False)
