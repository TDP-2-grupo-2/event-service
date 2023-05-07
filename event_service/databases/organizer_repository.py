from sqlalchemy.orm import Session
from . import user_model

def get_organizer_by_email(email:str, db:Session):
     return db.query(user_model.Organizer).filter(user_model.Organizer.email == email).first()


def create_organizer(email: str, name: str, db: Session):
    db_attende = user_model.Organizer(email=email, name=name)
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
        user_created = user
    return user_created