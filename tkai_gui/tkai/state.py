from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class AppState:
    selected_task: str = "Text-to-Image"  # or "Image Classification"
    last_prompt: str = ""
    last_negative_prompt: str = "blurry, low quality, watermark, extra fingers, extra hands"
    last_image_path: Optional[str] = None
    last_output_path: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    model_loaded: Dict[str, bool] = field(default_factory=lambda: {"Text-to-Image": False, "Image Classification": False})
    metadata: Dict[str, Any] = field(default_factory=dict)
