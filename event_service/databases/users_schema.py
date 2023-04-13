from pydantic import BaseModel

class GoogleLogin(BaseModel):
    token: str