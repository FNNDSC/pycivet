"""
Object-oriented wrappers for data paths and programs which process data.
"""
import abc
import dataclasses
import shutil
from os import path, PathLike
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ClassVar, Callable, ContextManager, TypeVar, Generic, Sequence, Iterable
import subprocess as sp
from contextlib import contextmanager, ExitStack


SubprocessRunner = Callable[[Sequence[str | PathLike]], None]


def subprocess_run(cmd: Sequence[str | PathLike]):
    sp.run(cmd, check=True)


class _ISavable(abc.ABC):
    """
    DAG node representing a source of data which can be "saved" to a given path.
    """
    @abc.abstractmethod
    def save(self, output: str | PathLike, shell: SubprocessRunner = subprocess_run,
             require_output: bool = True) -> None:
        """
        Resolve this data to a given path by executing the represented operations.

        Parameters
        ----------
        output : str | PathLike
            Path where output data should be written to
        shell : Callable[[Sequence[str | PathLike]], None]
            A function which runs a command. The default is a wrapper around
            `subprocess.run(cmd, check=True)`
        require_output : bool
            If True, checks whether the specified output path exists after
            running the program represented by this `_ISavable`. If the
            output path does not exist, raise `NoOutputException`.
        """
        ...

    @property
    def preferred_suffix(self) -> str:
        """
        :return: preferred file extension for this type
        """
        return ''


_S = TypeVar('_S', bound='_Intermediate')


class _Intermediate(_ISavable, Generic[_S], abc.ABC):
    """
    An `_Intermediate` can be saved as an intermediate file temporarily so
    that its result can be reused without recomputing it.
    """

    # Usually, but not always, (shell, require_output) are passed
    # transparently to self.save. Maybe there's a better way to reuse code?

    @contextmanager
    def intermediate_saved(self, shell: SubprocessRunner = subprocess_run,
                           require_output: bool = True) -> ContextManager[str | PathLike]:
        """
        Produce the result of this source to a temporary file.
        """
        with NamedTemporaryFile(suffix=self.preferred_suffix) as output:
            self.save(output.name, shell=shell, require_output=require_output)
            yield output.name

    @abc.abstractmethod
    def intermediate_source(self, shell: SubprocessRunner = subprocess_run,
                            require_output: bool = True) -> ContextManager[_S]:
        """
        Produce the result of this source, wrapped in its own type.
        """
        ...

#
# _CI = TypeVar('_CI', bound='CompositeIntermediate')
#
#
# class CompositeIntermediate(_Intermediate[_CI], Generic[_CI], abc.ABC):
#
#     @abc.abstractmethod
#     def resolve(self) -> _ISavable:
#         ...
#
#     def save(self, output: str | PathLike, shell: SubprocessRunner = subprocess_run,
#              require_output: bool = True) -> None:
#         self.resolve().save(output, shell, require_output)
#
#     def intermediate_source(self, shell: SubprocessRunner = subprocess_run,
#                             require_output: bool = True) -> ContextManager[_CI]:
#         yield self


_C = TypeVar('_C', bound='Creator')


class Creator(_Intermediate[_C], Generic[_C], abc.ABC):
    """
    A `Creator` represents a runnable command which creates output
    (without consuming an input path).

    In contrast to `DataSource`, it does not have any dependencies.

    """
    def save(self, output: str | PathLike, shell: SubprocessRunner = subprocess_run,
             require_output: bool = True) -> None:
        shell(self.command(output))
        if require_output and not path.exists(output):  # reuse code?
            raise NoOutputException()

    @contextmanager
    def intermediate_source(self, shell: SubprocessRunner = subprocess_run,
                            require_output: bool = True) -> ContextManager[_C]:
        yield self

    @abc.abstractmethod
    def command(self, output: str) -> Sequence[str]:
        """
        Defines the command represented by this `Creator`.
        """
        ...


@dataclasses.dataclass(frozen=True)
class _StartingFile(_ISavable):
    """
    DAG leaf containing a user-specified input file.

    In contrast to `DataSource`, a `_StartingFile` does not have dependencies (`DataSource.prev`).
    """

    starting_file: str | PathLike

    def __post_init__(self):
        if not path.isfile(self.starting_file):
            raise FileNotFoundError(f'Not a file: {self.starting_file}')

    def save(self, output: str | PathLike, shell: SubprocessRunner = subprocess_run,
             require_output: bool = True) -> None:
        """
        Copy this input file to a path.
        """
        shutil.copyfile(self.starting_file, output)


RunFunction = Callable[[tuple[Path, ...], str], Sequence[str | PathLike]]
"""
A `RunFunction` is a function which, given one or more inputs and one output path,
produces a subprocess command that creates the given output path when ran.

The returned value *must* include the given output path as a member.
"""

_D = TypeVar('_D', bound='DataSource')


def noop(inputs: tuple[Path, ...], output: str | PathLike) -> Sequence[str | PathLike]:
    """
    A `RunFunction` which wraps the `cp` command. It denotes that the `DataSource` does
    not represent a data-processing program.
    """
    if len(inputs) != 1:
        raise ValueError(f'Expected single input. Got: {inputs}')
    return ['cp', inputs[0], output]


