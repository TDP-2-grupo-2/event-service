class EventInfoException(Exception):
    ...


class InvalidDate(EventInfoException):
    def __init__(self):
        self.status_code = 409  # conflic
        self.detail = "the chosen date has passed"