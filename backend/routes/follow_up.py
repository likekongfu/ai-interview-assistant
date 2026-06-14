from fastapi import APIRouter, Depends

from schemas import FollowUpRequest, FollowUpResponse
from services.interview_flow_service import handle_follow_up
from utils.auth import verify_token

router = APIRouter()


@router.post("/follow_up", response_model=FollowUpResponse)
def follow_up(req: FollowUpRequest, user=Depends(verify_token)):
    return handle_follow_up(req, user_id=user["user_id"])
