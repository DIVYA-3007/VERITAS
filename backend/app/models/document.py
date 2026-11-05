import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    # Unique document identifier
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    # Original document filename
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Document format: PDF, DOCX, TXT, etc.
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Original file size in bytes
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    # Location of the uploaded file
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # Document processing status
    status: Mapped[str] = mapped_column(
        String(30),
        default="uploaded",
        nullable=False
    )

    # Upload timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    chunks = relationship(
    "DocumentChunk",
    back_populates="document",
    cascade="all, delete-orphan"
    )