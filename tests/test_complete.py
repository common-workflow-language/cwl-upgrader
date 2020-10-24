import filecmp

from cwlupgrader.main import main

from .util import get_data


def test_draft3_workflow(tmp_path):
    main([str(tmp_path), get_data('tests/draft-3-wf.cwl')])
    result = filecmp.cmp(get_data('tests/draft-3-wf-v1.0.cwl'), tmp_path/"draft-3-wf.cwl",
                         shallow=False)
    assert result
