from event_service.databases.event_database import EventDatabase

class EventRepository:
    def __init__(self, event_database):
        self.database = event_database