class EventInfoException(Exception):
    ...

class UserInfoException(Exception):
    ...

class AdminInfoException(Exception):
    ...

class ReportsInfoException(Exception):
    ...

class AdminWrongLoginInformation(AdminInfoException):
     def __init__(self):
        self.status_code = 401  # conflic
        self.detail = "El usuario/contraseña es incorrecta"



class AlreadyFinalizedEvent(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "Este evento ya finalizo"

class UserIsBlock(UserInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "Usted ha sido bloqueado, sus eventos activos han sido cancelados. Por favor contactese al mail admin@gmail.com"

class UserWrongLoginInformation(UserInfoException):
    def __init__(self):
        self.status_code = 401  # conflic
        self.detail = "El usuario/contraseña es incorrecta"

class UserNotFound(UserInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "El usuario no existe"

class UnauthorizeUser(UserInfoException):
    def __init__(self):
        self.status_code = 401
        self.detail = "El usuario no esta autorizado"

class InvalidDate(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "La fecha elegida ha pasado"

class EventNotFound(EventInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "Este evento no existe"

class EventIsNotActive(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "El evento no esta activo"

class ReservationNotFound(EventInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "No existe reservacion asociada con este usuario"

class ReservationAlreadyExists(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Ya existe una reservacion"

class TicketIsNotValid(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Este ticket no pertenece a este evento"

class TicketAlreadyUsed(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Este ticket ya fue utilizado"

class EventIsSuspended(EventInfoException): 
    def __init__(self):
        self.status_code = 409
        self.detail = "Este evento fue suspendido"

class EventIsCanceled(EventInfoException): 
    def __init__(self):
        self.status_code = 409
        self.detail = "Este evento fue cancelado"

class AlreadyReportedEvent(ReportsInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "Este evento ya fue reportado por este usuario"