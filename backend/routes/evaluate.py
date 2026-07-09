from fastapi import APIRouter, Depends, HTTPException
from schemas import EvaluateRequest, EvaluateResponse
from utils.auth import verify_token
from db.crud import get_practice_by_id, save_answer
from services.model_service import evaluate_answer_with_ai

router = APIRouter()


@router.post("", response_model=EvaluateResponse)
def evaluate_answer(req: EvaluateRequest, user=Depends(verify_token)):
    """刷题评分接口：提交答案后调用 AI 评分并保存刷题记录。"""
    if not req.answer.strip():
        raise HTTPException(status_code=400, detail="答案不能为空")

    practice = get_practice_by_id(req.interview_id)
    if not practice:
        raise HTTPException(
            status_code=400,
            detail="practice interview_id 不存在，请重新生成刷题题目",
        )
    if practice.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="无权访问该刷题记录")

    try:
        result = evaluate_answer_with_ai(req.question, req.answer)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI评分失败，请稍后重试") from exc

    save_answer(req.interview_id, req.question, req.answer, result)
    return {"result": result}
