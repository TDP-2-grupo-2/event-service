from event_service.exceptions import exceptions

class FirebaseMock:
    usersfireabse = {}
    usersfireabse["hfjdshfuidhysvcsbvs83hfsdf"] = {
        "uid": "asdasdasdslwlewed1213123",
        "email": "agus@gmail.com",
        "name": "agus",
        "picture": "picture",
        "block": False,
    }
    usersfireabse["ahsgdhauiwhfdiwhf"] = {
        "uid": "djdhdhdhd",
        "email": "sol@gmail.com",
        "name": "sol",
        "picture": "picture",
        "block": False,
    }
    usersfireabse["eujthfydhd"] = {
        "uid": "shdashdHSDY",
        "email": "ale@gmail.com",
        "name": "ale",
        "picture": "picture",
        "block": False,
    }
    usersfireabse["ueywepd"] = {
        "uid": "poiyres",
        "email": "franco@gmail.com",
        "name": "franco",
        "picture": "picture",
        "block": False,
    }

    def valid_user(self, token):
        info = None
        if token in self.usersfireabse.keys():
            info = self.usersfireabse[token]
            return info
        else:
            raise exceptions.UserWrongLoginInformation
