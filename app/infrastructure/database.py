from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.domain.Model import Model


class Base(DeclarativeBase):
    pass


class ModelRecord(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    def to_domain(self) -> Model:
        return Model(
            id=self.id,
            version=self.version,
            filename=self.filename,
            file_path=self.file_path,
            created_at=self.created_at,
            is_latest=self.is_latest,
        )


def create_engine_and_session(database_url: str):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return engine, session_factory
