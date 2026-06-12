from abc import abstractmethod, ABC
from pathlib import Path


class ModelConverter(ABC):
    @abstractmethod
    def convert(self, model_pt_path: Path, results_dir: Path) -> Path:
        raise NotImplementedError
