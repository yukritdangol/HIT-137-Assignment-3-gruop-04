import pytest
from tkai.services.logger_service import LoggerService
from tkai.models.t2i_controller import TextToImageController
from tkai.models.clf_controller import ImageClassifierController

# These are smoke-like tests to ensure controllers construct and can call load_model()
# Actual model downloads may be slow; run selectively if desired.

@pytest.mark.slow
def test_t2i_load():
    logger = LoggerService(log_file="logs/test.log")
    t2i = TextToImageController(logger)
    res = t2i.load_model()
    assert res["ok"] is True

@pytest.mark.slow
def test_clf_load():
    logger = LoggerService(log_file="logs/test.log")
    clf = ImageClassifierController(logger)
    res = clf.load_model()
    assert res["ok"] is True
