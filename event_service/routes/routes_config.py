from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import attende_repository, event_repository, reports_repository
from event_service.databases.events_database import get_mongo_db
from event_service.databases.reports_database import get_reports_db
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session


config_router = APIRouter()

@config_router.delete("/databases/events", status_code=status.HTTP_200_OK)
async def delete_events(events_db=Depends(get_mongo_db)):
    event_repository.delete_all_data(events_db)

@config_router.delete("/databases/users", status_code=status.HTTP_200_OK)
async def delete_attendees(reports_db: Session = Depends(get_reports_db)):
    reports_repository.delete_all_data(reports_db)

@config_router.delete("/databases/reports",status_code=status.HTTP_200_OK)
async def delete_reports(events_db=Depends(get_mongo_db)):
    event_repository.delete_all_data(events_db)