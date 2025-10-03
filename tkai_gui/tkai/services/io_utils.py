from __future__ import annotations
import json
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Any, Dict, List

from PIL import Image

SUPPORTED_IMAGE_EXTS = (".png", ".jpg", ".jpeg")

def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def validate_prompt(text: str, max_len: int = 300) -> str:
    if not text or not text.strip():
        raise ValueError("Prompt cannot be empty.")
    t = text.strip()
    if len(t) > max_len:
        raise ValueError(f"Prompt too long (>{max_len} chars).")
    return t

def validate_image_path(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")
    if p.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
        raise ValueError(f"Unsupported image format: {p.suffix}")
    return p

def load_image(path: str | Path) -> Image.Image:
    p = validate_image_path(path)
    return Image.open(p).convert("RGB")

def save_image(img: Image.Image, out_dir: str | Path, stem: str) -> Path:
    ensure_dir(out_dir)
    out_path = Path(out_dir) / f"{stem}.png"
    img.save(out_path)
    return out_path

def save_json(meta: Dict[str, Any], out_dir: str | Path, stem: str) -> Path:
    ensure_dir(out_dir)
    jpath = Path(out_dir) / f"{stem}.json"
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return jpath
