import shutil
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _copy_summarize_for_cli_tests(request, tmp_path):
    if "TestCLIOutput" not in request.node.nodeid:
        return
    src = Path(__file__).parent / "summarize_results.py"
    if src.exists():
        shutil.copy2(src, tmp_path / "summarize_results.py")
