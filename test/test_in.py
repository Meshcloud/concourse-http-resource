from helpers import cmd


def test_in(httpbin, tmpdir):
    """Test downloading versioned file."""

    source = {
        'uri_template': httpbin + '/range/{version}',
    }

    in_dir = tmpdir.mkdir('work_dir')

    output = cmd('in', source, [str(in_dir)], {'version': '9'})

    assert output['version'] == {'version': '9'}
    assert {'name': 'url', 'value': httpbin + '/range/9'} in output['metadata']
    assert {'name': 'Content-Type', 'value': 'application/octet-stream'} in output['metadata']

    assert in_dir.join('9').exists()
    assert len(in_dir.join('9').read()) == 9
    assert in_dir.join('version').exists()
    assert in_dir.join('version').read() == '9'

def test_in_filename(httpbin, tmpdir):
    """Test downloading versioned file with predetermined filename."""

    source = {
        'uri_template': httpbin + '/range/{version}',
        'filename': 'filename_{version}',
    }

    in_dir = tmpdir.mkdir('work_dir')

    output = cmd('in', source, [str(in_dir)], {'version': '9'})

    assert output['version'] == {'version': '9'}
    assert {'name': 'url', 'value': httpbin + '/range/9'} in output['metadata']
    assert {'name': 'Content-Type', 'value': 'application/octet-stream'} in output['metadata']

    assert in_dir.join('filename_9').exists()
    assert len(in_dir.join('filename_9').read()) == 9

