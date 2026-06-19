# Pydantic schemas
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

class AskRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's Question",
        examples = ["can AWS suspend my account?"]
    )

class IngestResponse(BaseModel):
    message: str

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]

class FrequentQuestion(BaseModel):
    question: str
    frequency: int

class AnalyticsResponse(BaseModel):
    total_queries: int
    average_latency: Optional[float]
    success_rate: Optional[float]
    most_frequent_questions: List[FrequentQuestion]
    no_answer_queries: List[str]