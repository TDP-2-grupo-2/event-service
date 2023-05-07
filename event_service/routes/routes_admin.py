from fastapi import APIRouter, Depends, HTTPException, status
from event_service.databases import admin_repository, users_schema
from event_service.exceptions import exceptions


admin_router = APIRouter()

@admin_router.post("/login", status_code=status.HTTP_200_OK)
async def login (adminLogin: users_schema.adminLogin):
   
    try:
        admin = admin_repository.login(adminLogin.email, adminLogin.password)

        return {'message': admin}
    except exceptions.AdminInfoException as error:
        raise HTTPException(**error.__dict__)

