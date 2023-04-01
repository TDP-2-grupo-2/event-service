from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import event_repository
from event_service.databases.schema import Event

from event_service.databases.events_database import get_mongo_db
from event_service.exceptions import exceptions


event_router = APIRouter()



@event_router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(event: Event, db=Depends(get_mongo_db)):
    try:
       
        created_event = event_repository.createEvent(event, db)
        return {"message": created_event}
    except  (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)