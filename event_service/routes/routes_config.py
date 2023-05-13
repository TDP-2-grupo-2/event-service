from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import attende_repository, event_repository, users_schema, users_database
from event_service.databases.events_database import get_mongo_db
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import jwt_handler

config_router = APIRouter()

@config_router.delete("/databases/events", status_code=status.HTTP_200_OK)
async def delete_events(events_db=Depends(get_mongo_db)):
    event_repository.delete_all_data(events_db)

@config_router.delete("/databases/users", status_code=status.HTTP_200_OK)
async def delete_attendees():
    users_database.delete_all_data()