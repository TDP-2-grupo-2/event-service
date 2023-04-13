def init_firebase():
    from event_service.utils.firebase_implementation import Firebase
    
    import firebase_admin
    from firebase_admin import credentials, auth

    cred = credentials.Certificate("event_service/utils/firebase_keys.json")

    default_app = firebase_admin.initialize_app(cred, name="test")

    # Initialize the default app
    default_app = firebase_admin.initialize_app(cred)
    global firebase
    firebase = Firebase(auth, default_app)


def get_fb():
    try:
        yield firebase
    finally:
        firebase