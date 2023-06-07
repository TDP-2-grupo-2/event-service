import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status

from event_service.databases import admin_repository, event_repository, events_database, reports_database, reports_repository, users_schema, organizer_repository, users_database

from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import jwt_handler, authentification_handler
from event_service.utils.events_statistics_handler import EventsStatisticsHandler

admin_router = APIRouter()
eventStatisticsHandler = EventsStatisticsHandler()

@admin_router.post("/login", status_code=status.HTTP_200_OK)
async def login (adminLogin: users_schema.adminLogin):
   
    try:
        admin = admin_repository.login(adminLogin.email, adminLogin.password)

        return {'message': admin}
    except exceptions.AdminInfoException as error:
        raise HTTPException(**error.__dict__)


@admin_router.patch("/unsuspended_events/{event_id}", status_code=status.HTTP_200_OK)
async def unsuspend_active_event(event_id: str,
                                event_db: Session = Depends(events_database.get_mongo_db)
                                ):
    try:
      
        canceled_event = event_repository.unsuspend_event(event_db, event_id)
        return {"message": canceled_event}

    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)



@admin_router.patch("/suspended_events/{event_id}", status_code=status.HTTP_200_OK)
async def cancel_active_event(rq:Request, event_id: str,
                                motive: str, 
                                event_db: Session = Depends(events_database.get_mongo_db),
                                reports_db: Session = Depends(reports_database.get_reports_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)
        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser
        canceled_event = event_repository.suspend_event(event_db, event_id, motive)
        reports_repository.update_events_status_by_event_id(reports_db, event_id)

        return {"message": canceled_event}

    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)


@admin_router.get("/reports/attendees", status_code=status.HTTP_200_OK)
async def get_reporting_attendees(rq:Request, from_date: datetime.date = None, to_date: datetime.date = None, 
                                  reports_db: Session = Depends(reports_database.get_reports_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)
        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser
        reports_by_attendee = reports_repository.get_reporting_attendees(reports_db, from_date, to_date)
        return {"message": reports_by_attendee}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)

@admin_router.get("/reports/events", status_code=status.HTTP_200_OK)
async def get_reporting_events(rq:Request, from_date: datetime.date = None, to_date: datetime.date = None, 
                               reports_db: Session = Depends(reports_database.get_reports_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)
        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser
        reports_by_attendee = reports_repository.get_reporting_events(reports_db, from_date, to_date)
        
        return {"message": reports_by_attendee}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)

@admin_router.patch("/suspended_organizers/{organizer_id}", status_code=status.HTTP_200_OK)
async def suspend_organizer(rq:Request, organizer_id: int, user_db: Session = Depends(users_database.get_postg_db),
                             event_db: Session = Depends(events_database.get_mongo_db),
                             reports_db: Session = Depends(reports_database.get_reports_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)

        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser
        isBlock = organizer_repository.suspend_organizer(user_db, organizer_id)
        reports_repository.update_events_status_by_organizer(reports_db, organizer_id)
        reservations = event_repository.suspend_organizers_events_and_reservations(event_db, organizer_id)
        return {"message": reservations}
    except (exceptions.UserInfoException) as error:
        raise HTTPException(**error.__dict__)


@admin_router.patch("/unsuspend/{organizer_id}", status_code=status.HTTP_200_OK)
async def unsuspend_organizer(organizer_id: int, user_db: Session = Depends(users_database.get_postg_db)):
    try:
        isBlock = organizer_repository.unsuspend_organizer(user_db, organizer_id)
        return {"message": isBlock}
    except (exceptions.UserInfoException) as error:
        raise HTTPException(**error.__dict__)


@admin_router.get("/statistics/events/status", status_code=status.HTTP_200_OK)
async def get_events_status_statistics(rq:Request, event_db: Session = Depends(events_database.get_mongo_db), 
                                       from_date: datetime.date = None, to_date: datetime.date = None, ):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)

        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser
        
        statistics = eventStatisticsHandler.get_events_status_statistics(event_db, from_date, to_date)

        return {"message": statistics}
    except (exceptions.UserInfoException) as error:
        raise HTTPException(**error.__dict__)
    



@admin_router.get("/statistics/events/registered_entries", status_code=status.HTTP_200_OK)

async def get_events_registered_entries_statistics(rq:Request, event_db: Session = Depends(events_database.get_mongo_db), 
                                       from_date: datetime.date = None, to_date: datetime.date = None, scale_type: str = "months"):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        decoded_token = jwt_handler.decode_token(token)

        if decoded_token["rol"] != 'admin':
            raise exceptions.UnauthorizeUser

        statistics = eventStatisticsHandler.get_registered_entries_amount_per_event(event_db, from_date, to_date, scale_type)

        return {"message": statistics}
    except (exceptions.UserInfoException) as error:
        raise HTTPException(**error.__dict__)
