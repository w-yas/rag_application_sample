import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "database")


def get_db_config():
    return {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
    }


_db = get_db_config()
DATABASE_URL = f"""
    postgresql://{_db['DB_USER']}:{_db['DB_PASSWORD']}@{_db['DB_HOST']}:{_db['DB_PORT']}/{_db['DB_NAME']}
    """

Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
