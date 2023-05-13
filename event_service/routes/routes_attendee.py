from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request, status
from event_service.databases import attende_repository, event_repository, events_database, reports_database, reports_repository, users_schema, users_database
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import authentification_handler, jwt_handler
from event_service.databases.report_schema import EventReport


attendee_router = APIRouter()

@attendee_router.post("/loginGoogle", status_code=status.HTTP_200_OK)
async def login_google(
    googleUser: users_schema.GoogleLogin,
    db: Session = Depends(users_database.get_postg_db),
):
    try:
        user_created = attende_repository.login_google(
            googleUser.email,
            googleUser.name,
            db,
        )
        token = jwt_handler.create_access_token(user_created.id, "attendee")
        return token
    except exceptions.UserInfoException as error:
        raise HTTPException(**error.__dict__)
    
@attendee_router.post('/report/event', status_code=status.HTTP_201_CREATED)
async def report_event(event_report: EventReport, rq:Request, reports_db: Session= Depends(reports_database.get_reports_db), events_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        user_id = jwt_handler.decode_token(token)["id"]
        report_event = reports_repository.report_event(user_id, jsonable_encoder(event_report), reports_db, events_db)
        return {"message": report_event}
    except (exceptions.UserInfoException, exceptions.EventInfoException, exceptions.ReportsInfoException) as error:
        raise HTTPException(**error.__dict__)
    