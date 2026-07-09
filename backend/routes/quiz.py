from fastapi import APIRouter

from schemas.quiz import QuizGenerateRequest, QuizGenerateResponse
from services.quiz_service import generate_quiz

router = APIRouter()


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz_questions(req: QuizGenerateRequest):
    """生成 AI 应用开发选择题。"""

    return generate_quiz(req)
