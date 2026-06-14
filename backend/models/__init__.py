from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    DateTime,
    String,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from db.database import Base


# 刷题模式的记录表
class Interview(Base):

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    jd = Column(Text)

    user_id = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())


# 面试模式记录
class AIInterviewInfo(Base):

    __tablename__ = "ai_interview_info"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    status = Column(String(20), nullable=False, default="in_progress")

    created_at = Column(DateTime, server_default=func.now())

    finished_at = Column(DateTime, nullable=True)


# 回答记录表
class InterviewAnswer(Base):

    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)

    interview_id = Column(Integer, ForeignKey("interviews.id"))

    question = Column(Text)

    answer = Column(Text)

    technical_score = Column(Integer)

    logic_score = Column(Integer)

    experience_score = Column(Integer)

    communication_score = Column(Integer)

    overall_score = Column(Integer)

    feedback = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())


# ai面试聊天记录表
class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True)

    interview_id = Column(Integer, ForeignKey("ai_interview_info.id"))

    role = Column(String(20))

    content = Column(Text)

    created_at = Column(DateTime, default=func.now())

    topic_id = Column(Integer, ForeignKey("interview_topics.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "topic_id": self.topic_id,
        }


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255))
    resume_text = Column(Text)
    created_at = Column(DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class InterviewTopic(Base):
    __tablename__ = "interview_topics"

    id = Column(Integer, primary_key=True, index=True)

    # 所属面试
    interview_id = Column(Integer, ForeignKey("ai_interview_info.id"), nullable=False)

    # 技术主题
    topic = Column(String(255), nullable=False)

    # 顺序
    topic_order = Column(Integer, nullable=False)

    # 已追问次数
    follow_up_count = Column(Integer, default=0)

    # 是否完成
    finished = Column(Boolean, default=False)

    # 创建时间
    created_at = Column(TIMESTAMP, server_default=func.now())


class InterviewReport(Base):
    __tablename__ = "interview_reports"
    __table_args__ = (UniqueConstraint("interview_id", name="uq_interview_reports_interview_id"),)

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("ai_interview_info.id"), nullable=False)
    overall_score = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    topic_scores_json = Column(Text, nullable=False)
    improvement_suggestions = Column(Text, nullable=False)
    study_plan = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
