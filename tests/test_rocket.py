from pathlib import Path

import pytest

from visualizer import rocket


@pytest.mark.parametrize("path", ["simple.ork"])
def test_import_ork_file(path: Path):
    assert rocket.import_ork_file(path) is not None
