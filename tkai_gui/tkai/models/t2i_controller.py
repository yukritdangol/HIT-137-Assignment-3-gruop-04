from __future__ import annotations
import torch
from pathlib import Path
from typing import Any, Dict, Tuple

from PIL import Image

from tkai.models.base import BaseModelController, measure_time, catch_exceptions, require_loaded
from tkai.services.logger_service import LoggerService
from tkai.services.io_utils import validate_prompt, save_image, save_json, timestamp
from tkai.config import DEFAULTS, MODEL_DESCRIPTIONS

# Mixins for multiple inheritance
class TextIOMixin:
    def _prepare_text(self, prompt: str, max_len: int) -> str:
        return validate_prompt(prompt, max_len=max_len)

class ImageIOMixin:
    def _save_outputs(self, img: Image.Image, meta: Dict[str, Any]) -> Dict[str, Any]:
        stem = f"t2i_{timestamp()}"
        out_img = save_image(img, "outputs", stem)
        out_json = save_json(meta, "outputs", stem)
        return {"image_path": str(out_img), "json_path": str(out_json)}

class TextToImageController(BaseModelController, TextIOMixin, ImageIOMixin):
    """
    Polymorphic controller for Text-to-Image using diffusers AutoPipelineForText2Image.
    Overridden methods: load_model(), run()
    """
    def __init__(self, logger: LoggerService):
        super().__init__(logger)
        self._name = DEFAULTS["t2i_model"]
        self._category = "Text → Image"
        self._pipe = None

    @catch_exceptions
    @measure_time
    def load_model(self) -> Dict[str, Any]:
        import torch
        from diffusers import AutoPipelineForText2Image

        self._logger.info("Loading Text-to-Image model...")
        device = "cpu"
        torch.set_num_threads(max(1, torch.get_num_threads()))
        self._pipe = AutoPipelineForText2Image.from_pretrained(
            self._name,
            torch_dtype=torch.float32,
            use_safetensors=True
        )
        self._pipe.to("cpu")
        self._loaded = True
        return {"ok": True, "model": self._name, "device": device}

    def summarize_info(self) -> Dict[str, str]:
        return {
            "Model Name": self._name,
            "Category": self._category,
            "Description": MODEL_DESCRIPTIONS.get(self._name, "N/A")
        }

    def validate_input(self, prompt: str, negative_prompt: str = "", **kwargs) -> None:
        _ = self._prepare_text(prompt, DEFAULTS["prompt_maxlen"])
        # negative prompt may be empty; keep simple

    @catch_exceptions
    @require_loaded
    @measure_time
    def run(self, prompt: str, negative_prompt: str = "", width: int = None, height: int = None, steps: int = None, guidance: float = None) -> Dict[str, Any]:
        width = width or DEFAULTS["image_size"][0]
        height = height or DEFAULTS["image_size"][1]
        steps = steps or DEFAULTS["t2i_steps"]
        guidance = guidance if guidance is not None else DEFAULTS["t2i_guidance"]

        prompt = self._prepare_text(prompt, DEFAULTS["prompt_maxlen"])
        n_prompt = (negative_prompt or "").strip()

        self._logger.info(f"Generating image {width}x{height}, steps={steps}, guidance={guidance}")
        img = self._pipe(
            prompt=prompt,
            negative_prompt=n_prompt if n_prompt else None,
            num_inference_steps=int(steps),
            guidance_scale=float(guidance),
            width=int(width),
            height=int(height)
        ).images[0]

        meta = {
            "ok": True,
            "task": "text-to-image",
            "model": self._name,
            "prompt": prompt,
            "negative_prompt": n_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance": guidance,
        }
        paths = self._save_outputs(img, meta)
        meta.update(paths)
        return meta
