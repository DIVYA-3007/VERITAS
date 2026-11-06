
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.document import Document
from app.services.document_service import process_pdf_document


router = APIRouter(prefix="/documents", tags=["Documents"])

# Project storage directory
PROJECT_ROOT = Path(__file__).resolve().parents[5]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a PDF document."""

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique server-side filename
    saved_filename = f"{uuid4()}.pdf"
    saved_path = UPLOAD_DIR / saved_filename

    try:
        contents = await file.read(MAX_FILE_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="PDF exceeds the 20 MB upload limit.",
            )

        # Basic PDF signature validation
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file.",
            )

        saved_path.write_bytes(contents)

        document = process_pdf_document(
            db=db,
            pdf_path=saved_path,
            original_filename=Path(file.filename).name,
            file_size=len(contents),
        )

        return {
            "message": "PDF uploaded and processed successfully.",
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status,
            "file_size": document.file_size,
        }

    except HTTPException:
        saved_path.unlink(missing_ok=True)
        raise

    except Exception as exc:
        saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(exc)}",
        ) from exc

    finally:
        await file.close()


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """Return all uploaded documents."""

    documents = db.query(Document).order_by(
        Document.created_at.desc()
    ).all()

    return [
        {
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve a document using its UUID."""

    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "status": document.status,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "created_at": document.created_at,
    }
