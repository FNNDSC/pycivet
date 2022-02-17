import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from pathlib import Path
import tempfile
from typing import Optional
from civet.abstract_data import DataSource, NoOutputException, noop


class ConcreteDataSource(DataSource['ConcreteDataSource']):
    pass


def test_input_exists(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        DataSource(tmp_path / 'dne')


def test_save_file(tmp_path: Path):
    input_file = tmp_path / 'in'
    output_file = tmp_path / 'out'
    input_file.write_text('sample text')
    ConcreteDataSource(input_file).save(output_file)
    assert output_file.is_file()
    assert output_file.read_text() == 'sample text'


@pytest.fixture()
def noop_spy(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(wraps=noop)


def test_lazy(noop_spy: MagicMock, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    starting = ConcreteDataSource(input_file)
    appended = starting.append(noop_spy)
    noop_spy.assert_not_called()
    starting.save(tmp_path / 'whatever')
    noop_spy.assert_not_called()
    appended.save(tmp_path / 'done')
    noop_spy.assert_called_once()


def test_intermediate(noop_spy: MagicMock, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    expected_out = tmp_path / 'whatever'
    ConcreteDataSource(input_file).append(noop_spy).save(expected_out)
    noop_spy.assert_called_once()
    inter_in, inter_out = noop_spy.call_args[0]
    assert len(inter_in) == 1
    assert inter_in[0].is_relative_to(tempfile.gettempdir())
    assert inter_out == expected_out


def test_missing_output(mocker: MockerFixture, tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    run = mocker.Mock(wraps=lambda i, o: ['true', o])
    operation = ConcreteDataSource(input_file).append(lambda i, o: run(i, o))
    with pytest.raises(NoOutputException):
        operation.save(tmp_path / 'whatever')


def test_command_doesnt_include_output(tmp_path: Path):
    input_file = tmp_path / 'in'
    input_file.touch()
    cmd = ['true']
    op = ConcreteDataSource(input_file).append(lambda i, o: cmd)
    with pytest.raises(ValueError, match=r'Output path "/tmp/.+" not found in command: .+'):
        op.save(tmp_path / 'out')


def test_multiple_prev(mocker: MockerFixture, tmp_path: Path):
    r"""
    Creates a dependency tree like this:

        in1  in2  in3
         O    O    O    actual input files
         |    |    |
         O    O    O    wrapped call spies
          \   |   /
            \ | /
              O         actual output file
    """
    original_output = tmp_path / 'out'
    input1 = tmp_path / 'in1'
    input2 = tmp_path / 'in2'
    input3 = tmp_path / 'in3'
    input1.write_text('hello')
    input2.write_text('world')
    input3.write_text('seeya')

    intermediate_files: Optional[tuple[Path, Path, Path]] = None

    def check_inputs_exist(passed_inputs: tuple[Path, ...], output: str) -> list[str | Path]:
        assert len(passed_inputs) == 3
        assert passed_inputs[0].read_text() == 'hello'
        assert passed_inputs[1].read_text() == 'world'
        assert passed_inputs[2].read_text() == 'seeya'
        assert output == original_output
        nonlocal intermediate_files
        intermediate_files = passed_inputs  # share local variable to outer scope
        return ['touch', output]

    original_inputs: tuple[Path, Path, Path] = (input1, input2, input3)
    data_inputs = (ConcreteDataSource(i) for i in original_inputs)
    intermediate_spies = tuple(d.append(mocker.MagicMock(wraps=noop)) for d in data_inputs)

    with pytest.raises(ValueError, match=r'`self` must be in `inputs`'):
        ConcreteDataSource(input1).append_join(check_inputs_exist, inputs=intermediate_spies)

    op = intermediate_spies[0].append_join(check_inputs_exist, inputs=intermediate_spies)
    op.save(original_output)

    assert original_output.exists(), 'Output was not created'

    for intermediate, spy in zip(intermediate_files, intermediate_spies):
        assert not intermediate.exists(), '_Intermediate files were not removed'
        spy.run.assert_called_once_with((mocker.ANY,), intermediate)
