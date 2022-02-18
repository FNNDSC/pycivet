"""
Further subtyping of `GenericSurface` to be either an `IrregularSurface`
or `RegularSurface` depending on mesh connectivity.
"""

from typing import TypeVar, Generic
from civet.obj import GenericSurface

_IS = TypeVar('_IS', bound='GenericIrregularSurface')
_RS = TypeVar('_RS', bound='GenericRegularSurface')


class IrregularSurface(GenericSurface[_IS], Generic[_IS]):
    """
    Represents a mesh (`.obj`) with irregular connectivity.
    """
    pass


class RegularSurface(GenericSurface[_RS], Generic[_RS]):
    """
    Represents a mesh (`.obj`) with standard connectivity.

    Typically, standard connectivity means 81,920 triangles, 41,962
    vertices. By convention, the file name for such a surface should
    have the suffix `_81920.obj`.

    A general definition for "standard connectivity" would be a
    polygonal mesh of *N* triangles where 320 and 4 are common
    denominators of *N*.
    """
    pass
