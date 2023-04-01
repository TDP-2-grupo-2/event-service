from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean

Base = declarative_base()

class Attende(Base):
    __tablename__ = "attendes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("user_name", String(255), nullable=False)
