from pydantic import BaseModel


class FollowUpRequest(BaseModel):
    resume_id: int
    answer: str
    interview_id: int


class FollowUpResponse(BaseModel):
    next_question: str | None = None
    topic: str | None = None
    follow_up_count: int | None = None
    finished: bool = False
    message: str | None = None
    action: str | None = None
    score: int | None = None
    reason: str | None = None


class StartInterviewResponse(BaseModel):
    interview_id: int
    first_question: str
