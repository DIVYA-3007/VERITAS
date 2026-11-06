
from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    Integer,
    Text,
    String,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    extraction_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    ocr_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True
    )

    document = relationship("Document", back_populates="chunks")
