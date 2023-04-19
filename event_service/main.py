import uvicorn
from event_service.app import app
from event_service.databases import events_database, users_database


users_database.init_database()
events_database.init_database()



# TODO: Disconnect dbs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)