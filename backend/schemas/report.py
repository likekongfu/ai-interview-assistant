from pydantic import BaseModel


class TopicScore(BaseModel):
    topic: str
    score: int
    comment: str


class InterviewReportResponse(BaseModel):
    interview_id: int
    overall_score: int
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    topic_scores: list[TopicScore]
    improvement_suggestions: list[str]
    study_plan: list[str]


class ReportStatusResponse(BaseModel):
    status: str
    interview_id: int
