from pydantic import BaseModel

class GoogleLogin(BaseModel):
    email: str
    name: str

class adminLogin(BaseModel):
    email: str
    password: str