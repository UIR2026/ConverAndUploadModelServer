from datetime import datetime, timezone

from app.domain.Model import Model
from app.domain.Exception import *
from app.domain.ModelRepository import ModelRepository
from app.domain.ModelStorage import ModelStorage
from app.domain.ModelConverter import ModelConverter


class UploadModelUseCase:
    def __init__(
        self,
        repository: ModelRepository,
        storage: ModelStorage,
        converter: ModelConverter,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._converter = converter

    def execute(self, version: str, upload_file) -> Model:
        normalized_version = version.strip()
        if not normalized_version:
            raise InvalidModelVersionError("Version must not be empty.")
        if self._repository.get_by_version(normalized_version) is not None:
            raise DuplicateModelVersionError(f"Model version '{normalized_version}' already exists.")

        safe_filename = self._storage.validate_upload_filename(upload_file.filename)
        tmp_path = self._storage.save_upload_to_tmp(upload_file.file, safe_filename)
        conversion_input_path = None
        final_model_path = None

        try:
            model_filename = self._storage.build_model_filename(normalized_version)
            conversion_input_path = self._storage.prepare_conversion_input(
                tmp_path=tmp_path,
                model_filename=model_filename,
            )
            converted_path = self._converter.convert(
                model_pt_path=conversion_input_path,
                results_dir=self._storage.models_dir,
            )
            final_model_path = self._storage.finalize_converted_model(
                converted_path=converted_path,
                model_filename=model_filename,
            )

            model = self._repository.add(
                Model(
                    id=None,
                    version=normalized_version,
                    filename=model_filename,
                    file_path=str(final_model_path),
                    created_at=datetime.now(timezone.utc),
                    is_latest=True,
                )
            )
            return model
        except Exception as exc:
            self._storage.delete_file_if_exists(final_model_path)
            if isinstance(
                exc,
                (
                    InvalidModelVersionError,
                    DuplicateModelVersionError,
                    ModelNotFoundError,
                ),
            ):
                raise
            raise ModelConversionError(f"Model conversion failed: {exc}") from exc
        finally:
            upload_file.file.close()
            self._storage.delete_file_if_exists(tmp_path)
            self._storage.delete_file_if_exists(conversion_input_path)