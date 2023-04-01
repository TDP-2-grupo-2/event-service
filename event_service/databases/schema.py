from typing import List, Optional, Union
from pydantic import BaseModel
from datetime import date, datetime

class Event(BaseModel):
    key: Optional[str]
    name: str
    owner: str
    description: str
    location: str
    capacity: Optional[int] = None # no se si si es obligaotiro o puede no haber cupos por evento
    date: datetime = None 
    photos: Union[List[str], None] = None
    attendance: Optional[int] = 0
    tags: List[str]
    latitud: float
    longitud: float
   