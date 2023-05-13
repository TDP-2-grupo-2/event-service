from pydantic import BaseModel
import datetime

class EventReport(BaseModel):
    event_id: str
    event_name: str
    event_description: str
    report_date: datetime.date
    reason: str
    user_name: str
    user_email: str
    organizer_name: str