from visualizer import rocket
from pathlib import Path
import pytest


@pytest.mark.parametrize("path", ["simple.ork"])
def test_import_ork_file(path: Path):
    assert rocket.import_ork_file(path) is not None
