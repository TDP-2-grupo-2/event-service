from pydantic import BaseModel
import datetime

class EventReport(BaseModel):
    event_id: str
    report_date: datetime.date
    reason: str