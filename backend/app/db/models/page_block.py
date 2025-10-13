from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class PageBlock(Base):
    __tablename__ = "page_blocks"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)

    # e.g. 'text', 'image', 'html', 'video', 'gallery', etc.
    type = Column(String(50), nullable=False)

    # Flexible JSON content for WYSIWYG blocks
    content = Column(JSON, nullable=False, default={})

    # Positioning within a page
    order = Column(Integer, default=0, nullable=False)

    # Visibility toggle
    is_visible = Column(Boolean, default=True, nullable=False)

    # Creator / Timestamps
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # -------------------------
    # Relationships
    # -------------------------
    page = relationship("Page", back_populates="blocks")
    creator = relationship("User", lazy="joined")

    def __repr__(self):
        return f"<PageBlock id={self.id} page_id={self.page_id} type={self.type} order={self.order}>"
