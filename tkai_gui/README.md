# Tkinter AI GUI (CPU-only, Hugging Face)

A fully working Tkinter desktop app that demonstrates two Hugging Face models on **CPU only**:

- **Text-to-Image**: `stabilityai/sd-turbo` via `diffusers.AutoPipelineForText2Image`
- **Image Classification**: `apple/mobilevit-xx-small` via `transformers.pipeline("image-classification")`

The codebase demonstrates **OOP concepts**: multiple inheritance via mixins, encapsulation, polymorphism, method overriding, and stacked decorators for timing, exception handling, and "require loaded" checks.

---

## Quickstart

```bash
# 1) Create & activate a virtualenv (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Install requirements (CPU wheels for torch from PyTorch index)
pip install -r requirements.txt

# 3) Run
python app.py
```

> First run will download models into your Hugging Face cache. Keep internet on for the first run.

---

## Features

- CPU-only execution (device=-1, dtype=float32)
- Non-blocking UI using threads + `after(...)`
- Robust error handling with stacked decorators
- Logs to **logs/app.log** and on-screen console
- Saves outputs to **outputs/** with timestamped filenames
- JSON sidecars with generation parameters and timings
- OOP concepts explained inside the app (OOP pane)

---

## OOP Concepts Mapping

- **Multiple Inheritance**: `TextToImageController(BaseModelController, TextIOMixin, ImageIOMixin)`, `ImageClassifierController(BaseModelController, ImageIOMixin)`
- **Encapsulation**: protected/private attrs such as `_model`, `_name`, `_category`, `_loaded`
- **Polymorphism & Overriding**: `load_model()` and `run()` are specialized in each controller
- **Multiple Decorators**: `@measure_time`, `@catch_exceptions`, `@require_loaded` stacked on methods
- **Composition**: `AppState` and `LoggerService` are injected into the UI and controllers

---

## Known Limits

- CPU-only: large images or long prompts will be slow
- `sd-turbo` is optimized for speed but still heavier than tiny classifiers; defaults are conservative (256×256, 2 steps)

---

## Troubleshooting

- **Pillow / DLL issues on Windows**: reinstall Pillow `pip install --force-reinstall Pillow`
- **Hugging Face auth**: models used are public; no token required
- **Slow first run**: downloading models can take time; subsequent runs use cache

---

## License & Credits

- Models: `stabilityai/sd-turbo` (Stability AI), `apple/mobilevit-xx-small` (Apple)
- Libraries: PyTorch, diffusers, transformers, Pillow
- This sample is for educational use.
