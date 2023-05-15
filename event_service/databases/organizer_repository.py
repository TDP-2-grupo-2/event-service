from sqlalchemy.orm import Session
from . import user_model
from event_service.exceptions import exceptions

def get_organizer_by_email(email:str, db:Session):
     return db.query(user_model.Organizer).filter(user_model.Organizer.email == email).first()


def get_organizer_by_id(id:str, db:Session):
     return db.query(user_model.Organizer).filter(user_model.Organizer.id== id).first()

def create_organizer(email: str, name: str, db: Session):
    db_attende = user_model.Organizer(email=email, name=name, isBlock=False)
    db.add(db_attende)
    db.commit()
    db.refresh(db_attende)
    return db_attende

def login_google(email: str, name: str, db: Session):

    user = get_organizer_by_email(email, db)
    if user is None:
        ## creo al usuario
        user_created = create_organizer(email, name, db)
    else: 
        ## ya existe en la base
        if isOrganizerBlock(db, user.id):
            raise exceptions.UserIsBlock
        else:
            user_created = user
    return user_created

def suspend_organizer(db:Session, organizer_id):
    user = get_organizer_by_id(organizer_id, db)
    if user is None:
        print("usuaio no existe")
        raise exceptions.UserNotFound
    user.isBlock = True
    db.commit()
    db.refresh(user)
    return user


def isOrganizerBlock(db:Session, organizer_id):
    user = get_organizer_by_id(organizer_id, db)
    if user is None:
        raise exceptions.UserNotFound
    return user.isBlock