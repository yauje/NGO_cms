from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="public")  # public, editor, admin
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    page_revisions = relationship("PageRevision", back_populates="created_by", cascade="all, delete-orphan")
    uploads = relationship("Media", back_populates="uploaded_by", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', is_active={self.is_active})>"

    # Utility methods for auth routes
    @classmethod
    async def get_by_email(cls, db, email: str):
        from sqlalchemy.future import select
        result = await db.execute(select(cls).filter_by(email=email))
        return result.scalars().first()

    @classmethod
    async def create(cls, db, email: str, hashed_password: str, role: str = "public"):
        """Create a new user record."""
        user = cls(email=email, hashed_password=hashed_password, role=role)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
