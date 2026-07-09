from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.database import Base, engine
import models
from routes import generate, evaluate, history, auth,follow_up,report,upload_resume,start_interview,interview_records, users
# quiz 路由已停用（改用本地固定题库），代码保留备用
# from routes import quiz

app = FastAPI()

# 启动时根据 SQLAlchemy Model 自动建表。
# 当前项目适合本地和作品集演示，生产环境建议改用 Alembic 管理迁移。
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各业务模块路由。
app.include_router(generate.router, prefix="/generate_questions")
app.include_router(evaluate.router, prefix="/evaluate_answer")
app.include_router(history.router, prefix="/history")
app.include_router(upload_resume.router,prefix="/upload_resume")
app.include_router(auth.router, prefix="")
app.include_router(users.router)
app.include_router(follow_up.router,prefix="")
app.include_router(report.router)
app.include_router(start_interview.router,prefix="/interview")
app.include_router(interview_records.router)
# quiz 路由已停用（改用本地固定题库），代码保留备用
# app.include_router(quiz.router, prefix="/quiz")
# app.include_router(quiz.router, prefix="/api/quiz")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
