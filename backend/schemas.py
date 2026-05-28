from pydantic import BaseModel

class InterviewRequest(BaseModel):
    jd: str

class EvaluateRequest(BaseModel):
    interview_id: int
    question: str
    answer: str