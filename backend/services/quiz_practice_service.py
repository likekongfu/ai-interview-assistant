import json
import random
from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func

from db.database import SessionLocal
from models import (
    PracticeAnswer,
    PracticeSession,
    PracticeSessionQuestion,
    QuizQuestion,
    User,
)

QUESTION_SCORE = 10


CATEGORY_ALIASES = {
    "python": "Python",
    "database": "MySQL 与 Redis",
    "db": "MySQL 与 Redis",
    "fastapi": "FastAPI 与后端",
    "backend": "FastAPI 与后端",
    "docker": "Docker 与部署",
    "linux": "Linux",
    "ai": "大模型工程化",
    "llm": "大模型工程化",
}


def category_name(category: str) -> str:
    key = (category or "").strip()
    return CATEGORY_ALIASES.get(key.lower(), key)


def category_key(category: str) -> str:
    normalized = category_name(category)
    reverse = {
        "Python": "python",
        "MySQL 与 Redis": "database",
        "FastAPI 与后端": "fastapi",
        "Docker 与部署": "docker",
        "Linux": "linux",
        "大模型工程化": "ai",
    }
    return reverse.get(normalized, normalized.lower())


def parse_options(question: QuizQuestion) -> list[dict]:
    return json.loads(question.options_json)


def public_question(question: QuizQuestion, order: int, total: int) -> dict:
    return {
        "id": question.id,
        "category": question.category,
        "stem": question.stem,
        "options": parse_options(question),
        "difficulty": question.difficulty,
        "order": order,
        "total": total,
    }


def get_dashboard(user_id: int) -> dict:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        answered_count = user.answered_count if user else 0
        correct_count = user.correct_count if user else 0
        total_score = user.total_score if user else 0
        streak_days = user.streak_days if user else 0
        accuracy = int(round(correct_count / answered_count * 100)) if answered_count else 0
        sessions = (
            db.query(PracticeSession)
            .filter(PracticeSession.user_id == user_id)
            .order_by(PracticeSession.started_at.desc(), PracticeSession.id.desc())
            .limit(5)
            .all()
        )
        recent = []
        for session in sessions:
            answered = (
                db.query(func.count(PracticeAnswer.id))
                .filter(PracticeAnswer.session_id == session.id)
                .scalar()
                or 0
            )
            correct = (
                db.query(func.count(PracticeAnswer.id))
                .filter(PracticeAnswer.session_id == session.id, PracticeAnswer.is_correct == True)
                .scalar()
                or 0
            )
            recent.append(
                {
                    "session_id": session.id,
                    "category": session.category,
                    "status": session.status,
                    "total_questions": session.total_questions,
                    "answered_count": answered,
                    "accuracy": int(round(correct / answered * 100)) if answered else 0,
                    "score": session.score,
                    "started_at": session.started_at.isoformat() if session.started_at else "",
                    "completed_at": session.completed_at.isoformat() if session.completed_at else "",
                }
            )
        return {
            "answered_count": answered_count,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "streak_days": streak_days,
            "total_score": total_score,
            "recent_practices": recent,
        }


def get_categories(user_id: int) -> list[dict]:
    with SessionLocal() as db:
        rows = (
            db.query(QuizQuestion.category, func.count(QuizQuestion.id))
            .filter(QuizQuestion.status == "active")
            .group_by(QuizQuestion.category)
            .all()
        )
        categories = []
        for name, total in rows:
            completed = (
                db.query(func.count(func.distinct(PracticeAnswer.question_id)))
                .join(PracticeSession, PracticeSession.id == PracticeAnswer.session_id)
                .join(QuizQuestion, QuizQuestion.id == PracticeAnswer.question_id)
                .filter(PracticeSession.user_id == user_id, QuizQuestion.category == name)
                .scalar()
                or 0
            )
            categories.append(
                {
                    "name": name,
                    "key": category_key(name),
                    "total_count": total,
                    "completed_count": completed,
                    "progress": int(round(completed / total * 100)) if total else 0,
                }
            )
        return categories


def _last_session_question_ids(db, user_id: int, category: str) -> set[int]:
    last_session = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == user_id, PracticeSession.category == category)
        .order_by(PracticeSession.started_at.desc(), PracticeSession.id.desc())
        .first()
    )
    if not last_session:
        return set()
    return {
        row.question_id
        for row in db.query(PracticeSessionQuestion.question_id)
        .filter(PracticeSessionQuestion.session_id == last_session.id)
        .all()
    }


def _pick_questions(db, user_id: int, category: str, count: int) -> list[QuizQuestion]:
    pool = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.category == category, QuizQuestion.status == "active")
        .all()
    )
    if not pool:
        raise HTTPException(status_code=404, detail="该分类暂无题目")

    last_ids = _last_session_question_ids(db, user_id, category)
    preferred = [question for question in pool if question.id not in last_ids]
    fallback = [question for question in pool if question.id in last_ids]
    random.shuffle(preferred)
    random.shuffle(fallback)
    return (preferred + fallback)[: min(count, len(pool))]


def create_practice_session(user_id: int, category: str, count: int) -> dict:
    normalized_category = category_name(category)
    with SessionLocal() as db:
        questions = _pick_questions(db, user_id, normalized_category, count)
        session = PracticeSession(
            user_id=user_id,
            category=normalized_category,
            status="in_progress",
            total_questions=len(questions),
            score=0,
            current_index=0,
        )
        db.add(session)
        db.flush()
        for index, question in enumerate(questions):
            db.add(
                PracticeSessionQuestion(
                    session_id=session.id,
                    question_id=question.id,
                    question_order=index,
                )
            )
        db.commit()
        first = questions[0]
        return {
            "session_id": session.id,
            "total_questions": len(questions),
            "question": public_question(first, 1, len(questions)),
        }


