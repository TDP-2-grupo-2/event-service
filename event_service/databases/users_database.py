import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import find_dotenv, load_dotenv
from event_service.databases.user_model import Base

load_dotenv(find_dotenv())

def init_database():
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')
    db_url =  f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/event_services_db"
    print(db_url)
    engine = create_engine(db_url, echo=True)
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

def get_postg_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()