import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://pkg:pkg@localhost/packages")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
session_local = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()