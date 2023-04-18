from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import event_repository
from event_service.databases.event_schema import Event, EventFilter

from event_service.databases.events_database import get_mongo_db
from event_service.exceptions import exceptions
from typing import Optional, List

event_router = APIRouter()

@event_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event, db=Depends(get_mongo_db)):
    try:
       
        created_event = event_repository.createEvent(event, db)
        return {"message": created_event}
    except  (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)


@event_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_event_by_id(id:str, db=Depends(get_mongo_db)):
    try:
        event = event_repository.get_event_by_id(id, db)
        return {"message": event}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)


@event_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_event_by_id(id:str, db=Depends(get_mongo_db)):
    try:
        event = event_repository.delete_event_with_id(id, db)
        return {"message": "ok"}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)
        

@event_router.get("/", status_code=status.HTTP_200_OK)
async def get_events(event_filter: EventFilter,
                    db=Depends(get_mongo_db)):
    events = event_repository.get_events(db, event_filter)
    return {"message": events}


@event_router.patch("/favourites/{event_id}/user/{user_id}", status_code=status.HTTP_200_OK)
async def toggle_favourite(event_id: str,user_id: str, db=Depends(get_mongo_db)):
    try:
        result = event_repository.toggle_favourite(db, event_id, user_id)
        return {"message": result}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/favourites/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_favourites(user_id: str, db=Depends(get_mongo_db)):
    try: 
        events = event_repository.get_favourites(db, user_id)
        return {"message": events}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.post("/reservations/user/{user_id}/event/{event_id}", status_code=status.HTTP_201_CREATED)
async def reserve_event(event_id: str,user_id: str, db=Depends(get_mongo_db)):
    try:
        result = event_repository.reserve_event(db, event_id, user_id)
        return {"message": result}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/reservations/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_reservations(user_id: str, db=Depends(get_mongo_db)):
    try:
        reservations = event_repository.get_user_reservations(db, user_id)
        return {"message": reservations}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 
            

@event_router.get("/near", status_code=status.HTTP_200_OK)
async def get_near_events(longitude: float, latitude: float, distance: int, db=Depends(get_mongo_db)):
    try:
        near_events = event_repository.get_near_events(db, longitude, latitude, distance)
        return {"message": near_events}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 
            

