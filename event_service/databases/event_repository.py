import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from event_service.exceptions import exceptions

def createEvent(event: dict, db):
    if event.dateEvent < datetime.date.today():
        raise exceptions.InvalidDate()
    event = jsonable_encoder(event)
    new_event = db["events"].insert_one(event)
    print(new_event)
    event_created = db["events"].find_one(
            {"_id": new_event.inserted_id})
    return json.loads(json_util.dumps(event_created))


def get_event_by_id(id: str, db):
    event = db["events"].find_one({"_id": ObjectId(id)})
    if event is None:
            raise exceptions.EventNotFound
    return json.loads(json_util.dumps(event))


def get_events(db):
    events = db["events"].find()
    return list(json.loads(json_util.dumps(events)))