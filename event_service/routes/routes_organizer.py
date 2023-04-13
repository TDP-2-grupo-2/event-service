from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import organizer_repository, users_schema, users_database
from event_service.exceptions import exceptions
from sqlalchemy.orm import Session
from event_service.utils import firebase_handler, jwt_handler

organizer_router = APIRouter()

@organizer_router.post("/loginGoogle", status_code=status.HTTP_200_OK)
async def login_google(
    googleUser: users_schema.GoogleLogin,
    db: Session = Depends(users_database.get_postg_db),
    firebase = Depends(firebase_handler.get_fb),
):
    try:
        user = firebase.valid_user(googleUser.token)
        email = firebase.get_email(user.get("uid"))

        user_created = organizer_repository.login_google(
            user.get("uid"),
            email,
            user.get("name"),
            user.get("picture"),
            db,
        )
        token = jwt_handler.create_access_token(user_created.id, "organizer")
        return token
    except exceptions.UserInfoException as error:
        raise HTTPException(**error.__dict__)
