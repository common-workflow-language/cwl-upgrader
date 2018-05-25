import filecmp
from cwlupgrader.main import main
from .util import get_data


def test_draft3_workflow(tmpdir, capsys):
    main([get_data('tests/draft-3-wf.cwl')])
    test_path = tmpdir.join("test.cwl")
    with test_path.open('w') as outfile:
        outfile.write(capsys.readouterr().out)
        outfile.flush()
        outfile.close()
    result = filecmp.cmp(get_data('tests/draft-3-wf-v1.0.cwl'), str(test_path),
                         shallow=False)
    assert result
