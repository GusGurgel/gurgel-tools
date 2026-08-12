import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()
url = os.getenv("DATABASE_URL")

if url == None:
    raise ValueError("ENV parameter DATABASE_URL is missing.")

engine = create_engine(url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
