from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import event_repository, attende_repository
from event_service.databases.event_schema import Event, Coordinates
from event_service.utils import jwt_handler
from event_service.databases.events_database import get_mongo_db
from event_service.databases.users_database import get_postg_db
from event_service.exceptions import exceptions
from typing import Optional, List

event_router = APIRouter()

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
async def get_events(name: Optional[str] = None,
                    eventType: Optional[str] = None,
                    taglist: Optional[str] = None,
                    owner: Optional[str] = None,
                    coordinates: Optional[str] = None,
                    distances_range: Optional[str] = None,
                    db=Depends(get_mongo_db)):
    events = event_repository.get_events(db, name, eventType, taglist, owner, coordinates, distances_range)
    return {"message": events}


@event_router.patch("/favourites/{event_id}/user/{token}", status_code=status.HTTP_200_OK)
async def toggle_favourite(event_id: str,token: str, db=Depends(get_mongo_db),  user_db=Depends(get_postg_db)):
    try:
        
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        result = event_repository.toggle_favourite(db, event_id, user_id)
        return {"message": result}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/favourites/{token}", status_code=status.HTTP_200_OK)
async def get_user_favourites(token: str, db=Depends(get_mongo_db), user_db=Depends(get_postg_db)):
    try: 
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        events = event_repository.get_favourites(db, user_id)
        return {"message": events}
    except (exceptions.EventInfoException, exceptions.UserInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.post("/reservations/user/{token}/event/{event_id}", status_code=status.HTTP_201_CREATED)
async def reserve_event(event_id: str,token: str, db=Depends(get_mongo_db), user_db=Depends(get_postg_db)):
    try:
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        result = event_repository.reserve_event(db, event_id, user_id)
        return {"message": result}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/reservations/user/{token}", status_code=status.HTTP_200_OK)
async def get_user_reservations(token: str, db=Depends(get_mongo_db), user_db=Depends(get_postg_db)):
    try:
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        reservations = event_repository.get_user_reservations(db, user_id)
        return {"message": reservations}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/favourites/{event_id}/user/{token}", status_code=status.HTTP_200_OK)
async def is_users_favourite_event(event_id: str,token: str, db=Depends(get_mongo_db), user_db=Depends(get_postg_db)):
    try:
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        result = event_repository.is_favourite_event_of_user(db, event_id, user_id)
        return {"message": result}
    except (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__) 


@event_router.get("/reservations/user/{token}/event/{event_id}", status_code=status.HTTP_200_OK)
async def get_event_reservation_for_user(token: str, event_id: str, db=Depends(get_mongo_db),  user_db=Depends(get_postg_db)):
    try:
        user_id = jwt_handler.decode_token(token)["id"]
        attende_repository.verify_user_exists(user_id, user_db)
        result = event_repository.get_event_reservation(db, user_id, event_id)
        return {"message": result}
    except (exceptions.ReservationNotFound) as error:
        raise HTTPException(**error.__dict__)
    