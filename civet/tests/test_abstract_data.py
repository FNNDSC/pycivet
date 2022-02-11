import shutil

import pytest
from pytest_mock import MockerFixture
from pathlib import Path
import tempfile
from civet.abstract_data import DataSource, NoOutputException


def test_path_exists(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        DataSource(tmp_path / 'dne')


def test_save_file(tmp_path: Path):
    input_file = tmp_path / 'in'
    output_file = tmp_path / 'out'
    input_file.write_text('sample text')
    DataSource(input_file).save(output_file)
    assert output_file.is_file()
    assert output_file.read_text() == 'sample text'


def test_lazy(mocker: MockerFixture, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    starting = DataSource(input_file)
    run = mocker.Mock(wraps=shutil.copyfile)
    appended = starting.append(lambda i, o: run(i, o))
    run.assert_not_called()
    starting.save(tmp_path / 'whatever')
    run.assert_not_called()
    appended.save(tmp_path / 'done')
    run.assert_called_once()


def test_intermediate(mocker: MockerFixture, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    expected_out = tmp_path / 'whatever'
    run = mocker.Mock(wraps=shutil.copyfile)
    DataSource(input_file).append(lambda i, o: run(i, o)).save(expected_out)
    run.assert_called_once()
    inter_in, inter_out = run.call_args[0]
    assert inter_in.startswith(tempfile.gettempdir())
    assert inter_out == expected_out


def test_missing_output(mocker: MockerFixture, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    run = mocker.Mock()
    operation = DataSource(input_file).append(lambda i, o: run(i, o))
    with pytest.raises(NoOutputException):
        operation.save(tmp_path / 'whatever')
