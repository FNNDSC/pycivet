from civet.mask import GenericMask
from civet.extraction.surfaces import IrregularSurface
from civet.extraction.starting_models import WHITE_MODEL_320
from enum import Enum
from typing import TypeVar, Generic, Optional


class Side(Enum):
    LEFT = 'left'
    RIGHT = 'right'


_M = TypeVar('_M', bound='GenericHemisphere')


class GenericHemisphere(GenericMask[_M], Generic[_M]):
    """
    Provides helper functions which operate on hemisphere masks (`.mnc` files).
    """

    def just_sphere_mesh(self, side: Optional[Side]) -> IrregularSurface:
        """
        Extract surface using `sphere_mesh` (marching-cubes).
        """
        # https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L118-L135
        initial_model = WHITE_MODEL_320
        if side is Side.LEFT:
            sided_model = initial_model.slide_left()
        elif side is Side.RIGHT:
            sided_model = initial_model.flip_x().slide_right()
        else:
            sided_model = initial_model

        return self.sphere_mesh_from(sided_model)

    def sphere_mesh_from(self, initial_model: ...) -> IrregularSurface:
        """
        Prepare mask for maching cubes using given model surface as a starting point,
        and then execute `sphere_mesh`.
        """
        ...


class HemisphereMask(GenericHemisphere['HemisphereMask']):
    """
    Wraps a `.mnc` file representing a binary mask for a brain hemisphere.
    """
    pass
