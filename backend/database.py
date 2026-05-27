from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:123456@localhost/ai_interview"
pool_size=10
max_overflow=20
pool_timeout=60
pool_recycle=300

engine = create_engine(
    DATABASE_URL,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_timeout=pool_timeout,
    pool_recycle=pool_recycle
                       )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)