from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models import QueryLog

def get_total_queries(db: Session) -> int:
    return db.query(func.count(QueryLog.id)).scalar() or 0


def get_average_latency(db: Session) -> Optional[float]:    
    result = db.query(func.avg(QueryLog.latency_seconds)).scalar()
    return round(result, 4) if result is not None else None


def get_success_rate(db: Session) -> Optional[float]:    
    total = get_total_queries(db)
    if total == 0:
        return None
    success = (
        db.query(func.count(QueryLog.id))
        .filter(QueryLog.answer_found == True)  
        .scalar()
        or 0
    )
    return round((success / total) * 100, 2)


def get_most_frequent_questions(db: Session, limit: int = 10) -> List[Dict[str, Any]]:

    rows = (
        db.query(
            QueryLog.question,
            func.count(QueryLog.id).label("frequency"),
        )
        .group_by(QueryLog.question)
        .order_by(func.count(QueryLog.id).desc())
        .limit(limit)
        .all()
    )
    return [{"question": q, "frequency": f} for q, f in rows]


def get_no_answer_queries(db: Session) -> List[str]:
    
    rows = (
        db.query(QueryLog.question)
        .filter(QueryLog.answer_found == False)  
        .distinct()
        .all()
    )
    return [row[0] for row in rows]


def get_full_analytics(db: Session) -> Dict[str, Any]:
    
    return {
        "total_queries": get_total_queries(db),
        "average_latency": get_average_latency(db),
        "success_rate": get_success_rate(db),
        "most_frequent_questions": get_most_frequent_questions(db),
        "no_answer_queries": get_no_answer_queries(db),
    }