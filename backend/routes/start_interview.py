from fastapi import APIRouter, Depends

from schemas import StartInterviewResponse
from services.interview_start_service import start_interview_session
from utils.auth import verify_token

router = APIRouter()


@router.post("/start", response_model=StartInterviewResponse)
def start_interview(resume_id: int, user=Depends(verify_token)):
    return start_interview_session(resume_id=resume_id, user_id=user["user_id"])
