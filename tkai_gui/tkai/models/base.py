from __future__ import annotations
import functools
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from tkai.services.logger_service import LoggerService

def measure_time(func):
    """Decorator to measure execution time and add 'duration_sec' in return dict (if dict)."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        t0 = time.time()
        result = func(self, *args, **kwargs)
        dt = time.time() - t0
        if isinstance(result, dict):
            result.setdefault("duration_sec", dt)
        return result
    return wrapper

def catch_exceptions(func):
    """Decorator to catch exceptions and return structured error dict."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if hasattr(self, "_logger"):
                self._logger.exception(f"Error in {func.__name__}: {e}")
            return {"ok": False, "error": str(e)}
    return wrapper

def require_loaded(func):
    """Ensure model is loaded before running."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "_loaded", False):
            return {"ok": False, "error": "Model not loaded yet. Click 'Load Model' first."}
        return func(self, *args, **kwargs)
    return wrapper

class BaseModelController(ABC):
    """
    Abstract base for model controllers.
    Demonstrates encapsulation via protected attrs: _model, _name, _category, _loaded.
    """
    def __init__(self, logger: LoggerService):
        self._logger = logger
        self._model: Any = None
        self._name: str = "Base"
        self._category: str = "Generic"
        self._loaded: bool = False

    @abstractmethod
    def load_model(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def summarize_info(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        pass
