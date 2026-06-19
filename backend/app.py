from __future__ import annotations

import logging
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from backend.analytics import get_full_analytics
from backend.database import get_db, init_db
from backend.rag import ask_question, ingest_pdf
from backend.schemas import (
    AnalyticsResponse,
    AskRequest,
    AskResponse,
    IngestResponse,
)
from backend.utils import log_query, measure_latency

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Document Q&A Systerm",
    )

@app.on_event("startup")
def on_startup()->None:
    init_db()
    logger.info("Database tables created / verified.")


@app.post("/ingest", response_model = IngestResponse, status_code = 200)
def ingest_document()->IngestResponse:

    try:
        result = ingest_pdf()
        logger.info("Ingestion complete: %s", result["message"])
        return IngestResponse(message=result["message"])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")


@app.post("/ask", response_model = AskResponse, status_code = 200)
def ask( payload: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail = "Question cannot be empty.")

    try: 
        with measure_latency() as timing:
            answer, sources, answer_found = ask_question(question)

        log_query(
            db=db,
            question=question,
            answer=answer,
            latency=timing["seconds"],
            chunks=sources,
            answer_found=answer_found
            )

        logger.info(
            "Answered in %.2fs | found=%s | q='%s'",
            timing["seconds"],
            answer_found,
            question[:60]
        )

        return AskResponse(
            question = question,
            answer=answer,
            sources=sources
        )
    except RuntimeError as exc:
        raise HTTPException(status_code = 503, detail=str(exc))
    except Exception as exc:
        logger.exception("Ask failed")
        raise HTTPException(status_code = 503, detail=f"Failed to process question: {str(exc)}")

@app.get("/analytics", response_model = AnalyticsResponse, status_code = 200)
def analytics(db: Session = Depends(get_db)) -> AnalyticsResponse:
    try:
        data = get_full_analytics(db)
        return AnalyticsResponse(**data)
    except Exception as exc:
        logger.exception("Analytics query failed")
        raise HTTPException(status_code = 500, detail = f"Analytics error : {str(exc)}")
    
