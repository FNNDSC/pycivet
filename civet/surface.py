"""
Classes for working with surface (`.obj`) files.
"""

from abc import ABC

from civet.abstract_data import DataSource, DataFile
from civet.xfm import XfmTransformationMixin


class HemisphereMixin(DataSource, ABC):
    """
    Provides a subclass with XFM-related helper functions for `.obj` files.
    """
    preferred_suffix = '.obj'

    def flip_x(self) -> 'HemisphereMixin':
        """
        Flip this surface along the *x*-axis.
        """
        return _XfmObjTransformation(self, '-scales', -1, 1, 1)

    def translate_x(self, x: float) -> 'HemisphereMixin':
        """
        Translate this surface along the *x*-axis.
        """
        return _XfmObjTransformation(self, '-translation', x, 0, 0)

    def slide_left(self) -> 'HemisphereMixin':
        """
        Translate this surface 25 units to the left.
        """
        return self.translate_x(-25)

    def slide_right(self) -> 'HemisphereMixin':
        """
        Translate this surface 25 units to the right.
        """
        return self.translate_x(25)


class _XfmObjTransformation(HemisphereMixin, XfmTransformationMixin):
    transform_program = 'transform_objects'


class ObjFile(DataFile, HemisphereMixin):
    """
    Wraps a MNI `.obj` file, which is a polygonal mesh representing
    the surface of a brain hemisphere.

    Examples
    --------

    ```python
    from civet import MNI_DATAPATH, ObjFile

    starting_model = ObjFile(MNI_DATAPATH / 'surface-extraction' / 'white_model_320.obj')
    starting_model.flip_x().slide_right().save('./output.obj')
    ```
    """
    pass
