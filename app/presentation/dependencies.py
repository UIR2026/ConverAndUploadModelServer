from collections.abc import Generator
from hmac import compare_digest

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.domain.usecase.GetLatestModelUseCase import GetLatestModelUseCase
from app.domain.usecase.UploadModelUseCase import UploadModelUseCase
from app.infrastructure.bootstrap import get_container
from app.infrastructure.constants import API_KEY_HEADER_NAME, API_KEYS
from app.infrastructure.ModelRepositoryImpl import ModelRepositoryImpl

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    if api_key and any(compare_digest(api_key, valid_key) for valid_key in API_KEYS):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )


def get_db_session() -> Generator[Session, None, None]:
    container = get_container()
    session = container.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_upload_model_use_case(
    session: Session = Depends(get_db_session),
) -> UploadModelUseCase:
    container = get_container()
    repository = ModelRepositoryImpl(session)
    return UploadModelUseCase(
        repository=repository,
        storage=container.storage,
        converter=container.converter,
    )


def get_latest_model_use_case(
    session: Session = Depends(get_db_session),
) -> GetLatestModelUseCase:
    container = get_container()
    repository = ModelRepositoryImpl(session)
    return GetLatestModelUseCase(repository=repository, storage=container.storage)
