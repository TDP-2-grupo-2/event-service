from sqlalchemy.orm import Session
from event_service.exceptions import exceptions
from . import user_model

def get_attendee_by_email(email:str, db:Session):
     return db.query(user_model.Attende).filter(user_model.Attende.email == email).first()

def verify_user_exists(id:int, db:Session):
    user = db.query(user_model.Attende).filter(user_model.Attende.id == id).first()
    if user is None:
        raise exceptions.UserNotFound
    

def create_attende(email: str, name: str, db: Session):
    db_attende = user_model.Attende(email=email, name=name)
    db.add(db_attende)
    db.commit()
    db.refresh(db_attende)
    return db_attende

def login_google(email: str, name: str, db: Session):

    user = get_attendee_by_email(email, db)
    if user is None:
        ## creo al usuario
        print("usuario no existe")
        user_created = create_attende(email, name, db)
    else: 
        ## ya existe en la base
        print("usuario existe")
        user_created = user

    return user_created
