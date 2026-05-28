from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas import InterviewRequest
from utils.auth import verify_token
from services.model_service import stream_generate_questions
from db.crud import create_interview

router = APIRouter()

@router.post("")
def stream_questions(req: InterviewRequest, user=Depends(verify_token)):
    interview = create_interview(user["user_id"], req.jd)
    return StreamingResponse(
        stream_generate_questions(req.jd, interview.id),
        media_type="text/plain"
    )