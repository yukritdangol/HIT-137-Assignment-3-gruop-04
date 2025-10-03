from dataclasses import dataclass

DEFAULTS = {
    "t2i_model": "stabilityai/sd-turbo",
    "clf_model": "apple/mobilevit-xx-small",
    "image_size": (256, 256),
    "t2i_steps": 2,
    "t2i_guidance": 0.0,
    "clf_topk": 5,
    "prompt_maxlen": 300,
}

MODEL_DESCRIPTIONS = {
    "stabilityai/sd-turbo": "Fast text-to-image generation model (diffusers), good for quick drafts.",
    "apple/mobilevit-xx-small": "Tiny MobileViT classifier suitable for CPU-bound inference.",
}
