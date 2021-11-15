import filecmp
from pathlib import Path

from cwlupgrader.main import load_cwl_document, main, upgrade_document

from .util import get_data


def test_draft3_workflow(tmp_path: Path) -> None:
    """Basic draft3 to CWL v1.1 test."""
    main([f"--dir={tmp_path}", "--v1-only", get_data("testdata/draft-3/wf.cwl")])
    result = filecmp.cmp(
        get_data("testdata/v1.0/wf.cwl"),
        tmp_path / "wf.cwl",
        shallow=False,
    )
    assert result


def test_invalid_target(tmp_path: Path) -> None:
    """Test for invalid target version"""
    doc = load_cwl_document(get_data("testdata/v1.0/listing_deep1.cwl"))
    result = upgrade_document(doc, str(tmp_path), "invalid-version")
    assert result is None


def test_v1_0_to_v1_1(tmp_path: Path) -> None:
    """Basic CWL v1.0 to CWL v1.1 test."""
    doc = load_cwl_document(get_data("testdata/v1.0/listing_deep1.cwl"))
    upgraded = upgrade_document(doc, str(tmp_path), "v1.1")
    assert doc == upgraded


def test_v1_1_to_v1_2(tmp_path: Path) -> None:
    """Basic CWL v1.1 to CWL v1.2 test."""
    doc = load_cwl_document(get_data("testdata/v1.1/listing_deep1.cwl"))
    upgraded = upgrade_document(doc, str(tmp_path), "v1.2")
    assert doc == upgraded


def test_packed_graph(tmp_path: Path) -> None:
    """Test packed document with $graph."""
    main([f"--dir={tmp_path}", "--v1.1-only", get_data("testdata/v1.0/conflict-wf.cwl")])
    assert filecmp.cmp(
        get_data("testdata/v1.1/conflict-wf.cwl"),
        tmp_path / "conflict-wf.cwl",
        shallow=False,
    )
