
# app/db/models/page.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    
    # FIX APPLIED: Corrected the index redundancy issue. 
    # Relying only on 'unique=True' to create the necessary unique index.
    slug = Column(String(100), unique=True, nullable=False)
    
    title = Column(String(255), nullable=False)
    
    # Added based on Page schema for completeness
    is_published = Column(Boolean, nullable=False, default=False) 

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # -------------------------
    # Relationships
    # -------------------------
    
    # Standard relationship loading
    revisions = relationship(
        "PageRevision",
        back_populates="page",
        cascade="all, delete-orphan",
    )

    
    blocks = relationship(
        "PageBlock",
        back_populates="page",
        cascade="all, delete-orphan",
        lazy="selectin" 
    )

    def __repr__(self):
        return f"<Page(id={self.id}, slug='{self.slug}', title='{self.title}')>"
