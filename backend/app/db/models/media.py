#app/db/models/media.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    mimetype = Column(String(50), nullable=False)
    filesize_bytes = Column(BigInteger, nullable=False)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    uploaded_by = relationship("User", back_populates="uploads")
