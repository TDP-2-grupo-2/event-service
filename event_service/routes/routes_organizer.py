from fastapi import APIRouter, Depends, HTTPException, status, Request
from event_service.databases import organizer_repository, users_schema, users_database, event_schema, events_database, event_repository
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import jwt_handler, authentification_handler
from fastapi.encoders import jsonable_encoder

organizer_router = APIRouter()

@organizer_router.post("/loginGoogle", status_code=status.HTTP_200_OK)
async def login_google(
    googleUser: users_schema.GoogleLogin,
    db: Session = Depends(users_database.get_postg_db),
):
    try:
        user_created = organizer_repository.login_google(
            googleUser.email,
            googleUser.name,
            db,
        )
        token = jwt_handler.create_access_token(user_created.id, "organizer")
        return token
    except exceptions.UserInfoException as error:
        raise HTTPException(**error.__dict__)

@organizer_router.post("/save_draft", status_code=status.HTTP_200_OK)
async def save_event_draft(rq: Request, event_draft: event_schema.Event_draft,
                            event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        id = jwt_handler.decode_token(token)["id"]
        draft_event_created = event_repository.save_event_draft(event_draft,id, event_db)

        return {"message": draft_event_created}
    except exceptions.UserInfoException as error:
        raise HTTPException(**error.__dict__)

@organizer_router.get("/draft_events", status_code=status.HTTP_200_OK)
async def get_draft_events(rq:Request, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        id = jwt_handler.decode_token(token)["id"]
        draft_events = event_repository.get_draft_events_by_owner(id, event_db)
        return {"message": draft_events}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)


@organizer_router.patch("/draft_events/{event_id}", status_code=status.HTTP_200_OK)
async def edit_draft_event(rq:Request, event_id: str, draftEventEdit : dict, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
 
        authentification_handler.is_auth(rq.headers)
        draft_event = event_repository.edit_draft_event_by_id(event_id, draftEventEdit, event_db)
        return {"message": draft_event}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)