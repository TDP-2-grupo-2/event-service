
from fastapi import APIRouter, Depends, status
from event_service.databases import event_repository
from event_service.databases.schema import Event
from fastapi.encoders import jsonable_encoder
from event_service.databases.events_database import get_mongo_db



event_router = APIRouter()

def convert_datetime(dateEvent):
    return dateEvent.isoformat()


@event_router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(event: Event, db=Depends(get_mongo_db)):
    event_aux = jsonable_encoder(event)
    created_event = event_repository.createEvent(event_aux, db)
    return {"message": created_event}