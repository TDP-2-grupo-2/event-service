from event_service.exceptions import exceptions

class FirebaseMock:
    usersfireabse = {}
    usersfireabse["hfjdshfuidhysvcsbvs83hfsdf"] = {
        "uid": "asdasdasdslwlewed1213123",
        "email": "agus@gmail.com",
        "name": "agus",
        "picture": "picture",

    }
    usersfireabse["ahsgdhauiwhfdiwhf"] = {
        "uid": "djdhdhdhd",
        "email": "sol@gmail.com",
        "name": "sol",
        "picture": "picture",

    }
    usersfireabse["eujthfydhd"] = {
        "uid": "shdashdHSDY",
        "email": "ale@gmail.com",
        "name": "ale",
        "picture": "picture",

    }
    usersfireabse["ueywepd"] = {
        "uid": "poiyres",
        "email": "franco@gmail.com",
        "name": "franco",
        "picture": "picture",

    }

    def valid_user(self, token):
        info = None
        if token in self.usersfireabse.keys():
            info = self.usersfireabse[token]
            return info
        else:
            raise exceptions.UserWrongLoginInformation
        
    def get_email(self, uid):
        email = None
        for value in self.usersfireabse.values():
            if value["uid"] == uid:
                email = value["email"]
        return email