def _get_session(db, user_id: int, session_id: int) -> PracticeSession:
    session = (
        db.query(PracticeSession)
        .filter(PracticeSession.id == session_id, PracticeSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="练习不存在")
    return session


def _question_at_current(db, session: PracticeSession):
    row = (
        db.query(PracticeSessionQuestion, QuizQuestion)
        .join(QuizQuestion, QuizQuestion.id == PracticeSessionQuestion.question_id)
        .filter(
            PracticeSessionQuestion.session_id == session.id,
            PracticeSessionQuestion.question_order == session.current_index,
        )
        .first()
    )
    if not row:
        return None
    session_question, question = row
    return public_question(question, session_question.question_order + 1, session.total_questions)


def get_current_question(user_id: int, session_id: int) -> dict:
    with SessionLocal() as db:
        session = _get_session(db, user_id, session_id)
        question = _question_at_current(db, session)
        if not question:
            raise HTTPException(status_code=404, detail="当前题目不存在")
        return question


def submit_answer(user_id: int, session_id: int, question_id: int, answer: str) -> dict:
    with SessionLocal() as db:
        session = _get_session(db, user_id, session_id)
        row = (
            db.query(PracticeSessionQuestion, QuizQuestion)
            .join(QuizQuestion, QuizQuestion.id == PracticeSessionQuestion.question_id)
            .filter(
                PracticeSessionQuestion.session_id == session.id,
                PracticeSessionQuestion.question_id == question_id,
            )
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="题目不属于当前练习")
        _, question = row
        existing = (
            db.query(PracticeAnswer)
            .filter(PracticeAnswer.session_id == session.id, PracticeAnswer.question_id == question.id)
            .first()
        )
        if existing:
            return {
                "question_id": question.id,
                "is_correct": existing.is_correct,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "tags": [question.knowledge_point] if question.knowledge_point else [],
                "score_added": 0,
                "already_answered": True,
            }

        is_correct = answer == question.correct_answer
        score = QUESTION_SCORE if is_correct else 0
        db.add(
            PracticeAnswer(
                session_id=session.id,
                question_id=question.id,
                user_answer=answer,
                is_correct=is_correct,
                score=score,
            )
        )
        session.score += score
        db.commit()
        return {
            "question_id": question.id,
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "tags": [question.knowledge_point] if question.knowledge_point else [],
            "score_added": score,
            "already_answered": False,
        }


def _finish_session_if_needed(db, session: PracticeSession):
    if session.status == "completed":
        return
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    answered = (
        db.query(func.count(PracticeAnswer.id))
        .filter(PracticeAnswer.session_id == session.id)
        .scalar()
        or 0
    )
    correct = (
        db.query(func.count(PracticeAnswer.id))
        .filter(PracticeAnswer.session_id == session.id, PracticeAnswer.is_correct == True)
        .scalar()
        or 0
    )
    user = db.query(User).filter(User.id == session.user_id).first()
    if user:
        today = date.today()
        previous_date = user.last_practice_date
        user.answered_count = (user.answered_count or 0) + answered
        user.correct_count = (user.correct_count or 0) + correct
        user.total_score = (user.total_score or 0) + (session.score or 0)
        if previous_date == today:
            user.streak_days = user.streak_days or 1
        elif previous_date == today - timedelta(days=1):
            user.streak_days = (user.streak_days or 0) + 1
        else:
            user.streak_days = 1
        user.last_practice_date = today


def next_question(user_id: int, session_id: int) -> dict:
    with SessionLocal() as db:
        session = _get_session(db, user_id, session_id)
        if session.current_index < session.total_questions - 1:
            session.current_index += 1
            db.commit()
            question = _question_at_current(db, session)
            return {"session_id": session.id, "completed": False, "question": question}

        _finish_session_if_needed(db, session)
        db.commit()
        return {"session_id": session.id, "completed": True, "question": None}


def get_result(user_id: int, session_id: int) -> dict:
    with SessionLocal() as db:
        session = _get_session(db, user_id, session_id)
        answers = (
            db.query(PracticeAnswer, QuizQuestion, PracticeSessionQuestion)
            .join(QuizQuestion, QuizQuestion.id == PracticeAnswer.question_id)
            .join(
                PracticeSessionQuestion,
                (PracticeSessionQuestion.session_id == PracticeAnswer.session_id)
                & (PracticeSessionQuestion.question_id == PracticeAnswer.question_id),
            )
            .filter(PracticeAnswer.session_id == session.id)
            .order_by(PracticeSessionQuestion.question_order.asc())
            .all()
        )
        answered = len(answers)
        correct = sum(1 for answer, _, _ in answers if answer.is_correct)
        if answered >= session.total_questions:
            _finish_session_if_needed(db, session)
            db.commit()
        details = [
            {
                "question_id": question.id,
                "order": session_question.question_order + 1,
                "stem": question.stem,
                "user_answer": answer.user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": answer.is_correct,
                "score": answer.score,
                "explanation": question.explanation,
                "tags": [question.knowledge_point] if question.knowledge_point else [],
            }
            for answer, question, session_question in answers
        ]
        return {
            "session_id": session.id,
            "total_questions": session.total_questions,
            "answered_count": answered,
            "correct_count": correct,
            "wrong_count": answered - correct,
            "accuracy": int(round(correct / answered * 100)) if answered else 0,
            "score": session.score,
            "details": details,
        }
