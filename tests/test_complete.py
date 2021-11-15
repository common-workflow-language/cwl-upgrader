import filecmp
from pathlib import Path

from cwlupgrader.main import load_cwl_document, upgrade_all_documents, upgrade_document

from .util import get_data


# def test_draft3_workflow(tmp_path: Path) -> None:
#     """Basic draft3 to CWL v1.1 test."""
#     main([f"--dir={tmp_path}", "--v1-only", get_data("testdata/draft-3/wf.cwl")])
#     result = filecmp.cmp(
#         get_data("testdata/v1.0/wf.cwl"),
#         tmp_path / "wf.cwl",
#         shallow=False,
#     )
#     assert result

def test_upgrade_all_documents(tmp_path: Path) -> None:
    """Test `upgrade_all_documents`"""
    upgrade_all_documents(
        base_dir=get_data("testdata/draft-3"),
        output_dir=tmp_path,
        target_version="v1.0",
        overwrite=True)
    result = filecmp.cmp(
        get_data("testdata/v1.0/wf.cwl"),
        tmp_path / "wf.cwl",
        shallow=False,
    )
    assert result


def test_invalid_target() -> None:
    """Test for invalid target version"""
    doc = load_cwl_document(get_data("testdata/v1.0/listing_deep1.cwl"))
    result = upgrade_document(doc, "invalid-version")
    assert result is None


def test_v1_0_to_v1_1() -> None:
    """Basic CWL v1.0 to CWL v1.1 test."""
    doc = load_cwl_document(get_data("testdata/v1.0/listing_deep1.cwl"))
    upgraded = upgrade_document(doc, "v1.1")
    assert doc == upgraded


def test_v1_1_to_v1_2() -> None:
    """Basic CWL v1.1 to CWL v1.2 test."""
    doc = load_cwl_document(get_data("testdata/v1.1/listing_deep1.cwl"))
    upgraded = upgrade_document(doc, "v1.2")
    assert doc == upgraded
