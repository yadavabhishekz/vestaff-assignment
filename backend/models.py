from sqlalchemy import TEXT
from datetime import datetime, timezone
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class base(DeclarativeBase):
    pass

class QueryLog(base):

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(2000), nullable=False, index=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    latency_seconds: Mapped[float] = mapped_column(nullable=False)
    retrieved_chunks: Mapped[str] = mapped_column(Text, nullable=False)  # stored as JSON string
    answer_found: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<QueryLog(id={self.id}, question='{self.question[:40]}...', "
            f"answer_found={self.answer_found})>"
        )
