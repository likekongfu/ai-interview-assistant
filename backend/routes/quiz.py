from fastapi import APIRouter, Depends, HTTPException

from schemas.quiz import (
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeNextResponse,
    PracticeQuestionResponse,
    PracticeResultResponse,
    PracticeSessionCreateRequest,
    PracticeSessionCreateResponse,
    QuizCategoryResponse,
    QuizDashboardResponse,
    QuizGenerateRequest,
    QuizGenerateResponse,
)
from services import quiz_practice_service
from services.quiz_service import generate_quiz
from utils.auth import verify_token

router = APIRouter()


def current_user_id(payload: dict = Depends(verify_token)) -> int:
    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(user_id)


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz_questions(req: QuizGenerateRequest):
    """生成 AI 应用开发选择题。"""

    return generate_quiz(req)


@router.get("/dashboard", response_model=QuizDashboardResponse)
def quiz_dashboard(user_id: int = Depends(current_user_id)):
    """返回当前用户真实刷题统计和最近练习。"""

    return quiz_practice_service.get_dashboard(user_id)


@router.get("/categories", response_model=list[QuizCategoryResponse])
def quiz_categories(user_id: int = Depends(current_user_id)):
    """返回题库分类和当前用户完成进度。"""

    return quiz_practice_service.get_categories(user_id)


@router.post("/practice/sessions", response_model=PracticeSessionCreateResponse)
def create_practice_session(
    req: PracticeSessionCreateRequest,
    user_id: int = Depends(current_user_id),
):
    """随机抽取固定题序，创建一轮刷题练习。"""

    return quiz_practice_service.create_practice_session(user_id, req.category, req.count)


@router.get(
    "/practice/sessions/{session_id}/current",
    response_model=PracticeQuestionResponse,
)
def current_practice_question(session_id: int, user_id: int = Depends(current_user_id)):
    """返回当前题目，不包含答案和解析。"""

    return quiz_practice_service.get_current_question(user_id, session_id)


@router.post(
    "/practice/sessions/{session_id}/answer",
    response_model=PracticeAnswerResponse,
)
def answer_practice_question(
    session_id: int,
    req: PracticeAnswerRequest,
    user_id: int = Depends(current_user_id),
):
    """提交答案后才返回判题结果、正确答案和解析。"""

    return quiz_practice_service.submit_answer(user_id, session_id, req.question_id, req.answer)


@router.post("/practice/sessions/{session_id}/next", response_model=PracticeNextResponse)
def next_practice_question(session_id: int, user_id: int = Depends(current_user_id)):
    """进入下一题；最后一题后完成本轮并结算用户统计。"""

    return quiz_practice_service.next_question(user_id, session_id)


@router.get("/practice/sessions/{session_id}/result", response_model=PracticeResultResponse)
def practice_result(session_id: int, user_id: int = Depends(current_user_id)):
    """返回当前用户本轮练习结果。"""

    return quiz_practice_service.get_result(user_id, session_id)
