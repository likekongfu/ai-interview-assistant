from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    Date,
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
    """刷题练习主表，保存一次刷题任务的 JD/题库描述和所属用户。"""

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    jd = Column(Text)

    user_id = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())


# 面试模式记录
class AIInterviewInfo(Base):
    """AI 面试主表，保存简历驱动面试的状态和归属关系。"""

    __tablename__ = "ai_interview_info"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    status = Column(String(20), nullable=False, default="in_progress")

    created_at = Column(DateTime, server_default=func.now())

    finished_at = Column(DateTime, nullable=True)


# 回答记录表
class InterviewAnswer(Base):
    """刷题模式答题记录表，保存题目、答案、各维度评分和反馈。"""

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
    """AI 面试对话消息表，保存面试官和候选人的聊天内容。"""
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True)

    interview_id = Column(Integer, ForeignKey("ai_interview_info.id"))

    role = Column(String(20))

    content = Column(Text)

    created_at = Column(DateTime, default=func.now())

    topic_id = Column(Integer, ForeignKey("interview_topics.id"), nullable=True)

    def to_dict(self):
        """把消息 ORM 对象转换成普通字典。"""
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "topic_id": self.topic_id,
        }


class Resume(Base):
    """简历表，保存用户上传文件名和解析后的简历文本。"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255))
    resume_text = Column(Text)
    created_at = Column(DateTime, default=func.now())


class User(Base):
    """用户表，保存账号登录和微信小程序用户资料。"""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "wechat_appid",
            "wechat_openid",
            name="uq_users_wechat_identity",
        ),
    )

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=True)
    wechat_appid = Column(String(64), nullable=True)
    wechat_openid = Column(String(128), nullable=True)
    nickname = Column(String(255), nullable=True)
    avatar_url = Column(String(1024), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    answered_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    streak_days = Column(Integer, nullable=False, default=0)
    total_score = Column(Integer, nullable=False, default=0)
    last_practice_date = Column(Date, nullable=True)
    last_login_at = Column(DateTime, nullable=True)


class InterviewTopic(Base):
    """AI 面试 Topic 表，记录每个技术主题的顺序、追问次数和完成状态。"""
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
    """AI 面试报告表，保存结构化报告和 Topic 得分 JSON。"""
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


class QuizQuestion(Base):
    """刷题小程序题库表，只保存可自动判分的选择题。"""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), unique=True, nullable=True)
    category = Column(String(64), nullable=False, index=True)
    stem = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)
    correct_answer = Column(String(8), nullable=False)
    explanation = Column(Text, nullable=False)
    knowledge_point = Column(String(255), nullable=True)
    difficulty = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now())


class PracticeSession(Base):
    """一次固定题序的刷题练习。"""
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    status = Column(String(20), nullable=False, default="in_progress")
    total_questions = Column(Integer, nullable=False, default=0)
    score = Column(Integer, nullable=False, default=0)
    current_index = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class PracticeSessionQuestion(Base):
    """练习内题目顺序表，保证同一轮顺序固定。"""
    __tablename__ = "practice_session_questions"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_practice_session_question"),
        UniqueConstraint("session_id", "question_order", name="uq_practice_session_order"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)


class PracticeAnswer(Base):
    """用户在某轮练习中的答题记录，重复提交不重复加分。"""
    __tablename__ = "practice_answers"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_practice_answer_question"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    user_answer = Column(String(8), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    score = Column(Integer, nullable=False, default=0)
    answered_at = Column(DateTime, server_default=func.now())

