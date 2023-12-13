import filecmp
import logging
import re
from pathlib import Path

import pytest

from cwlupgrader.main import load_cwl_document, main, upgrade_document

from .util import get_data


def test_import_parent_directory(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Confirm that $import to a superior directory still preserves the directory structure."""
    caplog.set_level(logging.WARN)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    doc = load_cwl_document(get_data("testdata/v1.0/subdir/params.cwl"))
    upgraded = upgrade_document(doc, out_dir, out_dir, "v1.1")
    expected = load_cwl_document(get_data("testdata/v1.1/subdir/params.cwl"))
    assert upgraded == expected
    assert len(caplog.records) == 1
    assert re.search(
        re.escape(
            f"Writing file, '{tmp_path}/params_inc.yml', outside of the output directory, '{out_dir}'."
        ),
        caplog.records[0].getMessage(),
    )


def test_import_parent_directory_safe(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Confirm no warning when $import to a superior directory (but still in the current working directory) still preserves the directory structure."""
    caplog.set_level(logging.WARN)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    doc = load_cwl_document(get_data("testdata/v1.0/subdir/params.cwl"))
    upgraded = upgrade_document(doc, out_dir, tmp_path, "v1.1")
    expected = load_cwl_document(get_data("testdata/v1.1/subdir/params.cwl"))
    assert upgraded == expected
    assert len(caplog.records) == 0
