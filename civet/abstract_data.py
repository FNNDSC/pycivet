"""
Object-oriented wrappers for data paths and programs which process data.
"""
import abc
import dataclasses
import shutil
from os import path, PathLike
from tempfile import NamedTemporaryFile
from typing import ClassVar, Callable, ContextManager, TypeVar, Generic
from contextlib import contextmanager


class _ISavable(abc.ABC):
    """
    Linked-list node.
    """
    @abc.abstractmethod
    def save(self, output: PathLike | str) -> None:
        """
        Resolve this data to a given path by executing the represented operations.
        """
        ...

    @property
    def preferred_suffix(self) -> str:
        """
        :return: preferred file extension for this type
        """
        return ''


@dataclasses.dataclass(frozen=True)
class _StartingFile(_ISavable):
    """
    Linked-list front node.
    """

    starting_file: str | PathLike

    def __post_init__(self):
        if not path.isfile(self.starting_file):
            raise FileNotFoundError(f'Not a file: {self.starting_file}')

    def save(self, output: PathLike | str) -> None:
        """
        Copy this input file to a path.
        """
        shutil.copyfile(self.starting_file, output)


RunFunction = Callable[[str | PathLike, str | PathLike], None]
_D = TypeVar('_D', bound='DataSource')


@dataclasses.dataclass(frozen=True)
class DataSource(_ISavable, Generic[_D]):
    """
    A `DataSource` is a node of a linked-list representing a chain of programs
    which process data. It itself represents a data-processing program. The
    front of this linked-list is an input file.

    Its operation is lazy and the programs are only run when `DataSource.save`
    is called.
    """

    input: dataclasses.InitVar[str | PathLike | _ISavable]
    """
    Input data for this `DataSource`.
    """
    prev: ClassVar[_ISavable]
    run: RunFunction = shutil.copyfile
    """
    A function which defines the program for this `DataSource`.
    """
    require_output: bool = True
    """
    If `True`, raises `NoOutputException` when calling `run` does not create
    output at the path it was given.
    """

    def __post_init__(self, input: str | PathLike | _ISavable):
        if isinstance(input, _ISavable):
            object.__setattr__(self, 'prev', input)
        elif isinstance(input, str) or isinstance(input, PathLike):
            object.__setattr__(self, 'prev', _StartingFile(input))
        else:
            raise TypeError(f'{input} ({type(input)}')

    def save(self, output: str | PathLike):
        """
        Call `save` on all previous `DataSource` before this one, writing
        intermediate outputs to temporary files. After that, invoke this
        object's `run` method on the given `output` path.
        """
        with NamedTemporaryFile(suffix=self.prev.preferred_suffix) as real_input:
            self.prev.save(real_input.name)
            self.run(real_input.name, output)

        if self.require_output and not path.exists(output):
            raise NoOutputException()

    @contextmanager
    def intermediate_saved(self) -> ContextManager[str | PathLike]:
        """
        Produce the result of this source to a temporary file.
        """
        with NamedTemporaryFile(suffix=self.preferred_suffix) as output:
            self.save(output.name)
            yield output.name

    @contextmanager
    def intermediate_source(self) -> ContextManager[_D]:
        """
        Produce the result of this source, wrapped in its own type.
        """
        with self.intermediate_saved() as saved_file:
            yield dataclasses.replace(self, input=saved_file, run=shutil.copyfile)

    def append(self, run: RunFunction):
        """
        Append a program to this linked-list.

        Returns
        -------
        next : the `DataSource` representing the just-added program
        """
        return dataclasses.replace(self, input=self, run=run)


class NoOutputException(Exception):
    """
    Raised when a program fails to write an output file to its given output path.
    """
    pass
