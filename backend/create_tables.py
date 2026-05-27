from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

print("数据表创建成功")