from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean

Base = declarative_base()

class Attende(Base):
    __tablename__ = "attendes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    googleId = Column("googleId", String(255), nullable=False)
    name = Column("name", String(255), nullable=False)
    email = Column("email", String(255), nullable=False)
    picture = Column("picture",  String(255), nullable=True)


class Organizer(Base):
    __tablename__ = "organizers"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    googleId = Column("googleId", String(255), nullable=False)
    name = Column("name", String(255), nullable=False)
    email = Column("email", String(255), nullable=False)
    picture = Column("picture",  String(255), nullable=True)