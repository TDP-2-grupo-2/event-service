class EventInfoException(Exception):
    ...


class InvalidDate(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "the chosen date has passed"

class EventNotFound(EventInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "The event does not exists"

class ReservationAlreadyExists(EventInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Already existing reservation"