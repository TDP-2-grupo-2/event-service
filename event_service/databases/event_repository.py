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


def get_events(db, name: Union[str, None] = None, eventType: Union[str, None] = None, tags: Union[str, None] = None):
    pipeline = [{"$match": {}}]
    if (name is not None):
        pipeline.append({"$match": {"name": { "$regex": name, "$options":'i'} }})
    if (tags is not None): 
        tagList = tags.split(',')
        print(tagList)
        pipeline.append({"$match": {"tags": {"$all": tagList}}})
    if (eventType is not None):
        pipeline.append({"$match": {"eventType": { "$regex": eventType, "$options":'i'} }})
    
    events = db["events"].aggregate(pipeline)
    return list(json.loads(json_util.dumps(events)))