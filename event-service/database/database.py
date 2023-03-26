import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import find_dotenv, load_dotenv

from model import Base
load_dotenv(find_dotenv())


def init_database():
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    db_url =  f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:{POSTGRES_PORT}/event_services_db"
    engine = create_engine(db_url, echo=True)
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    print(db)
    try:
        yield db
    finally:
        db.close()