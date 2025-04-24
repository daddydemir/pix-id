from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    encodings = relationship("Encoding", back_populates="person")
    matches = relationship("Match", back_populates="person")