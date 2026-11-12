
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.search_service import search_similar_chunks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Semantic Search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/")
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    try:
        results = search_similar_chunks(
            db=db,
            query=request.query,
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Semantic search failed for query: %s",
            request.query,
        )

        raise HTTPException(
            status_code=500,
            detail="Semantic search failed. Check backend logs.",
        ) from None
