import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from event_service.exceptions import exceptions
from typing import Union, List
from ..utils.distance_calculator import DistanceCalculator



ALPHA = 0.25

distance_calculator = DistanceCalculator()

def save_event_draft(event:dict, id:int, db):
    
    event = jsonable_encoder(event)
    if event['eventType'] is not None :
        event['eventType'] = event['eventType'].upper()
    event['ownerId'] = id
    new_event = db["events_drafts"].insert_one(event)
    event_created = db["events_drafts"].find_one(
            {"_id": new_event.inserted_id})
    return json.loads(json_util.dumps(event_created))


def createEvent(event: dict, owner_id: int, db):
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


def get_events(db, name: Union[str, None] = None,
                eventType: Union[str, None] = None,
                tags: Union[str, None] = None,
                owner: Union[str, None] = None,
                coordinates: Union[str, None] = None,
                distances: Union[str, None] = None):

    pipeline = [{"$match": {}}]
    if (name is not None):
        pipeline.append({"$match": {"name": { "$regex": name, "$options":'i'} }})
    if (tags is not None): 
        tagList = tags.split(',')
        pipeline.append({"$match": {"tags": {"$all": tagList}}})
    if (eventType is not None):
        pipeline.append({"$match": {"eventType": { "$regex": eventType, "$options":'i'} }})
    if(owner is not None):
        pipeline.append({"$match": {"owner": { "$regex": owner, "$options":'i'} }})
    
    events = db["events"].aggregate(pipeline)
    filtered_events = list(json.loads(json_util.dumps(events)))
    if (coordinates is not None and distances is not None):
        coordinates_list = coordinates.split(',')
        distances_list = distances.split(',')
        if (len(distances_list) == 2 and len(coordinates_list) == 2):
            filtered_by_distance_events = []
            for e in filtered_events:
                coords_1 = (e["latitud"], e["longitud"])
                coords_2 = (coordinates_list[0], coordinates_list[1])
                if distance_calculator.coordinates_in_range(coords_1, coords_2, int(distances_list[0]), int(distances_list[1])):
                    filtered_by_distance_events.append(e)
                filtered_events = filtered_by_distance_events

    return filtered_events


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

def is_favourite_event_of_user(db, event_id, user_id):
    
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound
    favourite = db["favourites"].find_one({"user_id": user_id, "event_id": event_id})
    if favourite is None:
            return False
    else:
        return True

        

def get_favourites(db, user_id: str):
    favourites = db["favourites"].find({"user_id": user_id})
    events = []
    for fav in favourites:
        events.append(get_event_by_id(fav["event_id"], db))
    return events 
        
def get_user_reservations(db, user_id: str):
    reservations = db["reservations"].find({"user_id": user_id})
    events = []
    for res in reservations:
        events.append(get_event_by_id(res["event_id"], db))
    return events 


def get_event_reservation(db, user_id: str, event_id: str):
    reservation = db["reservations"].find_one({"user_id": user_id, "event_id": event_id})
    if reservation is None:
         print("reservacion no existe")
         raise exceptions.ReservationNotFound
    return json.loads(json_util.dumps(reservation))



def reserve_event(db, event_id: str, user_id: str):
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound

    reservation = db["reservations"].find_one({"user_id": user_id, "event_id": event_id})
    if reservation is None:
        db["events"].update_one(
            {"_id": ObjectId(event_id)}, {"$set": {'attendance': event['attendance'] + 1}}
        )
        new_reservation = {"user_id": user_id, "event_id": event_id}
        db["reservations"].insert_one(new_reservation)
        reservation = db["reservations"].find_one({"user_id": user_id, "event_id": event_id})
        return json.loads(json_util.dumps(reservation))
    else:
        raise exceptions.ReservationAlreadyExists
