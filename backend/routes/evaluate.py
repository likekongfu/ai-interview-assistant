from fastapi import APIRouter, Depends
from schemas import EvaluateRequest
from utils.auth import verify_token
from db.crud import save_answer
from services.model_service import evaluate_answer_with_ai

router = APIRouter()

@router.post("")
def evaluate_answer(req: EvaluateRequest, user=Depends(verify_token)):
    result = evaluate_answer_with_ai(req.question, req.answer)
    save_answer(req.interview_id, req.question, req.answer, result)
    return {"result": result}