from firebase_admin import exceptions as fb_exceptions
from event_service.exceptions import exceptions

class Firebase:
    def __init__(self, auth, app):
        self.auth = auth
        self.app = app

    def valid_user(self, token):
        try:
            user = self.auth.verify_id_token(token, app=self.app)
            return user
        except (
            self.auth.CertificateFetchError,
            self.auth.RevokedIdTokenError,
            self.auth.ExpiredIdTokenError,
            self.auth.InvalidIdTokenError,
        ):
            raise exceptions.UserWrongLoginInformation
        except (self.auth.UserDisabledError):
            raise exceptions.UserIsBlock
