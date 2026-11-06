
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.qa_service import answer_question


router = APIRouter(
    prefix="/qa",
    tags=["Question Answering"],
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


@router.post("/")
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    try:
        result = answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Question answering service failed.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An internal question answering error occurred.",
        ) from exc
