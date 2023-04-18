from pymongo import MongoClient
import sys
sys.path.append("../")
from event_service.app import app
from event_service.databases import events_database, user_model, users_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def init_postg_db(app):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    user_model.Base.metadata.drop_all(engine)
    user_model.Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[users_database.get_postg_db] = override_get_db
    return TestingSessionLocal()



def init_db():
    client = MongoClient( 'mongodb+srv://events:events@eventscluster.hgv9toh.mongodb.net/?retryWrites=true&w=majority', 8000)
    db_test = client['events']
    def override_get_db():
        try:
            db = db_test
            yield db
        finally:
            db

    app.dependency_overrides[events_database.get_mongo_db] = override_get_db
    return db_test


def clear_db_collection(db):
    result = db["events"].delete_many({})