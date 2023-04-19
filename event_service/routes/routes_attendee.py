from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import attende_repository, users_schema, users_database
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import jwt_handler

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