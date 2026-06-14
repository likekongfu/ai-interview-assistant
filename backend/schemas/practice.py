from pydantic import BaseModel


class InterviewRequest(BaseModel):
    jd: str


class EvaluateRequest(BaseModel):
    # 兼容旧前端字段名；这里指向 interviews.id，不是 ai_interview_info.id。
    interview_id: int
    question: str
    answer: str


class EvaluateResult(BaseModel):
    technical_score: int
    logic_score: int
    experience_score: int
    communication_score: int
    overall_score: int
    feedback: str


class EvaluateResponse(BaseModel):
    result: EvaluateResult
