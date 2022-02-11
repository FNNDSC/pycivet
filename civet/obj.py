"""
Classes for working with surface (`.obj`) files.

Examples
--------

```python
from civet import Surface
from civet.extraction.starting_models import WHITE_MODEL_320

starting_model = WHITE_MODEL_320
starting_model.flip_x().slide_right().save('./output.obj')
```
"""
from typing import TypeVar, Generic
from dataclasses import dataclass

from civet.xfm import Transformable

_S = TypeVar('_S', bound='GenericSurface')


@dataclass(frozen=True)
class GenericSurface(Transformable[_S], Generic[_S]):
    """
    Provides subclasses with helper functions which operate on `.obj` files.
    """

    preferred_suffix = '.obj'
    transform_program = 'transform_objects'

    def flip_x(self) -> _S:
        """
        Flip this surface along the *x*-axis.
        """
        return self.append_xfm('-scales', -1, 1, 1)

    def translate_x(self, x: float) -> _S:
        """
        Translate this surface along the *x*-axis.
        """

        return self.append_xfm('-translation', x, 0, 0)

    def slide_left(self) -> _S:
        """
        Translate this surface 25 units to the left.
        """
        return self.translate_x(-25)

    def slide_right(self) -> _S:
        """
        Translate this surface 25 units to the right.
        """
        return self.translate_x(25)


@dataclass(frozen=True)
class Surface(GenericSurface['Surface']):
    """
    Represents a polygonal mesh of a brain surface in `.obj` file format.
    """
    pass
