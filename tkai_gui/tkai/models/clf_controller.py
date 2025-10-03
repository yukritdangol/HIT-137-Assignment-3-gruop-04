from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image

from tkai.models.base import BaseModelController, measure_time, catch_exceptions, require_loaded
from tkai.services.logger_service import LoggerService
from tkai.services.io_utils import validate_image_path, load_image, save_json, timestamp
from tkai.config import DEFAULTS, MODEL_DESCRIPTIONS

class ImageIOMixin:
    def _load_image(self, path: str | Path) -> Image.Image:
        return load_image(path)

class ImageClassifierController(BaseModelController, ImageIOMixin):
    """
    Polymorphic controller for Image Classification using transformers pipeline.
    Overridden methods: load_model(), run()
    """
    def __init__(self, logger: LoggerService):
        super().__init__(logger)
        self._name = DEFAULTS["clf_model"]
        self._category = "Image → Labels"
        self._pipe = None

    @catch_exceptions
    @measure_time
    def load_model(self) -> Dict[str, Any]:
        from transformers import pipeline as hf_pipeline
        self._logger.info("Loading Image Classification model...")
        self._pipe = hf_pipeline("image-classification", model=self._name, device=-1)  # CPU
        self._loaded = True
        return {"ok": True, "model": self._name, "device": "cpu"}

    def summarize_info(self) -> Dict[str, str]:
        return {
            "Model Name": self._name,
            "Category": self._category,
            "Description": MODEL_DESCRIPTIONS.get(self._name, "N/A")
        }

    def validate_input(self, image_path: str, **kwargs) -> None:
        validate_image_path(image_path)

    @catch_exceptions
    @require_loaded
    @measure_time
    def run(self, image_path: str, top_k: int | None = None) -> Dict[str, Any]:
        top_k = top_k or DEFAULTS["clf_topk"]
        img = self._load_image(image_path)
        self._logger.info(f"Classifying image: {image_path} | top_k={top_k}")
        preds = self._pipe(img, top_k=int(top_k))
        stem = f"clf_{timestamp()}"
        meta = {
            "ok": True,
            "task": "image-classification",
            "model": self._name,
            "image_path": str(image_path),
            "top_k": top_k,
            "predictions": preds,
        }
        jpath = save_json(meta, "outputs", stem)
        meta["json_path"] = str(jpath)
        return meta
