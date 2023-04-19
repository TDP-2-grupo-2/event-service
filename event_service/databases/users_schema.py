from pydantic import BaseModel

class GoogleLogin(BaseModel):
    email: str
    name: str