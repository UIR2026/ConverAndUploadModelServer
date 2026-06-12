import shutil
from pathlib import Path
from uuid import uuid4

from app.domain.Exception import InvalidModelFileError, ModelFileMissingError
from app.domain.ModelStorage import ModelStorage
from app.infrastructure.constants import TMP_DIR, MODEL_DIR


class ModelStorageImpl(ModelStorage):
    @property
    def models_dir(self) -> Path:
        return MODEL_DIR

    def ensure_directories(self) -> None:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        TMP_DIR.mkdir(parents=True, exist_ok=True)

    def validate_upload_filename(self, filename: str | None) -> str:
        if not filename:
            raise InvalidModelFileError("Uploaded file must have a filename.")

        safe_name = Path(filename).name
        if Path(safe_name).suffix.lower() != ".pt":
            raise InvalidModelFileError("Only .pt model files are supported.")
        return safe_name

    def save_upload_to_tmp(self, source_file, filename: str) -> Path:
        tmp_path = TMP_DIR / f"{uuid4().hex}_{filename}"
        with tmp_path.open("wb") as buffer:
            shutil.copyfileobj(source_file, buffer)
        return tmp_path

    def build_model_filename(self, version: str) -> str:
        return f"model_v{version}.ort"

    def prepare_conversion_input(self, tmp_path: Path, model_filename: str) -> Path:
        conversion_input_path = TMP_DIR / f"{uuid4().hex}_{Path(model_filename).stem}.pt"
        tmp_path.rename(conversion_input_path)
        return conversion_input_path

    def finalize_converted_model(self, converted_path: Path, model_filename: str) -> Path:
        target_path = MODEL_DIR / model_filename
        if converted_path.resolve() != target_path.resolve():
            converted_path.replace(target_path)
        return target_path

    def ensure_model_file_exists(self, file_path: str) -> Path:
        resolved_path = Path(file_path)
        if not resolved_path.exists():
            raise ModelFileMissingError("Latest model file is missing on disk.")
        return resolved_path

    def delete_file_if_exists(self, file_path: Path | None) -> None:
        if file_path and file_path.exists():
            file_path.unlink()
