from typing import List, Optional, Union
from pydantic import BaseModel
import datetime

class Event(BaseModel):
    name: str
    owner: str
    description: str
    location: str
    locationDescription: str
    capacity: Optional[int] = None # no se si si es obligaotiro o puede no haber cupos por evento
    dateEvent: datetime.date
    photos: Union[List[str], None] = None
    attendance: Optional[int] = 0
    eventType: str
    tags: List[str]
    faqs: Optional[List] = None
    agenda: Optional[List] = None
    latitud: float
    longitud: float
    start: datetime.time
    end:datetime.time
