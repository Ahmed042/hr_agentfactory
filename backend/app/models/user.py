from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), default="")
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")  # admin|hr_manager|recruiter|viewer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
