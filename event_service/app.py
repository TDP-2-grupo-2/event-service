from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from event_service.routes.routes_events import event_router
from event_service.routes.routes_attendee import attendee_router
from event_service.routes.routes_organizer import organizer_router
from event_service.routes.routes_admin import admin_router
# from .routes import routes_admin, routes_attendee, routes_events, routes_organizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(attendee_router, prefix="/attendees", tags=["Attendees"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(organizer_router, prefix="/organizers", tags=["Organizers"])

@app.get("/")
async def welcome(status_code = status.HTTP_200_OK):
    return "Welcome to event service!!" 