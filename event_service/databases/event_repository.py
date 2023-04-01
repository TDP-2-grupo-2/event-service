import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from event_service.exceptions import exceptions


     
def createEvent(event: dict, db):
    if event.dateEvent < datetime.date.today():
        raise exceptions.InvalidDate()
    event = jsonable_encoder(event)
    new_event = db["events"].insert_one(event)
    event_created = db["events"].find_one(
            {"_id": new_event.inserted_id})
    return json.loads(json_util.dumps(event_created))