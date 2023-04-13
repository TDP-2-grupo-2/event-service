from sqlalchemy.orm import Session
from . import user_model

def get_user_by_email(email:str, db:Session):
     return db.query(user_model.Attende).filter(user_model.Attende.email == email).first()


def create_attende(uid: str, email: str, name: str, picture: str, db: Session):
    db_attende = user_model.Attende(googleId=uid, email=email, name=name, picture= picture)
    db.add(db_attende)
    db.commit()
    db.refresh(db_attende)
    return db_attende

def login_google(uid: str, email: str, name: str, picture: str, db: Session):

    user = get_user_by_email(email, db)
    if user is None:
        ## creo al usuario
        print("usuario no existe")
        user_created = create_attende(uid, email, name, picture, db)
    else: 
        ## ya existe en la base
        print("usuario existe")
        user_created = user

    print(user_created)
    return user_created
