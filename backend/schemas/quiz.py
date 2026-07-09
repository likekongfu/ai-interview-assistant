from typing import Literal

from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    """选择题生成请求参数。"""

    topic: str = Field(min_length=1, max_length=50)
    count: int = Field(default=5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    jd: str = Field(default="", max_length=3000)
    question_index: int = Field(default=1, ge=1, le=10)
    total_count: int | None = Field(default=None, ge=1, le=10)
    exclude_stems: list[str] = Field(default_factory=list, max_length=20)


class QuizOption(BaseModel):
    """单选题选项。"""

    key: Literal["A", "B", "C", "D"]
    text: str = Field(min_length=1)


class QuizQuestion(BaseModel):
    """单道 AI 应用开发选择题。"""

    id: str
    stem: str = Field(min_length=1)
    options: list[QuizOption]
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str = Field(min_length=1)
    knowledge_point: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]


class QuizGenerateResponse(BaseModel):
    """选择题生成响应。"""

    questions: list[QuizQuestion]

