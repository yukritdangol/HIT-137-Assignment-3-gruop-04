from tkai.services.io_utils import validate_prompt, ensure_dir

def test_validate_prompt():
    assert validate_prompt("hello", 10) == "hello"

def test_ensure_dir(tmp_path):
    p = ensure_dir(tmp_path / "x" / "y")
    assert p.exists()
