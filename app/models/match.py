from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.uuid"), nullable=False)
    matched_image_id = Column(UUID(as_uuid=True), ForeignKey("images.uuid"), nullable=False)
    confidence_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    person = relationship("Person", back_populates="matches")
    image = relationship("Image", back_populates="matches")