import os
from helpers import cmd


def test_out(httpbin, tmpdir):
    """Test uploading versioned file."""

    source = {
        'uri_template': httpbin + '/put',
    }

    out_dir = tmpdir.mkdir('work_dir')
    file_path = os.path.join(out_dir, '9.txt')
    with open(file_path, 'w') as out_file:
        out_file.write("9")
        out_file.close()

    output = cmd('out', source, [str(out_dir)], {}, {'file': '9.txt'})

    assert output['version'] == {'version': '9.txt'}
    assert {'name': 'url', 'value': httpbin + '/put'} in output['metadata']

