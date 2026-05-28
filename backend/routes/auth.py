from fastapi import APIRouter
import jwt, datetime, pymysql
from core.config import SECRET_KEY
router = APIRouter()


@router.post("/register")
def register(data: dict):
    username = data.get("username")
    password = data.get("password")
    conn = pymysql.connect(
        host="localhost", user="root", password="123456", database="ai_interview"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "insert into users(username,password) values(%s,%s)", (username, password)
        )
        conn.commit()
        return {"message": "注册成功"}
    except:
        return {"message": "用户已存在"}


@router.post("/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    conn = pymysql.connect(
        host="localhost", user="root", password="123456", database="ai_interview"
    )
    cursor = conn.cursor()
    cursor.execute(
        "select * from users where username=%s and password=%s", (username, password)
    )
    user = cursor.fetchone()
    if not user:
        return {"message": "账号或密码错误"}
    token = jwt.encode(
        {
            "user_id": user[0],
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    return {"token": token, "username": username, "user_id": user[0]}
