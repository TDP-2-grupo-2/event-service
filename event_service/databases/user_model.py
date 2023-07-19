from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Boolean

Base = declarative_base()

class Attende(Base):
    __tablename__ = "attendes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(255), nullable=False)
    email = Column("email", String(255), nullable=False)



class Organizer(Base):
    __tablename__ = "organizers"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(255), nullable=False)
    email = Column("email", String(255), nullable=False)
    isBlock = Column("isBlock", Boolean, unique=False, default=False)
