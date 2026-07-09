from contextlib import contextmanager
from datetime import datetime

from db.database import SessionLocal
from models import (
    AIInterviewInfo,
    Interview,
    InterviewAnswer,
    InterviewMessage,
    InterviewReport,
    InterviewTopic,
    Resume,
    User,
)


@contextmanager
def session_scope(commit: bool = False):
    """统一管理数据库 Session，支持自动提交、回滚和关闭连接。"""
    db = SessionLocal()
    try:
        yield db
        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _create_record(record):
    """通用新增记录方法：添加、提交并刷新 ORM 对象。"""
    with session_scope() as db:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


def create_practice(user_id: int, jd: str):
    """创建刷题模式的一次练习记录。"""
    return _create_record(Interview(jd=jd, user_id=user_id))


def get_practice_by_id(interview_id: int):
    """按 ID 查询刷题练习记录。"""
    with session_scope() as db:
        return db.query(Interview).filter(Interview.id == interview_id).first()


def create_interview(user_id: int, resume_id: int):
    """创建 AI 面试记录，关联用户和简历。"""
    return _create_record(AIInterviewInfo(user_id=user_id, resume_id=resume_id))


def get_ai_interview_by_id(interview_id: int):
    """按 ID 查询 AI 面试记录。"""
    with session_scope() as db:
        return (
            db.query(AIInterviewInfo)
            .filter(AIInterviewInfo.id == interview_id)
            .first()
        )


def finish_ai_interview(interview_id: int):
    """标记 AI 面试已结束，并写入结束时间。"""
    with session_scope(commit=True) as db:
        interview = (
            db.query(AIInterviewInfo)
            .filter(AIInterviewInfo.id == interview_id)
            .first()
        )
        if interview:
            interview.status = "finished"
            interview.finished_at = datetime.now()


def save_answer(interview_id: int, question: str, answer: str, scores: dict):
    """保存刷题模式下某道题的回答和评分结果。"""
    return _create_record(
        InterviewAnswer(
            interview_id=interview_id,
            question=question,
            answer=answer,
            technical_score=scores["technical_score"],
            logic_score=scores["logic_score"],
            experience_score=scores["experience_score"],
            communication_score=scores["communication_score"],
            overall_score=scores["overall_score"],
            feedback=scores["feedback"],
        )
    )


def get_interview_context(interview_id: int):
    """查询刷题模式下某次练习的全部回答记录。"""
    with session_scope() as db:
        return (
            db.query(InterviewAnswer)
            .filter(InterviewAnswer.interview_id == interview_id)
            .all()
        )


def finish_interview(interview_id: int):
    """标记刷题练习已结束。"""
    with session_scope(commit=True) as db:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            interview.status = "finished"
            interview.finished_at = datetime.now()


def create_message(interview_id: int, role: str, content: str, topic_id: int):
    """保存 AI 面试中的一条对话消息。"""
    return _create_record(
        InterviewMessage(
            interview_id=interview_id,
            role=role,
            content=content,
            topic_id=topic_id,
        )
    )


def get_current_topic(interview_id: int):
    """查询当前 AI 面试中第一个未完成的 Topic。"""
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(
                InterviewTopic.interview_id == interview_id,
                InterviewTopic.finished == False,
            )
            .order_by(InterviewTopic.topic_order.asc())
            .first()
        )


def get_next_topic(interview_id: int, current_order: int):
    """根据当前 Topic 顺序查询下一个 Topic。"""
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(
                InterviewTopic.interview_id == interview_id,
                InterviewTopic.topic_order > current_order,
            )
            .order_by(InterviewTopic.topic_order.asc())
            .first()
        )


def update_follow_up_count(topic_id: int, count: int):
    """更新某个 Topic 的追问次数。"""
    with session_scope(commit=True) as db:
        topic = db.query(InterviewTopic).filter(InterviewTopic.id == topic_id).first()
        if topic:
            topic.follow_up_count = count


def finish_topic(topic_id: int):
    """标记某个 Topic 已完成。"""
    with session_scope(commit=True) as db:
        topic = db.query(InterviewTopic).filter(InterviewTopic.id == topic_id).first()
        if topic:
            topic.finished = True


def save_resume(user_id: int, file_name: str, resume_text: str):
    """保存用户上传简历解析后的文本。"""
    return _create_record(
        Resume(user_id=user_id, file_name=file_name, resume_text=resume_text)
    )


