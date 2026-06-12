from abc import ABC, abstractmethod
from pathlib import Path


class ModelStorage(ABC):
    @property
    @abstractmethod
    def models_dir(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def ensure_directories(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate_upload_filename(self, filename: str | None) -> str:
        raise NotImplementedError

    @abstractmethod
    def save_upload_to_tmp(self, source_file, filename: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def build_model_filename(self, version: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def prepare_conversion_input(self, tmp_path: Path, model_filename: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def finalize_converted_model(self, converted_path: Path, model_filename: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def ensure_model_file_exists(self, file_path: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def delete_file_if_exists(self, file_path: Path | None) -> None:
        raise NotImplementedError
