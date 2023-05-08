from typing import List, Optional, Union
from pydantic import BaseModel
import datetime

class Event(BaseModel):
    name: str
    ownerName: str
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
    status: Optional[str] = None
    draftId: Optional[str] = None

class Event_draft(BaseModel):
    name: Optional[str] = None
    ownerName: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    locationDescription: Optional[str] = None
    capacity: Optional[int] = None 
    dateEvent: Optional[datetime.date] = None
    photos: Union[List[str], None] = None
    attendance: Optional[int] = 0
    eventType: Optional[str] = None
    faqs: Optional[List] = None
    agenda: Optional[List] = None
    latitud: Optional[float] = None
    tags: Optional[List[str]] = None
    longitud: Optional[float] = None
    start: Optional[datetime.time] = None
    end:Optional[datetime.time] = None



    

class Coordinates(BaseModel):
    latitude: float
    longitude: float
    min_distance: int
    max_distance: int
