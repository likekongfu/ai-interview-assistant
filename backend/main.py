from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate, evaluate, history, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(generate.router, prefix="/stream_generate_questions")
app.include_router(evaluate.router, prefix="/evaluate_answer")
app.include_router(history.router, prefix="/history")
app.include_router(auth.router, prefix="")