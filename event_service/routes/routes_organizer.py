from fastapi import APIRouter, Depends, HTTPException, status, Request
from event_service.databases import organizer_repository, users_schema, users_database, event_schema, events_database, event_repository
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import jwt_handler, authentification_handler
from fastapi.encoders import jsonable_encoder
from event_service.databases.event_schema import Event

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

@organizer_router.post("/draft_events", status_code=status.HTTP_200_OK)
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
    
@organizer_router.get("/draft_events/{event_id}", status_code=status.HTTP_200_OK)
async def get_draft_event_by_id(rq:Request, event_id: str, event_db: Session=Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        draft_event = event_repository.get_draft_event_by_id(event_id, event_db)
        return {"message": draft_event}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)

@organizer_router.get("/active_events", status_code=status.HTTP_200_OK)
def get_active_events_by_owner(rq:Request, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        user_id = jwt_handler.decode_token(token)["id"]
        active_events = event_repository.get_events_by_owner_with_status(event_db, user_id, 'active')
        return {"message": active_events}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)
    
@organizer_router.post("/active_events", status_code=status.HTTP_201_CREATED)
async def create_event(rq:Request, event: Event, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        user_id = jwt_handler.decode_token(token)["id"]
        created_event = event_repository.createEvent(user_id, event, event_db)
        return {"message": created_event}
    except  (exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)


@organizer_router.patch("/canceled_events/{event_id}", status_code=status.HTTP_200_OK)
async def cancel_active_event(rq:Request, event_id: str, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        user_id = jwt_handler.decode_token(token)["id"]
        canceled_event = event_repository.cancel_event(event_db, event_id, user_id)
        return {"message": canceled_event}

    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)
    

@organizer_router.get("/canceled_events", status_code=status.HTTP_200_OK)
def get_active_events_by_owner(rq:Request, event_db: Session= Depends(events_database.get_mongo_db)):
    try:
        authentification_handler.is_auth(rq.headers)
        token = authentification_handler.get_token(rq.headers)
        user_id = jwt_handler.decode_token(token)["id"]
        canceled_events = event_repository.get_events_by_owner_with_status(event_db, user_id, 'canceled')
        return {"message": canceled_events}
    except (exceptions.UserInfoException, exceptions.EventInfoException) as error:
        raise HTTPException(**error.__dict__)