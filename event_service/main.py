import uvicorn
from event_service.app import app
from event_service.databases import users_database, events_database

users_database.init_database()
event_db = events_database.EventDatabase()

# TODO: Disconnect dbs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)