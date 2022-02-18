from pytest_mock import MockFixture
from civet.memoization import Session
from civet.abstract_data import AbstractDataCommand


def test_simple(mocker: MockFixture):
    mock_data = mocker.MagicMock(spec=AbstractDataCommand)
    mock_data.preferred_suffix = ''
    mock_data.command.return_value = ('one', 'two')

    shell = mocker.Mock()
    with Session(require_output=False, shell=shell) as s:
        s.save(mock_data, 'output')

    mock_data.command.assert_called_once()
    cache_path, = mock_data.command.call_args.args
    expected = [
        mocker.call(('one', 'two')),
        mocker.call(('cp', '-r', cache_path, 'output'))
    ]
    assert shell.call_args_list == expected


def test_reuses_cache(mocker: MockFixture):
    mock_data = mocker.MagicMock(spec=AbstractDataCommand)
    mock_data.preferred_suffix = ''
    mock_data.command.return_value = ('one', 'two')

    shell = mocker.Mock()
    with Session(require_output=False, shell=shell) as s:
        s.save(mock_data, 'output1')
        s.save(mock_data, 'output2')

    mock_data.command.assert_called_once()
    cache_path, = mock_data.command.call_args.args
    shell.assert_has_calls([
        mocker.call(('cp', '-r', cache_path, 'output1')),
        mocker.call(('cp', '-r', cache_path, 'output2'))
    ])
