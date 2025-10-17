#app/db/models/page_revision.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PageRevision(Base):
    __tablename__ = "page_revisions"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)  # draft / published / archived
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    page = relationship("Page", back_populates="revisions")
    created_by = relationship("User", back_populates="page_revisions")

    # Index for faster filtering by page and status
    __table_args__ = (
        Index("ix_page_revisions_page_status", "page_id", "status"),
    )
