from fastapi import APIRouter, Depends, HTTPException

from chains.question_chain import question_chain
from db.crud import create_practice
from schemas import InterviewRequest
from services.llm_output_parser import parse_json_response
from utils.auth import verify_token

router = APIRouter()


@router.post("", summary="生成面试题")
def generate_interview_questions(req: InterviewRequest, user=Depends(verify_token)):
    if not req.jd.strip():
        raise HTTPException(status_code=400, detail="请输入题库、题型或技术方向")

    interview = create_practice(user["user_id"], req.jd)
    try:
        questions = parse_json_response(question_chain.invoke(req.jd))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="题目生成失败，请稍后重试") from exc

    return {"interview_id": interview.id, **questions}
