from pymongo import MongoClient
import sys
sys.path.append("../")
from event_service.app import app
from event_service.databases import events_database


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


def clear_db_events_collection(db):
    result = db["events"].delete_many({})


def clear_db_favourites_collection(db):
    result = db["favourites"].delete_many({})


