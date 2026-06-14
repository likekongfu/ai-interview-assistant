from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import Base, engine
import models
from routes import generate, evaluate, history, auth,follow_up,report,upload_resume,start_interview,interview_records

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(generate.router, prefix="/generate_questions")
app.include_router(evaluate.router, prefix="/evaluate_answer")
app.include_router(history.router, prefix="/history")
app.include_router(upload_resume.router,prefix="/upload_resume")
app.include_router(auth.router, prefix="")
app.include_router(follow_up.router,prefix="")
app.include_router(report.router)
app.include_router(start_interview.router,prefix="/interview")
app.include_router(interview_records.router)
