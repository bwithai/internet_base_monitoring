# models.py
from sqlmodel import SQLModel, Field
from datetime import datetime


class RegisteredPcs(SQLModel, table=True):
    __tablename__ = 'registered_pcs'

    System_UUID: str = Field(primary_key=True, unique=True)
    username: str = Field()
    updated_username: str = Field(nullable=True)
    # timestamp: datetime = Field(default=datetime.utcnow())
    username_changed: bool = Field(default=False)
