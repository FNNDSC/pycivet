from typing import Generic, TypeVar
from civet.obj import GenericSurface


_IS = TypeVar('_IS', bound='GenericIrregularSurface')
_RS = TypeVar('_RS', bound='GenericSurface')


class GenericIrregularSurface(GenericSurface[_IS], Generic[_IS]):
    """
    Provides subclasses with helper functions which can operate on
    a polygonal mesh with non-standard connectivity.
    """
    pass


class IrregularSurface(GenericIrregularSurface['IrregularSurface']):
    """
    Represents a mesh (`.obj`) with irregular connectivity.
    """
    pass


class GenericRegularSurface(GenericSurface[_RS], Generic[_RS]):
    """
    Provides subclasses with helper functions which can operate on
    a polygonal mesh of standard connectivity.
    """
    pass


class RegularSurface(GenericRegularSurface['RegularSurface']):
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
