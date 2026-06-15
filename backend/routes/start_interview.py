import logging

from fastapi import APIRouter, Depends, HTTPException

from schemas import StartInterviewResponse
from services.interview_start_service import start_interview_session
from utils.auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start", response_model=StartInterviewResponse)
def start_interview(resume_id: int, user=Depends(verify_token)):
    try:
        return start_interview_session(resume_id=resume_id, user_id=user["user_id"])
    except HTTPException:
        logger.exception("start_interview_http_error resume_id=%s user_id=%s", resume_id, user["user_id"])
        raise
    except Exception as exc:
        logger.exception(
            "start_interview_unhandled_error resume_id=%s user_id=%s error=%s",
            resume_id,
            user["user_id"],
            exc,
        )
        raise HTTPException(status_code=500, detail="开始面试失败，请稍后重试") from exc
