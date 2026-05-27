from fastapi import FastAPI
from langchain_ollama import OllamaLLM,ChatOllama
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json,re
import jwt
import datetime
import pymysql
from database import SessionLocal
from models import Interview, InterviewAnswer
from auth import verify_token
from fastapi import Depends
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model=OllamaLLM(model='qwen2.5:7b')
class InterviewRequest(BaseModel):
    jd:str

class EvaluateRequest(BaseModel):
    interview_id:int
    question:str
    answer:str


"""生成问题"""
@app.post('/generate_questions')
def generate_questions(req:InterviewRequest,user = Depends(verify_token)):
    prompt=f"""
你是资深技术面试官。

根据以下JD生成5个技术面试问题。

严格返回JSON数组。
不要返回markdown。
不要返回解释。

格式如下：

[
  {{
    "question":"问题内容",
    "type":"专业知识"
  }}
]

JD:


JD:{req.jd}

    """
    response=model.invoke(prompt)
    question=json.loads(response)
    print(question)
    # 保存面试记录
    db = SessionLocal()

    interview = Interview(
        jd=req.jd,
        user_id=user['user_id']
    )

    db.add(interview)

    db.commit()

    db.refresh(interview)

    db.close()
    return {"interview_id": interview.id,'question':question}




"""评估回答"""
@app.post('/evaluate_answer')
def evaluate_answer(req:EvaluateRequest,user = Depends(verify_token)):
    """过滤无效回答"""
    invalid_answers = [
    "1",
    "2",
    "3",
    "不会",
    "不知道",
    "不懂",
    "无"
]
    if len(req.answer.strip()) < 10 or req.answer.strip() in invalid_answers or re.fullmatch(r"\d+", req.answer):
        result={
            "technical_score": 20,
            "logic_score": 20,
            "experience_score": 20,
            "communication_score": 20,
            "overall_score": 20,
            "feedback": "回答过短或无意义，请详细作答。"
        }
    else:
        prompt = f"""
你是一名严格的大厂面试官。
请根据下面的面试题和候选人的回答进行评分。
【面试题】
{req.question}
候选人回答】
{req.answer}
评分规则：
1. 如果回答出现以下情况：
- 少于10个字
- 纯数字
- 乱码
- 无意义内容
- 与问题无关
- “不知道”
- “不会”
- “1”
- “2”
- 随机字符
则必须判定为低质量回答。
此时直接返回：
{{
  "technical_score": 20,
  "logic_score": 20,
  "experience_score": 20,
  "communication_score": 20,
  "overall_score": 20,
  "feedback": "回答无意义或过短，请认真作答。"
}}
2. 如果回答正常：
请从以下维度评分：
1. technical_score（技术能力）
2. logic_score（逻辑表达）
3. engineering_score（工程经验）
4. communication_score（沟通表达）
5. overall_score（综合评分）
进行严格评分。
注意：
不要因为回答里出现技术名词就给高分。
必须真正解释原理、细节、场景。
评分标准：
- 90以上：高级工程师水平
- 80-89：中高级
- 70-79：合格
- 60-69：基础薄弱
- 60以下：回答错误或明显不会
如果回答过短、无意义、错误：
必须低于40分。
如果回答只有一句话，
或者没有技术细节，
综合分不得高于50。
返回格式：
[
  {{
    "technical_score":90,
    "logic_score":80,
    "experience_score":70,
    "communication_score":85,
    "overall_score":82,
    "feedback":"回答不错"
  }}
]
严格返回JSON数组。
不要markdown。
不要解释。
"""
    
        response = json.loads(model.invoke(prompt))
        print(response)
        result = response[0]
    # 保存数据库
    db = SessionLocal()


    answer_record = InterviewAnswer(
        

        interview_id=req.interview_id,

        question=req.question,

        answer=req.answer,

        technical_score=result["technical_score"],

        logic_score=result["logic_score"],

        experience_score=result["experience_score"],

        communication_score=result["communication_score"],

        overall_score=result["overall_score"],

        feedback=result["feedback"]
    )

    db.add(answer_record)

    db.commit()

    db.close()
     
    return {"result": result}


"""历史记录"""
@app.get("/history")
def get_history(user = Depends(verify_token)):

    db = SessionLocal()
    
    user_id = user['user_id']

    interviews = db.query(Interview).filter(
        Interview.user_id == user_id
        ).all()

    result = []

    for item in interviews:
        answers=db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_id==item.id
        ).all()
        overall_score=0
        feedback='暂无评价'
        if answers:
            overall_score=answers[0].overall_score
            feedback=answers[0].feedback
        result.append({
            "id": item.id,
            "jd": item.jd,
            "created_at": item.created_at,
            "overall_score":overall_score,
            "feedback":feedback
        })

    return result

"""查询历史记录"""

@app.get("/history/{interview_id}")
def get_interview_detail(interview_id: int,user = Depends(verify_token)):

    db = SessionLocal()

    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.interview_id == interview_id
    ).all()

    result = []

    for item in answers:

        result.append({
            "question": item.question,
            "answer": item.answer,
            "technical_score": item.technical_score,
            "logic_score": item.logic_score,
            "experience_score": item.experience_score,
            "communication_score": item.communication_score,
            "overall_score": item.overall_score,
            "feedback": item.feedback
        })

    return result




"""用户注册"""
@app.post("/register")
def register(data: dict):

    username = data.get("username")
    password = data.get("password")

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="ai_interview"
    )

    cursor = conn.cursor()

    sql = """
    insert into users(username, password)
    values(%s, %s)
    """

    try:

        cursor.execute(sql, (username, password))
        conn.commit()

        return {
            "message": "注册成功"
        }

    except:

        return {
            "message": "用户已存在"
        }
        


SECRET_KEY = "ai_interview"
"""登录"""
@app.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="ai_interview"
    )

    cursor = conn.cursor()

    sql = """
    select * from users
    where username=%s and password=%s
    """

    cursor.execute(sql, (username, password))

    user = cursor.fetchone()

    if not user:

        return {
            "message": "账号或密码错误"
        }

    token = jwt.encode(
        {
            "user_id": user[0],
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "token": token,
        "username":username,
        "user_id":user[0]
    }
