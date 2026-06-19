from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator, List
from sqlalchemy.orm import Session
from backend.models import QueryLog


@contextmanager
def measure_latency() -> Generator[dict, None, None]:
    result: dict = {"seconds": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["seconds"] = round(time.perf_counter() - start, 4)


def log_query(
    db: Session,
    question: str,
    answer: str,
    latency: float,
    chunks: List[str],
    answer_found: bool,
) -> QueryLog:

    record = QueryLog(
        question=question,
        answer=answer,
        latency_seconds=latency,
        retrieved_chunks=json.dumps(chunks),
        answer_found=answer_found,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
