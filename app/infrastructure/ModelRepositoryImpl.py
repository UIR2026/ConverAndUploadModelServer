from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.Exception import DuplicateModelVersionError
from app.domain.Model import Model
from app.domain.ModelRepository import ModelRepository
from app.infrastructure.database import ModelRecord


class ModelRepositoryImpl(ModelRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_latest(self) -> Model | None:
        stmt = (
            select(ModelRecord)
            .order_by(ModelRecord.is_latest.desc(), ModelRecord.created_at.desc())
            .limit(1)
        )
        record = self._session.scalar(stmt)
        return record.to_domain() if record else None

    def get_by_version(self, version: str) -> Model | None:
        stmt = select(ModelRecord).where(ModelRecord.version == version)
        record = self._session.scalar(stmt)
        return record.to_domain() if record else None

    def add(self, model: Model) -> Model:
        record = ModelRecord(
            version=model.version,
            filename=model.filename,
            file_path=model.file_path,
            created_at=model.created_at,
            is_latest=model.is_latest,
        )
        try:
            self._session.execute(update(ModelRecord).values(is_latest=False))
            self._session.add(record)
            self._session.commit()
            self._session.refresh(record)
            return record.to_domain()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateModelVersionError(
                f"Model version '{model.version}' already exists."
            ) from exc

