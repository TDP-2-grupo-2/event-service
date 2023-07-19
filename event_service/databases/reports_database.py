import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
import json
from bson import json_util
from bson.objectid import ObjectId

load_dotenv(find_dotenv())

def init_reports_database():
        MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
        MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
        MONGO_DATABASE_NAME = os.getenv('MONGO_REPORTS_INITDB_DATABASE')

        client = MongoClient(f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongo:27017/event_reports',authSource="admin")
        global db
        db = client[MONGO_DATABASE_NAME]
       

def get_reports_db():
    try:
        yield db
    finally:
        db