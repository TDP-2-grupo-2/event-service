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
        self.detail = "The username/password is incorrect"

class AlreadyFinalizedEvent(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "Este evento ya finalizo"

class UserWrongLoginInformation(UserInfoException):
    def __init__(self):
        self.status_code = 401  # conflic
        self.detail = "The username/password is incorrect"

class UserNotFound(UserInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "The user does not exists"

class UnauthorizeUser(UserInfoException):
    def __init__(self):
        self.status_code = 401
        self.detail = "The user is not authorize"

class InvalidDate(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "the chosen date has passed"

class EventNotFound(EventInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "Este evento no existe"

class EventIsNotActive(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "The event is not active"

class ReservationNotFound(EventInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "There is no reservation associated to this user"

class ReservationAlreadyExists(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Already existing reservation"

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