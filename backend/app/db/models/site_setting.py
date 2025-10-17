#app/db/models/site-settngs.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for fast key lookups
    __table_args__ = (
        Index("ix_site_settings_key", "key"),
    )
    def __repr__(self):
        return f"<SiteSetting(id={self.id}, key='{self.key}', value='{self.value}')>"