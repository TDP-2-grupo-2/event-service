import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
import json
from bson import json_util
from bson.objectid import ObjectId

load_dotenv(find_dotenv())

def init_database():
        MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
        MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
        print(MONGO_INITDB_ROOT_PASSWORD)
        print(MONGO_INITDB_ROOT_USERNAME)
        client = MongoClient(f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongo:27017/event_db',authSource="admin")
        global db
        db = client['event_db']
       

def get_mongo_db():
    try:
        yield db
    finally:
        db
