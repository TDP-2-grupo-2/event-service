from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import event_repository
from event_service.databases.event_schema import Event

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

@event_router.get("/", status_code=status.HTTP_200_OK)
async def get_events(name: Optional[str] = None, taglist: Optional[str] = None, db=Depends(get_mongo_db)):
    events = event_repository.get_events(db, name, taglist)
    return {"message": events}