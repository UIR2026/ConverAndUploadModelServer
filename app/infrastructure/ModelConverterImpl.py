from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import (
    CalibrationDataReader,
    QuantFormat,
    QuantType,
    quantize_static,
)
from onnxruntime.tools.convert_onnx_models_to_ort import (
    OptimizationStyle,
    convert_onnx_models_to_ort,
)
from PIL import Image
from ultralytics import YOLO

from app.domain.ModelConverter import ModelConverter
from app.infrastructure.constants import BASE_DIR


IMAGES_DIR = BASE_DIR / "storage" / "images"


class ModelConverterImpl(ModelConverter):
    def convert(self, model_pt_path: Path, results_dir: Path) -> Path:
        model_pt_path = Path(model_pt_path)
        results_dir = Path(results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)

        result_path = results_dir / f"{model_pt_path.stem}.ort"
        if result_path.exists():
            result_path.unlink()

        with TemporaryDirectory(dir=results_dir) as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            fp32_onnx_path = temp_dir / f"{model_pt_path.stem}_fp32.onnx"
            int8_onnx_path = temp_dir / f"{model_pt_path.stem}_int8_static.onnx"

            model = YOLO(str(model_pt_path), task="detect")
            exported_path = Path(
                model.export(
                    format="onnx",
                    imgsz=640,
                    opset=20,
                    dynamic=False,
                    simplify=False,
                    half=False,
                )
            ).resolve()
            shutil.move(str(exported_path), str(fp32_onnx_path))

            calibration_reader = ImageCalibrationDataReader(fp32_onnx_path, IMAGES_DIR)
            quantize_static(
                model_input=str(fp32_onnx_path),
                model_output=str(int8_onnx_path),
                calibration_data_reader=calibration_reader,
                quant_format=QuantFormat.QDQ,
                activation_type=QuantType.QUInt8,
                weight_type=QuantType.QInt8,
                op_types_to_quantize=["Conv"],
            )

            convert_onnx_models_to_ort(
                int8_onnx_path,
                output_dir=temp_dir,
                optimization_styles=[OptimizationStyle.Fixed],
            )
            generated_ort_path = temp_dir / f"{int8_onnx_path.stem}.ort"
            generated_ort_path.replace(result_path)

        return result_path


class ImageCalibrationDataReader(CalibrationDataReader):
    def __init__(self, model_path: Path, images_dir: Path, limit: int = 32):
        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.image_paths = [
            path
            for path in sorted(images_dir.glob("*"))
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
        ][:limit]
        self.index = 0

        if not self.image_paths:
            raise FileNotFoundError(f"calibration images not found in {images_dir}")

    def get_next(self) -> dict[str, np.ndarray] | None:
        if self.index >= len(self.image_paths):
            return None

        image_path = self.image_paths[self.index]
        self.index += 1
        image = Image.open(image_path).convert("RGB")

        height = int(self.input_shape[2]) if isinstance(self.input_shape[2], int) else 640
        width = int(self.input_shape[3]) if isinstance(self.input_shape[3], int) else 640
        scale = min(width / image.width, height / image.height)
        resized_width = int(round(image.width * scale))
        resized_height = int(round(image.height * scale))
        resized_image = image.resize((resized_width, resized_height), Image.BILINEAR)

        padded_image = Image.new("RGB", (width, height), (114, 114, 114))
        left = (width - resized_width) // 2
        top = (height - resized_height) // 2
        padded_image.paste(resized_image, (left, top))

        image_array = np.asarray(padded_image, dtype=np.float32) / 255.0
        image_array = np.transpose(image_array, (2, 0, 1))
        return {self.input_name: np.expand_dims(image_array, axis=0)}

    def rewind(self) -> None:
        self.index = 0
