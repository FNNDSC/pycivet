"""
Wrappers for data paths and programs which process data.
"""
import abc
import shutil
from dataclasses import dataclass
from os import path, PathLike
from tempfile import NamedTemporaryFile


class DataSource(abc.ABC):
    """
    A `DataSource` is something which can provide data, such as an
    input file, input directory, a command which processes input, or
    a chain of commands. In the latter case, the commands are executed
    "lazily" and will only actually run when `DataSource.save` is called.
    Intermediate files are written to temporary files and then removed.
    """

    preferred_suffix: str = ''
    """
    Preferred output file suffix.
    """

    @abc.abstractmethod
    def save(self, output: PathLike | str) -> None:
        """
        Resolve this data to a given path by executing the
        represented operations.
        """
        ...


@dataclass(frozen=True)
class DataFile(DataSource):
    """
    A wrapper around a file path.
    """
    input: str | PathLike

    def __post_init__(self):
        if not path.exists(self.input):
            raise FileNotFoundError(f'Input does not exist: {self.input}')

    def save(self, output: PathLike | str) -> None:
        """
        Copy the file to a given destination.
        """
        shutil.copyfile(self.input, output)


@dataclass(frozen=True)
class DataOperation(DataSource, abc.ABC):
    """
    A recursive data structure representing an operation to perform on input data.
    """

    input: DataSource

    @abc.abstractmethod
    def run(self, input: str | PathLike, output: str | PathLike):
        ...

    def save(self, output: str | PathLike):
        """
        Perform the operation on its input data.
        """
        with NamedTemporaryFile(suffix=self.input.preferred_suffix) as real_input:
            self.input.save(real_input.name)
            self.run(real_input.name, output)
