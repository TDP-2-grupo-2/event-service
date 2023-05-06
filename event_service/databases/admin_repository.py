from event_service.exceptions import exceptions


emailAdmin = "admin@gmail.com"
passwordAdmin = "admintdp2"


def login(email:str, password:str):

    if emailAdmin != email or password != passwordAdmin:
        raise exceptions.AdminWrongLoginInformation  
    
    return "Ok"