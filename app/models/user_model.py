import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    # Each Column = one column in your database table
    # Integer, String etc. → the database column type
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name     = Column(String(50), nullable=False)
    email    = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # will store hashed password
    is_active = Column(Boolean, default=True)

    # server_default=func.now() → DB sets this automatically on insert
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")