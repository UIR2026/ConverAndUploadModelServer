from app.domain.ModelStorage import ModelStorage
from app.domain.Model import Model
from app.domain.Exception import ModelNotFoundError
from app.domain.ModelRepository import ModelRepository


class GetLatestModelUseCase:
    def __init__(self, repository: ModelRepository, storage: ModelStorage) -> None:
        self._repository = repository
        self._storage = storage

    def execute(self, version: str | None = None, filename: str | None = None) -> Model:
        model = self._repository.get_latest()
        if model is None:
            raise ModelNotFoundError("No models have been uploaded yet.")
        if version is not None and model.version != version:
            raise ModelNotFoundError("Latest model does not match requested version.")
        if filename is not None and model.filename != filename:
            raise ModelNotFoundError("Latest model does not match requested filename.")
        self._storage.ensure_model_file_exists(model.file_path)
        return model
