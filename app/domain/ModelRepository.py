from abc import ABC, abstractmethod

from app.domain.Model import Model


class ModelRepository(ABC):
    @abstractmethod
    def get_latest(self) -> Model | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_version(self, version: str) -> Model | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, model: Model) -> Model:
        raise NotImplementedError
