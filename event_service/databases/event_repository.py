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
            filter={"_id": new_event.inserted_id}, projection={'ownerId':0})
    return json.loads(json_util.dumps(event_created))

def get_draft_events_by_owner(id, db):
    returned_events = db["events_drafts"].find(filter={'ownerId': id}, projection={'ownerId':0})
    events = list(json.loads(json_util.dumps(returned_events)))
    return events

def edit_draft_event_by_id(event_id:str, fields:dict,db):
    
    event = db["events_drafts"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound
    
    updated_event = db["events_drafts"].update_one(
            {"_id": ObjectId(event_id)}, {"$set": fields}
    )

    event_edited = db["events_drafts"].find_one(filter={"_id": ObjectId(event_id)}, projection={'ownerId':0})
    return json.loads(json_util.dumps(event_edited))

def edit_active_event_by_id(event_id:str, fields:dict,db):
    
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound
    
    updated_event = db["events"].update_one(
            {"_id": ObjectId(event_id)}, {"$set": fields}
    )

    event_edited = db["events"].find_one(filter={"_id": ObjectId(event_id)}, projection={'ownerId':0})
    return json.loads(json_util.dumps(event_edited))

def get_draft_event_by_id(event_id, db):
    event = db["events_drafts"].find_one(filter={"_id": ObjectId(event_id)}, projection={'ownerId':0})
    if event is None:
            raise exceptions.EventNotFound
    return json.loads(json_util.dumps(event))

def remove_draft_event(db, event_id: str):
    db["events_drafts"].delete_one({"_id": ObjectId(event_id)})

def createEvent(owner_id: str, event: dict, db):
    if event.dateEvent < datetime.date.today():
        raise exceptions.InvalidDate()
    event = jsonable_encoder(event)
    tagsToUpper = []
    for t in event['tags']:
        tagsToUpper.append(t.upper())
    event['ownerId'] = owner_id
    event['tags'] = tagsToUpper
    event['eventType'] = event['eventType'].upper()
    event['status'] = "active"
    event['suspendMotive'] = "None"
    new_event = db["events"].insert_one(event)
    event_created = db["events"].find_one(
            filter={"_id": new_event.inserted_id}, projection={'ownerId':0})
    if event['draftId'] is not None:
        remove_draft_event(db, event['draftId'])
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

def set_finished_events(db):
    today = datetime.date.today().isoformat()

    query = {"status": "active", "dateEvent": {"$lt": today}}
    update = {"$set": {"status": "finished"}}

    db["events"].update_many(query, update)

def get_events(db, name: Union[str, None] = None,
                eventType: Union[str, None] = None,
                tags: Union[str, None] = None,
                ownerName: Union[str, None] = None,
                coordinates: Union[str, None] = None,
                distances: Union[str, None] = None):

    set_finished_events(db)

    pipeline = [{"$match": {"status": "active"}}, { "$project" : { "ownerId": 0}}]
    if (name is not None):
        pipeline.append({"$match": {"name": { "$regex": name, "$options":'i'} }})
    if (tags is not None): 
        tagList = tags.split(',')
        pipeline.append({"$match": {"tags": {"$all": tagList}}})
    if (eventType is not None):
        pipeline.append({"$match": {"eventType": { "$regex": eventType, "$options":'i'} }})
    if(ownerName is not None):
        pipeline.append({"$match": {"ownerName": { "$regex": ownerName, "$options":'i'} }})
    
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
         raise exceptions.ReservationNotFound
    return json.loads(json_util.dumps(reservation))


def reserve_event(db, event_id: str, user_id: str):
    event = get_event_by_id(event_id, db)
    #TODO cambiar esto por find por id

    if event['status'] != 'active':
        raise exceptions.EventIsNotActive

    reservation = db["reservations"].find_one({"user_id": user_id, "event_id": event_id})
    if reservation is None:
        db["events"].update_one(
            {"_id": ObjectId(event_id)}, {"$set": {'attendance': event['attendance'] + 1}}
        )

        new_reservation = {
            "user_id": user_id, 
            "event_id": event_id, 
            "status": 'to_be_used', 
            "event_name": event['name'],
            "event_date": event['dateEvent'],
            "event_start_time": event['start'],
        }

        db["reservations"].insert_one(new_reservation)
        reservation = db["reservations"].find_one({"user_id": user_id, "event_id": event_id})
        return json.loads(json_util.dumps(reservation))
    else:
        raise exceptions.ReservationAlreadyExists

def update_event_ticket_status(db, ticket_id: str, status: str):
    db["reservations"].update_one({"_id": ObjectId(ticket_id)}, {"$set": {'status': status}})
    ticket = db["reservations"].find_one({"_id": ObjectId(ticket_id)})
    return json.loads(json_util.dumps(ticket))

def update_event_tickets_status(db, event_id: str, status): 
    db["reservations"].update_many({"event_id": event_id}, {"$set": {'status': status}})
    result=db["reservations"].find_one({"event_id": event_id})

def cancel_event(db, event_id: str, user_id: str):
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound
    
    if event['ownerId'] != user_id:
        raise exceptions.UnauthorizeUser

    event_date = datetime.datetime.strptime(event['dateEvent'], "%Y-%m-%d").date()
    if event_date < datetime.date.today(): 
        update_event_tickets_status(db, event_id, 'finalized')
        raise exceptions.AlreadyFinalizedEvent 
    
    if event['status'] == 'active':
        db["events"].update_one(
                {"_id": ObjectId(event_id)}, {"$set": {'status': 'canceled'}}
        )

    canceled_event = db["events"].find_one({"_id": ObjectId(event_id)})
    update_event_tickets_status(db, event_id, 'canceled')
    return json.loads(json_util.dumps(canceled_event))


def get_events_by_owner_with_status(db, user_id: str, status: str = None):
    set_finished_events(db)
    query = {"ownerId": user_id}
    if status is not None:
        query["status"] = status
    print(query)
    events_by_owner = db['events'].find(query)
    print(events_by_owner)
    return list(json.loads(json_util.dumps(events_by_owner)))


def delete_all_data(db):
    db["reservations"].delete_many({})
    db["events"].delete_many({})
    db["favourites"].delete_many({})
    db["events_drafts"].delete_many({})

def validate_event_ticket(db, user_id: str, event_id: str, ticket_id: str):
         
    event = get_event_by_id(event_id, db)
    if event["ownerId"] != user_id:
         raise exceptions.UnauthorizeUser
             
    event_ticket = db["reservations"].find_one({"event_id": event_id, "_id": ObjectId(ticket_id)})
    if event_ticket is None:
         raise exceptions.TicketIsNotValid
    
    if event['status'] == 'active' and event_ticket['status'] == 'to_be_used':
        return update_event_ticket_status(db, ticket_id, 'used')
        
    elif event['status'] == 'active' and event_ticket['status'] == 'used':  
        # error
        raise exceptions.TicketAlreadyUsed 
    elif event['status'] == 'canceled':
        raise exceptions.EventIsCanceled
    elif event['status'] == 'finished':
        raise exceptions.AlreadyFinalizedEvent
    elif event['status'] == 'suspended':
        raise exceptions.EventIsSuspended

def suspend_event(db, event_id: str, motive: str):
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if event is None:
            raise exceptions.EventNotFound

    event_date = datetime.datetime.strptime(event['dateEvent'], "%Y-%m-%d").date()
    if event_date < datetime.date.today(): 
        update_event_tickets_status(db, event_id, 'finalized')
        raise exceptions.AlreadyFinalizedEvent 
    
    if event['status'] == 'active':
        db["events"].update_one(
                {"_id": ObjectId(event_id)}, {"$set": {'status': 'suspended', 'suspendMotive': motive}}
        )

    suspended_event = db["events"].find_one({"_id": ObjectId(event_id)})
    update_event_tickets_status(db, event_id, 'suspended')
    return json.loads(json_util.dumps(suspended_event))

def get_events_happening_tomorrow(events_db):
    today = datetime.date.today()
    tomorrows_date = (today + datetime.timedelta(days=1)).isoformat()
    tomorrow_events = events_db["reservations"].find(filter={"event_date": tomorrows_date, "status": 'to_be_used'}, projection={'status': 0})
    return list(json.loads(json_util.dumps(tomorrow_events)))


def get_reservations_for_event(db, event_id: str):
    reservation = db["reservations"].find({"event_id": event_id})
    return json.loads(json_util.dumps(reservation))

def get_attendess_by_event_reserved(db, event_id: str):
    
    attendes_ids = []
    reservations = get_reservations_for_event(db, event_id)
    for reservation in reservations:
         print(reservation)
         attendes_ids.append(reservation['user_id'])
    
    return attendes_ids
         

def suspend_organizers_events_and_reservations(db, organizer_id):
    events = get_events_by_owner_with_status(db, organizer_id, "active")
    print("eventos q tengo")
    #print(events)
    reservations = []
    for event in events:
        suspend_event(db, event['_id']["$oid"], "Organizador suspendido")
        reservation = get_reservations_for_event(db,  event['_id']["$oid"])
        for reserv in reservation:
             print(reserv)
             reservations.append(reserv['_id']["$oid"])
       
    return reservations