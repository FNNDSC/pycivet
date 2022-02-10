import abc
import pytest
from os import PathLike, path
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from civet.abstract_data import DataSource, DataFile, DataOperation
from dataclasses import dataclass
import tempfile


def test_path_exists(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        DataFile(tmp_path / 'dne')


@patch('shutil.copyfile')
def test_save_file(mock_copyfile: MagicMock, tmp_path: Path):
    @dataclass(frozen=True)
    class ExampleOperation(DataOperation):
        spy = Mock()

        def run(self, input: str | PathLike, output: str | PathLike):
            assert path.exists(input)
            self.spy.run(input, output)

    ExampleOperation(DataFile(tmp_path)).save('last_output')
    mock_copyfile.assert_called_once()
    src, dst = mock_copyfile.call_args[0]
    assert tmp_path == src
    assert dst.startswith(tempfile.gettempdir())
    ExampleOperation.spy.run.assert_called_once_with(dst, 'last_output')


def test_lazy(tmp_path: Path):

    class ExampleMixin(DataSource, abc.ABC):
        def do_something(self, _: int):
            return ExampleOperation(self)

    @dataclass(frozen=True)
    class ExampleOperation(DataOperation, ExampleMixin):
        spy = Mock()

        def run(self, input: str | PathLike, output: str | PathLike):
            self.spy.run(input, output)

    class ExampleFile(DataFile, ExampleMixin):
        spy = Mock()

        def save(self, output: PathLike | str) -> None:
            self.spy.save(output)

    # object.__setattr__(ExampleOperation, 'run', Mock)

    example = ExampleFile(tmp_path)
    # object.__setattr__(example, 'save', Mock)
    do_op = example.do_something(123)
    ExampleOperation.spy.save.assert_not_called()
    ExampleFile.spy.run.assert_not_called()

    do_op.save('result.out')
    ExampleFile.spy.save.assert_called_once()
    copied_input, = ExampleFile.spy.save.call_args[0]
    ExampleOperation.spy.run.assert_called_once_with(copied_input, 'result.out')

    ExampleFile.spy.reset_mock()
    ExampleOperation.spy.reset_mock()
    do_op_again = do_op.do_something(300)
    ExampleOperation.spy.save.assert_not_called()
    ExampleFile.spy.run.assert_not_called()
    do_op_again.save('result.out')
    assert len(ExampleFile.spy.method_calls) == 1
    assert len(ExampleOperation.spy.method_calls) == 2
