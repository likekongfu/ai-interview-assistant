from fastapi import APIRouter, Depends

from schemas import InterviewReportResponse
from services.report_service import (
    generate_ai_interview_report,
    generate_report,
    get_ai_interview_report,
)
from utils.auth import verify_token

router = APIRouter()


@router.get("/report/{interview_id}")
def report(interview_id: int):

    return generate_report(interview_id)


@router.post(
    "/interviews/{interview_id}/report/generate",
    response_model=InterviewReportResponse,
)
def generate_interview_report(interview_id: int, user=Depends(verify_token)):
    return generate_ai_interview_report(
        interview_id=interview_id,
        user_id=user["user_id"],
    )


@router.get("/interviews/{interview_id}/report")
def get_interview_report(interview_id: int, user=Depends(verify_token)):
    return get_ai_interview_report(
        interview_id=interview_id,
        user_id=user["user_id"],
    )
