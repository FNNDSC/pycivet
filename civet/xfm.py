import abc
from os import PathLike
import subprocess as sp
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import Literal, TypeVar, Generic
from civet.abstract_data import DataSource


@contextmanager
def param2xfm(*args):
    with NamedTemporaryFile(suffix='.xfm') as f:
        sp.run(['param2xfm', '-clobber', *map(str, args), f.name], check=True)
        yield f.name


TransformProgram = Literal['transform_objects', 'transform_volume']


def xfm_transform(transform_program: TransformProgram,
                  op: str, x: float, y: float, z: float,
                  input: str | PathLike, output: str | PathLike):
    with param2xfm(op, x, y, z) as xfm:
        sp.run([transform_program, input, xfm, output], check=True)


_T = TypeVar('_T', bound='Transformable')


class Transformable(DataSource[_T], abc.ABC):
    def append_xfm(self, op: str, x: float, y: float, z: float):
        def curried_xfm(input: str | PathLike, output: str | PathLike) -> None:
            xfm_transform(self.transform_program, op, x, y, z, input, output)
        return self.append(curried_xfm)

    @property
    @abc.abstractmethod
    def transform_program(self) -> TransformProgram:
        ...
