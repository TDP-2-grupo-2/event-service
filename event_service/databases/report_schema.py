from pydantic import BaseModel
import datetime

class EventReport(BaseModel):
    event_id: str
    reason: str