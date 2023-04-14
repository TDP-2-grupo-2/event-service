import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from event_service.exceptions import exceptions
from typing import Union, List
import re

def createEvent(event: dict, db):
    if event.dateEvent < datetime.date.today():
        raise exceptions.InvalidDate()
    event = jsonable_encoder(event)
    tagsToUpper = []
    for t in event['tags']:
        tagsToUpper.append(t.upper())
    event['tags'] = tagsToUpper
    event['eventType'] = event['eventType'].upper()
    new_event = db["events"].insert_one(event)
    event_created = db["events"].find_one(
            {"_id": new_event.inserted_id})
    return json.loads(json_util.dumps(event_created))


def get_event_by_id(id: str, db):
    event = db["events"].find_one({"_id": ObjectId(id)})
    if event is None:
            raise exceptions.EventNotFound
    return json.loads(json_util.dumps(event))


def delete_event_with_id(id: str, db):
    deleted_event = db["events"].delete_one(
            {"_id": ObjectId(id)})
    if deleted_event.deleted_count == 0:
            raise exceptions.EventNotFound
    return deleted_event


def get_events(db, name: Union[str, None] = None, eventType: Union[str, None] = None, tags: Union[str, None] = None):
    pipeline = [{"$match": {}}]
    if (name is not None):
        pipeline.append({"$match": {"name": { "$regex": name, "$options":'i'} }})
    if (tags is not None): 
        tagList = tags.split(',')
        pipeline.append({"$match": {"tags": {"$all": tagList}}})
    if (eventType is not None):
        pipeline.append({"$match": {"eventType": { "$regex": eventType, "$options":'i'} }})
    
    events = db["events"].aggregate(pipeline)
    return list(json.loads(json_util.dumps(events)))


def toggle_favourite(db, event_id: str, user_id: str):
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound

    favourite = db["favourites"].find_one({"user_id": user_id, "event_id": event_id})
    if favourite is None:
        new_favourite = {"user_id": user_id, "event_id": event_id}
        db["favourites"].insert_one(new_favourite)
        return "Se agregó como favorito el evento"
    else:
        db["favourites"].delete_one({"user_id": user_id, "event_id": event_id})
        return "Se eliminó como favorito el evento"
        

def get_favourites(db, user_id: str):
    favourites = db["favourites"].find({"user_id": user_id})
    
    events = []
    for fav in favourites:
        events.append(get_event_by_id(fav["event_id"], db))

    return events 
        