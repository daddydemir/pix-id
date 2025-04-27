from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class Encoding(Base):
    __tablename__ = "encods"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.uuid"), nullable=False)
    face_path = Column(String, nullable=False)
    encoding = Column(LargeBinary, nullable=False)
    
    person = relationship("Person", back_populates="encodings")