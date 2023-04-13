from sqlalchemy.orm import Session
from . import user_model

def get_organizer_by_email(email:str, db:Session):
     return db.query(user_model.Organizer).filter(user_model.Organizer.email == email).first()


def create_organizer(uid: str, email: str, name: str, picture: str, db: Session):
    db_attende = user_model.Organizer(googleId=uid, email=email, name=name, picture= picture)
    db.add(db_attende)
    db.commit()
    db.refresh(db_attende)
    return db_attende

def login_google(uid: str, email: str, name: str, picture: str, db: Session):

    user = get_organizer_by_email(email, db)
    if user is None:
        ## creo al usuario
        print("usuario no existe")
        user_created = create_organizer(uid, email, name, picture, db)
    else: 
        ## ya existe en la base
        print("usuario existe")
        user_created = user
    return user_created