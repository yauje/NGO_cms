from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_published = Column(Boolean, default=False)

    # Optional layout & theme fields for WYSIWYG flexibility
    layout = Column(String(50), default="stacked")  # "stacked", "grid", "custom"
    theme_variant = Column(String(50), default="default")  # link to site theme palette

    # SEO metadata (optional)
    meta_description = Column(String(255), nullable=True)
    meta_keywords = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    # Revisions (for draft and version control)
    revisions = relationship("PageRevision", back_populates="page", cascade="all, delete-orphan")

    # PageBlocks (for WYSIWYG modular content)
    blocks = relationship("PageBlock", back_populates="page", cascade="all, delete-orphan", order_by="PageBlock.order")

    # Optionally link to the user who created the page
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="pages", lazy="joined")

    def __repr__(self):
        return f"<Page(title='{self.title}', slug='{self.slug}', published={self.is_published})>"
