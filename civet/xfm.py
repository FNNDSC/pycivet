import abc
from os import PathLike
import subprocess as sp
from dataclasses import dataclass
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import Literal
from civet.abstract_data import DataOperation


@dataclass(frozen=True)
class XfmTransformationMixin(DataOperation, abc.ABC):
    """
    Chains the `param2xfm` command and a `transform_objects` or `transform_volume` command.
    """

    op: str
    x: float
    y: float
    z: float

    def run(self, input: str | PathLike, output: str | PathLike):
        with self._param2xfm(self.op, self.x, self.y, self.z) as xfm:
            sp.run([self.transform_program, input, xfm, output], check=True)

    @staticmethod
    @contextmanager
    def _param2xfm(*args):
        with NamedTemporaryFile(suffix='.xfm') as f:
            sp.run(['param2xfm', '-clobber', *map(str, args), f.name], check=True)
            yield f.name

    @property
    @abc.abstractmethod
    def transform_program(self) -> Literal['transform_objects', 'transform_volume']:
        ...
