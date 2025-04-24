from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    matches = relationship("Match", back_populates="image")