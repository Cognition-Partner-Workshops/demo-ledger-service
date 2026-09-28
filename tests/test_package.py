import tomllib
from pathlib import Path

import ledger


def test_package_version_matches_pyproject():
    pyproject = tomllib.loads((Path(__file__).parent.parent / "pyproject.toml").read_text())
    assert ledger.__version__ == pyproject["project"]["version"]