@dataclasses.dataclass(frozen=True)
class DataSource(_Intermediate[_D], Generic[_D], abc.ABC):
    """
    A `DataSource` represents a program which processes data. It is a recursive data
    structure: `DataSource` are nodes of a dependency tree, where the root is the
    output path given by `DataSource.save`. Leaves of the tree are input files
    created by passing `str | PathLike` to a constructor of a `DataSource` subclass.
    The dependency tree is constructed from leaves to root, i.e. the code you write
    should describe input files first and how output files are composed of input files.

    `DataSource` is meant to be used as a superclass to classes which represent file
    types and define filetype-specific functionality. Such a subclass should pass
    themselves as the generic type to `DataSource`:

    ```python
    class ConcreteDataSource(DataSource['ConcreteDataSource']):
        pass

    ConcreteDataSource('input.txt').save('output.txt')
    ```

    Its operation is lazy and invocations represented by `DataSource` are only run when
    `DataSource.save` is called.
    """

    input: dataclasses.InitVar[str | PathLike | _ISavable | Iterable[_ISavable]]
    """
    Input data for this `DataSource`.
    """
    prev: ClassVar[tuple[_ISavable, ...]]
    """
    The dependencies of this `DataSource`.
    """
    run: RunFunction = noop
    """
    A function which defines the program for this `DataSource`.
    """

    def __post_init__(self, input: str | PathLike | _ISavable | Iterable[_ISavable]):
        if isinstance(input, Iterable):
            if not all(map(lambda i: isinstance(i, _ISavable), input)):
                raise TypeError(f'input contains invalid types: {input}')
            object.__setattr__(self, 'prev', input)
        elif isinstance(input, _ISavable):
            object.__setattr__(self, 'prev', (input,))
        elif isinstance(input, str) or isinstance(input, PathLike):
            object.__setattr__(self, 'prev', (_StartingFile(input),))
        else:
            raise TypeError(f'{input} ({type(input)}')

    def save(self, output: str | PathLike, shell: SubprocessRunner = subprocess_run,
             require_output: bool = True) -> None:
        """
        Call `save` on all previous `DataSource` which this depends on,
        writing intermediate outputs to temporary files. After that,
        invoke this object's `run` method on the given `output` path.

        Parameters
        ----------
        output : str | PathLike
            Path where output data should be written to
        shell : Callable[[Sequence[str | PathLike]], None]
            A function which runs a command. The default is a wrapper around
            `subprocess.run(cmd, check=True)`
        require_output : bool
            If True, checks whether the specified output path exists after
            running the program represented by this `_ISavable`. If the
            output path does not exist, raise `NoOutputException`.
        """
        file_cms = tuple(NamedTemporaryFile(suffix=p.preferred_suffix) for p in self.prev)
        with ExitStack() as stack:
            real_input_names = tuple(Path(stack.enter_context(f).name) for f in file_cms)
            for dependency, prev_output in zip(self.prev, real_input_names):
                dependency.save(prev_output, shell=shell, require_output=require_output)
            cmd = self.run(real_input_names, output)
            if output not in cmd:
                raise ValueError(f'Output path "{output}" not found in command: {cmd}')
            shell(cmd)

        if require_output and not path.exists(output):
            raise NoOutputException()

    @contextmanager
    def intermediate_saved(self, shell: SubprocessRunner = subprocess_run,
                           require_output: bool = True) -> ContextManager[str | PathLike]:
        """
        Produce the result of this source to a temporary file.
        """
        with NamedTemporaryFile(suffix=self.preferred_suffix) as output:
            self.save(output.name, shell=shell, require_output=require_output)
            yield output.name

    @contextmanager
    def intermediate_source(self, shell: SubprocessRunner = subprocess_run,
                            require_output: bool = True) -> ContextManager[_D]:
        """
        Produce the result of this source, wrapped in its own type.
        """
        with self.intermediate_saved(shell, require_output) as saved_file:
            yield dataclasses.replace(self, input=saved_file, run=noop)

    def append(self, run: RunFunction) -> _D:
        """
        Create a `DataSource` with the same type as this, where the new `DataSource`
        takes this one as its input.

        In other words, the given program is added to the dependency tree linearly,
        such that the output of this program is used as the input for the given program.

        Returns
        -------
        next : the `DataSource` representing the just-added program
        """
        return self.append_join(run, (self,))

    def append_join(self, run: RunFunction, inputs: tuple[_ISavable, ...] = None) -> _D:
        """
        Create a `DataSource` with the same type as this, where the new `DataSource`
        takes this and other `DataSource` as inputs.
        """
        if self not in inputs:
            raise ValueError('`self` must be in `inputs`')
        return dataclasses.replace(self, input=inputs, run=run)


class NoOutputException(Exception):
    """
    Raised when a program fails to write an output file to its given output path.
    """
    pass
