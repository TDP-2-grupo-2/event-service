from event_service.exceptions import exceptions
from event_service.utils import jwt_handler


emailAdmin = "admin@gmail.com"
passwordAdmin = "admintdp2"


def login(email:str, password:str):

    if emailAdmin != email or password != passwordAdmin:
        raise exceptions.AdminWrongLoginInformation  
    
    token = jwt_handler.create_access_token(0, "admin")
    return token