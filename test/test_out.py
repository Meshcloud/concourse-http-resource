import os
from helpers import cmd


def write_testfile(out_dir, name):
    file_path = os.path.join(out_dir, name)
    with open(file_path, 'w') as out_file:
        out_file.write(name)
        out_file.close()


def test_out(httpbin, tmpdir):
    """Test uploading versioned file."""

    source = {
        'uri_template': httpbin + '/put',
    }

    out_dir = tmpdir.mkdir('work_dir')
    write_testfile(out_dir, '9.txt')

    output = cmd('out', source, [str(out_dir)], {}, {'file': '9.txt'})

    assert output['version'] == {'version': '9.txt'}
    assert {'name': 'url', 'value': httpbin + '/put'} in output['metadata']


def test_out_with_glob(httpbin, tmpdir):
    """Test uploading versioned file using glob pattern."""

    source = {
        'uri_template': httpbin + '/put',
    }

    out_dir = tmpdir.mkdir('work_dir')
    write_testfile(out_dir, '9.txt')
 
    output = cmd('out', source, [str(out_dir)], {}, {'file': '*.txt'})

    assert output['version'] == {'version': '9.txt'}
    assert {'name': 'url', 'value': httpbin + '/put'} in output['metadata']


def test_out_glob_multimatch(httpbin, tmpdir):
    """Test uploading versioned file using glob pattern with too many matches."""

    source = {
        'uri_template': httpbin + '/put',
    }

    out_dir = tmpdir.mkdir('work_dir')
    write_testfile(out_dir, '9.txt')
    write_testfile(out_dir, '10.txt')

    raised = False
    try:
        cmd('out', source, [str(out_dir)], {}, {'file': '*.txt'})
    except Exception:
        raised = True

    assert raised == True