def get_resume_by_id(resume_id: int) -> Resume:
    """按 ID 查询简历记录。"""
    with session_scope() as db:
        return db.query(Resume).filter(Resume.id == resume_id).first()


def get_messages_by_topic(interview_id: int, topic_id: int):
    """查询某场 AI 面试中某个 Topic 下的全部消息。"""
    with session_scope() as db:
        return (
            db.query(InterviewMessage)
            .filter(
                InterviewMessage.interview_id == interview_id,
                InterviewMessage.topic_id == topic_id,
            )
            .order_by(InterviewMessage.id.asc())
            .all()
        )


def get_messages_by_interview(interview_id: int):
    """查询某场 AI 面试的完整对话消息。"""
    with session_scope() as db:
        return (
            db.query(InterviewMessage)
            .filter(InterviewMessage.interview_id == interview_id)
            .order_by(InterviewMessage.id.asc())
            .all()
        )


def get_topics_by_interview(interview_id: int):
    """查询某场 AI 面试的全部 Topic。"""
    with session_scope() as db:
        return (
            db.query(InterviewTopic)
            .filter(InterviewTopic.interview_id == interview_id)
            .order_by(InterviewTopic.topic_order.asc())
            .all()
        )


def get_report_by_interview_id(interview_id: int):
    """查询某场 AI 面试已经生成的报告。"""
    with session_scope() as db:
        return (
            db.query(InterviewReport)
            .filter(InterviewReport.interview_id == interview_id)
            .first()
        )


def save_interview_report(
    interview_id: int,
    overall_score: int,
    summary: str,
    strengths: str,
    weaknesses: str,
    topic_scores_json: str,
    improvement_suggestions: str,
    study_plan: str,
):
    """新增或更新某场 AI 面试的结构化报告。"""
    with session_scope(commit=True) as db:
        report = (
            db.query(InterviewReport)
            .filter(InterviewReport.interview_id == interview_id)
            .first()
        )
        if not report:
            report = InterviewReport(interview_id=interview_id)
            db.add(report)

        report.overall_score = overall_score
        report.summary = summary
        report.strengths = strengths
        report.weaknesses = weaknesses
        report.topic_scores_json = topic_scores_json
        report.improvement_suggestions = improvement_suggestions
        report.study_plan = study_plan
        report.updated_at = datetime.now()
        db.flush()
        db.refresh(report)
        return report


def save_topics(interview_id: int, topic: str, topic_order: int):
    """保存 AI 面试中的一个 Topic。"""
    return _create_record(
        InterviewTopic(
            interview_id=interview_id,
            topic=topic,
            topic_order=topic_order,
        )
    )


def get_user_by_username(username: str):
    """根据用户名查询用户。"""
    with session_scope() as db:
        return db.query(User).filter(User.username == username).first()


def get_user_by_id(user_id: int):
    """根据用户 ID 查询用户。"""
    with session_scope() as db:
        return db.query(User).filter(User.id == user_id).first()


def get_user_by_wechat_openid(openid: str):
    """根据微信 openid 查询用户。兼容旧调用，默认不区分 appid。"""
    with session_scope() as db:
        return db.query(User).filter(User.wechat_openid == openid).first()


def get_user_by_wechat_identity(appid: str, openid: str):
    """根据微信 appid + openid 查询用户。"""
    with session_scope() as db:
        return (
            db.query(User)
            .filter(User.wechat_appid == appid, User.wechat_openid == openid)
            .first()
        )


def create_user(username: str, password: str):
    """创建用户，密码应传入哈希后的值。"""
    return _create_record(User(username=username, password=password))


def create_wechat_user(openid: str, appid: str = None):
    """创建微信小程序用户。"""
    return _create_record(
        User(
            username=None,
            password=None,
            wechat_appid=appid,
            wechat_openid=openid,
            nickname="微信用户",
            avatar_url="",
            level=1,
            answered_count=0,
            correct_count=0,
            streak_days=0,
            total_score=0,
        )
    )


def update_user_last_login(user_id: int, login_at: datetime):
    """更新用户最近登录时间。"""
    with session_scope(commit=True) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.last_login_at = login_at
        db.flush()
        db.refresh(user)
        return user


def update_user_profile(user_id: int, nickname: str = None, avatar_url: str = None):
    """更新用户资料。"""
    with session_scope(commit=True) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url
        db.flush()
        db.refresh(user)
        return user


def update_user_password(user_id: int, password: str):
    """更新用户密码，密码应传入哈希后的值。"""
    with session_scope(commit=True) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.password = password

