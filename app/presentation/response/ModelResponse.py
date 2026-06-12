from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer

from app.domain.Model import Model


class ModelResponse(BaseModel):
    version: str
    created_at: datetime
    filename: str
    is_latest: bool

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def from_model(model: Model) -> ModelResponse:
        return ModelResponse(
            version=model.version,
            created_at=model.created_at,
            filename=model.filename,
            is_latest=model.is_latest,
        )
