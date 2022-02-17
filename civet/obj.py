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


@dataclass(frozen=True)
class Surface(GenericSurface['Surface']):
    """
    Represents a polygonal mesh of a brain surface in `.obj` file format.
    """
    pass
