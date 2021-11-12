import filecmp
from pathlib import Path

from cwlupgrader.main import main

from .util import get_data


def test_draft3_workflow(tmp_path: Path) -> None:
    """Basic draft3 to CWL v1.1 test."""
    main([f"--dir={tmp_path}", "--v1-only", get_data("testdata/draft-3/draft-3-wf.cwl")])
    result = filecmp.cmp(
        get_data("testdata/v1.0/draft-3-wf-v1.0.cwl"),
        tmp_path / "draft-3-wf.cwl",
        shallow=False,
    )
    assert result
