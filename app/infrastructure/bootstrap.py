from dataclasses import dataclass
from pathlib import Path
from app.infrastructure.constants import DATABASE_URL
from app.infrastructure.ModelConverterImpl import ModelConverterImpl
from app.infrastructure.database import Base, create_engine_and_session
from app.infrastructure.ModelStorageImpl import ModelStorageImpl


@dataclass(slots=True)
class Container:
    storage: ModelStorageImpl
    converter: ModelConverterImpl
    engine: object
    session_factory: object


_container: Container | None = None


def get_container() -> Container:
    global _container
    if _container is None:
        storage = ModelStorageImpl()
        engine, session_factory = create_engine_and_session(DATABASE_URL)
        _container = Container(
            storage=storage,
            converter=ModelConverterImpl(),
            engine=engine,
            session_factory=session_factory,
        )
    return _container


def initialize_application() -> None:
    container = get_container()
    container.storage.ensure_directories()
    engine_path = container.engine.url.database
    if engine_path:
        Path(engine_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=container.engine)
