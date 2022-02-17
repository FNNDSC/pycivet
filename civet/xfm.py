import abc
from pathlib import Path
from typing import Literal, TypeVar
from enum import Enum
from civet.abstract_data import Creator, DataSource
from dataclasses import dataclass


class Transformations(Enum):
    CENTER = '-center'
    TRANSLATION = '-translation'
    ROTATIONS = '-rotations'
    SCALES = '-scales'
    SHEARS = '-shears'


@dataclass(frozen=True)
class Xfm(Creator['Xfm']):
    """
    Represents a `.xfm` file created by `param2xfm`.

    `Xfm` can only represent a single `param2xfm` option.
    Would be nice to support multiple transformations in go, but it's not implemented.
    """

    transformation: Transformations
    x: float
    y: float
    z: float

    def command(self, output: str) -> list[str]:
        return ['param2xfm', '-clobber', self.transformation.name,
                self.x, self.y, self.z, output]


TransformProgram = Literal['transform_objects', 'transform_volume']
_T = TypeVar('_T', bound='Transformable')


class Transformable(DataSource[_T], abc.ABC):
    @property
    @abc.abstractmethod
    def transform_program(self) -> TransformProgram:
        """
        Specifies which program is used to transform objects of this type.
        """
        ...

    def append_xfm(self, xfm: Xfm):
        def apply_xfm(inputs: tuple[Path, Path], output: str) -> list[str | Path]:
            input_obj, saved_xfm = inputs
            return [self.transform_program, input_obj, saved_xfm, output]
        return self.append_join(apply_xfm, inputs=(self, xfm))

    def flip_x(self) -> _T:
        """
        Flip this surface along the *x*-axis.
        """
        return self.append_xfm(Xfm(Transformations.SCALES, -1, 1, 1))

    def translate_x(self, x: float) -> _T:
        """
        Translate this surface along the *x*-axis.
        """
        return self.append_xfm(Xfm(Transformations.TRANSLATION, x, 0, 0))

    def slide_left(self) -> _T:
        """
        Translate this surface 25 units to the left.
        """
        return self.translate_x(-25)

    def slide_right(self) -> _T:
        """
        Translate this surface 25 units to the right.
        """
        return self.translate_x(25)
