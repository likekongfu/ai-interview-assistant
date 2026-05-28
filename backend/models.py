from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from db.database import Base


# 面试记录表
class Interview(Base):

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    jd = Column(Text)
    
    user_id = Column(Integer)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


# 回答记录表
class InterviewAnswer(Base):

    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)

    interview_id = Column(Integer)

    question = Column(Text)

    answer = Column(Text)

    technical_score = Column(Integer)

    logic_score = Column(Integer)

    experience_score = Column(Integer)

    communication_score = Column(Integer)

    overall_score = Column(Integer)

    feedback = Column(Text)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )