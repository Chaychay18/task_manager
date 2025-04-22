from sqlalchemy import Column, String, Text
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    result = Column(Text)
