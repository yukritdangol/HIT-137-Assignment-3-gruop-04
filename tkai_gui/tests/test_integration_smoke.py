import pytest
from PIL import Image
from tkai.services.logger_service import LoggerService
from tkai.models.t2i_controller import TextToImageController
from tkai.models.clf_controller import ImageClassifierController

@pytest.mark.slow
def test_integration_smoke(tmp_path):
    logger = LoggerService(log_file="logs/test.log")

    t2i = TextToImageController(logger)
    assert t2i.load_model()["ok"]
    gen = t2i.run(prompt="a tiny sketch of a house", steps=1, width=128, height=128)
    assert gen["ok"]
    img_path = gen["image_path"]

    clf = ImageClassifierController(logger)
    assert clf.load_model()["ok"]
    res = clf.run(image_path=img_path, top_k=3)
    assert res["ok"]
    assert "predictions" in res
