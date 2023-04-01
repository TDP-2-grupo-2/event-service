import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
import json
from bson import json_util
from bson.objectid import ObjectId

load_dotenv(find_dotenv())

class EventDatabase:
    def __init__(self):
        MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
        MONGO_INITDB_ROOT_PASSOWRD = os.getenv('MONGO_INITDB_ROOT_PASSOWRD')
        self.client = MongoClient(f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSOWRD}@mongo:27017/event_db')
        self.db = self.client.event_db
        self.event_collection = self.event_db.event_collection

    def get_events(self):
        return self.event_collection.find()
